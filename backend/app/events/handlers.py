"""Event handlers for Dapr bindings and Kafka subscriptions.

This module contains:
- Dapr cron binding handlers (scheduled jobs)
- Kafka subscription handlers (event consumers)
- Dead letter queue handlers (failed message processing)
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.dapr.pubsub import get_pubsub
from app.database import get_session
from app.events.schemas import (
    ActivityLogData,
    NotificationData,
    NotificationEvent,
    ReminderDueData,
)
from app.events.topics import KafkaTopic
from app.models.reminder import ReminderStatus
from app.services.activity_service import ActivityService
from app.services.recurrence_service import RecurrenceService
from app.services.reminder_service import ReminderService
from app.services.websocket_manager import get_websocket_manager

logger = logging.getLogger(__name__)

# Router for Dapr binding and subscription endpoints
router = APIRouter(prefix="/dapr", tags=["dapr"])


# =============================================================================
# Dapr Cron Binding Handlers
# =============================================================================


@router.post("/bindings/reminder-scheduler")
async def handle_reminder_scheduler(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Handle the reminder scheduler cron binding.

    This endpoint is called by Dapr every minute via the cron binding
    configured in infrastructure/dapr/components/binding-cron.yaml.

    It checks for due reminders and publishes them to Kafka for delivery.

    Binding configuration:
        name: reminder-scheduler
        type: bindings.cron
        spec:
            schedule: "* * * * *"  # Every minute
    """
    logger.info("Reminder scheduler triggered")

    try:
        service = ReminderService(session)
        processed = await service.process_due_reminders()

        return {
            "status": "success",
            "processed": processed,
        }
    except Exception as e:
        logger.error(f"Reminder scheduler failed: {e}")
        return {
            "status": "error",
            "error": str(e),
        }


@router.post("/bindings/daily-digest")
async def handle_daily_digest(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Handle the daily digest cron binding.

    Sends daily task summary notifications to users.

    Binding configuration:
        name: daily-digest
        type: bindings.cron
        spec:
            schedule: "0 8 * * *"  # Every day at 8 AM
    """
    logger.info("Daily digest triggered")

    # TODO: Implement daily digest logic
    return {"status": "success", "message": "Daily digest not yet implemented"}


# =============================================================================
# Kafka Subscription Handlers (via Dapr Pub/Sub)
# =============================================================================


@router.post("/subscribe/reminder-due")
async def handle_reminder_due(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Handle reminder.due events from Kafka.

    This endpoint is called by Dapr when a message is received on the
    reminder.due topic. It processes the reminder and delivers the notification.

    Subscription configuration (via Dapr programmatic subscription):
        pubsubname: kafka-pubsub
        topic: reminder.due
        route: /dapr/subscribe/reminder-due

    The subscription is registered via DaprApp in main.py.
    """
    try:
        body = await request.json()
        logger.info(f"Received reminder.due event: {body}")

        # Extract CloudEvents data
        event_data = body.get("data", {})
        if isinstance(event_data, str):
            import json
            event_data = json.loads(event_data)

        reminder_data = ReminderDueData(**event_data)
        service = ReminderService(session)

        # Get the reminder to check its status
        reminder = await service.get_reminder_by_id(reminder_data.reminder_id)
        if not reminder:
            logger.warning(f"Reminder {reminder_data.reminder_id} not found")
            return {"status": "DROP"}

        if reminder.status != ReminderStatus.PENDING:
            logger.info(f"Reminder {reminder_data.reminder_id} already processed, skipping")
            return {"status": "SUCCESS"}

        # Deliver the notification
        try:
            await _deliver_reminder_notification(reminder_data)
            await service.mark_reminder_sent(reminder_data.reminder_id)
            logger.info(f"Reminder {reminder_data.reminder_id} delivered successfully")
            return {"status": "SUCCESS"}

        except Exception as delivery_error:
            logger.error(f"Failed to deliver reminder {reminder_data.reminder_id}: {delivery_error}")
            await service.mark_reminder_failed(
                reminder_data.reminder_id,
                str(delivery_error),
            )

            # Check if we should send to DLQ
            reminder = await service.get_reminder_by_id(reminder_data.reminder_id)
            if reminder and reminder.status == ReminderStatus.FAILED:
                await _send_to_dlq(reminder_data, str(delivery_error))

            # Return RETRY to have Dapr retry delivery
            if reminder and reminder.retry_count < 3:
                return {"status": "RETRY"}

            return {"status": "DROP"}

    except Exception as e:
        logger.error(f"Error processing reminder.due event: {e}")
        return {"status": "RETRY"}


@router.post("/subscribe/task-events")
async def handle_task_events(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Handle task lifecycle events from Kafka.

    This endpoint processes task.created, task.updated, task.completed,
    and task.deleted events to:
    - Schedule reminders for new tasks with due dates
    - Update reminders when tasks are modified
    - Cancel reminders when tasks are completed/deleted
    - Log activities for audit trail

    Subscription configuration:
        pubsubname: kafka-pubsub
        topic: task.events
        route: /dapr/subscribe/task-events
    """
    try:
        body = await request.json()
        logger.info(f"Received task event: {body.get('type', 'unknown')}")

        event_type = body.get("type", "")
        event_data = body.get("data", {})

        if isinstance(event_data, str):
            import json
            event_data = json.loads(event_data)

        task_id = event_data.get("task_id")
        user_id = event_data.get("user_id")

        if not task_id:
            logger.warning("Task event missing task_id")
            return {"status": "DROP"}

        reminder_service = ReminderService(session)
        recurrence_service = RecurrenceService(session)

        if event_type == "task.completed":
            # Cancel any pending reminder
            cancelled = await reminder_service.cancel_reminder(task_id)
            if cancelled:
                logger.info(f"Cancelled reminder for completed task {task_id}")

            # Generate next occurrence for recurring tasks
            try:
                from uuid import UUID
                from sqlmodel import select
                from app.models.task import Task

                # Get the completed task
                statement = select(Task).where(Task.id == UUID(task_id))
                result = await session.execute(statement)
                completed_task = result.scalar_one_or_none()

                if completed_task and completed_task.recurrence_id:
                    new_task = await recurrence_service.generate_next_task(completed_task)
                    if new_task:
                        logger.info(
                            f"Generated next occurrence {new_task.id} for recurring task {task_id}"
                        )
                    else:
                        logger.info(f"No more occurrences for recurring task {task_id}")
            except Exception as recurrence_error:
                logger.error(f"Error generating next occurrence for task {task_id}: {recurrence_error}")
                # Don't fail the whole event processing for recurrence errors

        elif event_type == "task.deleted":
            # Cancel any pending reminder
            cancelled = await reminder_service.cancel_reminder(task_id)
            if cancelled:
                logger.info(f"Cancelled reminder for deleted task {task_id}")

        # task.created and task.updated events are handled by TaskService
        # when it calls ReminderService.schedule_reminder()

        return {"status": "SUCCESS"}

    except Exception as e:
        logger.error(f"Error processing task event: {e}")
        return {"status": "RETRY"}


@router.post("/subscribe/sync-events")
async def handle_sync_events(
    request: Request,
) -> dict[str, Any]:
    """Handle sync events from Kafka for WebSocket broadcast.

    This endpoint receives sync events and broadcasts them to connected
    WebSocket clients for real-time updates.

    Subscription configuration:
        pubsubname: kafka-pubsub
        topic: sync.events
        route: /dapr/subscribe/sync-events
    """
    try:
        body = await request.json()
        logger.debug(f"Received sync event: {body}")

        event_data = body.get("data", {})
        if isinstance(event_data, str):
            import json
            event_data = json.loads(event_data)

        user_id = event_data.get("user_id")
        if not user_id:
            logger.warning("Sync event missing user_id")
            return {"status": "DROP"}

        # Broadcast to WebSocket connections
        manager = get_websocket_manager()
        sent_count = await manager.broadcast_sync_event(
            user_id=user_id,
            entity_type=event_data.get("entity_type", "task"),
            entity_id=event_data.get("entity_id", ""),
            operation=event_data.get("operation", "update"),
            payload=event_data.get("payload", {}),
        )

        logger.info(f"Broadcast sync event to {sent_count} connections for user {user_id}")
        return {"status": "SUCCESS"}

    except Exception as e:
        logger.error(f"Error processing sync event: {e}")
        return {"status": "RETRY"}


@router.post("/subscribe/notifications")
async def handle_notification_events(
    request: Request,
) -> dict[str, Any]:
    """Handle notification events from Kafka for WebSocket delivery.

    This endpoint receives notification events and delivers them to
    connected WebSocket clients.

    Subscription configuration:
        pubsubname: kafka-pubsub
        topic: notification.send
        route: /dapr/subscribe/notifications
    """
    try:
        body = await request.json()
        logger.debug(f"Received notification event: {body}")

        event_data = body.get("data", {})
        if isinstance(event_data, str):
            import json
            event_data = json.loads(event_data)

        user_id = event_data.get("user_id")
        if not user_id:
            logger.warning("Notification event missing user_id")
            return {"status": "DROP"}

        # Broadcast notification to WebSocket connections
        manager = get_websocket_manager()
        sent_count = await manager.broadcast_notification(
            user_id=user_id,
            title=event_data.get("title", "Notification"),
            body=event_data.get("body", ""),
            notification_type=event_data.get("channel", "info"),
            action_url=event_data.get("action_url"),
        )

        logger.info(f"Broadcast notification to {sent_count} connections for user {user_id}")
        return {"status": "SUCCESS"}

    except Exception as e:
        logger.error(f"Error processing notification event: {e}")
        return {"status": "RETRY"}


@router.post("/subscribe/activity-log")
async def handle_activity_log_events(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Handle activity log events from Kafka for persistence.

    This endpoint receives activity log events from Kafka and persists
    them to the database for audit trail and productivity tracking.

    Subscription configuration:
        pubsubname: kafka-pubsub
        topic: activity.log
        route: /dapr/subscribe/activity-log
    """
    try:
        body = await request.json()
        logger.debug(f"Received activity log event: {body}")

        event_data = body.get("data", {})
        if isinstance(event_data, str):
            import json
            event_data = json.loads(event_data)

        # Validate required fields
        user_id = event_data.get("user_id")
        if not user_id:
            logger.warning("Activity log event missing user_id")
            return {"status": "DROP"}

        # Parse the activity log data
        try:
            activity_data = ActivityLogData(**event_data)
        except Exception as parse_error:
            logger.error(f"Failed to parse activity log data: {parse_error}")
            return {"status": "DROP"}

        # Persist to database
        service = ActivityService(session)
        entry = await service.log_activity(
            user_id=activity_data.user_id,
            event_type=activity_data.event_type,
            entity_type=activity_data.entity_type,
            entity_id=activity_data.entity_id,
            timestamp=activity_data.timestamp,
            details=activity_data.details,
            correlation_id=activity_data.correlation_id,
        )

        logger.info(
            f"Persisted activity log entry {entry.id}: "
            f"{activity_data.event_type} for {activity_data.entity_type}/{activity_data.entity_id}"
        )
        return {"status": "SUCCESS"}

    except Exception as e:
        logger.error(f"Error processing activity log event: {e}")
        return {"status": "RETRY"}


# =============================================================================
# Helper Functions
# =============================================================================


async def _deliver_reminder_notification(reminder_data: ReminderDueData) -> None:
    """Deliver a reminder notification via the configured channel.

    Args:
        reminder_data: The reminder event data

    Raises:
        Exception: If notification delivery fails
    """
    pubsub = get_pubsub()

    # Create notification event
    notification = NotificationEvent(
        data=NotificationData(
            user_id=reminder_data.user_id,
            channel=reminder_data.delivery_channel,
            title="Task Reminder",
            body=f"Reminder: {reminder_data.task_title} is due at {reminder_data.task_due_date.strftime('%Y-%m-%d %H:%M')}",
            action_url=f"/tasks/{reminder_data.task_id}",
            metadata={
                "reminder_id": str(reminder_data.reminder_id),
                "task_id": str(reminder_data.task_id),
            },
        )
    )

    # Publish to notification topic
    await pubsub.publish(
        topic=KafkaTopic.NOTIFICATION_SEND.value,
        data=notification,
        metadata={"user_id": reminder_data.user_id},
    )

    logger.info(f"Published notification for reminder {reminder_data.reminder_id}")


async def _send_to_dlq(reminder_data: ReminderDueData, error_message: str) -> None:
    """Send a failed reminder to the dead letter queue.

    Args:
        reminder_data: The failed reminder data
        error_message: The error that caused the failure
    """
    pubsub = get_pubsub()

    dlq_data = {
        "original_topic": KafkaTopic.REMINDER_DUE.value,
        "reminder_id": str(reminder_data.reminder_id),
        "task_id": str(reminder_data.task_id),
        "user_id": reminder_data.user_id,
        "error": error_message,
        "attempts": reminder_data.attempt,
    }

    await pubsub.publish(
        topic=KafkaTopic.NOTIFICATION_DLQ.value,
        data=dlq_data,
        metadata={"user_id": reminder_data.user_id},
    )

    logger.info(f"Sent reminder {reminder_data.reminder_id} to DLQ")


# =============================================================================
# Dapr Subscription Configuration
# =============================================================================


def get_subscriptions() -> list[dict[str, Any]]:
    """Return the Dapr pub/sub subscription configuration.

    This is used by the /dapr/subscribe endpoint to tell Dapr
    which topics this service subscribes to.
    """
    return [
        {
            "pubsubname": "kafka-pubsub",
            "topic": KafkaTopic.REMINDER_DUE.value,
            "route": "/dapr/subscribe/reminder-due",
        },
        {
            "pubsubname": "kafka-pubsub",
            "topic": KafkaTopic.TASK_EVENTS.value,
            "route": "/dapr/subscribe/task-events",
        },
        {
            "pubsubname": "kafka-pubsub",
            "topic": KafkaTopic.SYNC_EVENTS.value,
            "route": "/dapr/subscribe/sync-events",
        },
        {
            "pubsubname": "kafka-pubsub",
            "topic": KafkaTopic.NOTIFICATION_SEND.value,
            "route": "/dapr/subscribe/notifications",
        },
        {
            "pubsubname": "kafka-pubsub",
            "topic": KafkaTopic.ACTIVITY_LOG.value,
            "route": "/dapr/subscribe/activity-log",
        },
    ]


@router.get("/subscribe")
async def get_dapr_subscriptions() -> list[dict[str, Any]]:
    """Return Dapr subscription configuration.

    Dapr calls this endpoint to discover which topics this service
    subscribes to. This is an alternative to declarative subscriptions.
    """
    return get_subscriptions()
