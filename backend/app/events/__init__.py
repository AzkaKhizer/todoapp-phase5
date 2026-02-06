"""Event-driven architecture module for Kafka and Dapr integration."""

from app.events.handlers import router as handlers_router
from app.events.schemas import (
    CloudEvent,
    ReminderDueData,
    ReminderDueEvent,
    SyncEvent,
    SyncEventData,
    TaskCreatedData,
    TaskDeletedData,
    TaskEvent,
    TaskEventData,
    TaskEventType,
    TaskUpdatedData,
)
from app.events.topics import KafkaTopic

__all__ = [
    "CloudEvent",
    "KafkaTopic",
    "ReminderDueData",
    "ReminderDueEvent",
    "SyncEvent",
    "SyncEventData",
    "TaskCreatedData",
    "TaskDeletedData",
    "TaskEvent",
    "TaskEventData",
    "TaskEventType",
    "TaskUpdatedData",
    "handlers_router",
]
