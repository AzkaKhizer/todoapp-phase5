# Kafka Event Contracts

**Feature**: 010-advanced-cloud-deployment
**Date**: 2026-02-03

## Overview

All events follow the [CloudEvents](https://cloudevents.io/) specification v1.0.

## Topics

| Topic | Purpose | Key | Partitions | Retention |
|-------|---------|-----|------------|-----------|
| `task.events` | Task lifecycle events | user_id | 12 | 7 days |
| `reminder.due` | Due reminders | user_id | 6 | 1 day |
| `notification.send` | Outbound notifications | user_id | 6 | 1 day |
| `notification.dlq` | Failed notifications | user_id | 3 | 30 days |
| `activity.log` | Activity stream | user_id | 12 | 30 days |
| `sync.events` | Real-time sync | user_id | 12 | 1 hour |

---

## Event: task.created

**Topic**: `task.events`
**Trigger**: Task is created via API
**Consumers**: sync-service, activity-service, reminder-scheduler

```json
{
  "specversion": "1.0",
  "type": "task.created",
  "source": "/api/tasks",
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "time": "2026-02-03T10:30:00.000Z",
  "datacontenttype": "application/json",
  "data": {
    "task_id": "123e4567-e89b-12d3-a456-426614174000",
    "user_id": "user_abc123",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "due_date": "2026-02-04T18:00:00.000Z",
    "priority": "high",
    "is_complete": false,
    "tags": ["shopping", "personal"],
    "reminder_offset_minutes": 60,
    "recurrence_id": null,
    "parent_task_id": null
  }
}
```

**Schema**:
```python
class TaskCreatedData(BaseModel):
    task_id: UUID
    user_id: str
    title: str = Field(max_length=200)
    description: str = Field(default="", max_length=2000)
    due_date: Optional[datetime]
    priority: Literal["low", "medium", "high", "urgent"]
    is_complete: bool = False
    tags: List[str] = []
    reminder_offset_minutes: Optional[int]
    recurrence_id: Optional[UUID]
    parent_task_id: Optional[UUID]
```

---

## Event: task.updated

**Topic**: `task.events`
**Trigger**: Task is modified via API
**Consumers**: sync-service, activity-service

```json
{
  "specversion": "1.0",
  "type": "task.updated",
  "source": "/api/tasks",
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "time": "2026-02-03T11:45:00.000Z",
  "datacontenttype": "application/json",
  "data": {
    "task_id": "123e4567-e89b-12d3-a456-426614174000",
    "user_id": "user_abc123",
    "changes": {
      "title": {"old": "Buy groceries", "new": "Buy groceries (ASAP)"},
      "priority": {"old": "high", "new": "urgent"}
    },
    "current_state": {
      "title": "Buy groceries (ASAP)",
      "description": "Milk, eggs, bread",
      "due_date": "2026-02-04T18:00:00.000Z",
      "priority": "urgent",
      "is_complete": false,
      "tags": ["shopping", "personal"]
    }
  }
}
```

---

## Event: task.completed

**Topic**: `task.events`
**Trigger**: Task is marked complete
**Consumers**: sync-service, activity-service, recurrence-service

```json
{
  "specversion": "1.0",
  "type": "task.completed",
  "source": "/api/tasks",
  "id": "770e8400-e29b-41d4-a716-446655440002",
  "time": "2026-02-03T14:00:00.000Z",
  "datacontenttype": "application/json",
  "data": {
    "task_id": "123e4567-e89b-12d3-a456-426614174000",
    "user_id": "user_abc123",
    "title": "Buy groceries (ASAP)",
    "completed_at": "2026-02-03T14:00:00.000Z",
    "recurrence_id": "999e4567-e89b-12d3-a456-426614174999"
  }
}
```

**Note**: If `recurrence_id` is present, recurrence-service will generate the next occurrence.

---

## Event: task.deleted

**Topic**: `task.events`
**Trigger**: Task is deleted
**Consumers**: sync-service, activity-service, reminder-service (to cancel reminders)

```json
{
  "specversion": "1.0",
  "type": "task.deleted",
  "source": "/api/tasks",
  "id": "880e8400-e29b-41d4-a716-446655440003",
  "time": "2026-02-03T15:30:00.000Z",
  "datacontenttype": "application/json",
  "data": {
    "task_id": "123e4567-e89b-12d3-a456-426614174000",
    "user_id": "user_abc123",
    "title": "Buy groceries (ASAP)"
  }
}
```

---

## Event: reminder.due

**Topic**: `reminder.due`
**Trigger**: Scheduler detects reminder is due
**Producer**: reminder-scheduler (cron binding)
**Consumer**: notification-service

```json
{
  "specversion": "1.0",
  "type": "reminder.due",
  "source": "/scheduler/reminders",
  "id": "990e8400-e29b-41d4-a716-446655440004",
  "time": "2026-02-04T17:00:00.000Z",
  "datacontenttype": "application/json",
  "data": {
    "reminder_id": "aaa14567-e89b-12d3-a456-426614174aaa",
    "task_id": "123e4567-e89b-12d3-a456-426614174000",
    "user_id": "user_abc123",
    "task_title": "Buy groceries (ASAP)",
    "task_due_date": "2026-02-04T18:00:00.000Z",
    "delivery_channel": "in-app",
    "attempt": 1
  }
}
```

**Schema**:
```python
class ReminderDueData(BaseModel):
    reminder_id: UUID
    task_id: UUID
    user_id: str
    task_title: str
    task_due_date: datetime
    delivery_channel: str = "in-app"
    attempt: int = 1
```

---

## Event: notification.send

**Topic**: `notification.send`
**Trigger**: Notification ready for delivery
**Consumer**: notification-delivery-service (WebSocket broadcaster, email sender)

```json
{
  "specversion": "1.0",
  "type": "notification.send",
  "source": "/notifications",
  "id": "bbb14567-e89b-41d4-a716-446655440bbb",
  "time": "2026-02-04T17:00:05.000Z",
  "datacontenttype": "application/json",
  "data": {
    "notification_id": "ccc14567-e89b-12d3-a456-426614174ccc",
    "user_id": "user_abc123",
    "channel": "in-app",
    "title": "Task Reminder",
    "body": "\"Buy groceries (ASAP)\" is due in 1 hour",
    "action_url": "/tasks/123e4567-e89b-12d3-a456-426614174000",
    "metadata": {
      "reminder_id": "aaa14567-e89b-12d3-a456-426614174aaa",
      "task_id": "123e4567-e89b-12d3-a456-426614174000"
    }
  }
}
```

---

## Event: sync.broadcast

**Topic**: `sync.events`
**Trigger**: Any task mutation
**Consumer**: websocket-service (broadcasts to connected clients)

```json
{
  "specversion": "1.0",
  "type": "sync.broadcast",
  "source": "/api",
  "id": "ddd14567-e89b-41d4-a716-446655440ddd",
  "time": "2026-02-03T10:30:01.000Z",
  "datacontenttype": "application/json",
  "data": {
    "user_id": "user_abc123",
    "entity_type": "task",
    "entity_id": "123e4567-e89b-12d3-a456-426614174000",
    "operation": "create",
    "payload": {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "due_date": "2026-02-04T18:00:00.000Z",
      "priority": "high",
      "is_complete": false,
      "tags": ["shopping", "personal"]
    }
  }
}
```

---

## Error Handling

### Retry Policy

| Topic | Max Retries | Backoff | DLQ |
|-------|-------------|---------|-----|
| reminder.due | 3 | Exponential (1s, 2s, 4s) | notification.dlq |
| notification.send | 3 | Exponential (1s, 2s, 4s) | notification.dlq |
| task.events | 5 | Linear (1s) | task.events.dlq |

### Dead Letter Queue Event

```json
{
  "specversion": "1.0",
  "type": "dlq.message",
  "source": "/notification-service",
  "id": "eee14567-e89b-41d4-a716-446655440eee",
  "time": "2026-02-04T17:05:00.000Z",
  "data": {
    "original_topic": "notification.send",
    "original_event": { /* full original event */ },
    "error": "Connection timeout to notification gateway",
    "attempt_count": 3,
    "last_attempt_at": "2026-02-04T17:04:58.000Z"
  }
}
```

---

## Consumer Groups

| Group ID | Topics | Purpose |
|----------|--------|---------|
| `todo-backend` | task.events | Main backend processing |
| `reminder-scheduler` | task.events | Schedule/cancel reminders |
| `recurrence-service` | task.events (task.completed) | Generate recurring tasks |
| `sync-service` | task.events | Real-time WebSocket broadcast |
| `activity-service` | task.events | Persist to activity log |
| `notification-delivery` | notification.send | Deliver notifications |

---

## Idempotency

All consumers MUST handle duplicate messages gracefully:

1. Use event `id` as idempotency key
2. Store processed event IDs in Redis (TTL: topic retention + 1 hour)
3. Skip processing if event ID already exists

```python
async def process_event(event: CloudEvent):
    event_id = str(event.id)
    if await redis.exists(f"processed:{event_id}"):
        logger.info(f"Skipping duplicate event {event_id}")
        return

    # Process event...

    await redis.setex(f"processed:{event_id}", 86400, "1")  # 24h TTL
```
