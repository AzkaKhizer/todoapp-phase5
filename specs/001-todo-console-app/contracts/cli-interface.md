# CLI Interface Contract

**Branch**: `001-todo-console-app` | **Date**: 2026-01-04
**Module**: `src/todo/cli.py`

---

## Overview

This document defines the user-facing interface contract for the console application. It specifies the exact input prompts and output formats that the CLI must implement.

---

## Menu System

### Main Menu

**Display Format**:
```
========================================
          TODO APPLICATION
========================================

1. Add Task
2. View Tasks
3. Update Task
4. Delete Task
5. Toggle Complete
6. Exit

Enter your choice (1-6):
```

**Input**: Single character or number (1-6)

**Invalid Input Response**:
```
Invalid choice. Please enter a number between 1 and 6.
```

**Spec Reference**: FR-014, SC-010

---

## Operations

### 1. Add Task

**Prompts**:
```
Enter task title:
```
(wait for input)
```
Enter task description (press Enter to skip):
```
(wait for input)

**Success Output**:
```
Task added successfully! (ID: {id})
```

**Error Output** (empty title):
```
Error: Title is required.
```

**Behavior**:
- Empty description input = empty string stored
- After success or error, return to main menu

**Spec Reference**: FR-001, FR-002, FR-013, User Story 1

---

### 2. View Tasks

**Non-Empty List Output**:
```
========================================
             YOUR TASKS
========================================

ID: {id}
[ ] {title}
    {description}

ID: {id}
[X] {title}
    {description}

========================================
Total: {count} tasks ({complete} complete, {incomplete} incomplete)
```

**Status Indicators**:
- `[ ]` = incomplete (`is_complete = False`)
- `[X]` = complete (`is_complete = True`)

**Empty List Output**:
```
========================================
             YOUR TASKS
========================================

No tasks found. Add a task to get started!

========================================
```

**Behavior**:
- Display all tasks in order of creation (by ID)
- Show description indented below title
- After display, return to main menu

**Spec Reference**: FR-005, FR-006, User Story 2

---

### 3. Update Task

**Prompts**:
```
Enter task ID to update:
```
(wait for input)
```
Enter new title (press Enter to keep current):
```
(wait for input)
```
Enter new description (press Enter to keep current):
```
(wait for input)

**Success Output**:
```
Task updated successfully!
```

**Error Output** (task not found):
```
Error: Task not found with ID: {id}
```

**Error Output** (invalid ID format):
```
Error: Invalid ID format. Please enter a number.
```

**Error Output** (invalid ID value):
```
Error: Invalid ID. Please enter a positive number.
```

**Behavior**:
- Empty input for title/description = keep current value
- Non-empty input = replace value
- Validate ID before prompting for title/description
- After success or error, return to main menu

**Spec Reference**: FR-007, FR-008, FR-009, FR-012, FR-013, User Story 3

---

### 4. Delete Task

**Prompts**:
```
Enter task ID to delete:
```
(wait for input)

**Success Output**:
```
Task deleted successfully!
```

**Error Output** (task not found):
```
Error: Task not found with ID: {id}
```

**Error Output** (invalid ID format):
```
Error: Invalid ID format. Please enter a number.
```

**Behavior**:
- No confirmation prompt required (per spec)
- After success or error, return to main menu

**Spec Reference**: FR-010, FR-012, FR-013, User Story 4

---

### 5. Toggle Complete

**Prompts**:
```
Enter task ID to toggle:
```
(wait for input)

**Success Output** (marked complete):
```
Task marked as complete!
```

**Success Output** (marked incomplete):
```
Task marked as incomplete!
```

**Error Output** (task not found):
```
Error: Task not found with ID: {id}
```

**Error Output** (invalid ID format):
```
Error: Invalid ID format. Please enter a number.
```

**Behavior**:
- Flip current status
- Message varies based on new status
- After success or error, return to main menu

**Spec Reference**: FR-011, FR-012, FR-013, User Story 5

---

### 6. Exit

**Output**:
```
Thank you for using Todo App. Goodbye!
```

**Behavior**:
- Display message and terminate application
- No confirmation required

**Spec Reference**: FR-017, User Story 6

---

## Input Validation Rules

| Input Type | Valid | Invalid | Error Message |
|------------|-------|---------|---------------|
| Menu choice | "1" to "6" | Other | "Invalid choice. Please enter a number between 1 and 6." |
| Task ID | Positive integer string | Non-numeric | "Error: Invalid ID format. Please enter a number." |
| Task ID | > 0 | <= 0 | "Error: Invalid ID. Please enter a positive number." |
| Title | Non-empty after strip | Empty/whitespace | "Error: Title is required." |
| Description | Any string | N/A | N/A (always valid) |

**Spec Reference**: FR-013, SC-007, Edge Cases section

---

## Flow Diagram

```
┌──────────────────┐
│   Application    │
│     Start        │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   Display Menu   │◄────────────────────────┐
└────────┬─────────┘                         │
         │                                   │
         ▼                                   │
┌──────────────────┐                         │
│   Get Choice     │                         │
└────────┬─────────┘                         │
         │                                   │
    ┌────┴────┬────┬────┬────┬────┐          │
    ▼         ▼    ▼    ▼    ▼    ▼          │
   1:Add   2:View 3:Upd 4:Del 5:Tog 6:Exit   │
    │         │    │    │    │    │          │
    └────┬────┴────┴────┴────┴────│          │
         │                        │          │
         │                        ▼          │
         │               ┌─────────────┐     │
         │               │   Display   │     │
         │               │   Goodbye   │     │
         │               └──────┬──────┘     │
         │                      │            │
         │                      ▼            │
         │               ┌─────────────┐     │
         │               │  Terminate  │     │
         │               └─────────────┘     │
         │                                   │
         └───────────────────────────────────┘
```

---

## Console Width Assumptions

- Header separators: 40 `=` characters
- Task display: Fits within 80 character terminal
- No wrapping logic required (long titles/descriptions display as-is)

**Spec Reference**: Assumptions - Console supports standard ASCII
