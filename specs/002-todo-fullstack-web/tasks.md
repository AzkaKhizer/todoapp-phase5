# Tasks: Todo Full-Stack Web Application (Phase II)

**Branch**: `002-todo-fullstack-web`
**Date**: 2026-01-05
**Input**: Design documents from `/specs/002-todo-fullstack-web/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/openapi.yaml, research.md, quickstart.md

**Tests**: Tests are included as part of Phase 11 (QA Readiness) as specified in the implementation plan.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/app/` for source, `backend/tests/` for tests
- **Frontend**: `frontend/src/` for source, `frontend/__tests__/` for tests

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and monorepo structure per @specs/002-todo-fullstack-web/plan.md Phase 1

- [x] T001 Create monorepo directory structure with backend/ and frontend/ directories
- [x] T002 [P] Initialize Python backend project with UV in backend/pyproject.toml
- [x] T003 [P] Initialize Next.js 16+ frontend with App Router in frontend/
- [x] T004 [P] Create backend/.env.example with DATABASE_URL, JWT_SECRET, JWT_EXPIRY_HOURS, CORS_ORIGINS
- [x] T005 [P] Create frontend/.env.example with NEXT_PUBLIC_API_URL
- [x] T006 [P] Configure Tailwind CSS in frontend/tailwind.config.ts
- [x] T007 [P] Configure TypeScript in frontend/tsconfig.json

**Checkpoint**: Monorepo structure ready - both `uv run` and `pnpm dev` execute without errors

---

## Phase 2: Database Schema & Connection

**Purpose**: Database layer implementation per @specs/002-todo-fullstack-web/plan.md Phase 2 and @specs/002-todo-fullstack-web/database/schema.md

- [x] T008 Create environment configuration module in backend/app/config.py
- [x] T009 Create async database connection with Neon PostgreSQL in backend/app/database.py
- [x] T010 [P] Create User SQLModel with email, password_hash, created_at in backend/app/models/user.py
- [x] T011 [P] Create Task SQLModel with title, description, is_complete, user_id, timestamps in backend/app/models/task.py
- [x] T012 Create models __init__.py with exports in backend/app/models/__init__.py
- [x] T013 Add table creation on startup in backend/app/database.py

**Checkpoint**: Database models defined - connection to Neon PostgreSQL succeeds

---

## Phase 3: Backend Core Architecture

**Purpose**: FastAPI application structure per @specs/002-todo-fullstack-web/plan.md Phase 3

- [x] T014 Create FastAPI application instance with metadata in backend/app/main.py
- [x] T015 Configure CORS middleware for frontend origin in backend/app/main.py
- [x] T016 Create custom exception classes in backend/app/exceptions.py
- [x] T017 Add structured exception handlers in backend/app/main.py
- [x] T018 Create health check endpoint at /api/health in backend/app/main.py
- [x] T019 Create routers __init__.py with router registration in backend/app/routers/__init__.py

**Checkpoint**: Backend core ready - `uvicorn app.main:app --reload` starts, /api/health returns 200, /docs available

---

## Phase 4: Authentication Infrastructure

**Purpose**: JWT authentication foundation per @specs/002-todo-fullstack-web/plan.md Phase 4 and @specs/002-todo-fullstack-web/features/authentication.md

- [x] T020 Implement password hashing with bcrypt (cost factor 12) in backend/app/services/auth.py
- [x] T021 Implement JWT token generation with HS256 in backend/app/services/auth.py
- [x] T022 Implement JWT token verification in backend/app/services/auth.py
- [x] T023 Create auth request/response Pydantic schemas in backend/app/schemas/auth.py
- [x] T024 Create get_current_user dependency in backend/app/dependencies/auth.py
- [x] T025 Create dependencies __init__.py in backend/app/dependencies/__init__.py

**Checkpoint**: Auth infrastructure ready - JWT generation and verification functions work

---

## Phase 5: User Story 1 & 2 - Registration and Login (Priority: P1)

**Goal**: Users can register and log in to access the application per @specs/002-todo-fullstack-web/spec.md US1 and US2

**Independent Test**: Navigate to /register, create account, verify redirect to dashboard; Navigate to /login, enter credentials, verify access to tasks

### Backend Implementation (US1 & US2)

- [x] T026 [US1] Implement user registration endpoint POST /api/auth/register in backend/app/routers/auth.py
- [x] T027 [US2] Implement user login endpoint POST /api/auth/login in backend/app/routers/auth.py
- [x] T028 [US1][US2] Implement get current user endpoint GET /api/auth/me in backend/app/routers/auth.py
- [x] T029 Register auth router in backend/app/main.py

### Frontend Scaffolding (US1 & US2)

- [x] T030 [P] Create root layout with global styles in frontend/src/app/layout.tsx
- [x] T031 [P] Create landing page in frontend/src/app/page.tsx
- [x] T032 [P] Create API types definitions in frontend/src/lib/types.ts
- [x] T033 Create API client with fetch and JWT attachment in frontend/src/lib/api.ts
- [x] T034 Create auth utilities for token storage in frontend/src/lib/auth.ts
- [x] T035 Create AuthContext provider in frontend/src/contexts/AuthContext.tsx
- [x] T036 Create useAuth hook in frontend/src/hooks/useAuth.ts

### Frontend UI (US1 & US2)

- [x] T037 [P] [US1][US2] Create Button component with variants in frontend/src/components/ui/Button.tsx
- [x] T038 [P] [US1][US2] Create Input component with error state in frontend/src/components/ui/Input.tsx
- [x] T039 [P] [US1][US2] Create Card component in frontend/src/components/ui/Card.tsx
- [x] T040 [P] [US1][US2] Create Loading component in frontend/src/components/ui/Loading.tsx
- [x] T041 [US1] Create RegisterForm component in frontend/src/components/forms/RegisterForm.tsx
- [x] T042 [US2] Create LoginForm component in frontend/src/components/forms/LoginForm.tsx
- [x] T043 [US1] Create register page in frontend/src/app/register/page.tsx
- [x] T044 [US2] Create login page in frontend/src/app/login/page.tsx

**Checkpoint**: Users can register and login - session persists across page refreshes

---

## Phase 6: User Story 3 - Create Task (Priority: P1)

**Goal**: Logged-in users can create new tasks per @specs/002-todo-fullstack-web/spec.md US3

**Independent Test**: Login, click "Add Task", enter title, verify task appears in list with incomplete status

### Backend Implementation (US3)

- [x] T045 Create task request/response Pydantic schemas in backend/app/schemas/task.py
- [x] T046 [US3] Implement task creation service in backend/app/services/task.py
- [x] T047 [US3] Implement create task endpoint POST /api/tasks in backend/app/routers/tasks.py
- [x] T048 Register tasks router in backend/app/main.py

### Frontend Implementation (US3)

- [x] T049 Create useTasks hook in frontend/src/hooks/useTasks.ts
- [x] T050 [US3] Create TaskForm component in frontend/src/components/forms/TaskForm.tsx
- [x] T051 [P] [US3] Create EmptyState component in frontend/src/components/tasks/EmptyState.tsx

**Checkpoint**: Users can create tasks - new task appears in list immediately

---

## Phase 7: User Story 4 - View Tasks (Priority: P1)

**Goal**: Logged-in users can view all their tasks per @specs/002-todo-fullstack-web/spec.md US4

**Independent Test**: Login with user who has tasks, verify all tasks display with correct status indicators

### Backend Implementation (US4)

- [x] T052 [US4] Implement list tasks service with user filtering in backend/app/services/task.py
- [x] T053 [US4] Implement list tasks endpoint GET /api/tasks with pagination in backend/app/routers/tasks.py
- [x] T054 [US4] Implement get single task endpoint GET /api/tasks/{id} in backend/app/routers/tasks.py

### Frontend Implementation (US4)

- [x] T055 [P] [US4] Create TaskCard component in frontend/src/components/tasks/TaskCard.tsx
- [x] T056 [US4] Create TaskList component in frontend/src/components/tasks/TaskList.tsx
- [x] T057 Create ProtectedRoute wrapper in frontend/src/components/layout/ProtectedRoute.tsx
- [x] T058 [US4] Create dashboard page with task list in frontend/src/app/dashboard/page.tsx

**Checkpoint**: Users see their tasks on dashboard - multi-user isolation verified

---

## Phase 8: User Story 5 - Update Task (Priority: P1)

**Goal**: Logged-in users can update their tasks per @specs/002-todo-fullstack-web/spec.md US5

**Independent Test**: Edit existing task's title, save, verify change persists

### Backend Implementation (US5)

- [x] T059 [US5] Implement update task service with ownership check in backend/app/services/task.py
- [x] T060 [US5] Implement full update endpoint PUT /api/tasks/{id} in backend/app/routers/tasks.py
- [x] T061 [US5] Implement partial update endpoint PATCH /api/tasks/{id} in backend/app/routers/tasks.py

### Frontend Implementation (US5)

- [x] T062 [P] [US5] Create Modal component in frontend/src/components/ui/Modal.tsx
- [x] T063 [US5] Add edit functionality to TaskCard component in frontend/src/components/tasks/TaskCard.tsx
- [x] T064 [US5] Create EditTaskModal component in frontend/src/components/tasks/EditTaskModal.tsx

**Checkpoint**: Users can edit tasks - changes persist on refresh

---

## Phase 9: User Story 6 - Delete Task (Priority: P1)

**Goal**: Logged-in users can delete their tasks per @specs/002-todo-fullstack-web/spec.md US6

**Independent Test**: Delete a task, verify it no longer appears in the task list

### Backend Implementation (US6)

- [x] T065 [US6] Implement delete task service with ownership check in backend/app/services/task.py
- [x] T066 [US6] Implement delete endpoint DELETE /api/tasks/{id} in backend/app/routers/tasks.py

### Frontend Implementation (US6)

- [x] T067 [US6] Add delete functionality with confirmation to TaskCard in frontend/src/components/tasks/TaskCard.tsx
- [x] T068 [US6] Create ConfirmDialog component in frontend/src/components/ui/ConfirmDialog.tsx

**Checkpoint**: Users can delete tasks - deletion persists on refresh

---

## Phase 10: User Story 7 & 8 - Toggle Completion and Logout (Priority: P1/P2)

**Goal**: Users can toggle task completion and securely log out per @specs/002-todo-fullstack-web/spec.md US7 and US8

**Independent Test**: Click checkbox to toggle, verify status changes; Click logout, verify redirect to login

### Backend Implementation (US7 & US8)

- [x] T069 [US7] Implement toggle task service in backend/app/services/task.py
- [x] T070 [US7] Implement toggle endpoint PATCH /api/tasks/{id}/toggle in backend/app/routers/tasks.py
- [x] T071 [US8] Implement logout endpoint POST /api/auth/logout in backend/app/routers/auth.py

### Frontend Implementation (US7 & US8)

- [x] T072 [US7] Add toggle checkbox functionality to TaskCard in frontend/src/components/tasks/TaskCard.tsx
- [x] T073 [P] Create Header component with logout button in frontend/src/components/layout/Header.tsx
- [x] T074 [US8] Implement logout functionality in useAuth hook in frontend/src/hooks/useAuth.ts
- [x] T075 Add Header to dashboard layout in frontend/src/app/dashboard/page.tsx

**Checkpoint**: Toggle and logout work - all core functionality complete

---

## Phase 11: Validation & QA Readiness

**Purpose**: Testing and final validation per @specs/002-todo-fullstack-web/plan.md Phase 10

### Backend Tests

- [x] T076 [P] Create test fixtures and conftest in backend/tests/conftest.py
- [x] T077 [P] Create auth endpoint tests in backend/tests/test_auth.py
- [x] T078 [P] Create task endpoint tests in backend/tests/test_tasks.py
- [x] T079 [P] Create user isolation tests in backend/tests/test_isolation.py

### Frontend Tests

- [x] T080 [P] Create component test setup in frontend/__tests__/setup.ts
- [x] T081 [P] Create auth form tests in frontend/__tests__/components/forms.test.tsx
- [x] T082 [P] Create task components tests in frontend/__tests__/components/tasks.test.tsx

### Integration Validation

- [x] T083 Validate registration → login → dashboard flow
- [x] T084 Validate task CRUD operations end-to-end
- [x] T085 Validate multi-user isolation
- [x] T086 Validate mobile responsiveness (320px viewport)
- [x] T087 Run quickstart.md validation checklist

**Checkpoint**: All tests pass - application ready for QA

---

## Phase 12: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements and documentation

- [x] T088 [P] Add error boundary component in frontend/src/components/ErrorBoundary.tsx
- [x] T089 [P] Create Container layout component in frontend/src/components/layout/Container.tsx
- [x] T090 [P] Create Footer component in frontend/src/components/layout/Footer.tsx
- [x] T091 Add loading states to all API calls
- [x] T092 Add error handling and user-friendly messages
- [x] T093 Ensure WCAG 2.1 AA keyboard navigation
- [x] T094 Final code cleanup and formatting
- [x] T095 Update README with setup instructions

**Final Checkpoint**: Application complete and polished

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup)
    ↓
Phase 2 (Database)
    ↓
Phase 3 (Backend Core)
    ↓
Phase 4 (Auth Infrastructure)
    ↓
Phase 5 (US1 & US2: Registration & Login) ──────────────────┐
    ↓                                                        │
Phase 6 (US3: Create Task)                                   │
    ↓                                                        │
Phase 7 (US4: View Tasks)                                    │ (Can proceed in parallel
    ↓                                                        │  after Phase 4 with
Phase 8 (US5: Update Task)                                   │  experienced team)
    ↓                                                        │
Phase 9 (US6: Delete Task)                                   │
    ↓                                                        │
Phase 10 (US7 & US8: Toggle & Logout) ──────────────────────┘
    ↓
Phase 11 (Validation & QA)
    ↓
Phase 12 (Polish)
```

### User Story Dependencies

| Story | Depends On | Can Start After |
|-------|-----------|-----------------|
| US1 (Registration) | Auth Infrastructure | Phase 4 complete |
| US2 (Login) | Auth Infrastructure | Phase 4 complete |
| US3 (Create Task) | US1, US2 | Phase 5 complete |
| US4 (View Tasks) | US3 | Phase 6 complete |
| US5 (Update Task) | US4 | Phase 7 complete |
| US6 (Delete Task) | US4 | Phase 7 complete |
| US7 (Toggle) | US4 | Phase 7 complete |
| US8 (Logout) | US2 | Phase 5 complete |

### Parallel Opportunities

**Phase 1 Parallel Tasks:**
- T002, T003, T004, T005, T006, T007 (different directories/files)

**Phase 2 Parallel Tasks:**
- T010, T011 (different model files)

**Phase 5 Parallel Tasks:**
- T030, T031, T032 (different files)
- T037, T038, T039, T040 (different component files)

**Phase 7 Parallel Tasks:**
- T055 (TaskCard can be built independently)

**Phase 11 Parallel Tasks:**
- T076, T077, T078, T079 (different test files)
- T080, T081, T082 (different test files)

---

## Parallel Example: Phase 5 UI Components

```bash
# Launch all UI components for Phase 5 together:
Task: "Create Button component in frontend/src/components/ui/Button.tsx"
Task: "Create Input component in frontend/src/components/ui/Input.tsx"
Task: "Create Card component in frontend/src/components/ui/Card.tsx"
Task: "Create Loading component in frontend/src/components/ui/Loading.tsx"
```

---

## Implementation Strategy

### MVP First (User Stories 1-4)

1. Complete Phase 1: Setup
2. Complete Phase 2: Database
3. Complete Phase 3: Backend Core
4. Complete Phase 4: Auth Infrastructure
5. Complete Phase 5: Registration & Login
6. Complete Phase 6: Create Task
7. Complete Phase 7: View Tasks
8. **STOP and VALIDATE**: Test core functionality independently
9. Deploy/demo if ready

### Incremental Delivery

1. Setup + Database + Backend Core + Auth → Foundation ready
2. Add US1 & US2 (Registration/Login) → Test → Demo
3. Add US3 (Create Task) → Test → Demo
4. Add US4 (View Tasks) → Test → Demo (MVP Complete!)
5. Add US5, US6, US7, US8 → Test → Demo
6. Add Testing & Polish → Final Release

---

## Summary

| Category | Count |
|----------|-------|
| **Total Tasks** | 95 |
| **Setup Tasks** | 7 |
| **Database Tasks** | 6 |
| **Backend Core Tasks** | 6 |
| **Auth Infrastructure Tasks** | 6 |
| **US1 & US2 Tasks** | 19 |
| **US3 Tasks** | 6 |
| **US4 Tasks** | 7 |
| **US5 Tasks** | 6 |
| **US6 Tasks** | 4 |
| **US7 & US8 Tasks** | 7 |
| **Validation Tasks** | 12 |
| **Polish Tasks** | 8 |

**MVP Scope**: Phases 1-7 (Tasks T001-T058) = 58 tasks
**Parallel Opportunities**: 32 tasks marked [P]

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- Each phase should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate independently
- All paths are relative to repository root
