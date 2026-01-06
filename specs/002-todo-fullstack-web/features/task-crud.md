# Feature Specification: Task CRUD Operations

**Parent Spec**: @specs/002-todo-fullstack-web/spec.md
**Feature Branch**: `002-todo-fullstack-web`
**Created**: 2026-01-05

---

## Overview

This document specifies the Create, Read, Update, and Delete (CRUD) operations for task management in the Todo Full-Stack Web Application. All operations require authentication and enforce user-based data isolation.

---

## User Stories

### US-TASK-1: Create Task (Priority: P1)

**As a** logged-in user,
**I want to** create new tasks,
**So that** I can track work I need to complete.

**Acceptance Criteria**:

| AC ID | Scenario | Given | When | Then |
|-------|----------|-------|------|------|
| AC-1.1 | Create with title only | I am on the dashboard | I enter title "Buy groceries" and submit | Task appears in list with empty description, is_complete=false |
| AC-1.2 | Create with title and description | I am on the dashboard | I enter title and description | Task is saved with both fields |
| AC-1.3 | Empty title rejected | I am creating a task | I submit with empty title | Validation error "Title is required" shown |
| AC-1.4 | Whitespace-only title rejected | I am creating a task | I submit with "   " as title | Validation error "Title is required" shown |
| AC-1.5 | Task receives UUID | I create a task | Task is saved | Task has unique UUID identifier |
| AC-1.6 | Task owned by creator | I create a task | Task is saved | Task.user_id matches my user ID |
| AC-1.7 | Timestamps recorded | I create a task | Task is saved | created_at and updated_at are set |

**Validation Rules**:
- Title: Required, 1-200 characters, trimmed whitespace
- Description: Optional, 0-2000 characters

---

### US-TASK-2: View Tasks (Priority: P1)

**As a** logged-in user,
**I want to** view all my tasks,
**So that** I can see what needs to be done.

**Acceptance Criteria**:

| AC ID | Scenario | Given | When | Then |
|-------|----------|-------|------|------|
| AC-2.1 | View all tasks | I have 5 tasks | I load the dashboard | All 5 tasks displayed with title, description, status |
| AC-2.2 | Empty state | I have no tasks | I load the dashboard | Message "No tasks yet. Create your first task!" |
| AC-2.3 | Status indicators | I have complete and incomplete tasks | I view the list | Complete: checkmark, Incomplete: empty checkbox |
| AC-2.4 | User isolation | Another user has tasks | I view my dashboard | I see only my tasks (0 cross-user leakage) |
| AC-2.5 | Order by creation | I have multiple tasks | I view the list | Tasks ordered by created_at descending (newest first) |
| AC-2.6 | Show timestamps | Task exists | I view task details | Created and updated times visible |

**Display Fields**:
- Task ID (for operations, may be hidden in UI)
- Title (always visible)
- Description (if present)
- Completion checkbox/indicator
- Created timestamp (optional display)

---

### US-TASK-3: Update Task (Priority: P1)

**As a** logged-in user,
**I want to** update my tasks,
**So that** I can correct mistakes or add details.

**Acceptance Criteria**:

| AC ID | Scenario | Given | When | Then |
|-------|----------|-------|------|------|
| AC-3.1 | Update title | Task exists with title "Buy grocries" | I change to "Buy groceries" and save | Title is updated |
| AC-3.2 | Update description | Task exists | I add/change description and save | Description is updated |
| AC-3.3 | Clear description | Task has description | I clear description and save | Description becomes empty |
| AC-3.4 | Empty title rejected | I am editing a task | I clear title and save | Validation error shown |
| AC-3.5 | Cancel discards changes | I made unsaved edits | I click cancel | Original values remain |
| AC-3.6 | Updated_at changes | I update a task | Save completes | updated_at timestamp refreshed |
| AC-3.7 | Cannot update others' tasks | Task belongs to another user | I attempt to update | 403 Forbidden error |
| AC-3.8 | Non-existent task | Task ID doesn't exist | I attempt to update | 404 Not Found error |

**Update Rules**:
- Only owner can update
- Title cannot become empty
- Description can be cleared
- ID cannot be changed
- user_id cannot be changed
- created_at cannot be changed

---

### US-TASK-4: Delete Task (Priority: P1)

**As a** logged-in user,
**I want to** delete tasks,
**So that** I can remove items I no longer need.

**Acceptance Criteria**:

| AC ID | Scenario | Given | When | Then |
|-------|----------|-------|------|------|
| AC-4.1 | Delete own task | I have a task | I click delete and confirm | Task removed from list |
| AC-4.2 | Cancel delete | Delete confirmation shown | I click cancel | Task remains in list |
| AC-4.3 | Deletion persists | I delete a task | I refresh the page | Deleted task not in list |
| AC-4.4 | Cannot delete others' tasks | Task belongs to another user | I attempt to delete | 403 Forbidden error |
| AC-4.5 | Non-existent task | Task ID doesn't exist | I attempt to delete | 404 Not Found error |
| AC-4.6 | Immediate UI update | I confirm delete | UI updates | Task disappears without page refresh |

**Delete Confirmation**:
- Modal or inline confirmation required
- Message: "Delete this task? This action cannot be undone."
- Options: "Delete" (danger), "Cancel" (neutral)

---

### US-TASK-5: Toggle Task Completion (Priority: P1)

**As a** logged-in user,
**I want to** mark tasks as complete or incomplete,
**So that** I can track my progress.

**Acceptance Criteria**:

| AC ID | Scenario | Given | When | Then |
|-------|----------|-------|------|------|
| AC-5.1 | Mark complete | Task is incomplete | I click the checkbox | Task becomes complete, visual indicator changes |
| AC-5.2 | Mark incomplete | Task is complete | I click the checkbox | Task becomes incomplete |
| AC-5.3 | Toggle persists | I toggle completion | I refresh the page | Status remains as set |
| AC-5.4 | Updated_at changes | I toggle completion | API responds | updated_at timestamp refreshed |
| AC-5.5 | Instant feedback | I click checkbox | Immediately | Visual feedback within 200ms |
| AC-5.6 | Cannot toggle others' tasks | Task belongs to another user | I attempt to toggle | 403 Forbidden error |

**Visual States**:
- Incomplete: Empty checkbox/circle
- Complete: Filled checkbox with checkmark, optional strikethrough on title

---

## Input/Output Specifications

### Create Task

**Input**:
| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| title | string | Yes | 1-200 chars, trimmed |
| description | string | No | 0-2000 chars |

**Output** (Success):
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Auto-generated identifier |
| title | string | As submitted |
| description | string | As submitted or empty |
| is_complete | boolean | false |
| user_id | UUID | Authenticated user's ID |
| created_at | datetime | Server timestamp |
| updated_at | datetime | Same as created_at |

---

### Read Tasks (List)

**Input**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Authorization | header | Yes | Bearer JWT token |

**Output** (Success):
| Field | Type | Description |
|-------|------|-------------|
| tasks | array | List of task objects |
| count | integer | Total number of tasks |

---

### Update Task

**Input**:
| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| id | UUID | Yes | Path parameter |
| title | string | No | 1-200 chars if provided |
| description | string | No | 0-2000 chars |

**Output** (Success): Updated task object with new updated_at

---

### Delete Task

**Input**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Yes | Path parameter |

**Output** (Success):
| Field | Type | Description |
|-------|------|-------------|
| message | string | "Task deleted successfully" |

---

### Toggle Completion

**Input**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Yes | Path parameter |

**Output** (Success): Updated task object with toggled is_complete and new updated_at

---

## Error Responses

| Error Code | HTTP Status | Message | Trigger |
|------------|-------------|---------|---------|
| TASK_NOT_FOUND | 404 | "Task not found" | Task ID doesn't exist |
| TASK_FORBIDDEN | 403 | "You don't have permission to access this task" | Task belongs to another user |
| VALIDATION_ERROR | 400 | "Title is required" | Empty/whitespace title |
| VALIDATION_ERROR | 400 | "Title must be 200 characters or less" | Title too long |
| VALIDATION_ERROR | 400 | "Description must be 2000 characters or less" | Description too long |
| UNAUTHORIZED | 401 | "Authentication required" | Missing/invalid JWT |

---

## Data Isolation Requirements

1. **Query Filtering**: All task queries MUST include `WHERE user_id = <authenticated_user_id>`
2. **Ownership Verification**: Before update/delete, verify `task.user_id == authenticated_user_id`
3. **No Cross-User Access**: API MUST never return tasks belonging to other users
4. **No ID Enumeration**: Use UUIDs to prevent guessing task IDs

---

## Related Documents

- @specs/002-todo-fullstack-web/api/rest-endpoints.md - API implementation details
- @specs/002-todo-fullstack-web/database/schema.md - Task table schema
- @specs/002-todo-fullstack-web/ui/components.md - TaskCard, TaskForm components
