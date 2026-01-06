# Implementation Plan: Todo Full-Stack Web Application (Phase II)

**Branch**: `002-todo-fullstack-web` | **Date**: 2026-01-05 | **Spec**: @specs/002-todo-fullstack-web/spec.md
**Input**: Feature specification from `/specs/002-todo-fullstack-web/spec.md`
**Status**: Ready for Implementation

---

## Summary

Phase II transforms the in-memory Python console Todo application into a full-stack web application with multi-user authentication and persistent storage. The technical approach uses Next.js 16+ with App Router for the frontend, FastAPI with SQLModel for the backend, PostgreSQL on Neon for persistence, and JWT-based authentication via Better Auth patterns.

---

## Technical Context

**Language/Version**: Python 3.13+ (backend), TypeScript 5+ (frontend)
**Primary Dependencies**: FastAPI, SQLModel, Next.js 16+, Tailwind CSS, React Hook Form
**Storage**: PostgreSQL on Neon (serverless)
**Testing**: pytest (backend), Vitest (frontend)
**Target Platform**: Web browsers (Chrome, Firefox, Safari, Edge)
**Project Type**: Web application (frontend + backend monorepo)
**Performance Goals**: <200ms API response time, 60fps UI interactions
**Constraints**: JWT 24-hour expiry, 100 tasks per page default
**Scale/Scope**: Multi-user, unlimited users, unlimited tasks per user

---

## Constitution Check

*GATE: Passed - All principles aligned*

| Principle | Status | Notes |
|-----------|--------|-------|
| Simplicity | PASS | Minimal dependencies, no over-engineering |
| Testability | PASS | All components designed for testing |
| Security | PASS | bcrypt passwords, JWT auth, input validation |
| Documentation | PASS | Comprehensive specs created |

---

## Project Structure

### Documentation (this feature)

```text
specs/002-todo-fullstack-web/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Technology decisions
├── data-model.md        # Entity definitions
├── quickstart.md        # Development setup
├── contracts/
│   └── openapi.yaml     # API contract
├── features/
│   ├── task-crud.md     # Task operations detail
│   └── authentication.md # Auth flow detail
├── api/
│   └── rest-endpoints.md # Endpoint specifications
├── database/
│   └── schema.md        # Database schema
├── ui/
│   ├── components.md    # Component specs
│   └── pages.md         # Page layouts
├── checklists/
│   └── requirements.md  # Validation checklist
└── tasks.md             # Task breakdown (from /sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── __init__.py
│   ├── main.py            # FastAPI application
│   ├── config.py          # Environment configuration
│   ├── database.py        # Async database connection
│   ├── exceptions.py      # Custom exceptions
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py        # User SQLModel
│   │   └── task.py        # Task SQLModel
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py        # Auth request/response schemas
│   │   └── task.py        # Task request/response schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth.py        # Password hashing, JWT utils
│   │   └── task.py        # Task CRUD operations
│   ├── dependencies/
│   │   ├── __init__.py
│   │   └── auth.py        # Authentication dependency
│   └── routers/
│       ├── __init__.py
│       ├── auth.py        # Auth endpoints
│       └── tasks.py       # Task endpoints
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_tasks.py
│   └── test_isolation.py
├── pyproject.toml
└── .env.example

frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx     # Root layout
│   │   ├── page.tsx       # Landing page
│   │   ├── login/
│   │   │   └── page.tsx
│   │   ├── register/
│   │   │   └── page.tsx
│   │   └── dashboard/
│   │       └── page.tsx
│   ├── components/
│   │   ├── ui/
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Modal.tsx
│   │   │   └── Loading.tsx
│   │   ├── forms/
│   │   │   ├── LoginForm.tsx
│   │   │   ├── RegisterForm.tsx
│   │   │   └── TaskForm.tsx
│   │   ├── tasks/
│   │   │   ├── TaskCard.tsx
│   │   │   ├── TaskList.tsx
│   │   │   └── EmptyState.tsx
│   │   └── layout/
│   │       ├── Header.tsx
│   │       ├── Footer.tsx
│   │       ├── Container.tsx
│   │       └── ProtectedRoute.tsx
│   ├── contexts/
│   │   └── AuthContext.tsx
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   └── useTasks.ts
│   └── lib/
│       ├── api.ts
│       ├── auth.ts
│       └── types.ts
├── __tests__/
├── package.json
├── tailwind.config.ts
├── tsconfig.json
└── .env.example
```

**Structure Decision**: Web application structure with separate `backend/` and `frontend/` directories in monorepo. This enables independent development cycles while sharing the same repository.

---

## Phase Overview

| Phase | Name | Dependencies | Deliverables |
|-------|------|--------------|--------------|
| 1 | Monorepo & Spec-Kit Setup | None | Project structure, tooling |
| 2 | Database Schema & Connection | Phase 1 | Neon DB, SQLModel models |
| 3 | Backend Core Architecture | Phase 2 | FastAPI app, config, deps |
| 4 | Authentication Pipeline | Phase 3 | JWT auth, user endpoints |
| 5 | REST API Implementation | Phase 4 | Task CRUD endpoints |
| 6 | Frontend Scaffolding | Phase 1 | Next.js app, routing |
| 7 | API Client & Auth Integration | Phase 4, 6 | Fetch client, auth hooks |
| 8 | UI Components & Pages | Phase 7 | React components, pages |
| 9 | End-to-End Integration | Phase 5, 8 | Full flow testing |
| 10 | Validation & QA Readiness | Phase 9 | Test suite, documentation |

---

## Phase 1: Monorepo & Spec-Kit Setup

### Purpose
Establish the foundational project structure with proper tooling, configuration, and development environment for both frontend and backend workspaces.

### Responsibilities
- Create monorepo directory structure
- Initialize Python backend with UV
- Initialize Next.js frontend with pnpm
- Configure shared development tools
- Set up environment variable templates

### Dependent Specs
- @specs/002-todo-fullstack-web/spec.md (Section: Project Structure)
- @specs/002-todo-fullstack-web/quickstart.md

### Expected Outcomes
1. `backend/` directory with Python project initialized
2. `frontend/` directory with Next.js 16+ App Router
3. `.env.example` files for both workspaces
4. Git configuration for monorepo
5. README with setup instructions

### Completion Criteria
- [ ] `backend/pyproject.toml` exists with dependencies
- [ ] `frontend/package.json` exists with dependencies
- [ ] Both `uv run` and `pnpm dev` execute without errors
- [ ] Environment templates document all required variables
- [ ] Project structure matches quickstart.md specification

---

## Phase 2: Database Schema & Connection

### Purpose
Implement the data layer with PostgreSQL on Neon, defining SQLModel models for User and Task entities with proper relationships, constraints, and indexes.

### Responsibilities
- Configure Neon PostgreSQL connection
- Define User SQLModel with fields and validation
- Define Task SQLModel with foreign key to User
- Implement async database session management
- Create database initialization script

### Dependent Specs
- @specs/002-todo-fullstack-web/database/schema.md
- @specs/002-todo-fullstack-web/data-model.md

### Expected Outcomes
1. Async database connection with connection pooling
2. User model with email uniqueness constraint
3. Task model with user_id foreign key
4. Automatic timestamp management
5. Tables created on first application start

### Completion Criteria
- [ ] Database connection succeeds with Neon
- [ ] User model matches schema specification
- [ ] Task model matches schema specification
- [ ] Indexes created for email and user_id
- [ ] CASCADE delete works (user deletion removes tasks)
- [ ] Timestamps auto-populate on insert/update

---

## Phase 3: Backend Core Architecture

### Purpose
Establish the FastAPI application structure with proper configuration, middleware, error handling, and dependency injection patterns.

### Responsibilities
- Create FastAPI application instance
- Configure CORS middleware
- Set up structured error handling
- Implement health check endpoint
- Organize router structure

### Dependent Specs
- @specs/002-todo-fullstack-web/api/rest-endpoints.md
- @specs/002-todo-fullstack-web/research.md (FastAPI patterns)

### Expected Outcomes
1. FastAPI app with proper metadata
2. CORS configured for frontend origin
3. Structured exception handlers
4. Health check endpoint at `/api/health`
5. Router mounting structure

### Completion Criteria
- [ ] `uvicorn app.main:app --reload` starts successfully
- [ ] `/api/health` returns 200 with status
- [ ] CORS allows requests from localhost:3000
- [ ] Error responses follow ErrorResponse schema
- [ ] OpenAPI docs available at `/docs`

---

## Phase 4: Authentication Pipeline

### Purpose
Implement complete JWT-based authentication including user registration, login, logout, and token verification middleware.

### Responsibilities
- Implement password hashing with bcrypt
- Create JWT token generation and verification
- Build registration endpoint with validation
- Build login endpoint with credential verification
- Create authentication dependency for protected routes
- Implement current user endpoint

### Dependent Specs
- @specs/002-todo-fullstack-web/features/authentication.md
- @specs/002-todo-fullstack-web/api/rest-endpoints.md (Auth section)

### Expected Outcomes
1. Registration creates user with hashed password
2. Login returns JWT token on valid credentials
3. Protected routes require valid JWT
4. Token contains user_id and email
5. Proper error responses for auth failures

### Completion Criteria
- [ ] POST `/api/auth/register` creates user, returns token
- [ ] POST `/api/auth/login` validates credentials, returns token
- [ ] POST `/api/auth/logout` returns success message
- [ ] GET `/api/auth/me` returns current user (authenticated)
- [ ] Invalid token returns 401 Unauthorized
- [ ] Duplicate email returns 400 with message
- [ ] Password hashed with bcrypt cost factor 12

---

## Phase 5: REST API Implementation

### Purpose
Implement complete Task CRUD operations with proper authorization, validation, and user isolation.

### Responsibilities
- Create task listing with pagination
- Implement task creation with validation
- Build task retrieval with ownership check
- Implement full and partial task updates
- Create task deletion with ownership check
- Add toggle completion endpoint

### Dependent Specs
- @specs/002-todo-fullstack-web/features/task-crud.md
- @specs/002-todo-fullstack-web/api/rest-endpoints.md (Tasks section)
- @specs/002-todo-fullstack-web/contracts/openapi.yaml

### Expected Outcomes
1. All task endpoints require authentication
2. Users can only access their own tasks
3. Pagination works with limit/offset
4. Validation enforces title requirements
5. Toggle endpoint inverts is_complete

### Completion Criteria
- [ ] GET `/api/tasks` lists only current user's tasks
- [ ] GET `/api/tasks` supports limit/offset pagination
- [ ] POST `/api/tasks` creates task owned by current user
- [ ] GET `/api/tasks/{id}` returns 404 for other user's task
- [ ] PUT `/api/tasks/{id}` updates title and description
- [ ] PATCH `/api/tasks/{id}` allows partial updates
- [ ] DELETE `/api/tasks/{id}` removes task
- [ ] PATCH `/api/tasks/{id}/toggle` inverts is_complete
- [ ] Title validation enforces 1-200 character limit

---

## Phase 6: Frontend Scaffolding

### Purpose
Establish the Next.js application structure with App Router, layouts, routing, and base styling with Tailwind CSS.

### Responsibilities
- Configure Next.js App Router structure
- Create root layout with global styles
- Set up page routing (/, /login, /register, /dashboard)
- Configure Tailwind CSS theme
- Create base UI component structure

### Dependent Specs
- @specs/002-todo-fullstack-web/ui/pages.md
- @specs/002-todo-fullstack-web/spec.md (UI Requirements)

### Expected Outcomes
1. App Router with proper layouts
2. All 4 main pages routable
3. Tailwind CSS configured and working
4. Responsive breakpoints defined
5. Component directory structure ready

### Completion Criteria
- [ ] `pnpm dev` starts without errors
- [ ] Landing page renders at `/`
- [ ] Login page renders at `/login`
- [ ] Register page renders at `/register`
- [ ] Dashboard page renders at `/dashboard`
- [ ] Tailwind classes apply correctly
- [ ] Mobile-responsive viewport meta tag present

---

## Phase 7: API Client & Auth Integration

### Purpose
Build the frontend API communication layer with fetch client, authentication state management, and protected route handling.

### Responsibilities
- Create typed API client with fetch
- Implement JWT token storage (localStorage)
- Build useAuth hook for auth state
- Create AuthProvider context
- Implement protected route wrapper
- Handle API errors consistently

### Dependent Specs
- @specs/002-todo-fullstack-web/features/authentication.md (Frontend section)
- @specs/002-todo-fullstack-web/research.md (State Management)

### Expected Outcomes
1. API client with typed request/response
2. Token attached to all authenticated requests
3. Auth state persisted across page reloads
4. Automatic redirect on 401 responses
5. Login/logout functions available globally

### Completion Criteria
- [ ] API client sends Authorization header when token exists
- [ ] useAuth hook provides user, login, logout, isLoading
- [ ] AuthProvider wraps application
- [ ] Protected routes redirect to /login when unauthenticated
- [ ] Token persisted in localStorage
- [ ] API errors parsed and surfaced properly

---

## Phase 8: UI Components & Pages

### Purpose
Implement all React components and complete page layouts according to the UI specification, with proper form handling and validation.

### Responsibilities
- Build reusable UI components (Button, Input, Card)
- Create form components (LoginForm, RegisterForm, TaskForm)
- Implement TaskCard and TaskList components
- Complete all 4 page layouts
- Add loading states and error displays
- Implement responsive design

### Dependent Specs
- @specs/002-todo-fullstack-web/ui/components.md
- @specs/002-todo-fullstack-web/ui/pages.md

### Expected Outcomes
1. All 15+ specified components implemented
2. Forms with validation feedback
3. Responsive layouts for mobile/desktop
4. Consistent styling with Tailwind
5. Accessibility requirements met

### Completion Criteria
- [ ] Button component with variants (primary, secondary, danger)
- [ ] Input component with error state display
- [ ] Card component with proper styling
- [ ] LoginForm with email/password validation
- [ ] RegisterForm with password requirements shown
- [ ] TaskCard displays title, description, completion status
- [ ] TaskList renders array of TaskCards
- [ ] TaskForm for creating/editing tasks
- [ ] Landing page with hero and CTA buttons
- [ ] Dashboard shows task list with add/edit/delete actions
- [ ] Mobile navigation works
- [ ] All interactive elements have focus states

---

## Phase 9: End-to-End Integration

### Purpose
Connect all frontend and backend components, verify complete user flows work correctly, and resolve any integration issues.

### Responsibilities
- Connect registration flow end-to-end
- Connect login flow end-to-end
- Implement task CRUD in dashboard
- Add optimistic updates for better UX
- Handle all error scenarios
- Test multi-user isolation

### Dependent Specs
- @specs/002-todo-fullstack-web/spec.md (User Stories)
- @specs/002-todo-fullstack-web/features/task-crud.md
- @specs/002-todo-fullstack-web/features/authentication.md

### Expected Outcomes
1. User can register and see dashboard
2. User can login and see their tasks
3. Task CRUD works with live API
4. Errors display user-friendly messages
5. Two users see isolated task lists

### Completion Criteria
- [ ] Registration → automatic login → dashboard redirect works
- [ ] Login → dashboard with user's tasks works
- [ ] Create task → appears in list immediately
- [ ] Toggle task → visual update reflects change
- [ ] Edit task → updated content shows
- [ ] Delete task → removed from list
- [ ] Logout → redirected to landing page
- [ ] Invalid credentials show error message
- [ ] Network errors show generic message
- [ ] User A cannot see User B's tasks

---

## Phase 10: Validation & QA Readiness

### Purpose
Ensure application quality through comprehensive testing, documentation updates, and preparation for quality assurance review.

### Responsibilities
- Write backend unit tests
- Write backend integration tests
- Write frontend component tests
- Create E2E test suite
- Update documentation
- Perform final validation against spec

### Dependent Specs
- @specs/002-todo-fullstack-web/spec.md (Success Criteria)
- @specs/002-todo-fullstack-web/checklists/requirements.md

### Expected Outcomes
1. Backend tests achieve 80%+ coverage
2. Frontend components tested
3. Critical flows covered by E2E tests
4. All success criteria validated
5. Documentation current and accurate

### Completion Criteria
- [ ] Backend pytest suite passes
- [ ] Backend coverage >= 80%
- [ ] Auth endpoints have integration tests
- [ ] Task endpoints have integration tests
- [ ] User isolation tested programmatically
- [ ] Frontend component tests pass
- [ ] E2E tests cover registration flow
- [ ] E2E tests cover login flow
- [ ] E2E tests cover task CRUD
- [ ] All 10 success criteria from spec verified

### Success Criteria Checklist

| # | Criterion | Verified |
|---|-----------|----------|
| 1 | Registration creates account and shows dashboard | [ ] |
| 2 | Login with valid credentials shows user's tasks | [ ] |
| 3 | Invalid login shows error without exposing which field wrong | [ ] |
| 4 | Create task with title appears in list | [ ] |
| 5 | Toggle task changes visual state immediately | [ ] |
| 6 | Edit task updates title/description | [ ] |
| 7 | Delete task removes from list | [ ] |
| 8 | Logout clears session and redirects | [ ] |
| 9 | Unauthenticated API access returns 401 | [ ] |
| 10 | User cannot access other user's tasks | [ ] |

---

## Dependency Graph

```
Phase 1 ─────────────────────────────────────┐
    │                                         │
    ▼                                         ▼
Phase 2                                   Phase 6
    │                                         │
    ▼                                         │
Phase 3                                       │
    │                                         │
    ▼                                         │
Phase 4 ──────────────────────────────────────┤
    │                                         │
    ▼                                         ▼
Phase 5                                   Phase 7
    │                                         │
    └─────────────────┬───────────────────────┘
                      │
                      ▼
                  Phase 8
                      │
                      ▼
                  Phase 9
                      │
                      ▼
                  Phase 10
```

---

## Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Neon connection issues | Low | High | Connection pooling, retry logic |
| JWT security vulnerability | Low | Critical | Use established libraries |
| CORS misconfiguration | Medium | Medium | Test cross-origin in Phase 3 |
| TypeScript type mismatches | Medium | Low | Generate types from OpenAPI |

---

## Complexity Tracking

> No constitution violations identified. Standard web application complexity.

---

## Related Documents

- @specs/002-todo-fullstack-web/spec.md - Feature specification
- @specs/002-todo-fullstack-web/research.md - Technology decisions
- @specs/002-todo-fullstack-web/data-model.md - Entity definitions
- @specs/002-todo-fullstack-web/contracts/openapi.yaml - API contract
- @specs/002-todo-fullstack-web/quickstart.md - Development setup

---

## Next Steps

1. Run `/sp.tasks` to decompose phases into actionable tasks
2. Begin Phase 1 implementation
3. Track progress in tasks.md

---

**Plan Status**: COMPLETE - Ready for task generation
