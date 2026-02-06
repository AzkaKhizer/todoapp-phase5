"""Kafka event schemas following CloudEvents specification v1.0."""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class TaskEventType(str, Enum):
    """Types of task lifecycle events."""

    CREATED = "task.created"
    UPDATED = "task.updated"
    COMPLETED = "task.completed"
    DELETED = "task.deleted"


class CloudEvent(BaseModel):
    """Base CloudEvents v1.0 schema."""

    specversion: str = "1.0"
    type: str
    source: str
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    time: datetime = Field(default_factory=datetime.utcnow)
    datacontenttype: str = "application/json"


class TaskEventData(BaseModel):
    """Base data for task events."""

    task_id: uuid.UUID
    user_id: str
    title: str
    due_date: Optional[datetime] = None
    priority: Literal["low", "medium", "high", "urgent"] = "medium"
    is_complete: bool = False
    tags: list[str] = Field(default_factory=list)
    recurrence_id: Optional[uuid.UUID] = None
    parent_task_id: Optional[uuid.UUID] = None


class TaskCreatedData(TaskEventData):
    """Data for task.created events."""

    description: str = Field(default="", max_length=2000)
    reminder_offset_minutes: Optional[int] = None


class TaskUpdatedData(BaseModel):
    """Data for task.updated events."""

    task_id: uuid.UUID
    user_id: str
    changes: dict[str, dict[str, Any]]  # {"field": {"old": ..., "new": ...}}
    current_state: dict[str, Any]


class TaskDeletedData(BaseModel):
    """Data for task.deleted events."""

    task_id: uuid.UUID
    user_id: str
    title: str


class TaskEvent(CloudEvent):
    """CloudEvents-compatible task event."""

    type: TaskEventType
    source: str = "/api/tasks"
    data: TaskEventData | TaskCreatedData | TaskUpdatedData | TaskDeletedData


class ReminderDueData(BaseModel):
    """Data for reminder.due events."""

    reminder_id: uuid.UUID
    task_id: uuid.UUID
    user_id: str
    task_title: str
    task_due_date: datetime
    delivery_channel: str = "in-app"
    attempt: int = 1


class ReminderDueEvent(CloudEvent):
    """CloudEvents-compatible reminder due event."""

    type: str = "reminder.due"
    source: str = "/scheduler/reminders"
    data: ReminderDueData


class SyncEventData(BaseModel):
    """Data for real-time sync events."""

    user_id: str
    entity_type: Literal["task", "tag", "reminder"]
    entity_id: uuid.UUID
    operation: Literal["create", "update", "delete"]
    payload: dict[str, Any]


class SyncEvent(CloudEvent):
    """CloudEvents-compatible sync event for WebSocket broadcast."""

    type: str = "sync.broadcast"
    source: str = "/api"
    data: SyncEventData


class NotificationData(BaseModel):
    """Data for notification events."""

    notification_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    user_id: str
    channel: str = "in-app"
    title: str
    body: str
    action_url: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class NotificationEvent(CloudEvent):
    """CloudEvents-compatible notification event."""

    type: str = "notification.send"
    source: str = "/notifications"
    data: NotificationData


class ActivityLogData(BaseModel):
    """Data for activity log events."""

    user_id: str
    event_type: str
    entity_type: str
    entity_id: uuid.UUID
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    details: dict[str, Any] = Field(default_factory=dict)
    correlation_id: Optional[str] = None
