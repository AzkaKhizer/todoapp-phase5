# Research: Todo In-Memory Python Console Application

**Branch**: `001-todo-console-app` | **Date**: 2026-01-04
**Purpose**: Resolve NEEDS CLARIFICATION items and document technology decisions

---

## Research Summary

This Phase I implementation has **no NEEDS CLARIFICATION items** in the Technical Context. The spec is complete and unambiguous. This document captures technology decisions and best practices for the implementation.

---

## Technology Decisions

### 1. Python Data Structures for Task Model

**Decision**: Use `dataclasses.dataclass` for the Task model

**Rationale**:
- Standard library (no external dependencies per NFR-003)
- Built-in support for default values
- Automatic `__init__`, `__repr__`, `__eq__` generation
- Supports frozen fields for immutability if needed
- Python 3.7+ feature, well within Python 3.13+ requirement

**Alternatives Considered**:
- Named tuples: Rejected - less flexible for mutable fields (title, description can change)
- Plain classes: Rejected - more boilerplate for same functionality
- Pydantic: Rejected - external dependency

### 2. In-Memory Storage Implementation

**Decision**: Use a Python `dict` keyed by task ID within TaskStore class

**Rationale**:
- O(1) lookup by ID (efficient for get_by_id, update, delete, toggle)
- Simple iteration for get_all
- Standard library (no external dependencies)
- Deterministic behavior (per NFR-004)

**Alternatives Considered**:
- List with linear search: Rejected - O(n) lookup by ID
- SQLite in-memory: Rejected - external complexity for simple use case
- OrderedDict: Not needed - insertion order preserved in dict since Python 3.7

### 3. ID Generation Strategy

**Decision**: Sequential counter starting at 1, incrementing for each new task

**Rationale**:
- Matches spec assumption: "Task IDs are sequential positive integers starting from 1"
- Simple and deterministic (per NFR-004)
- Counter stored as instance variable in TaskStore (per NFR-006)
- IDs are never reused even after deletion (simplifies uniqueness guarantee)

**Alternatives Considered**:
- UUID: Rejected - spec requires positive integer IDs
- Reusing deleted IDs: Rejected - adds complexity, potential for confusion
- Timestamp-based: Rejected - overkill for sequential single-user app

### 4. Console I/O Handling

**Decision**: Use `input()` for reading and `print()` for output

**Rationale**:
- Standard library (no external dependencies)
- Simple, synchronous flow matches spec (no concurrency)
- Cross-platform compatibility
- Sufficient for menu-driven interaction

**Alternatives Considered**:
- Rich library: Rejected - external dependency
- Curses/ncurses: Rejected - platform-specific complexity, overkill for simple menus
- Click/Typer: Rejected - external dependency

### 5. Input Validation Approach

**Decision**: Validate at CLI layer before passing to TaskStore

**Rationale**:
- Separation of concerns: CLI handles user input, services handle business logic
- Error messages can be formatted appropriately for console output
- Services receive only valid data

**Validation Rules**:
- Title: Strip whitespace, check if non-empty
- ID: Try int() conversion, check > 0

### 6. Project Layout

**Decision**: Use `src/` layout with `src/todo/` package

**Rationale**:
- Matches spec Project Structure Requirements exactly
- Standard Python packaging convention
- Clean separation from tests
- Enables `python -m todo` execution pattern

---

## Best Practices Applied

### Python CLI Best Practices

1. **Entry Point**: Use `__main__.py` for `python -m package` execution
2. **Error Handling**: Never let exceptions crash the app; catch and display user-friendly messages
3. **Input Loop**: Clear main loop structure with explicit exit condition
4. **Output Formatting**: Consistent visual structure (headers, separators)

### Testing Best Practices

1. **Unit vs Integration**: Separate test files for models, services, and CLI
2. **Test Isolation**: Each test creates its own TaskStore instance
3. **Edge Cases**: Test boundary conditions (empty input, zero/negative IDs, not found)
4. **Determinism**: Tests should produce same results on every run

### Code Quality Best Practices

1. **Type Hints**: Use type annotations for clarity (Python 3.13+ supports all modern syntax)
2. **Docstrings**: Document public classes and methods
3. **No Global State**: All state in TaskStore instance (per NFR-006)
4. **Single Responsibility**: Each module has one purpose

---

## Unknowns Resolved

| Original Unknown | Resolution |
|------------------|------------|
| None identified | All technical context was complete in spec |

---

## Dependencies Confirmed

| Dependency | Status | Notes |
|------------|--------|-------|
| Python 3.13+ | Required | Spec NFR-001 |
| UV | Required | Spec NFR-002; for environment management |
| pytest | Dev only | For running tests; not needed at runtime |
| Standard library | Only deps | dataclasses, typing modules |

---

## Next Steps

1. Proceed to Phase 1: Generate `data-model.md` with entity details
2. Generate internal API contracts in `contracts/`
3. Create `quickstart.md` for development setup
