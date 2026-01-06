# TaskStore Internal API Contract

**Branch**: `001-todo-console-app` | **Date**: 2026-01-04
**Module**: `src/todo/services.py`

---

## Overview

This document defines the internal API contract for the `TaskStore` class. Since this is a CLI application (not a web API), this contract describes the Python method signatures and behaviors that the CLI layer will use.

---

## Class: TaskStore

### Constructor

```
TaskStore()
```

**Description**: Creates a new TaskStore with empty task collection and ID counter starting at 1.

**Parameters**: None

**Returns**: TaskStore instance

**Side Effects**: None

---

## Methods

### add

```
add(title: str, description: str = "") -> Task
```

**Description**: Creates a new task with auto-generated ID.

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `title` | `str` | Yes | Task title (must be non-empty after strip) |
| `description` | `str` | No | Task description (default: empty string) |

**Returns**: `Task` - The newly created task with ID assigned

**Preconditions**:
- `title.strip()` must be non-empty

**Postconditions**:
- Task exists in store with unique ID
- `_next_id` incremented by 1

**Spec Reference**: FR-001, FR-002, FR-003, FR-004

---

### get_all

```
get_all() -> list[Task]
```

**Description**: Returns all tasks in the store.

**Parameters**: None

**Returns**: `list[Task]` - List of all tasks (may be empty)

**Preconditions**: None

**Postconditions**: Store unchanged

**Spec Reference**: FR-005

---

### get_by_id

```
get_by_id(task_id: int) -> Task | None
```

**Description**: Retrieves a task by its ID.

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `task_id` | `int` | Yes | The task ID to look up |

**Returns**:
- `Task` if found
- `None` if not found

**Preconditions**: None

**Postconditions**: Store unchanged

**Spec Reference**: FR-005, FR-012

---

### update

```
update(task_id: int, title: str | None = None, description: str | None = None) -> Task | None
```

**Description**: Updates a task's title and/or description. Only non-None values are applied.

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `task_id` | `int` | Yes | The task ID to update |
| `title` | `str | None` | No | New title (None = keep current) |
| `description` | `str | None` | No | New description (None = keep current) |

**Returns**:
- `Task` - The updated task if found
- `None` - If task not found

**Preconditions**:
- If `title` is provided and non-None, `title.strip()` must be non-empty

**Postconditions**:
- Task ID unchanged (FR-009)
- Only provided non-None fields updated

**Spec Reference**: FR-007, FR-008, FR-009, FR-012

---

### delete

```
delete(task_id: int) -> bool
```

**Description**: Removes a task from the store.

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `task_id` | `int` | Yes | The task ID to delete |

**Returns**:
- `True` - Task was deleted
- `False` - Task not found

**Preconditions**: None

**Postconditions**:
- If found: Task removed from store
- If not found: Store unchanged

**Spec Reference**: FR-010, FR-012

---

### toggle_complete

```
toggle_complete(task_id: int) -> Task | None
```

**Description**: Toggles the completion status of a task.

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `task_id` | `int` | Yes | The task ID to toggle |

**Returns**:
- `Task` - The updated task if found (with `is_complete` flipped)
- `None` - If task not found

**Preconditions**: None

**Postconditions**:
- `task.is_complete = not task.is_complete`

**Spec Reference**: FR-011, FR-012

---

## Error Handling

The TaskStore does **not** raise exceptions for business logic errors. Instead:

| Condition | Behavior |
|-----------|----------|
| Task not found | Return `None` or `False` |
| Invalid title | Should be validated at CLI layer before calling |

This design allows the CLI layer to handle user-facing error messages.

---

## Thread Safety

**Not applicable** - This Phase I implementation is single-threaded. The TaskStore is not thread-safe and should only be accessed from the main thread.

**Spec Reference**: Out of Scope - Concurrency
