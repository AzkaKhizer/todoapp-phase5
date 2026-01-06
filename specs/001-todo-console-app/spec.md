# Feature Specification: Todo In-Memory Python Console Application

**Feature Branch**: `001-todo-console-app`
**Created**: 2026-01-04
**Status**: Draft
**Input**: Phase I — Todo In-Memory Python Console Application for "The Evolution of Todo: Spec-Driven, Agentic AI Development" Hackathon

---

## Overview

This specification defines a command-line Todo application implemented in Python that stores all task data in memory. The application provides basic task management functionality including creating, viewing, updating, deleting, and completing tasks through a menu-driven console interface.

**Project Context**: This is Phase I of a multi-phase Hackathon project. This phase establishes the foundational task management functionality without persistence, external dependencies, or advanced features.

### Scope

**In Scope**:
- Add Task (title required, description optional, auto-generated ID, default status: incomplete)
- View Tasks (list all with ID, title, description, status with visual indicators)
- Update Task (modify title and/or description by ID)
- Delete Task (remove task by ID)
- Mark Task Complete/Incomplete (toggle status by ID)
- Menu-driven console interaction
- In-memory storage only (data resets on exit)

**Out of Scope**:
- File or database storage/persistence
- Web UI or REST APIs
- User authentication/authorization
- AI or NLP features
- Background jobs or scheduled tasks
- Concurrent/multi-threaded operations
- Task priorities or categories
- Due dates or reminders
- Search or filter functionality

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Add a New Task (Priority: P1)

As a user, I want to add a new task to my todo list so that I can track work I need to complete.

**Why this priority**: Adding tasks is the foundational capability. Without the ability to add tasks, no other features can function. This is the entry point for all user interaction with the application.

**Independent Test**: Can be fully tested by launching the application, selecting "Add Task", entering a title, and verifying the task appears in the task list with a unique ID and incomplete status.

**Acceptance Scenarios**:

1. **Given** the application is running and showing the main menu, **When** I select "Add Task" and enter a title "Buy groceries", **Then** a new task is created with an auto-generated unique ID, the title "Buy groceries", empty description, and status "incomplete".

2. **Given** the application is running, **When** I select "Add Task", enter title "Call doctor", and enter description "Schedule annual checkup", **Then** a new task is created with the title, description, unique ID, and status "incomplete".

3. **Given** the application is running, **When** I select "Add Task" and press Enter without typing a title (empty input), **Then** the system displays an error message "Title is required" and prompts me to enter a title again.

4. **Given** I have added two tasks, **When** I add a third task, **Then** the third task receives a unique ID different from the first two tasks.

---

### User Story 2 - View All Tasks (Priority: P1)

As a user, I want to view all my tasks so that I can see what I need to do and what I have completed.

**Why this priority**: Viewing tasks is essential for users to understand their task list. This is a read-only operation that enables users to make decisions about which tasks to work on.

**Independent Test**: Can be tested by adding several tasks and then selecting "View Tasks" to verify all tasks are displayed with correct information and visual status indicators.

**Acceptance Scenarios**:

1. **Given** I have added tasks "Task A" (incomplete) and "Task B" (complete), **When** I select "View Tasks", **Then** both tasks are displayed showing their ID, title, description, and status with a clear visual indicator distinguishing complete from incomplete (e.g., `[ ]` for incomplete, `[X]` for complete).

2. **Given** no tasks have been added, **When** I select "View Tasks", **Then** the system displays a message "No tasks found" or equivalent.

3. **Given** I have a task with ID 1, title "Buy milk", description "2% milk from store", status incomplete, **When** I view tasks, **Then** I see output formatted clearly showing all four attributes.

---

### User Story 3 - Update an Existing Task (Priority: P2)

As a user, I want to update a task's title or description so that I can correct mistakes or add more detail.

**Why this priority**: Users need to modify tasks after creation to fix errors or update information. This is secondary to creation and viewing.

**Independent Test**: Can be tested by creating a task, selecting "Update Task", entering the task ID, providing new title/description, and verifying the changes are reflected when viewing tasks.

**Acceptance Scenarios**:

1. **Given** a task exists with ID 1 and title "Buy grocries", **When** I select "Update Task", enter ID 1, and change the title to "Buy groceries", **Then** the task's title is updated and the ID remains 1.

2. **Given** a task exists with ID 2 and empty description, **When** I update the task and add description "Important meeting", **Then** the task now has the description "Important meeting".

3. **Given** a task exists with ID 3, **When** I update the task and leave title blank (press Enter), **Then** the original title is preserved (only non-empty inputs update fields).

4. **Given** no task exists with ID 99, **When** I select "Update Task" and enter ID 99, **Then** the system displays an error message "Task not found".

5. **Given** a task exists with ID 1, **When** I update it, **Then** the task's ID remains 1 (IDs are immutable).

---

### User Story 4 - Delete a Task (Priority: P2)

As a user, I want to delete a task so that I can remove tasks I no longer need.

**Why this priority**: Deletion allows users to clean up their task list. It's destructive, so careful handling is required.

**Independent Test**: Can be tested by creating a task, noting its ID, selecting "Delete Task", entering the ID, and verifying the task no longer appears when viewing tasks.

**Acceptance Scenarios**:

1. **Given** a task exists with ID 1, **When** I select "Delete Task" and enter ID 1, **Then** the task is removed and no longer appears in the task list.

2. **Given** no task exists with ID 99, **When** I select "Delete Task" and enter ID 99, **Then** the system displays an error message "Task not found".

3. **Given** a task with ID 1 is deleted, **When** I add a new task, **Then** the new task may reuse ID 1 or receive a new unique ID (implementation detail, but IDs must always be unique among existing tasks).

---

### User Story 5 - Mark Task Complete/Incomplete (Priority: P2)

As a user, I want to toggle a task's completion status so that I can track my progress.

**Why this priority**: Marking tasks complete is core to todo functionality, enabling users to track what they have accomplished.

**Independent Test**: Can be tested by creating an incomplete task, toggling it to complete, verifying the status change, then toggling again to verify it returns to incomplete.

**Acceptance Scenarios**:

1. **Given** a task exists with ID 1 and status "incomplete", **When** I select "Toggle Complete" and enter ID 1, **Then** the task's status changes to "complete".

2. **Given** a task exists with ID 1 and status "complete", **When** I select "Toggle Complete" and enter ID 1, **Then** the task's status changes to "incomplete".

3. **Given** no task exists with ID 99, **When** I select "Toggle Complete" and enter ID 99, **Then** the system displays an error message "Task not found".

---

### User Story 6 - Exit Application (Priority: P3)

As a user, I want to exit the application gracefully so that I can close the program when done.

**Why this priority**: Essential for application lifecycle but not core to task management functionality.

**Independent Test**: Can be tested by selecting "Exit" from the menu and verifying the application terminates cleanly.

**Acceptance Scenarios**:

1. **Given** the application is running, **When** I select "Exit", **Then** the application displays a goodbye message and terminates.

2. **Given** I have added tasks during the session, **When** I exit and restart the application, **Then** all previously added tasks are gone (in-memory only, no persistence).

---

### Edge Cases

- **Empty title on add**: System rejects and re-prompts for valid title
- **Non-numeric ID input**: System displays error "Invalid ID format" and re-prompts
- **Negative ID input**: System displays error "Invalid ID" (IDs are positive integers)
- **Very long title/description**: System accepts (no enforced limit in Phase I)
- **Special characters in title/description**: System accepts any printable characters
- **Whitespace-only title**: System treats as empty and rejects
- **ID 0**: System treats as invalid (IDs start from 1)
- **Duplicate title**: System allows (uniqueness is by ID only)
- **Rapid consecutive operations**: System handles sequentially (no concurrency)

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow users to add a task with a required title (non-empty, non-whitespace-only string)
- **FR-002**: System MUST allow users to add an optional description when creating a task
- **FR-003**: System MUST auto-generate a unique positive integer ID for each new task
- **FR-004**: System MUST set new tasks to "incomplete" status by default
- **FR-005**: System MUST display all tasks showing ID, title, description, and status
- **FR-006**: System MUST visually distinguish complete tasks from incomplete tasks (e.g., `[X]` vs `[ ]`)
- **FR-007**: System MUST allow users to update a task's title by providing the task ID
- **FR-008**: System MUST allow users to update a task's description by providing the task ID
- **FR-009**: System MUST preserve the task ID when updating title or description
- **FR-010**: System MUST allow users to delete a task by providing the task ID
- **FR-011**: System MUST allow users to toggle a task's status between complete and incomplete
- **FR-012**: System MUST display appropriate error messages when a task ID is not found
- **FR-013**: System MUST display appropriate error messages for invalid input (empty title, non-numeric ID)
- **FR-014**: System MUST provide a menu-driven interface with numbered options
- **FR-015**: System MUST loop back to the main menu after each operation until user exits
- **FR-016**: System MUST store all task data in memory only (no file or database persistence)
- **FR-017**: System MUST gracefully exit when user selects the exit option

### Key Entities

- **Task**: Represents a todo item
  - `id`: Positive integer, unique identifier, auto-generated, immutable after creation
  - `title`: Non-empty string, required, mutable
  - `description`: String (may be empty), optional, mutable
  - `is_complete`: Boolean, default False, toggleable

- **TaskStore**: In-memory collection of tasks
  - Holds all tasks during application runtime
  - Provides operations: add, get_all, get_by_id, update, delete
  - Generates unique IDs for new tasks

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can add a new task in under 30 seconds (title entry + confirmation)
- **SC-002**: Users can view all tasks and immediately identify which are complete vs incomplete
- **SC-003**: Users can update any task's title or description within 3 menu interactions
- **SC-004**: Users can delete a task within 2 menu interactions (select delete, enter ID)
- **SC-005**: Users can toggle task completion status within 2 menu interactions
- **SC-006**: All operations provide immediate feedback (success message or error)
- **SC-007**: Invalid input never causes application crash; user is always re-prompted
- **SC-008**: Application correctly handles at least 100 tasks in a single session
- **SC-009**: All error messages are human-readable and actionable (tell user what went wrong and how to fix)
- **SC-010**: Menu options are clearly numbered and labeled so users can navigate without documentation

---

## Console UX Requirements

### Main Menu Format

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

### Input Prompts

- **Add Task**:
  ```
  Enter task title:
  Enter task description (press Enter to skip):
  ```

- **Update Task**:
  ```
  Enter task ID to update:
  Enter new title (press Enter to keep current):
  Enter new description (press Enter to keep current):
  ```

- **Delete Task**:
  ```
  Enter task ID to delete:
  ```

- **Toggle Complete**:
  ```
  Enter task ID to toggle:
  ```

### Output Formats

- **Task List Display**:
  ```
  ========================================
               YOUR TASKS
  ========================================

  ID: 1
  [ ] Buy groceries
      Get milk, bread, and eggs

  ID: 2
  [X] Call mom
      Wish her happy birthday

  ========================================
  Total: 2 tasks (1 complete, 1 incomplete)
  ```

- **Empty Task List**:
  ```
  ========================================
               YOUR TASKS
  ========================================

  No tasks found. Add a task to get started!

  ========================================
  ```

- **Success Messages**:
  ```
  Task added successfully! (ID: 3)
  Task updated successfully!
  Task deleted successfully!
  Task marked as complete!
  Task marked as incomplete!
  ```

- **Error Messages**:
  ```
  Error: Title is required.
  Error: Invalid ID format. Please enter a number.
  Error: Task not found with ID: 99
  ```

- **Exit Message**:
  ```
  Thank you for using Todo App. Goodbye!
  ```

---

## Project Structure Requirements

```
todo-console-app/
├── pyproject.toml           # UV/Python project configuration
├── README.md                # Project documentation (minimal)
├── src/
│   └── todo/
│       ├── __init__.py      # Package marker
│       ├── __main__.py      # Entry point: python -m todo
│       ├── models.py        # Task dataclass/model
│       ├── services.py      # TaskStore and business logic
│       └── cli.py           # Menu, input/output handling
└── tests/
    ├── __init__.py
    ├── test_models.py       # Unit tests for Task model
    ├── test_services.py     # Unit tests for TaskStore
    └── test_cli.py          # Integration tests for CLI
```

### Module Responsibilities

- **models.py**: Define the `Task` data structure (dataclass or similar)
- **services.py**: Implement `TaskStore` class with CRUD operations and ID generation
- **cli.py**: Handle all console I/O, menu display, user prompts, and flow control
- **__main__.py**: Application entry point, instantiate TaskStore and run main loop

### Execution

```bash
# Using UV
uv run python -m todo

# Or after installation
python -m todo
```

---

## Non-Functional Requirements

- **NFR-001**: Application MUST be compatible with Python 3.13+
- **NFR-002**: Application MUST use UV for environment and dependency management
- **NFR-003**: Application MUST NOT use any external dependencies beyond Python standard library
- **NFR-004**: Application MUST exhibit deterministic behavior (same inputs produce same outputs)
- **NFR-005**: Code MUST be modular with clear separation between models, services, and CLI
- **NFR-006**: Application MUST NOT use mutable global state; state is encapsulated in TaskStore instance

---

## Assumptions

- User has Python 3.13+ installed and accessible
- User has UV installed for project execution
- Console/terminal supports standard ASCII characters
- Single user operates the application (no multi-user support needed)
- Task IDs are sequential positive integers starting from 1
- When updating a task with empty input for a field, the original value is preserved
- Maximum practical limit of tasks is constrained only by available memory

---

## Constraints

- No data persistence between sessions (in-memory only)
- No undo functionality for delete operations
- No bulk operations (add/delete/update multiple tasks at once)
- No sorting or filtering of task list
- No input validation beyond empty title and ID format
- English-only interface

---

## Dependencies

**External Dependencies**: None (standard library only)

**Development Dependencies**:
- UV (environment and package management)
- pytest (for running tests)

---

## Acceptance Criteria Summary

| Feature          | Criteria                                                                 | Verification Method                              |
|------------------|--------------------------------------------------------------------------|--------------------------------------------------|
| Add Task         | Task created with unique ID, title, optional description, status=incomplete | Add task, view tasks, verify all fields          |
| Add Task         | Empty title rejected with error message                                  | Attempt add with empty title, verify error       |
| View Tasks       | All tasks displayed with ID, title, description, status indicator        | Add multiple tasks, view, verify all shown       |
| View Tasks       | Empty list shows appropriate message                                     | View tasks with none added, verify message       |
| Update Task      | Title and/or description updated, ID unchanged                           | Update task, view, verify changes and ID         |
| Update Task      | Invalid ID shows error                                                   | Attempt update with non-existent ID              |
| Delete Task      | Task removed from list                                                   | Delete task, view, verify removal                |
| Delete Task      | Invalid ID shows error                                                   | Attempt delete with non-existent ID              |
| Toggle Status    | Incomplete becomes complete, complete becomes incomplete                 | Toggle twice, verify state changes               |
| Toggle Status    | Invalid ID shows error                                                   | Attempt toggle with non-existent ID              |
| Menu Loop        | Application returns to menu after each operation                         | Perform any operation, verify menu returns       |
| Exit             | Application terminates gracefully                                        | Select exit, verify clean termination            |
| Invalid Input    | Non-numeric ID rejected with error, app continues                        | Enter "abc" for ID, verify error and re-prompt   |
