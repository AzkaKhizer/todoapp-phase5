"""Reminder service for scheduling and managing task reminders.

This service handles:
- Scheduling reminders when tasks with due dates are created/updated
- Cancelling reminders when tasks are completed or deleted
- Querying due reminders for the scheduler to process
- Updating reminder status after delivery attempts
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.dapr.pubsub import get_pubsub
from app.events.schemas import ReminderDueData, ReminderDueEvent
from app.events.topics import KafkaTopic
from app.models.reminder import Reminder, ReminderStatus
from app.models.task import Task

logger = logging.getLogger(__name__)

# Maximum retry attempts for failed reminders
MAX_RETRY_ATTEMPTS = 3

# Delay between retry attempts (exponential backoff: 1min, 2min, 4min)
RETRY_DELAY_MINUTES = [1, 2, 4]


class ReminderService:
    """Service for managing task reminders.

    The reminder workflow:
    1. When a task is created/updated with due_date + reminder_offset_minutes,
       a Reminder record is created with scheduled_time = due_date - offset
    2. The Dapr cron binding triggers check_due_reminders() every minute
    3. Due reminders are published to Kafka (reminder.due topic)
    4. A consumer processes the event and delivers the notification
    5. Reminder status is updated to SENT or FAILED
    6. Failed reminders are retried up to MAX_RETRY_ATTEMPTS times
    """

    def __init__(self, session: AsyncSession):
        """Initialize the reminder service.

        Args:
            session: Database session for queries
        """
        self.session = session
        self._pubsub = get_pubsub()

    async def schedule_reminder(
        self,
        task: Task,
        delivery_channel: str = "in-app",
    ) -> Optional[Reminder]:
        """Schedule a reminder for a task based on its due date and offset.

        If the task already has a pending reminder, it will be updated.
        If the task has no due_date or reminder_offset_minutes, no reminder is created.

        Args:
            task: The task to schedule a reminder for
            delivery_channel: How to deliver the reminder (in-app, email, push)

        Returns:
            The created/updated Reminder, or None if no reminder needed
        """
        # No reminder if task has no due date or offset
        if not task.due_date or task.reminder_offset_minutes is None:
            logger.debug(f"Task {task.id} has no due date or reminder offset, skipping reminder")
            return None

        # Calculate scheduled time
        scheduled_time = task.due_date - timedelta(minutes=task.reminder_offset_minutes)

        # Don't schedule reminders in the past
        now = datetime.now(timezone.utc)
        if scheduled_time < now:
            logger.debug(f"Reminder time {scheduled_time} is in the past, skipping")
            return None

        # Check for existing pending reminder for this task
        existing = await self._get_pending_reminder(task.id)

        if existing:
            # Update existing reminder
            existing.scheduled_time = scheduled_time
            existing.delivery_channel = delivery_channel
            self.session.add(existing)
            await self.session.commit()
            await self.session.refresh(existing)
            logger.info(f"Updated reminder {existing.id} for task {task.id}")
            return existing

        # Create new reminder
        reminder = Reminder(
            task_id=task.id,
            user_id=task.user_id,
            scheduled_time=scheduled_time,
            status=ReminderStatus.PENDING,
            delivery_channel=delivery_channel,
        )
        self.session.add(reminder)
        await self.session.commit()
        await self.session.refresh(reminder)

        logger.info(f"Scheduled reminder {reminder.id} for task {task.id} at {scheduled_time}")
        return reminder

    async def cancel_reminder(self, task_id: UUID) -> bool:
        """Cancel any pending reminder for a task.

        Called when a task is completed or deleted.

        Args:
            task_id: The task ID to cancel reminders for

        Returns:
            True if a reminder was cancelled, False otherwise
        """
        reminder = await self._get_pending_reminder(task_id)

        if reminder:
            reminder.status = ReminderStatus.CANCELLED
            self.session.add(reminder)
            await self.session.commit()
            logger.info(f"Cancelled reminder {reminder.id} for task {task_id}")
            return True

        return False

    async def get_due_reminders(
        self,
        limit: int = 100,
        include_retries: bool = True,
    ) -> list[Reminder]:
        """Get reminders that are due for delivery.

        Returns reminders where:
        - Status is PENDING and scheduled_time <= now, OR
        - Status is FAILED, retry_count < MAX_RETRY_ATTEMPTS, and enough time has passed

        Args:
            limit: Maximum number of reminders to return
            include_retries: Whether to include failed reminders for retry

        Returns:
            List of due reminders
        """
        now = datetime.now(timezone.utc)

        # Base condition: pending reminders that are due
        conditions = [
            and_(
                Reminder.status == ReminderStatus.PENDING,
                Reminder.scheduled_time <= now,
            )
        ]

        # Add retry condition
        if include_retries:
            # For retries, we need to check if enough time has passed
            # This is simplified - ideally we'd calculate per-reminder
            conditions.append(
                and_(
                    Reminder.status == ReminderStatus.FAILED,
                    Reminder.retry_count < MAX_RETRY_ATTEMPTS,
                )
            )

        statement = (
            select(Reminder)
            .where(or_(*conditions))
            .order_by(Reminder.scheduled_time)
            .limit(limit)
        )

        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def process_due_reminders(self) -> int:
        """Process all due reminders by publishing them to Kafka.

        This method is called by the Dapr cron binding handler.

        Returns:
            Number of reminders processed
        """
        reminders = await self.get_due_reminders()
        processed = 0

        for reminder in reminders:
            try:
                # Get the associated task
                task = await self._get_task(reminder.task_id)
                if not task:
                    logger.warning(f"Task {reminder.task_id} not found for reminder {reminder.id}")
                    reminder.status = ReminderStatus.CANCELLED
                    reminder.error_message = "Task not found"
                    self.session.add(reminder)
                    continue

                # If task is already completed, cancel the reminder
                if task.is_complete:
                    reminder.status = ReminderStatus.CANCELLED
                    reminder.error_message = "Task already completed"
                    self.session.add(reminder)
                    continue

                # Publish reminder due event
                await self._publish_reminder_event(reminder, task)
                processed += 1

            except Exception as e:
                logger.error(f"Failed to process reminder {reminder.id}: {e}")
                await self._mark_reminder_failed(reminder, str(e))

        await self.session.commit()
        logger.info(f"Processed {processed} reminders")
        return processed

    async def mark_reminder_sent(self, reminder_id: UUID) -> bool:
        """Mark a reminder as successfully sent.

        Args:
            reminder_id: The reminder ID

        Returns:
            True if updated, False if not found
        """
        statement = select(Reminder).where(Reminder.id == reminder_id)
        result = await self.session.execute(statement)
        reminder = result.scalar_one_or_none()

        if not reminder:
            return False

        reminder.status = ReminderStatus.SENT
        reminder.sent_at = datetime.now(timezone.utc)
        self.session.add(reminder)
        await self.session.commit()

        logger.info(f"Marked reminder {reminder_id} as sent")
        return True

    async def mark_reminder_failed(
        self,
        reminder_id: UUID,
        error_message: str,
    ) -> bool:
        """Mark a reminder as failed and schedule retry if applicable.

        Args:
            reminder_id: The reminder ID
            error_message: Error description

        Returns:
            True if updated, False if not found
        """
        statement = select(Reminder).where(Reminder.id == reminder_id)
        result = await self.session.execute(statement)
        reminder = result.scalar_one_or_none()

        if not reminder:
            return False

        await self._mark_reminder_failed(reminder, error_message)
        await self.session.commit()
        return True

    async def get_reminder_by_id(self, reminder_id: UUID) -> Optional[Reminder]:
        """Get a reminder by its ID.

        Args:
            reminder_id: The reminder ID

        Returns:
            The reminder or None
        """
        statement = select(Reminder).where(Reminder.id == reminder_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_reminders_for_task(self, task_id: UUID) -> list[Reminder]:
        """Get all reminders for a specific task.

        Args:
            task_id: The task ID

        Returns:
            List of reminders for the task
        """
        statement = (
            select(Reminder)
            .where(Reminder.task_id == task_id)
            .order_by(Reminder.created_at.desc())
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get_pending_reminders_for_user(
        self,
        user_id: str,
        limit: int = 50,
    ) -> list[Reminder]:
        """Get pending reminders for a user.

        Args:
            user_id: The user ID
            limit: Maximum number to return

        Returns:
            List of pending reminders
        """
        statement = (
            select(Reminder)
            .where(
                and_(
                    Reminder.user_id == user_id,
                    Reminder.status == ReminderStatus.PENDING,
                )
            )
            .order_by(Reminder.scheduled_time)
            .limit(limit)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    # Private helper methods

    async def _get_pending_reminder(self, task_id: UUID) -> Optional[Reminder]:
        """Get the pending reminder for a task, if any."""
        statement = select(Reminder).where(
            and_(
                Reminder.task_id == task_id,
                Reminder.status == ReminderStatus.PENDING,
            )
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def _get_task(self, task_id: UUID) -> Optional[Task]:
        """Get a task by ID."""
        statement = select(Task).where(Task.id == task_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def _publish_reminder_event(self, reminder: Reminder, task: Task) -> None:
        """Publish a reminder due event to Kafka."""
        event_data = ReminderDueData(
            reminder_id=reminder.id,
            task_id=task.id,
            user_id=task.user_id,
            task_title=task.title,
            task_due_date=task.due_date,
            delivery_channel=reminder.delivery_channel,
            attempt=reminder.retry_count + 1,
        )

        event = ReminderDueEvent(data=event_data)

        await self._pubsub.publish(
            topic=KafkaTopic.REMINDER_DUE.value,
            data=event,
            metadata={"user_id": task.user_id},
        )

        logger.info(f"Published reminder due event for reminder {reminder.id}")

    async def _mark_reminder_failed(
        self,
        reminder: Reminder,
        error_message: str,
    ) -> None:
        """Mark a reminder as failed internally."""
        reminder.retry_count += 1
        reminder.error_message = error_message

        if reminder.retry_count >= MAX_RETRY_ATTEMPTS:
            reminder.status = ReminderStatus.FAILED
            logger.warning(
                f"Reminder {reminder.id} exceeded max retries ({MAX_RETRY_ATTEMPTS})"
            )
        else:
            # Schedule for retry - will be picked up on next cron run
            logger.info(
                f"Reminder {reminder.id} failed, attempt {reminder.retry_count}/{MAX_RETRY_ATTEMPTS}"
            )

        self.session.add(reminder)


# Dependency injection helper
async def get_reminder_service(session: AsyncSession) -> ReminderService:
    """Create a ReminderService instance.

    Usage in FastAPI:
        @router.get("/reminders")
        async def list_reminders(
            service: ReminderService = Depends(get_reminder_service),
        ):
            ...
    """
    return ReminderService(session)
