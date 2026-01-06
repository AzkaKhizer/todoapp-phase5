# Tasks: Todo In-Memory Python Console Application

**Input**: Design documents from `/specs/001-todo-console-app/`
**Prerequisites**: plan.md (complete), spec.md (complete), research.md, data-model.md, contracts/

**Tests**: Included per Constitution principle "IV. Test-Backed Progress" - tests written with implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

---

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization with UV and basic structure per NFR-001, NFR-002

- [x] T001 Create pyproject.toml with Python 3.13+ requirement and pytest dev dependency
- [x] T002 Create src/todo/__init__.py package marker
- [x] T003 [P] Create src/todo/__main__.py with minimal entry point (placeholder)
- [x] T004 [P] Create tests/__init__.py package marker
- [x] T005 [P] Create tests/unit/__init__.py package marker
- [x] T006 [P] Create tests/integration/__init__.py package marker
- [x] T007 Verify project runs with `uv run python -m todo` without errors

**Checkpoint**: Project structure complete, UV environment working

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core entities that ALL user stories depend on - Task model and TaskStore service

**CRITICAL**: No user story work can begin until this phase is complete

### Task Model (models.py)

- [x] T008 Implement Task dataclass in src/todo/models.py with fields: id (int), title (str), description (str), is_complete (bool)
- [x] T009 [P] Create tests/unit/test_models.py with unit tests for Task creation
- [x] T010 Add title validation to Task (reject empty/whitespace-only titles) in src/todo/models.py
- [x] T011 Add unit tests for Task title validation in tests/unit/test_models.py

### TaskStore Service (services.py)

- [x] T012 Implement TaskStore class with _tasks dict and _next_id counter in src/todo/services.py
- [x] T013 Implement TaskStore.add(title, description) method returning new Task in src/todo/services.py
- [x] T014 [P] Create tests/unit/test_services.py with unit tests for TaskStore.add()
- [x] T015 Implement TaskStore.get_all() method returning list of Tasks in src/todo/services.py
- [x] T016 Add unit tests for TaskStore.get_all() in tests/unit/test_services.py
- [x] T017 Implement TaskStore.get_by_id(task_id) method returning Task or None in src/todo/services.py
- [x] T018 Add unit tests for TaskStore.get_by_id() in tests/unit/test_services.py
- [x] T019 Implement TaskStore.update(task_id, title, description) method in src/todo/services.py
- [x] T020 Add unit tests for TaskStore.update() in tests/unit/test_services.py
- [x] T021 Implement TaskStore.delete(task_id) method returning bool in src/todo/services.py
- [x] T022 Add unit tests for TaskStore.delete() in tests/unit/test_services.py
- [x] T023 Implement TaskStore.toggle_complete(task_id) method in src/todo/services.py
- [x] T024 Add unit tests for TaskStore.toggle_complete() in tests/unit/test_services.py

**Checkpoint**: Foundation ready - all unit tests pass, user story implementation can begin

---

## Phase 3: User Story 1 - Add a New Task (Priority: P1)

**Goal**: Users can add tasks with title (required) and description (optional)

**Independent Test**: Launch app, select "Add Task", enter title, verify task created with unique ID

**Spec Reference**: FR-001, FR-002, FR-003, FR-004, FR-013

### Implementation for User Story 1

- [x] T025 [US1] Implement display_menu() function in src/todo/cli.py per Console UX Requirements
- [x] T026 [US1] Implement get_menu_choice() function with validation in src/todo/cli.py
- [x] T027 [US1] Implement add_task_handler(store) function in src/todo/cli.py
- [x] T028 [US1] Implement title input with empty/whitespace validation in add_task_handler() in src/todo/cli.py
- [x] T029 [US1] Implement description input (optional, Enter to skip) in add_task_handler() in src/todo/cli.py
- [x] T030 [US1] Display success message "Task added successfully! (ID: X)" in add_task_handler() in src/todo/cli.py
- [x] T031 [US1] Display error message "Error: Title is required." for empty title in src/todo/cli.py
- [x] T032 [US1] Wire add_task_handler to main loop in src/todo/__main__.py
- [x] T033 [P] [US1] Create tests/integration/test_cli.py with test for add task flow

**Checkpoint**: User Story 1 complete - users can add tasks via menu

---

## Phase 4: User Story 2 - View All Tasks (Priority: P1)

**Goal**: Users can view all tasks with ID, title, description, and status indicator

**Independent Test**: Add tasks, select "View Tasks", verify all displayed with [ ] or [X] indicators

**Spec Reference**: FR-005, FR-006

### Implementation for User Story 2

- [x] T034 [US2] Implement view_tasks_handler(store) function in src/todo/cli.py
- [x] T035 [US2] Implement task list formatting with status indicators ([ ] and [X]) in src/todo/cli.py
- [x] T036 [US2] Display "No tasks found. Add a task to get started!" for empty list in src/todo/cli.py
- [x] T037 [US2] Display task count summary "Total: X tasks (Y complete, Z incomplete)" in src/todo/cli.py
- [x] T038 [US2] Wire view_tasks_handler to main loop in src/todo/__main__.py
- [x] T039 [P] [US2] Add integration test for view tasks flow in tests/integration/test_cli.py

**Checkpoint**: User Stories 1 AND 2 complete - users can add and view tasks

---

## Phase 5: User Story 3 - Update an Existing Task (Priority: P2)

**Goal**: Users can update task title and/or description by ID

**Independent Test**: Create task, update title, verify change persists, ID unchanged

**Spec Reference**: FR-007, FR-008, FR-009, FR-012, FR-013

### Implementation for User Story 3

- [x] T040 [US3] Implement update_task_handler(store) function in src/todo/cli.py
- [x] T041 [US3] Implement ID input with validation (numeric, positive) in update_task_handler() in src/todo/cli.py
- [x] T042 [US3] Implement title/description prompts (Enter to keep current) in update_task_handler() in src/todo/cli.py
- [x] T043 [US3] Display success message "Task updated successfully!" in src/todo/cli.py
- [x] T044 [US3] Display error "Error: Task not found with ID: X" for invalid ID in src/todo/cli.py
- [x] T045 [US3] Wire update_task_handler to main loop in src/todo/__main__.py
- [x] T046 [P] [US3] Add integration test for update task flow in tests/integration/test_cli.py

**Checkpoint**: User Stories 1, 2, AND 3 complete

---

## Phase 6: User Story 4 - Delete a Task (Priority: P2)

**Goal**: Users can delete a task by ID

**Independent Test**: Create task, delete by ID, verify no longer in list

**Spec Reference**: FR-010, FR-012, FR-013

### Implementation for User Story 4

- [x] T047 [US4] Implement delete_task_handler(store) function in src/todo/cli.py
- [x] T048 [US4] Implement ID input with validation in delete_task_handler() in src/todo/cli.py
- [x] T049 [US4] Display success message "Task deleted successfully!" in src/todo/cli.py
- [x] T050 [US4] Display error "Error: Task not found with ID: X" for invalid ID in src/todo/cli.py
- [x] T051 [US4] Wire delete_task_handler to main loop in src/todo/__main__.py
- [x] T052 [P] [US4] Add integration test for delete task flow in tests/integration/test_cli.py

**Checkpoint**: User Stories 1-4 complete

---

## Phase 7: User Story 5 - Mark Task Complete/Incomplete (Priority: P2)

**Goal**: Users can toggle task completion status by ID

**Independent Test**: Create task (incomplete), toggle (complete), toggle again (incomplete)

**Spec Reference**: FR-011, FR-012, FR-013

### Implementation for User Story 5

- [x] T053 [US5] Implement toggle_complete_handler(store) function in src/todo/cli.py
- [x] T054 [US5] Implement ID input with validation in toggle_complete_handler() in src/todo/cli.py
- [x] T055 [US5] Display "Task marked as complete!" or "Task marked as incomplete!" based on new status in src/todo/cli.py
- [x] T056 [US5] Display error "Error: Task not found with ID: X" for invalid ID in src/todo/cli.py
- [x] T057 [US5] Wire toggle_complete_handler to main loop in src/todo/__main__.py
- [x] T058 [P] [US5] Add integration test for toggle complete flow in tests/integration/test_cli.py

**Checkpoint**: User Stories 1-5 complete

---

## Phase 8: User Story 6 - Exit Application (Priority: P3)

**Goal**: Users can exit the application gracefully

**Independent Test**: Select exit, verify goodbye message displayed and app terminates

**Spec Reference**: FR-015, FR-017

### Implementation for User Story 6

- [x] T059 [US6] Implement exit handler displaying "Thank you for using Todo App. Goodbye!" in src/todo/cli.py
- [x] T060 [US6] Implement main loop termination on exit choice in src/todo/__main__.py
- [x] T061 [US6] Ensure menu loops back after all operations except exit in src/todo/__main__.py
- [x] T062 [P] [US6] Add integration test for exit flow in tests/integration/test_cli.py

**Checkpoint**: All user stories complete - full application functional

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Error handling refinement, edge cases, final validation

- [x] T063 Implement invalid menu choice handling "Invalid choice. Please enter a number between 1 and 6." in src/todo/cli.py
- [x] T064 [P] Add edge case tests for invalid ID formats (non-numeric, negative, zero) in tests/integration/test_cli.py
- [x] T065 [P] Add edge case tests for whitespace-only titles in tests/integration/test_cli.py
- [x] T066 Verify all output formats match spec Console UX Requirements exactly
- [x] T067 Run full test suite and verify all tests pass
- [x] T068 Run quickstart.md validation (uv run python -m todo executes correctly)

**Checkpoint**: Phase I complete - ready for QA validation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **User Stories (Phases 3-8)**: All depend on Foundational completion
  - Can proceed sequentially P1 → P2 → P3
  - Or in parallel if multiple developers
- **Polish (Phase 9)**: Depends on all user stories complete

### User Story Dependencies

- **User Story 1 (P1)**: After Foundational - no dependencies on other stories
- **User Story 2 (P1)**: After Foundational - independent of US1
- **User Story 3 (P2)**: After Foundational - requires task to exist (but creates own in test)
- **User Story 4 (P2)**: After Foundational - independent
- **User Story 5 (P2)**: After Foundational - independent
- **User Story 6 (P3)**: After Foundational - independent

### Within Each User Story

- Handler implementation before wiring to main loop
- Main implementation before integration tests
- Tests can run in parallel with other stories' tests

### Parallel Opportunities

**Phase 1 (Setup):**
```
T003 [P] + T004 [P] + T005 [P] + T006 [P] (all package markers)
```

**Phase 2 (Foundational):**
```
T009 [P] (model tests) + T014 [P] (service tests init)
```

**User Stories (after Foundational):**
```
All user stories can run in parallel if team capacity allows:
- Developer A: US1 + US2 (P1 priority)
- Developer B: US3 + US4 (P2 priority)
- Developer C: US5 + US6 (P2/P3 priority)
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Add Task)
4. Complete Phase 4: User Story 2 (View Tasks)
5. **STOP and VALIDATE**: Add + View tasks working
6. Demo MVP

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 (Add) + US2 (View) → **MVP Demo!**
3. Add US3 (Update) → Test independently → Demo
4. Add US4 (Delete) → Test independently → Demo
5. Add US5 (Toggle) → Test independently → Demo
6. Add US6 (Exit) → Full application → Demo

---

## Task Count Summary

| Phase | Task Count | Parallel Tasks |
|-------|------------|----------------|
| Phase 1: Setup | 7 | 4 |
| Phase 2: Foundational | 17 | 4 |
| Phase 3: US1 Add Task | 9 | 1 |
| Phase 4: US2 View Tasks | 6 | 1 |
| Phase 5: US3 Update Task | 7 | 1 |
| Phase 6: US4 Delete Task | 6 | 1 |
| Phase 7: US5 Toggle Complete | 6 | 1 |
| Phase 8: US6 Exit | 4 | 1 |
| Phase 9: Polish | 6 | 2 |
| **Total** | **68** | **16** |

---

## Spec Traceability

| Requirement | Tasks |
|-------------|-------|
| FR-001 (title required) | T008, T010, T027, T028 |
| FR-002 (optional description) | T008, T029 |
| FR-003 (unique ID) | T012, T013 |
| FR-004 (default incomplete) | T008 |
| FR-005 (display all) | T015, T034, T035 |
| FR-006 (visual status) | T035 |
| FR-007, FR-008, FR-009 (update) | T019, T040-T044 |
| FR-010 (delete) | T021, T047-T050 |
| FR-011 (toggle) | T023, T053-T056 |
| FR-012 (not found error) | T044, T050, T056 |
| FR-013 (invalid input error) | T028, T031, T041, T048, T054, T063 |
| FR-014 (menu) | T025, T026 |
| FR-015 (loop) | T061 |
| FR-016 (in-memory) | T012 |
| FR-017 (graceful exit) | T059, T060 |
| NFR-001 (Python 3.13+) | T001 |
| NFR-002 (UV) | T001, T007 |
| NFR-005 (modular) | T002-T006 |
| NFR-006 (no global state) | T012 |

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All tasks reference spec FRs and Console UX Requirements
