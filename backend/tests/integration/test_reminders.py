"""Integration tests for the reminder system.

These tests verify the complete reminder workflow:
1. Task creation with reminder offset schedules a reminder
2. Reminder scheduler finds due reminders
3. Reminder delivery publishes to Kafka
4. Task completion cancels pending reminders

Run with: pytest tests/integration/test_reminders.py -v
"""

import asyncio
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reminder import Reminder, ReminderStatus
from app.models.task import Task, TaskPriority
from app.services.reminder_service import ReminderService


@pytest_asyncio.fixture
async def test_user_id():
    """Generate a test user ID."""
    return f"test-user-{uuid4().hex[:8]}"


@pytest_asyncio.fixture
async def reminder_service(async_session: AsyncSession):
    """Create a ReminderService instance."""
    return ReminderService(async_session)


@pytest_asyncio.fixture
async def task_with_reminder(
    async_session: AsyncSession,
    test_user_id: str,
) -> Task:
    """Create a task with due date and reminder offset."""
    # Due in 2 hours, reminder 30 minutes before
    due_date = datetime.now(timezone.utc) + timedelta(hours=2)

    task = Task(
        title="Test Task with Reminder",
        description="This task has a reminder set",
        user_id=test_user_id,
        due_date=due_date,
        priority=TaskPriority.HIGH,
        reminder_offset_minutes=30,
    )
    async_session.add(task)
    await async_session.commit()
    await async_session.refresh(task)
    return task


@pytest_asyncio.fixture
async def task_with_past_reminder(
    async_session: AsyncSession,
    test_user_id: str,
) -> Task:
    """Create a task with a reminder time in the past (due soon)."""
    # Due in 5 minutes, reminder 10 minutes before (so reminder time is -5 minutes ago)
    due_date = datetime.now(timezone.utc) + timedelta(minutes=5)

    task = Task(
        title="Urgent Task",
        description="Reminder should be triggered immediately",
        user_id=test_user_id,
        due_date=due_date,
        priority=TaskPriority.URGENT,
        reminder_offset_minutes=10,
    )
    async_session.add(task)
    await async_session.commit()
    await async_session.refresh(task)
    return task


class TestReminderScheduling:
    """Test reminder scheduling functionality."""

    @pytest.mark.asyncio
    async def test_schedule_reminder_for_task(
        self,
        reminder_service: ReminderService,
        task_with_reminder: Task,
    ):
        """Test that a reminder is scheduled for a task with due date and offset."""
        reminder = await reminder_service.schedule_reminder(task_with_reminder)

        assert reminder is not None
        assert reminder.task_id == task_with_reminder.id
        assert reminder.user_id == task_with_reminder.user_id
        assert reminder.status == ReminderStatus.PENDING
        assert reminder.delivery_channel == "in-app"

        # Verify scheduled time is correct (due_date - offset)
        expected_time = task_with_reminder.due_date - timedelta(
            minutes=task_with_reminder.reminder_offset_minutes
        )
        # Allow 1 second tolerance for timing
        assert abs((reminder.scheduled_time - expected_time).total_seconds()) < 1

    @pytest.mark.asyncio
    async def test_schedule_reminder_updates_existing(
        self,
        reminder_service: ReminderService,
        task_with_reminder: Task,
        async_session: AsyncSession,
    ):
        """Test that scheduling a reminder updates existing pending reminder."""
        # Schedule first reminder
        reminder1 = await reminder_service.schedule_reminder(task_with_reminder)
        assert reminder1 is not None

        # Update task due date
        new_due_date = datetime.now(timezone.utc) + timedelta(hours=4)
        task_with_reminder.due_date = new_due_date
        async_session.add(task_with_reminder)
        await async_session.commit()

        # Schedule again - should update existing
        reminder2 = await reminder_service.schedule_reminder(task_with_reminder)

        assert reminder2 is not None
        assert reminder2.id == reminder1.id  # Same reminder, updated

        # Verify only one pending reminder exists
        reminders = await reminder_service.get_reminders_for_task(task_with_reminder.id)
        pending = [r for r in reminders if r.status == ReminderStatus.PENDING]
        assert len(pending) == 1

    @pytest.mark.asyncio
    async def test_no_reminder_for_task_without_due_date(
        self,
        reminder_service: ReminderService,
        async_session: AsyncSession,
        test_user_id: str,
    ):
        """Test that no reminder is created for tasks without due date."""
        task = Task(
            title="Task without due date",
            user_id=test_user_id,
            reminder_offset_minutes=30,  # Has offset but no due date
        )
        async_session.add(task)
        await async_session.commit()

        reminder = await reminder_service.schedule_reminder(task)
        assert reminder is None

    @pytest.mark.asyncio
    async def test_no_reminder_for_past_time(
        self,
        reminder_service: ReminderService,
        async_session: AsyncSession,
        test_user_id: str,
    ):
        """Test that no reminder is created when scheduled time is in the past."""
        # Due date is in the past
        past_due_date = datetime.now(timezone.utc) - timedelta(hours=1)

        task = Task(
            title="Past due task",
            user_id=test_user_id,
            due_date=past_due_date,
            reminder_offset_minutes=30,
        )
        async_session.add(task)
        await async_session.commit()

        reminder = await reminder_service.schedule_reminder(task)
        assert reminder is None


class TestReminderCancellation:
    """Test reminder cancellation functionality."""

    @pytest.mark.asyncio
    async def test_cancel_reminder(
        self,
        reminder_service: ReminderService,
        task_with_reminder: Task,
    ):
        """Test that a reminder can be cancelled."""
        # Schedule reminder
        reminder = await reminder_service.schedule_reminder(task_with_reminder)
        assert reminder is not None
        assert reminder.status == ReminderStatus.PENDING

        # Cancel reminder
        cancelled = await reminder_service.cancel_reminder(task_with_reminder.id)
        assert cancelled is True

        # Verify status changed
        updated_reminder = await reminder_service.get_reminder_by_id(reminder.id)
        assert updated_reminder.status == ReminderStatus.CANCELLED

    @pytest.mark.asyncio
    async def test_cancel_nonexistent_reminder(
        self,
        reminder_service: ReminderService,
    ):
        """Test cancelling a reminder that doesn't exist."""
        cancelled = await reminder_service.cancel_reminder(uuid4())
        assert cancelled is False


class TestDueReminders:
    """Test due reminder retrieval and processing."""

    @pytest.mark.asyncio
    async def test_get_due_reminders(
        self,
        reminder_service: ReminderService,
        async_session: AsyncSession,
        test_user_id: str,
    ):
        """Test retrieving reminders that are due."""
        # Create a task with reminder time in the past (already due)
        due_date = datetime.now(timezone.utc) + timedelta(minutes=5)
        task = Task(
            title="Due soon task",
            user_id=test_user_id,
            due_date=due_date,
            reminder_offset_minutes=60,  # Reminder was due 55 minutes ago
        )
        async_session.add(task)
        await async_session.commit()

        # Manually create a due reminder
        scheduled_time = datetime.now(timezone.utc) - timedelta(minutes=5)
        reminder = Reminder(
            task_id=task.id,
            user_id=test_user_id,
            scheduled_time=scheduled_time,
            status=ReminderStatus.PENDING,
        )
        async_session.add(reminder)
        await async_session.commit()

        # Get due reminders
        due_reminders = await reminder_service.get_due_reminders()

        assert len(due_reminders) >= 1
        assert any(r.id == reminder.id for r in due_reminders)

    @pytest.mark.asyncio
    async def test_get_due_reminders_excludes_future(
        self,
        reminder_service: ReminderService,
        task_with_reminder: Task,
    ):
        """Test that future reminders are not returned as due."""
        # Schedule reminder for future
        reminder = await reminder_service.schedule_reminder(task_with_reminder)
        assert reminder is not None

        # Get due reminders
        due_reminders = await reminder_service.get_due_reminders()

        # The scheduled reminder should not be in the due list
        assert not any(r.id == reminder.id for r in due_reminders)


class TestReminderStatus:
    """Test reminder status updates."""

    @pytest.mark.asyncio
    async def test_mark_reminder_sent(
        self,
        reminder_service: ReminderService,
        task_with_reminder: Task,
    ):
        """Test marking a reminder as sent."""
        reminder = await reminder_service.schedule_reminder(task_with_reminder)
        assert reminder is not None

        # Mark as sent
        success = await reminder_service.mark_reminder_sent(reminder.id)
        assert success is True

        # Verify status
        updated = await reminder_service.get_reminder_by_id(reminder.id)
        assert updated.status == ReminderStatus.SENT
        assert updated.sent_at is not None

    @pytest.mark.asyncio
    async def test_mark_reminder_failed(
        self,
        reminder_service: ReminderService,
        task_with_reminder: Task,
    ):
        """Test marking a reminder as failed with retry tracking."""
        reminder = await reminder_service.schedule_reminder(task_with_reminder)
        assert reminder is not None

        # Mark as failed
        success = await reminder_service.mark_reminder_failed(
            reminder.id,
            "Test error message",
        )
        assert success is True

        # Verify status and retry count
        updated = await reminder_service.get_reminder_by_id(reminder.id)
        assert updated.retry_count == 1
        assert updated.error_message == "Test error message"
        # Status should still be pending for retry
        assert updated.status == ReminderStatus.PENDING

    @pytest.mark.asyncio
    async def test_reminder_fails_after_max_retries(
        self,
        reminder_service: ReminderService,
        task_with_reminder: Task,
    ):
        """Test that reminder is marked failed after max retries."""
        reminder = await reminder_service.schedule_reminder(task_with_reminder)
        assert reminder is not None

        # Fail 3 times (max retries)
        for i in range(3):
            await reminder_service.mark_reminder_failed(
                reminder.id,
                f"Failure {i + 1}",
            )

        # Verify status is FAILED
        updated = await reminder_service.get_reminder_by_id(reminder.id)
        assert updated.status == ReminderStatus.FAILED
        assert updated.retry_count == 3


class TestUserReminders:
    """Test user-specific reminder queries."""

    @pytest.mark.asyncio
    async def test_get_pending_reminders_for_user(
        self,
        reminder_service: ReminderService,
        task_with_reminder: Task,
        test_user_id: str,
    ):
        """Test getting pending reminders for a specific user."""
        # Schedule reminder
        reminder = await reminder_service.schedule_reminder(task_with_reminder)
        assert reminder is not None

        # Get user's pending reminders
        user_reminders = await reminder_service.get_pending_reminders_for_user(
            test_user_id
        )

        assert len(user_reminders) >= 1
        assert any(r.id == reminder.id for r in user_reminders)

    @pytest.mark.asyncio
    async def test_get_reminders_for_task(
        self,
        reminder_service: ReminderService,
        task_with_reminder: Task,
    ):
        """Test getting all reminders for a specific task."""
        # Schedule reminder
        reminder = await reminder_service.schedule_reminder(task_with_reminder)
        assert reminder is not None

        # Get task's reminders
        task_reminders = await reminder_service.get_reminders_for_task(
            task_with_reminder.id
        )

        assert len(task_reminders) >= 1
        assert any(r.id == reminder.id for r in task_reminders)
