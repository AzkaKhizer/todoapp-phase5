# Task API v2 Contract

**Feature**: 010-advanced-cloud-deployment
**Date**: 2026-02-03
**Base Path**: `/api/tasks`

## Overview

Extended Task API with support for due dates, priorities, tags, reminders, recurrence, and advanced filtering.

---

## Endpoints

### GET /api/tasks

List tasks with filtering, sorting, and pagination.

**Query Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `page` | integer | No | Page number (default: 1) |
| `limit` | integer | No | Items per page (default: 20, max: 100) |
| `search` | string | No | Full-text search on title/description |
| `priority` | string | No | Filter by priority (comma-separated: low,medium,high,urgent) |
| `due_before` | datetime | No | Tasks due before this date (ISO 8601) |
| `due_after` | datetime | No | Tasks due after this date (ISO 8601) |
| `tags` | string | No | Filter by tag names (comma-separated) |
| `is_complete` | boolean | No | Filter by completion status |
| `sort_by` | string | No | Sort field: due_date, priority, created_at, title |
| `sort_order` | string | No | Sort direction: asc, desc (default: asc) |
| `include_overdue` | boolean | No | Include overdue indicator in response (default: true) |

**Request**:
```http
GET /api/tasks?priority=high,urgent&due_before=2026-02-10T00:00:00Z&tags=work,urgent&sort_by=due_date&sort_order=asc
Authorization: Bearer <token>
```

**Response** (200 OK):
```json
{
  "data": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "title": "Finish report",
      "description": "Q4 quarterly report",
      "is_complete": false,
      "due_date": "2026-02-05T17:00:00.000Z",
      "priority": "high",
      "tags": [
        {"id": "tag-001", "name": "work", "color": "#3B82F6"},
        {"id": "tag-002", "name": "urgent", "color": "#EF4444"}
      ],
      "reminder": {
        "id": "rem-001",
        "scheduled_time": "2026-02-05T16:00:00.000Z",
        "status": "pending"
      },
      "recurrence": null,
      "is_overdue": false,
      "created_at": "2026-02-01T10:00:00.000Z",
      "updated_at": "2026-02-03T14:30:00.000Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total_items": 45,
    "total_pages": 3
  }
}
```

---

### POST /api/tasks

Create a new task with optional extended attributes.

**Request**:
```http
POST /api/tasks
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Weekly team meeting",
  "description": "Discuss sprint progress",
  "due_date": "2026-02-10T10:00:00.000Z",
  "priority": "medium",
  "tags": ["work", "meetings"],
  "reminder_offset_minutes": 30,
  "recurrence": {
    "type": "weekly",
    "interval": 1,
    "days_of_week": [1]
  }
}
```

**Request Schema**:
```python
class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)
    due_date: Optional[datetime] = None
    priority: Literal["low", "medium", "high", "urgent"] = "medium"
    tags: List[str] = []  # Tag names (will be created if not exist)
    reminder_offset_minutes: Optional[int] = Field(None, ge=0, le=10080)  # Max 7 days
    recurrence: Optional[RecurrenceCreate] = None

class RecurrenceCreate(BaseModel):
    type: Literal["daily", "weekly", "monthly", "yearly", "custom"]
    interval: int = Field(default=1, ge=1, le=365)
    days_of_week: Optional[List[int]] = Field(None, description="0=Mon, 6=Sun")
    day_of_month: Optional[int] = Field(None, ge=1, le=31)
    end_date: Optional[datetime] = None
```

**Response** (201 Created):
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Weekly team meeting",
  "description": "Discuss sprint progress",
  "is_complete": false,
  "due_date": "2026-02-10T10:00:00.000Z",
  "priority": "medium",
  "tags": [
    {"id": "tag-001", "name": "work", "color": null},
    {"id": "tag-003", "name": "meetings", "color": null}
  ],
  "reminder": {
    "id": "rem-002",
    "scheduled_time": "2026-02-10T09:30:00.000Z",
    "status": "pending"
  },
  "recurrence": {
    "id": "rec-001",
    "type": "weekly",
    "interval": 1,
    "days_of_week": [1],
    "end_date": null
  },
  "is_overdue": false,
  "created_at": "2026-02-03T15:00:00.000Z",
  "updated_at": "2026-02-03T15:00:00.000Z"
}
```

**Errors**:
- 400 Bad Request: Invalid recurrence pattern
- 401 Unauthorized: Missing or invalid token
- 422 Unprocessable Entity: Validation error

---

### PUT /api/tasks/{id}

Full update of a task.

**Request**:
```http
PUT /api/tasks/123e4567-e89b-12d3-a456-426614174000
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Weekly team meeting (updated)",
  "description": "Discuss sprint progress and blockers",
  "due_date": "2026-02-10T11:00:00.000Z",
  "priority": "high",
  "tags": ["work", "meetings", "important"],
  "reminder_offset_minutes": 60,
  "recurrence": {
    "type": "weekly",
    "interval": 1,
    "days_of_week": [1],
    "end_date": "2026-06-30T00:00:00.000Z"
  }
}
```

**Response** (200 OK): Same as POST response

**Side Effects**:
- If `due_date` changes and reminder exists, reminder is rescheduled
- If `recurrence` changes, future recurrence pattern is updated
- Publishes `task.updated` event to Kafka

---

### PATCH /api/tasks/{id}

Partial update of a task.

**Request**:
```http
PATCH /api/tasks/123e4567-e89b-12d3-a456-426614174000
Authorization: Bearer <token>
Content-Type: application/json

{
  "priority": "urgent"
}
```

**Response** (200 OK): Full task object with updates applied

---

### PATCH /api/tasks/{id}/toggle

Toggle task completion status.

**Request**:
```http
PATCH /api/tasks/123e4567-e89b-12d3-a456-426614174000/toggle
Authorization: Bearer <token>
```

**Response** (200 OK):
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "is_complete": true,
  ...
}
```

**Side Effects**:
- If marking complete and task has recurrence, new occurrence is created
- If marking complete, associated reminders are cancelled
- Publishes `task.completed` event to Kafka

---

### DELETE /api/tasks/{id}

Delete a task.

**Request**:
```http
DELETE /api/tasks/123e4567-e89b-12d3-a456-426614174000
Authorization: Bearer <token>
```

**Response** (204 No Content)

**Side Effects**:
- Associated reminders are cancelled/deleted
- Associated tags are NOT deleted (only TaskTag junction records)
- If recurring, recurrence pattern is NOT deleted (may be used by other instances)
- Publishes `task.deleted` event to Kafka

---

## Tag Endpoints

### GET /api/tags

List user's tags.

**Response** (200 OK):
```json
{
  "data": [
    {"id": "tag-001", "name": "work", "color": "#3B82F6", "task_count": 15},
    {"id": "tag-002", "name": "personal", "color": "#10B981", "task_count": 8}
  ]
}
```

### POST /api/tags

Create a new tag.

**Request**:
```json
{
  "name": "important",
  "color": "#EF4444"
}
```

**Response** (201 Created):
```json
{
  "id": "tag-003",
  "name": "important",
  "color": "#EF4444",
  "task_count": 0
}
```

### DELETE /api/tags/{id}

Delete a tag (removes from all tasks).

**Response** (204 No Content)

---

## Reminder Endpoints

### GET /api/tasks/{id}/reminder

Get reminder for a task.

**Response** (200 OK):
```json
{
  "id": "rem-001",
  "task_id": "123e4567-e89b-12d3-a456-426614174000",
  "scheduled_time": "2026-02-05T16:00:00.000Z",
  "status": "pending",
  "delivery_channel": "in-app"
}
```

### PUT /api/tasks/{id}/reminder

Set or update reminder for a task.

**Request**:
```json
{
  "offset_minutes": 60
}
```

**Response** (200 OK): Reminder object

### DELETE /api/tasks/{id}/reminder

Cancel/delete reminder for a task.

**Response** (204 No Content)

---

## Activity Log Endpoints

### GET /api/activity

Get user's activity log.

**Query Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `page` | integer | No | Page number |
| `limit` | integer | No | Items per page (max: 100) |
| `from` | datetime | No | Start date filter |
| `to` | datetime | No | End date filter |
| `event_type` | string | No | Filter by event type |

**Response** (200 OK):
```json
{
  "data": [
    {
      "id": "act-001",
      "event_type": "task.completed",
      "entity_type": "task",
      "entity_id": "123e4567-e89b-12d3-a456-426614174000",
      "timestamp": "2026-02-03T14:00:00.000Z",
      "details": {
        "title": "Buy groceries"
      }
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total_items": 127
  },
  "summary": {
    "tasks_created": 12,
    "tasks_completed": 8,
    "period": "2026-02-01 to 2026-02-03"
  }
}
```

---

## WebSocket Endpoint

### WS /api/ws/tasks

Real-time task synchronization.

**Connection**:
```javascript
const ws = new WebSocket('wss://api.example.com/api/ws/tasks?token=<jwt>');
```

**Server Messages**:
```json
{
  "type": "task.created",
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "title": "New task",
    ...
  }
}
```

```json
{
  "type": "task.updated",
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "changes": ["title", "priority"],
    ...
  }
}
```

```json
{
  "type": "notification",
  "data": {
    "title": "Task Reminder",
    "body": "\"Buy groceries\" is due in 1 hour",
    "task_id": "123e4567-e89b-12d3-a456-426614174000"
  }
}
```

**Client Messages**:
```json
{
  "type": "ping"
}
```

```json
{
  "type": "sync_request",
  "last_event_id": "evt-123"
}
```

---

## Error Responses

All errors follow RFC 7807 Problem Details format:

```json
{
  "type": "https://api.example.com/errors/validation",
  "title": "Validation Error",
  "status": 422,
  "detail": "Field 'title' is required",
  "instance": "/api/tasks",
  "errors": [
    {
      "field": "title",
      "message": "Field is required"
    }
  ]
}
```

| Status | Type | Description |
|--------|------|-------------|
| 400 | /errors/bad-request | Invalid request format |
| 401 | /errors/unauthorized | Missing or invalid token |
| 403 | /errors/forbidden | Insufficient permissions |
| 404 | /errors/not-found | Resource not found |
| 409 | /errors/conflict | Resource conflict (e.g., duplicate tag) |
| 422 | /errors/validation | Validation error |
| 500 | /errors/internal | Internal server error |
