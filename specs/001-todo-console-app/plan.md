# Implementation Plan: Todo In-Memory Python Console Application

**Branch**: `001-todo-console-app` | **Date**: 2026-01-04 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-todo-console-app/spec.md`

---

## Summary

Implement a Python command-line Todo application with in-memory storage that supports CRUD operations (Create, Read, Update, Delete) plus status toggling through a menu-driven interface. The application uses only Python standard library, follows modular architecture (models/services/CLI separation), and is executed via UV. This is Phase I of the Hackathon project establishing the foundational task management system.

---

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: None (Python standard library only)
**Storage**: In-memory (Python dictionary/list within TaskStore class)
**Testing**: pytest (development dependency only)
**Target Platform**: Console/Terminal (cross-platform: Windows, Linux, macOS)
**Project Type**: Single CLI application
**Performance Goals**: Instant response for all operations; supports 100+ tasks per session (per SC-008)
**Constraints**: No external dependencies; no persistence; single-user sequential operation
**Scale/Scope**: Single-session usage; task count limited only by available memory

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| **I. Spec First** | PASS | Spec exists at `specs/001-todo-console-app/spec.md` with 17 FRs, 6 NFRs, 10 SCs |
| **II. Agent Discipline** | PASS | Plan follows spec-agent/backend-agent/qa-agent boundaries |
| **III. Incremental Evolution** | PASS | This is Phase I; no prior phase requirements |
| **IV. Test-Backed Progress** | PLANNED | Test structure defined; tests to be written with implementation |
| **V. Traceability** | PLANNED | All implementation will reference FR/NFR IDs from spec |

**Phase I Exit Criteria (from Constitution)**:
- All CRUD operations work
- Tests pass
- QA confirms

**Status**: Gate PASSED - proceed to Phase 0

---

## Project Structure

### Documentation (this feature)

```text
specs/001-todo-console-app/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file (/sp.plan output)
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (internal API contracts)
├── checklists/          # Quality validation checklists
│   └── requirements.md  # Spec quality checklist (complete)
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
src/
└── todo/
    ├── __init__.py      # Package marker, version info
    ├── __main__.py      # Entry point: python -m todo
    ├── models.py        # Task dataclass (FR-001 to FR-004)
    ├── services.py      # TaskStore CRUD operations (FR-005 to FR-011)
    └── cli.py           # Menu loop, I/O handling (FR-012 to FR-017)

tests/
├── __init__.py
├── unit/
│   ├── test_models.py   # Task dataclass unit tests
│   └── test_services.py # TaskStore unit tests
└── integration/
    └── test_cli.py      # End-to-end CLI tests

pyproject.toml           # UV/Python configuration
README.md                # Minimal project documentation
```

**Structure Decision**: Single CLI application structure selected. Matches spec requirement for modular separation (models/services/CLI) per NFR-005. No web/mobile components in Phase I.

---

## Complexity Tracking

> No violations detected. All patterns match Phase I scope.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |

---

## Execution Phases

### Phase 1: Project Setup & Structure

**Purpose**: Establish the Python project foundation with UV configuration and directory structure.

**Responsibilities**:
- Initialize UV project with `pyproject.toml`
- Create source directory structure (`src/todo/`)
- Create test directory structure (`tests/unit/`, `tests/integration/`)
- Configure pytest as development dependency
- Verify Python 3.13+ compatibility

**Expected Outcomes**:
- Project runs with `uv run python -m todo` (exits cleanly even if empty)
- pytest discovers and runs tests (even if no tests exist yet)
- Directory structure matches spec Project Structure Requirements

**Dependencies**: None

**Spec Mapping**:
- NFR-001 (Python 3.13+)
- NFR-002 (UV environment)
- NFR-005 (modular structure)
- Project Structure Requirements section

**Completion Criteria**:
- [ ] `pyproject.toml` exists with Python 3.13+ requirement
- [ ] `src/todo/__init__.py` exists
- [ ] `src/todo/__main__.py` exists and is executable
- [ ] `tests/__init__.py` exists
- [ ] `uv run python -m todo` executes without import errors

---

### Phase 2: Core Domain Modeling

**Purpose**: Define the Task data structure as the foundational domain entity.

**Responsibilities**:
- Implement `Task` dataclass in `models.py`
- Define fields: `id` (int), `title` (str), `description` (str), `is_complete` (bool)
- Ensure immutability of `id` field after creation
- Set default values: `description=""`, `is_complete=False`
- Implement input validation for title (non-empty, non-whitespace)

**Expected Outcomes**:
- Task instances can be created with valid data
- Task instances reject empty/whitespace titles
- Task fields are accessible and modifiable (except id)

**Dependencies**: Phase 1 (project structure exists)

**Spec Mapping**:
- FR-001 (required title)
- FR-002 (optional description)
- FR-003 (auto-generated unique ID)
- FR-004 (default incomplete status)
- Key Entities: Task definition

**Completion Criteria**:
- [ ] `models.py` contains `Task` dataclass/class
- [ ] Task has all four required fields
- [ ] Title validation rejects empty/whitespace strings
- [ ] Unit tests verify Task creation and validation

---

### Phase 3: In-Memory Task Management Logic

**Purpose**: Implement the TaskStore service with all CRUD operations.

**Responsibilities**:
- Implement `TaskStore` class in `services.py`
- Implement ID generation (sequential positive integers starting from 1)
- Implement `add(title, description)` → returns new Task
- Implement `get_all()` → returns list of all Tasks
- Implement `get_by_id(id)` → returns Task or None
- Implement `update(id, title, description)` → returns updated Task or None
- Implement `delete(id)` → returns True/False
- Implement `toggle_complete(id)` → returns updated Task or None
- Ensure ID uniqueness among existing tasks
- Encapsulate state (no global mutable state)

**Expected Outcomes**:
- All CRUD operations work correctly
- ID generation is deterministic and unique
- Operations return appropriate results or None for not-found cases
- State is encapsulated within TaskStore instance

**Dependencies**: Phase 2 (Task model exists)

**Spec Mapping**:
- FR-003 (unique ID generation)
- FR-007, FR-008, FR-009 (update operations)
- FR-010 (delete operation)
- FR-011 (toggle status)
- FR-016 (in-memory storage)
- NFR-004 (deterministic behavior)
- NFR-006 (no global state)
- Key Entities: TaskStore definition

**Completion Criteria**:
- [ ] `services.py` contains `TaskStore` class
- [ ] All CRUD methods implemented
- [ ] ID generation starts at 1 and increments
- [ ] Operations return None/False for non-existent IDs
- [ ] Unit tests cover all TaskStore operations
- [ ] Unit tests cover edge cases (empty store, duplicate operations)

---

### Phase 4: CLI Interaction Flow

**Purpose**: Implement the menu-driven console interface connecting user input to TaskStore operations.

**Responsibilities**:
- Implement `cli.py` with menu display function
- Implement input handling for each menu option (1-6)
- Implement output formatting for task list display
- Implement success/error message display
- Implement main loop (show menu → get input → execute → repeat)
- Wire CLI to TaskStore instance
- Implement `__main__.py` entry point

**Expected Outcomes**:
- Application displays menu on startup
- User can select options 1-6
- Each operation executes and displays appropriate output
- Application returns to menu after each operation
- Option 6 exits cleanly with goodbye message

**Dependencies**: Phase 3 (TaskStore is complete)

**Spec Mapping**:
- FR-014 (menu-driven interface)
- FR-015 (loop until exit)
- FR-017 (graceful exit)
- Console UX Requirements (all formats)
- SC-010 (clear menu options)

**Completion Criteria**:
- [ ] `cli.py` contains menu display and input handling
- [ ] `__main__.py` instantiates TaskStore and runs main loop
- [ ] Menu displays with all 6 options
- [ ] Each option triggers correct operation
- [ ] Application loops back to menu after operations
- [ ] Exit option terminates cleanly

---

### Phase 5: Validation & Error Handling

**Purpose**: Ensure robust input validation and user-friendly error messages.

**Responsibilities**:
- Validate title input (empty, whitespace-only rejection)
- Validate ID input (non-numeric, negative, zero rejection)
- Display appropriate error messages per spec formats
- Ensure invalid input never crashes application
- Implement re-prompting for invalid inputs where specified
- Ensure all operations provide immediate feedback

**Expected Outcomes**:
- Empty/whitespace titles are rejected with "Title is required"
- Invalid IDs show "Invalid ID format" or "Invalid ID"
- Non-existent IDs show "Task not found with ID: X"
- Application never crashes on invalid input
- User is re-prompted after errors where appropriate

**Dependencies**: Phase 4 (CLI flow is complete)

**Spec Mapping**:
- FR-012 (task not found errors)
- FR-013 (invalid input errors)
- SC-006 (immediate feedback)
- SC-007 (no crashes on invalid input)
- SC-009 (human-readable error messages)
- Edge Cases section

**Completion Criteria**:
- [ ] All error message formats match spec
- [ ] Empty title rejected with correct message
- [ ] Non-numeric ID rejected with correct message
- [ ] Negative/zero ID rejected with correct message
- [ ] Non-existent ID shows task not found
- [ ] Application recovers from all invalid inputs
- [ ] Integration tests verify error handling

---

### Phase 6: Acceptance Validation Readiness

**Purpose**: Ensure all acceptance criteria are met and application is ready for QA validation.

**Responsibilities**:
- Verify all 13 acceptance criteria from spec are testable
- Create integration tests mapping to acceptance scenarios
- Verify console output formats match spec exactly
- Perform manual testing of all user stories
- Document any deviations or clarifications needed
- Prepare for QA agent review

**Expected Outcomes**:
- All acceptance criteria have corresponding tests
- All user story scenarios pass
- Output formats match spec examples
- Edge cases are handled correctly
- Application is ready for Phase I exit criteria validation

**Dependencies**: Phase 5 (all features and validation complete)

**Spec Mapping**:
- All User Stories (1-6)
- All Acceptance Scenarios
- Acceptance Criteria Summary table
- Success Criteria SC-001 to SC-010

**Completion Criteria**:
- [ ] Integration tests exist for all 13 acceptance criteria
- [ ] All tests pass
- [ ] Manual verification of each user story scenario
- [ ] Output formats verified against spec examples
- [ ] Edge cases tested and documented
- [ ] Ready for QA agent confirmation

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Python version compatibility | Low | Medium | Test on Python 3.13 specifically; use only stdlib |
| Console output formatting differences | Medium | Low | Use ASCII characters only; test on multiple terminals |
| ID generation edge cases | Low | Medium | Unit test ID generation exhaustively; document behavior |

---

## Next Steps

After plan approval:
1. Run `/sp.tasks` to generate atomic implementation tasks
2. Execute tasks in order with test-first approach
3. Run QA validation after Phase 6 completion
4. Document Phase I completion for constitution compliance
