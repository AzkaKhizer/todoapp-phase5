"""Kafka event producer for publishing task lifecycle events.

This service publishes events to Kafka via Dapr for:
- Real-time sync across browser tabs/devices
- Activity logging
- Reminder scheduling triggers
- Analytics and audit trail
"""

import logging
from typing import Any, Optional
from uuid import UUID

from app.dapr.pubsub import get_pubsub
from app.events.schemas import (
    ActivityLogData,
    SyncEvent,
    SyncEventData,
    TaskCreatedData,
    TaskDeletedData,
    TaskEvent,
    TaskEventType,
    TaskUpdatedData,
)
from app.events.topics import KafkaTopic
from app.models.task import Task

logger = logging.getLogger(__name__)


class KafkaProducer:
    """Producer for publishing task events to Kafka via Dapr.

    Events are published to multiple topics:
    - task.events: All task lifecycle events (for reminder/recurrence handlers)
    - sync.events: Real-time sync events (for WebSocket broadcast)
    - activity.log: Activity log entries (for audit trail)
    """

    def __init__(self):
        """Initialize the Kafka producer."""
        self._pubsub = get_pubsub()

    async def publish_task_created(
        self,
        task: Task,
        tags: list[str] | None = None,
    ) -> None:
        """Publish a task.created event.

        Args:
            task: The newly created task
            tags: List of tag names associated with the task
        """
        event_data = TaskCreatedData(
            task_id=task.id,
            user_id=task.user_id,
            title=task.title,
            description=task.description,
            due_date=task.due_date,
            priority=task.priority.value,
            is_complete=task.is_complete,
            tags=tags or [],
            recurrence_id=task.recurrence_id,
            parent_task_id=task.parent_task_id,
            reminder_offset_minutes=task.reminder_offset_minutes,
        )

        event = TaskEvent(
            type=TaskEventType.CREATED,
            data=event_data,
        )

        # Publish to task events topic
        await self._pubsub.publish(
            topic=KafkaTopic.TASK_EVENTS.value,
            data=event,
            metadata={"user_id": task.user_id},
        )

        # Publish sync event for real-time updates
        await self._publish_sync_event(
            user_id=task.user_id,
            entity_type="task",
            entity_id=task.id,
            operation="create",
            payload=self._task_to_dict(task, tags),
        )

        # Publish activity log
        await self._publish_activity(
            user_id=task.user_id,
            event_type="task.created",
            entity_type="task",
            entity_id=task.id,
            details={"title": task.title},
        )

        logger.info(f"Published task.created event for task {task.id}")

    async def publish_task_updated(
        self,
        task: Task,
        changes: dict[str, dict[str, Any]],
        tags: list[str] | None = None,
    ) -> None:
        """Publish a task.updated event.

        Args:
            task: The updated task
            changes: Dict of changed fields with old/new values
            tags: Current tag names
        """
        event_data = TaskUpdatedData(
            task_id=task.id,
            user_id=task.user_id,
            changes=changes,
            current_state=self._task_to_dict(task, tags),
        )

        event = TaskEvent(
            type=TaskEventType.UPDATED,
            data=event_data,
        )

        await self._pubsub.publish(
            topic=KafkaTopic.TASK_EVENTS.value,
            data=event,
            metadata={"user_id": task.user_id},
        )

        # Publish sync event
        await self._publish_sync_event(
            user_id=task.user_id,
            entity_type="task",
            entity_id=task.id,
            operation="update",
            payload=self._task_to_dict(task, tags),
        )

        # Publish activity log
        await self._publish_activity(
            user_id=task.user_id,
            event_type="task.updated",
            entity_type="task",
            entity_id=task.id,
            details={"changes": list(changes.keys())},
        )

        logger.info(f"Published task.updated event for task {task.id}")

    async def publish_task_completed(
        self,
        task: Task,
        tags: list[str] | None = None,
    ) -> None:
        """Publish a task.completed event.

        Args:
            task: The completed task
            tags: Current tag names
        """
        event_data = TaskCreatedData(
            task_id=task.id,
            user_id=task.user_id,
            title=task.title,
            description=task.description,
            due_date=task.due_date,
            priority=task.priority.value,
            is_complete=True,
            tags=tags or [],
            recurrence_id=task.recurrence_id,
            parent_task_id=task.parent_task_id,
        )

        event = TaskEvent(
            type=TaskEventType.COMPLETED,
            data=event_data,
        )

        await self._pubsub.publish(
            topic=KafkaTopic.TASK_EVENTS.value,
            data=event,
            metadata={"user_id": task.user_id},
        )

        # Publish sync event
        await self._publish_sync_event(
            user_id=task.user_id,
            entity_type="task",
            entity_id=task.id,
            operation="update",
            payload=self._task_to_dict(task, tags),
        )

        # Publish activity log
        await self._publish_activity(
            user_id=task.user_id,
            event_type="task.completed",
            entity_type="task",
            entity_id=task.id,
            details={"title": task.title},
        )

        logger.info(f"Published task.completed event for task {task.id}")

    async def publish_task_deleted(
        self,
        task: Task,
    ) -> None:
        """Publish a task.deleted event.

        Args:
            task: The deleted task
        """
        event_data = TaskDeletedData(
            task_id=task.id,
            user_id=task.user_id,
            title=task.title,
        )

        event = TaskEvent(
            type=TaskEventType.DELETED,
            data=event_data,
        )

        await self._pubsub.publish(
            topic=KafkaTopic.TASK_EVENTS.value,
            data=event,
            metadata={"user_id": task.user_id},
        )

        # Publish sync event
        await self._publish_sync_event(
            user_id=task.user_id,
            entity_type="task",
            entity_id=task.id,
            operation="delete",
            payload={"id": str(task.id)},
        )

        # Publish activity log
        await self._publish_activity(
            user_id=task.user_id,
            event_type="task.deleted",
            entity_type="task",
            entity_id=task.id,
            details={"title": task.title},
        )

        logger.info(f"Published task.deleted event for task {task.id}")

    async def _publish_sync_event(
        self,
        user_id: str,
        entity_type: str,
        entity_id: UUID,
        operation: str,
        payload: dict[str, Any],
    ) -> None:
        """Publish a sync event for real-time WebSocket broadcast."""
        sync_data = SyncEventData(
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            operation=operation,
            payload=payload,
        )

        event = SyncEvent(data=sync_data)

        await self._pubsub.publish(
            topic=KafkaTopic.SYNC_EVENTS.value,
            data=event,
            metadata={"user_id": user_id},
        )

    async def _publish_activity(
        self,
        user_id: str,
        event_type: str,
        entity_type: str,
        entity_id: UUID,
        details: dict[str, Any],
    ) -> None:
        """Publish an activity log event."""
        activity_data = ActivityLogData(
            user_id=user_id,
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
        )

        await self._pubsub.publish(
            topic=KafkaTopic.ACTIVITY_LOG.value,
            data=activity_data.model_dump(),
            metadata={"user_id": user_id},
        )

    def _task_to_dict(
        self,
        task: Task,
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        """Convert a task to a dictionary for sync events."""
        return {
            "id": str(task.id),
            "title": task.title,
            "description": task.description,
            "is_complete": task.is_complete,
            "user_id": task.user_id,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "priority": task.priority.value,
            "tags": tags or [],
            "recurrence_id": str(task.recurrence_id) if task.recurrence_id else None,
            "is_overdue": task.is_overdue,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "updated_at": task.updated_at.isoformat() if task.updated_at else None,
        }


# Global instance
_producer: KafkaProducer | None = None


def get_kafka_producer() -> KafkaProducer:
    """Get the global Kafka producer instance."""
    global _producer
    if _producer is None:
        _producer = KafkaProducer()
    return _producer
