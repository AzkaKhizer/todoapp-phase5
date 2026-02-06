"""Kafka topic definitions and configuration."""

from enum import Enum


class KafkaTopic(str, Enum):
    """Kafka topic names for the Todo application.

    Topics are organized by purpose:
    - task.events: All task lifecycle events (create, update, complete, delete)
    - reminder.due: Reminders that are due for delivery
    - notification.send: Notifications ready to be sent
    - notification.dlq: Dead letter queue for failed notifications
    - activity.log: Activity stream for audit trail
    - sync.events: Real-time sync events for WebSocket broadcast
    """

    TASK_EVENTS = "task.events"
    REMINDER_DUE = "reminder.due"
    NOTIFICATION_SEND = "notification.send"
    NOTIFICATION_DLQ = "notification.dlq"
    ACTIVITY_LOG = "activity.log"
    SYNC_EVENTS = "sync.events"


# Topic configuration for Kafka deployment
TOPIC_CONFIG = {
    KafkaTopic.TASK_EVENTS: {
        "partitions": 12,
        "retention_ms": 7 * 24 * 60 * 60 * 1000,  # 7 days
        "key": "user_id",
    },
    KafkaTopic.REMINDER_DUE: {
        "partitions": 6,
        "retention_ms": 1 * 24 * 60 * 60 * 1000,  # 1 day
        "key": "user_id",
    },
    KafkaTopic.NOTIFICATION_SEND: {
        "partitions": 6,
        "retention_ms": 1 * 24 * 60 * 60 * 1000,  # 1 day
        "key": "user_id",
    },
    KafkaTopic.NOTIFICATION_DLQ: {
        "partitions": 3,
        "retention_ms": 30 * 24 * 60 * 60 * 1000,  # 30 days
        "key": "user_id",
    },
    KafkaTopic.ACTIVITY_LOG: {
        "partitions": 12,
        "retention_ms": 30 * 24 * 60 * 60 * 1000,  # 30 days
        "key": "user_id",
    },
    KafkaTopic.SYNC_EVENTS: {
        "partitions": 12,
        "retention_ms": 1 * 60 * 60 * 1000,  # 1 hour
        "key": "user_id",
    },
}


# Consumer group definitions
CONSUMER_GROUPS = {
    "todo-backend": [KafkaTopic.TASK_EVENTS],
    "reminder-scheduler": [KafkaTopic.TASK_EVENTS],
    "recurrence-service": [KafkaTopic.TASK_EVENTS],
    "sync-service": [KafkaTopic.TASK_EVENTS, KafkaTopic.SYNC_EVENTS],
    "activity-service": [KafkaTopic.TASK_EVENTS],
    "notification-delivery": [KafkaTopic.NOTIFICATION_SEND],
}
