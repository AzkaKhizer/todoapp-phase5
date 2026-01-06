# Data Model: Todo In-Memory Python Console Application

**Branch**: `001-todo-console-app` | **Date**: 2026-01-04
**Source**: Extracted from [spec.md](./spec.md) Key Entities section

---

## Entity Definitions

### Task

Represents a single todo item managed by the application.

**Spec Reference**: Key Entities section, FR-001 to FR-004

| Field | Type | Required | Mutable | Default | Constraints |
|-------|------|----------|---------|---------|-------------|
| `id` | `int` | Yes | No | Auto-generated | Positive integer, unique, immutable after creation |
| `title` | `str` | Yes | Yes | N/A | Non-empty, non-whitespace-only string |
| `description` | `str` | No | Yes | `""` (empty string) | Any string, including empty |
| `is_complete` | `bool` | No | Yes | `False` | Boolean; toggleable via FR-011 |

**Validation Rules**:
- `id`: Must be positive integer (> 0)
- `title`: Must be non-empty after stripping whitespace; `"".strip()` or `"   ".strip()` both invalid
- `description`: No validation; accepts any string
- `is_complete`: Boolean only; no validation needed

**State Transitions**:
```
[Created] → is_complete = False
     │
     ▼
[Toggle] → is_complete = True ←──┐
     │                           │
     └───────────────────────────┘
```

---

### TaskStore

In-memory collection managing all Task instances during application runtime.

**Spec Reference**: Key Entities section, FR-016, NFR-006

| Attribute | Type | Description |
|-----------|------|-------------|
| `_tasks` | `dict[int, Task]` | Internal storage mapping ID → Task |
| `_next_id` | `int` | Counter for ID generation, starts at 1 |

**Operations**:

| Operation | Input | Output | Spec Reference |
|-----------|-------|--------|----------------|
| `add(title, description)` | `str`, `str` | `Task` | FR-001, FR-002, FR-003, FR-004 |
| `get_all()` | None | `list[Task]` | FR-005 |
| `get_by_id(id)` | `int` | `Task | None` | FR-005, FR-012 |
| `update(id, title, description)` | `int`, `str | None`, `str | None` | `Task | None` | FR-007, FR-008, FR-009 |
| `delete(id)` | `int` | `bool` | FR-010, FR-012 |
| `toggle_complete(id)` | `int` | `Task | None` | FR-011, FR-012 |

**Behavioral Rules**:
- `add`: Always creates new Task with next available ID; increments `_next_id`
- `get_all`: Returns list of all tasks (may be empty)
- `get_by_id`: Returns None if ID not found (does not raise exception)
- `update`: Returns None if ID not found; only updates non-None fields; preserves ID (FR-009)
- `delete`: Returns True if deleted, False if ID not found
- `toggle_complete`: Returns None if ID not found; flips `is_complete` boolean

---

## Relationships

```
┌─────────────────────────────────────────┐
│              TaskStore                  │
│                                         │
│  _tasks: dict[int, Task]                │
│     │                                   │
│     └──── 0..* ────┐                    │
│                    ▼                    │
│              ┌──────────┐               │
│              │   Task   │               │
│              ├──────────┤               │
│              │ id       │ (unique key)  │
│              │ title    │               │
│              │ description              │
│              │ is_complete              │
│              └──────────┘               │
│                                         │
│  _next_id: int (ID generator)           │
└─────────────────────────────────────────┘
```

**Cardinality**: TaskStore contains 0 to many Tasks

---

## ID Generation Behavior

**Spec Reference**: FR-003, Assumptions section

| Scenario | Behavior |
|----------|----------|
| First task added | ID = 1 |
| Second task added | ID = 2 |
| Task 1 deleted, third task added | ID = 3 (IDs not reused) |
| Empty store, add task | ID = 1 (if store cleared, counter resets with new instance) |

**Implementation Note**: The `_next_id` counter is instance state. Each TaskStore instance starts fresh. This aligns with the in-memory, session-based nature of Phase I.

---

## Data Lifecycle

```
Application Start
       │
       ▼
TaskStore instantiated (_tasks={}, _next_id=1)
       │
       ▼
┌─────────────────────────────────────┐
│         Main Loop                   │
│  ┌─────────────────────────────┐    │
│  │ Add Task                    │    │
│  │ → Task created, stored      │    │
│  └─────────────────────────────┘    │
│  ┌─────────────────────────────┐    │
│  │ View Tasks                  │    │
│  │ → List retrieved            │    │
│  └─────────────────────────────┘    │
│  ┌─────────────────────────────┐    │
│  │ Update Task                 │    │
│  │ → Task modified in place    │    │
│  └─────────────────────────────┘    │
│  ┌─────────────────────────────┐    │
│  │ Delete Task                 │    │
│  │ → Task removed from store   │    │
│  └─────────────────────────────┘    │
│  ┌─────────────────────────────┐    │
│  │ Toggle Complete             │    │
│  │ → Task status flipped       │    │
│  └─────────────────────────────┘    │
└─────────────────────────────────────┘
       │
       ▼
Application Exit → All data lost (FR-016)
```

---

## No External Persistence

**Spec Reference**: FR-016, Out of Scope section

This Phase I implementation has **no persistence**:
- No file storage
- No database
- No serialization
- Data exists only in memory during runtime
- Restart clears all tasks

This is intentional per Phase I scope and will be addressed in Phase II.
