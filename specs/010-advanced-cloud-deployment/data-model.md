# Data Model: Advanced Cloud Deployment

**Feature**: 010-advanced-cloud-deployment
**Date**: 2026-02-03
**Status**: Draft

## Entity Overview

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│    User     │───┬──▶│    Task     │◀──────│    Tag      │
│  (Better    │   │   │  (Extended) │       │             │
│   Auth)     │   │   └─────────────┘       └─────────────┘
└─────────────┘   │          │                     │
                  │          │                     │
                  │          ▼                     │
                  │   ┌─────────────┐             │
                  │   │  Reminder   │             │
                  │   └─────────────┘             │
                  │          │                     │
                  │          │                     │
                  │          ▼                     │
                  │   ┌─────────────┐             │
                  │   │  TaskEvent  │             │
                  │   │  (Kafka)    │             │
                  │   └─────────────┘             │
                  │                               │
                  │   ┌─────────────┐             │
                  └──▶│ ActivityLog │◀────────────┘
                      └─────────────┘
                             │
                      ┌──────┴──────┐
                      │ Recurrence  │
                      │   Pattern   │
                      └─────────────┘
```

## Extended Task Entity

### Task (Extended)

**Purpose**: Core task entity with enhanced attributes for due dates, priorities, and recurrence.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique task identifier |
| title | String(200) | Required | Task title |
| description | String(2000) | Optional, default="" | Task description |
| is_complete | Boolean | Default=false | Completion status |
| user_id | String(64) | Required, indexed | Better Auth user ID |
| **due_date** | DateTime | Optional, indexed | When task is due |
| **priority** | Enum | Default='medium' | low, medium, high, urgent |
| **reminder_offset** | Interval | Optional | Time before due_date for reminder |
| **recurrence_id** | UUID | FK, optional | Link to RecurrencePattern |
| **parent_task_id** | UUID | FK, optional | Original task (for recurring instances) |
| created_at | DateTime | Auto-set | Creation timestamp |
| updated_at | DateTime | Auto-updated | Last modification timestamp |

**Indexes**:
- `idx_task_user_id` on user_id
- `idx_task_due_date` on due_date
- `idx_task_priority` on priority
- `idx_task_user_due` on (user_id, due_date)

**SQLModel Definition**:
```python
class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=200)
    description: str = Field(default="", max_length=2000)
    is_complete: bool = Field(default=False)
    user_id: str = Field(sa_column=Column(String(64), index=True, nullable=False))

    # New fields
    due_date: Optional[datetime] = Field(default=None, index=True)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    reminder_offset: Optional[timedelta] = Field(default=None)
    recurrence_id: Optional[uuid.UUID] = Field(default=None, foreign_key="recurrence_patterns.id")
    parent_task_id: Optional[uuid.UUID] = Field(default=None, foreign_key="tasks.id")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    tags: List["Tag"] = Relationship(back_populates="tasks", link_model=TaskTag)
    reminders: List["Reminder"] = Relationship(back_populates="task")
    recurrence: Optional["RecurrencePattern"] = Relationship(back_populates="tasks")
```

---

## New Entities

### Tag

**Purpose**: User-defined tags for task categorization.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique tag identifier |
| name | String(50) | Required | Tag name |
| color | String(7) | Optional | Hex color code (#RRGGBB) |
| user_id | String(64) | Required, indexed | Owner user ID |
| created_at | DateTime | Auto-set | Creation timestamp |

**Constraints**:
- Unique (user_id, name) - no duplicate tag names per user

**SQLModel Definition**:
```python
class Tag(SQLModel, table=True):
    __tablename__ = "tags"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=50)
    color: Optional[str] = Field(default=None, max_length=7)
    user_id: str = Field(sa_column=Column(String(64), index=True, nullable=False))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    tasks: List["Task"] = Relationship(back_populates="tags", link_model=TaskTag)

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_tag_user_name"),
    )
```

### TaskTag (Junction Table)

**Purpose**: Many-to-many relationship between tasks and tags.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| task_id | UUID | PK, FK | Task reference |
| tag_id | UUID | PK, FK | Tag reference |

**SQLModel Definition**:
```python
class TaskTag(SQLModel, table=True):
    __tablename__ = "task_tags"

    task_id: uuid.UUID = Field(foreign_key="tasks.id", primary_key=True)
    tag_id: uuid.UUID = Field(foreign_key="tags.id", primary_key=True)
```

---

### Reminder

**Purpose**: Scheduled reminders for tasks with due dates.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique reminder identifier |
| task_id | UUID | FK, required | Associated task |
| user_id | String(64) | Required, indexed | Owner user ID |
| scheduled_time | DateTime | Required, indexed | When to send reminder |
| status | Enum | Default='pending' | pending, sent, cancelled, failed |
| delivery_channel | String(20) | Default='in-app' | Notification channel |
| sent_at | DateTime | Optional | When reminder was sent |
| error_message | String(500) | Optional | Error details if failed |
| retry_count | Integer | Default=0 | Number of delivery attempts |
| created_at | DateTime | Auto-set | Creation timestamp |

**Indexes**:
- `idx_reminder_scheduled` on (scheduled_time, status) for scheduler queries
- `idx_reminder_task` on task_id

**SQLModel Definition**:
```python
class ReminderStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    CANCELLED = "cancelled"
    FAILED = "failed"

class Reminder(SQLModel, table=True):
    __tablename__ = "reminders"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    task_id: uuid.UUID = Field(foreign_key="tasks.id", nullable=False)
    user_id: str = Field(sa_column=Column(String(64), index=True, nullable=False))
    scheduled_time: datetime = Field(nullable=False, index=True)
    status: ReminderStatus = Field(default=ReminderStatus.PENDING)
    delivery_channel: str = Field(default="in-app", max_length=20)
    sent_at: Optional[datetime] = Field(default=None)
    error_message: Optional[str] = Field(default=None, max_length=500)
    retry_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    task: "Task" = Relationship(back_populates="reminders")
```

---

### RecurrencePattern

**Purpose**: Defines how tasks repeat.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique pattern identifier |
| type | Enum | Required | daily, weekly, monthly, yearly, custom |
| interval | Integer | Default=1 | Every N periods |
| days_of_week | Array[Integer] | Optional | For weekly: 0=Mon, 6=Sun |
| day_of_month | Integer | Optional | For monthly: 1-31 |
| month_of_year | Integer | Optional | For yearly: 1-12 |
| end_date | DateTime | Optional | When recurrence stops |
| user_id | String(64) | Required | Owner user ID |
| created_at | DateTime | Auto-set | Creation timestamp |

**SQLModel Definition**:
```python
class RecurrenceType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    CUSTOM = "custom"

class RecurrencePattern(SQLModel, table=True):
    __tablename__ = "recurrence_patterns"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    type: RecurrenceType = Field(nullable=False)
    interval: int = Field(default=1, ge=1)
    days_of_week: Optional[List[int]] = Field(default=None, sa_column=Column(ARRAY(Integer)))
    day_of_month: Optional[int] = Field(default=None, ge=1, le=31)
    month_of_year: Optional[int] = Field(default=None, ge=1, le=12)
    end_date: Optional[datetime] = Field(default=None)
    user_id: str = Field(sa_column=Column(String(64), nullable=False))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    tasks: List["Task"] = Relationship(back_populates="recurrence")
```

---

### ActivityLogEntry

**Purpose**: Audit trail of all task operations.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique entry identifier |
| user_id | String(64) | Required, indexed | User who performed action |
| event_type | String(50) | Required | created, updated, completed, deleted |
| entity_type | String(20) | Required | task, reminder, tag |
| entity_id | UUID | Required | ID of affected entity |
| timestamp | DateTime | Required, indexed | When event occurred |
| details | JSON | Optional | Additional event data |
| correlation_id | String(64) | Optional | Request correlation ID |

**Indexes**:
- `idx_activity_user_time` on (user_id, timestamp DESC) for user queries
- `idx_activity_entity` on (entity_type, entity_id) for entity history

**SQLModel Definition**:
```python
class ActivityLogEntry(SQLModel, table=True):
    __tablename__ = "activity_log"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: str = Field(sa_column=Column(String(64), index=True, nullable=False))
    event_type: str = Field(max_length=50, nullable=False)
    entity_type: str = Field(max_length=20, nullable=False)
    entity_id: uuid.UUID = Field(nullable=False)
    timestamp: datetime = Field(nullable=False, index=True)
    details: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    correlation_id: Optional[str] = Field(default=None, max_length=64)
```

---

## Event Schemas (Kafka Messages)

### TaskEvent

**Purpose**: Published when any task operation occurs.

```python
class TaskEventType(str, Enum):
    CREATED = "task.created"
    UPDATED = "task.updated"
    COMPLETED = "task.completed"
    DELETED = "task.deleted"

class TaskEvent(BaseModel):
    """CloudEvents-compatible task event."""
    specversion: str = "1.0"
    type: TaskEventType
    source: str = "/api/tasks"
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    time: datetime = Field(default_factory=datetime.utcnow)
    datacontenttype: str = "application/json"
    data: TaskEventData

class TaskEventData(BaseModel):
    task_id: uuid.UUID
    user_id: str
    title: str
    due_date: Optional[datetime]
    priority: TaskPriority
    is_complete: bool
    tags: List[str]
    recurrence_id: Optional[uuid.UUID]
```

### ReminderDueEvent

**Purpose**: Published when a reminder is due.

```python
class ReminderDueEvent(BaseModel):
    specversion: str = "1.0"
    type: str = "reminder.due"
    source: str = "/scheduler"
    id: uuid.UUID
    time: datetime
    data: ReminderDueData

class ReminderDueData(BaseModel):
    reminder_id: uuid.UUID
    task_id: uuid.UUID
    user_id: str
    task_title: str
    due_date: datetime
    delivery_channel: str
```

### SyncEvent

**Purpose**: Published for real-time UI synchronization.

```python
class SyncEvent(BaseModel):
    specversion: str = "1.0"
    type: str  # task.created, task.updated, etc.
    source: str = "/api"
    id: uuid.UUID
    time: datetime
    data: SyncEventData

class SyncEventData(BaseModel):
    user_id: str
    entity_type: str  # task, tag, etc.
    entity_id: uuid.UUID
    operation: str  # create, update, delete
    payload: dict  # Full entity data for creates/updates
```

---

## Database Migration Plan

### Migration 001: Add Task Extended Fields

```sql
ALTER TABLE tasks
ADD COLUMN due_date TIMESTAMP WITH TIME ZONE,
ADD COLUMN priority VARCHAR(10) DEFAULT 'medium',
ADD COLUMN reminder_offset INTERVAL,
ADD COLUMN recurrence_id UUID,
ADD COLUMN parent_task_id UUID;

CREATE INDEX idx_task_due_date ON tasks(due_date);
CREATE INDEX idx_task_priority ON tasks(priority);
CREATE INDEX idx_task_user_due ON tasks(user_id, due_date);

ALTER TABLE tasks
ADD CONSTRAINT fk_task_recurrence FOREIGN KEY (recurrence_id) REFERENCES recurrence_patterns(id),
ADD CONSTRAINT fk_task_parent FOREIGN KEY (parent_task_id) REFERENCES tasks(id);
```

### Migration 002: Create Tags and TaskTags

```sql
CREATE TABLE tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL,
    color VARCHAR(7),
    user_id VARCHAR(64) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT uq_tag_user_name UNIQUE (user_id, name)
);

CREATE INDEX idx_tag_user ON tags(user_id);

CREATE TABLE task_tags (
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (task_id, tag_id)
);
```

### Migration 003: Create Reminders

```sql
CREATE TABLE reminders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    user_id VARCHAR(64) NOT NULL,
    scheduled_time TIMESTAMP WITH TIME ZONE NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    delivery_channel VARCHAR(20) DEFAULT 'in-app',
    sent_at TIMESTAMP WITH TIME ZONE,
    error_message VARCHAR(500),
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_reminder_scheduled ON reminders(scheduled_time, status);
CREATE INDEX idx_reminder_task ON reminders(task_id);
CREATE INDEX idx_reminder_user ON reminders(user_id);
```

### Migration 004: Create RecurrencePatterns

```sql
CREATE TABLE recurrence_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type VARCHAR(20) NOT NULL,
    interval INTEGER DEFAULT 1,
    days_of_week INTEGER[],
    day_of_month INTEGER,
    month_of_year INTEGER,
    end_date TIMESTAMP WITH TIME ZONE,
    user_id VARCHAR(64) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Migration 005: Create ActivityLog

```sql
CREATE TABLE activity_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(64) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    entity_type VARCHAR(20) NOT NULL,
    entity_id UUID NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    details JSONB,
    correlation_id VARCHAR(64)
);

CREATE INDEX idx_activity_user_time ON activity_log(user_id, timestamp DESC);
CREATE INDEX idx_activity_entity ON activity_log(entity_type, entity_id);
```

---

## Query Patterns

### Search/Filter/Sort Tasks

```sql
-- Example: Filter by priority, due date range, and tags with sorting
SELECT t.*, array_agg(tag.name) as tag_names
FROM tasks t
LEFT JOIN task_tags tt ON t.id = tt.task_id
LEFT JOIN tags tag ON tt.tag_id = tag.id
WHERE t.user_id = :user_id
  AND t.priority IN ('high', 'urgent')
  AND t.due_date BETWEEN :start_date AND :end_date
  AND (tag.name = ANY(:tag_filter) OR :tag_filter IS NULL)
GROUP BY t.id
ORDER BY t.due_date ASC, t.priority DESC
LIMIT :limit OFFSET :offset;
```

### Due Reminders Query (Scheduler)

```sql
-- Query for reminders due in the current minute
SELECT r.*, t.title as task_title, t.due_date
FROM reminders r
JOIN tasks t ON r.task_id = t.id
WHERE r.status = 'pending'
  AND r.scheduled_time <= NOW()
  AND r.scheduled_time > NOW() - INTERVAL '1 minute'
ORDER BY r.scheduled_time ASC
LIMIT 100;
```

### Activity Log Query

```sql
-- User's recent activity
SELECT * FROM activity_log
WHERE user_id = :user_id
  AND timestamp BETWEEN :start_date AND :end_date
ORDER BY timestamp DESC
LIMIT :limit OFFSET :offset;
```
