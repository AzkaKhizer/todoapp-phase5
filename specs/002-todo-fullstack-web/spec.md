# Feature Specification: Todo Full-Stack Web Application (Phase II)

**Feature Branch**: `002-todo-fullstack-web`
**Created**: 2026-01-05
**Status**: Draft
**Input**: Phase II — Evolution of Phase I Todo Console App to Full-Stack Web Application

---

## Overview

This specification defines a full-stack web-based Todo application that extends Phase I functionality with persistent storage, multi-user authentication, and a responsive web interface. The system consists of a Next.js frontend, FastAPI backend, and PostgreSQL database with JWT-based authentication.

**Project Context**: Phase II of the Hackathon project. Builds upon Phase I's in-memory task management by adding persistence, authentication, and web accessibility.

### Scope

**In Scope**:
- User registration and login with JWT authentication
- Persistent task storage in PostgreSQL database
- Multi-user task isolation (users only see their own tasks)
- RESTful API for all task operations
- Responsive web interface (mobile and desktop)
- Task CRUD operations: Create, Read, Update, Delete
- Task completion toggle functionality
- Real-time form validation
- Session management and secure logout

**Out of Scope**:
- Social login (OAuth providers)
- Email verification or password reset
- Task sharing between users
- Task categories, priorities, or due dates
- Real-time collaboration or WebSocket updates
- Task search or filtering
- Offline mode or progressive web app features
- Admin dashboard or user management
- File attachments to tasks
- Task reminders or notifications

---

## Tech Stack

| Layer | Technology | Version | Purpose |
|-------|------------|---------|---------|
| Frontend Framework | Next.js | 16+ | App Router, Server Components |
| Frontend Language | TypeScript | 5+ | Type safety |
| Styling | Tailwind CSS | 3+ | Utility-first CSS |
| Backend Framework | FastAPI | 0.100+ | REST API |
| Backend Language | Python | 3.13+ | Server logic |
| ORM | SQLModel | 0.0.14+ | Database models |
| Database | PostgreSQL (Neon) | 15+ | Persistent storage |
| Authentication | Better Auth | Latest | JWT token management |

---

## Project Structure

```
todo-fullstack/
├── frontend/                    # Next.js application
│   ├── app/                     # App Router pages
│   │   ├── (auth)/              # Auth group (login, register)
│   │   ├── (dashboard)/         # Protected routes
│   │   ├── layout.tsx           # Root layout
│   │   └── page.tsx             # Landing page
│   ├── components/              # React components
│   │   ├── ui/                  # Reusable UI components
│   │   ├── forms/               # Form components
│   │   └── tasks/               # Task-specific components
│   ├── lib/                     # Utilities and helpers
│   │   ├── api.ts               # API client
│   │   └── auth.ts              # Auth utilities
│   ├── types/                   # TypeScript types
│   └── package.json
├── backend/                     # FastAPI application
│   ├── app/
│   │   ├── api/                 # API routes
│   │   │   ├── auth.py          # Auth endpoints
│   │   │   └── tasks.py         # Task endpoints
│   │   ├── core/                # Core configuration
│   │   │   ├── config.py        # Settings
│   │   │   ├── security.py      # JWT utilities
│   │   │   └── database.py      # Database connection
│   │   ├── models/              # SQLModel models
│   │   │   ├── user.py          # User model
│   │   │   └── task.py          # Task model
│   │   ├── schemas/             # Pydantic schemas
│   │   └── main.py              # FastAPI app
│   ├── tests/                   # Backend tests
│   └── pyproject.toml
├── specs/                       # Specifications
│   └── 002-todo-fullstack-web/
├── .specify/                    # Spec-Kit Plus
└── CLAUDE.md                    # AI assistant guidelines
```

---

## Cross-Reference Documents

| Document | Path | Purpose |
|----------|------|---------|
| Task CRUD | @specs/002-todo-fullstack-web/features/task-crud.md | Task management user stories |
| Authentication | @specs/002-todo-fullstack-web/features/authentication.md | Auth user stories |
| REST Endpoints | @specs/002-todo-fullstack-web/api/rest-endpoints.md | API contracts |
| Database Schema | @specs/002-todo-fullstack-web/database/schema.md | Data models |
| UI Components | @specs/002-todo-fullstack-web/ui/components.md | Component specifications |
| UI Pages | @specs/002-todo-fullstack-web/ui/pages.md | Page layouts and flows |

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - User Registration (Priority: P1)

As a visitor, I want to create an account so that I can save and access my tasks from any device.

**Why this priority**: Without registration, users cannot have persistent task lists or multi-user isolation. This is the entry point for all authenticated functionality.

**Independent Test**: Can be fully tested by navigating to the registration page, entering valid credentials, and verifying successful account creation with redirect to dashboard.

**Acceptance Scenarios**:

1. **Given** I am on the registration page, **When** I enter a valid email "user@example.com" and password "SecurePass123!", **Then** my account is created and I am redirected to the dashboard.

2. **Given** I am on the registration page, **When** I enter an email that already exists, **Then** I see an error message "Email already registered" and remain on the registration page.

3. **Given** I am on the registration page, **When** I enter a password shorter than 8 characters, **Then** I see a validation error "Password must be at least 8 characters".

4. **Given** I am on the registration page, **When** I enter an invalid email format, **Then** I see a validation error "Please enter a valid email address".

---

### User Story 2 - User Login (Priority: P1)

As a registered user, I want to log in so that I can access my saved tasks.

**Why this priority**: Login is required for all authenticated features. Users cannot access their tasks without authentication.

**Independent Test**: Can be tested by navigating to login page, entering valid credentials, and verifying redirect to dashboard with task list visible.

**Acceptance Scenarios**:

1. **Given** I am a registered user on the login page, **When** I enter correct email and password, **Then** I am redirected to my dashboard and see my tasks.

2. **Given** I am on the login page, **When** I enter incorrect credentials, **Then** I see an error message "Invalid email or password" and remain on the login page.

3. **Given** I am logged in, **When** I close and reopen the browser, **Then** I remain logged in (session persists).

4. **Given** I am logged in, **When** my session expires (24 hours), **Then** I am redirected to login page on next action.

---

### User Story 3 - Create Task (Priority: P1)

As a logged-in user, I want to create new tasks so that I can track work I need to complete.

**Why this priority**: Task creation is the core functionality. Without it, the application has no purpose.

**Independent Test**: Can be tested by logging in, clicking "Add Task", entering a title, and verifying the task appears in the list with incomplete status.

**Acceptance Scenarios**:

1. **Given** I am on my dashboard, **When** I enter a title "Buy groceries" and click "Add Task", **Then** a new task appears in my list with status "incomplete".

2. **Given** I am creating a task, **When** I add a description "Get milk and bread", **Then** the task is saved with both title and description.

3. **Given** I am creating a task, **When** I leave the title empty and click "Add Task", **Then** I see a validation error "Title is required".

4. **Given** I have created multiple tasks, **When** I view my dashboard, **Then** all my tasks are displayed in the order they were created.

---

### User Story 4 - View Tasks (Priority: P1)

As a logged-in user, I want to view all my tasks so that I can see what needs to be done.

**Why this priority**: Viewing tasks is essential for users to understand their workload and track progress.

**Independent Test**: Can be tested by logging in with a user who has tasks and verifying all tasks display with correct status indicators.

**Acceptance Scenarios**:

1. **Given** I am logged in with 5 tasks, **When** I view my dashboard, **Then** I see all 5 tasks with their titles, descriptions, and completion status.

2. **Given** I am logged in with no tasks, **When** I view my dashboard, **Then** I see a message "No tasks yet. Create your first task!"

3. **Given** I have tasks marked complete and incomplete, **When** I view my dashboard, **Then** complete tasks show a checkmark indicator and incomplete tasks show an empty checkbox.

4. **Given** another user has tasks, **When** I log in with my account, **Then** I see only my tasks (not the other user's).

---

### User Story 5 - Update Task (Priority: P1)

As a logged-in user, I want to update my tasks so that I can correct mistakes or add details.

**Why this priority**: Users need to modify tasks after creation to maintain accurate information.

**Independent Test**: Can be tested by editing an existing task's title, saving, and verifying the change persists.

**Acceptance Scenarios**:

1. **Given** I have a task with title "Buy grocries", **When** I click edit, change to "Buy groceries", and save, **Then** the task shows the updated title.

2. **Given** I am editing a task, **When** I update the description and save, **Then** the new description is displayed.

3. **Given** I am editing a task, **When** I clear the title and try to save, **Then** I see a validation error "Title is required".

4. **Given** I am editing a task, **When** I click cancel, **Then** my changes are discarded and the original values remain.

---

### User Story 6 - Delete Task (Priority: P1)

As a logged-in user, I want to delete tasks so that I can remove items I no longer need.

**Why this priority**: Users need to clean up their task lists by removing completed or irrelevant items.

**Independent Test**: Can be tested by deleting a task and verifying it no longer appears in the task list.

**Acceptance Scenarios**:

1. **Given** I have a task in my list, **When** I click delete and confirm, **Then** the task is removed from my list.

2. **Given** I click delete on a task, **When** the confirmation dialog appears, **Then** I can cancel to keep the task.

3. **Given** I delete a task, **When** I refresh the page, **Then** the deleted task remains gone (deletion is persisted).

---

### User Story 7 - Toggle Task Completion (Priority: P1)

As a logged-in user, I want to mark tasks as complete or incomplete so that I can track my progress.

**Why this priority**: Completion tracking is core to todo functionality.

**Independent Test**: Can be tested by clicking a task's checkbox and verifying the status toggles visually and persists on refresh.

**Acceptance Scenarios**:

1. **Given** I have an incomplete task, **When** I click the completion checkbox, **Then** the task is marked as complete with visual feedback.

2. **Given** I have a complete task, **When** I click the completion checkbox, **Then** the task is marked as incomplete.

3. **Given** I toggle a task's completion, **When** I refresh the page, **Then** the completion status persists.

---

### User Story 8 - User Logout (Priority: P2)

As a logged-in user, I want to log out so that I can secure my account on shared devices.

**Why this priority**: Security feature that's important but not blocking core functionality.

**Independent Test**: Can be tested by clicking logout and verifying redirect to login page with session cleared.

**Acceptance Scenarios**:

1. **Given** I am logged in, **When** I click "Logout", **Then** I am redirected to the login page.

2. **Given** I have logged out, **When** I try to access the dashboard directly, **Then** I am redirected to the login page.

3. **Given** I have logged out, **When** I use the browser back button, **Then** I cannot see my tasks (session is cleared).

---

### Edge Cases

- **Empty title on task creation**: System rejects and shows validation error
- **Very long title (>200 characters)**: System truncates or rejects with error
- **Very long description (>2000 characters)**: System truncates or rejects with error
- **Concurrent edits from multiple tabs**: Last write wins (optimistic update)
- **Network failure during save**: Error message displayed, retry option available
- **Invalid JWT token**: User redirected to login with "Session expired" message
- **Cross-user access attempt**: API returns 403 Forbidden
- **SQL injection in inputs**: SQLModel parameterized queries prevent injection
- **XSS in task content**: React escapes output by default
- **Rapid successive API calls**: Standard rate limiting (100 requests/minute)

---

## Requirements *(mandatory)*

### Functional Requirements

**Authentication**
- **FR-AUTH-001**: System MUST allow visitors to register with email and password
- **FR-AUTH-002**: System MUST validate email format (contains @ and domain)
- **FR-AUTH-003**: System MUST validate password strength (minimum 8 characters)
- **FR-AUTH-004**: System MUST hash passwords before storage (bcrypt or argon2)
- **FR-AUTH-005**: System MUST issue JWT token on successful login
- **FR-AUTH-006**: System MUST reject invalid credentials with generic error message
- **FR-AUTH-007**: System MUST invalidate session on logout (client-side token removal)
- **FR-AUTH-008**: System MUST protect all /api/tasks endpoints with authentication
- **FR-AUTH-009**: JWT tokens MUST expire after 24 hours
- **FR-AUTH-010**: System MUST return 401 Unauthorized for missing/invalid tokens

**Task Management**
- **FR-TASK-001**: System MUST allow authenticated users to create tasks with title (required) and description (optional)
- **FR-TASK-002**: System MUST auto-generate UUID for each task
- **FR-TASK-003**: System MUST associate each task with creator's user_id
- **FR-TASK-004**: System MUST set new tasks to is_complete=false by default
- **FR-TASK-005**: System MUST allow users to retrieve only their own tasks
- **FR-TASK-006**: System MUST allow users to update title/description of their own tasks
- **FR-TASK-007**: System MUST allow users to delete their own tasks
- **FR-TASK-008**: System MUST allow users to toggle is_complete of their own tasks
- **FR-TASK-009**: System MUST persist all task data to PostgreSQL database
- **FR-TASK-010**: System MUST return 404 for operations on non-existent tasks
- **FR-TASK-011**: System MUST return 403 for operations on tasks owned by other users
- **FR-TASK-012**: System MUST record created_at timestamp for each task
- **FR-TASK-013**: System MUST record updated_at timestamp on each modification

**User Interface**
- **FR-UI-001**: Frontend MUST display login form on /login route
- **FR-UI-002**: Frontend MUST display registration form on /register route
- **FR-UI-003**: Frontend MUST redirect authenticated users from auth pages to dashboard
- **FR-UI-004**: Frontend MUST redirect unauthenticated users from dashboard to login
- **FR-UI-005**: Frontend MUST display task list with completion checkboxes
- **FR-UI-006**: Frontend MUST provide task creation form
- **FR-UI-007**: Frontend MUST provide task edit functionality
- **FR-UI-008**: Frontend MUST provide task delete with confirmation
- **FR-UI-009**: Frontend MUST be responsive (mobile: 320px+, tablet: 768px+, desktop: 1024px+)
- **FR-UI-010**: Frontend MUST display loading indicators during API calls
- **FR-UI-011**: Frontend MUST display error messages for failed operations
- **FR-UI-012**: Frontend MUST attach JWT token to all authenticated API requests
- **FR-UI-013**: Frontend MUST store JWT token in localStorage or httpOnly cookie

### Key Entities

- **User**: Represents a registered user
  - Unique identifier (UUID)
  - Email address (unique, required)
  - Password hash (required)
  - Created timestamp
  - Relationship: One user has many tasks

- **Task**: Represents a todo item
  - Unique identifier (UUID)
  - Title (required, max 200 characters)
  - Description (optional, max 2000 characters)
  - Completion status (boolean, default false)
  - Owner reference (user_id, required)
  - Created timestamp
  - Updated timestamp
  - Relationship: Belongs to one user

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can complete registration in under 30 seconds (from page load to dashboard)
- **SC-002**: Users can log in within 10 seconds (from page load to dashboard)
- **SC-003**: Users can create a task in under 5 seconds (from form fill to task visible)
- **SC-004**: Task list loads within 2 seconds with up to 100 tasks
- **SC-005**: Users see only their own tasks (0% cross-user data leakage)
- **SC-006**: All CRUD operations succeed with 99.9% reliability
- **SC-007**: All forms show validation errors within 500ms of submission
- **SC-008**: Toggle completion provides visual feedback within 200ms
- **SC-009**: Mobile users can complete all operations (tested on 320px viewport)
- **SC-010**: Session persists across page refreshes for 24 hours

---

## Non-Functional Requirements

- **NFR-001**: Frontend MUST use Next.js 16+ with App Router
- **NFR-002**: Frontend MUST use TypeScript for all source files
- **NFR-003**: Frontend MUST use Tailwind CSS for styling
- **NFR-004**: Backend MUST use FastAPI with Python 3.13+
- **NFR-005**: Backend MUST use SQLModel for database operations
- **NFR-006**: Database MUST be PostgreSQL 15+ hosted on Neon
- **NFR-007**: Authentication MUST use Better Auth library with JWT
- **NFR-008**: API responses MUST be JSON with appropriate Content-Type
- **NFR-009**: API MUST follow REST conventions (proper HTTP methods and status codes)
- **NFR-010**: Passwords MUST be hashed with bcrypt (cost factor 12+)
- **NFR-011**: JWT tokens MUST expire after 24 hours
- **NFR-012**: System MUST handle 100 concurrent users
- **NFR-013**: API response time MUST be under 500ms for p95
- **NFR-014**: Frontend MUST be accessible (WCAG 2.1 AA keyboard navigation)
- **NFR-015**: All API endpoints MUST use HTTPS in production

---

## Assumptions

- Users have modern web browsers (Chrome, Firefox, Safari, Edge - latest 2 versions)
- Neon PostgreSQL database is pre-provisioned with connection string available
- Network latency is acceptable for standard web operations (<100ms)
- Email addresses are unique identifiers for users
- UTC timezone for all timestamps (frontend can display local time)
- English-only interface for Phase II
- Users accept standard cookie/localStorage usage for authentication

---

## Constraints

- No file uploads or media attachments
- No real-time collaboration features
- No offline functionality
- No email-based password recovery in Phase II
- No social authentication providers
- Maximum 1000 tasks per user
- Maximum title length: 200 characters
- Maximum description length: 2000 characters
- No bulk operations (import/export)
- No undo for delete operations

---

## Dependencies

### External Services
- Neon PostgreSQL (database hosting)
- Better Auth library (authentication)

### Development Dependencies
- Node.js 20+ (frontend runtime)
- Python 3.13+ (backend runtime)
- UV (Python package management)
- pnpm (Node package management, preferred)

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Database connection issues | Medium | High | Connection pooling, retry logic, health checks |
| JWT token theft | Low | High | HTTPS only, short expiry, secure storage |
| Cross-user data exposure | Low | Critical | Strict user_id filtering on all queries |
| Password brute force | Medium | Medium | Rate limiting on auth endpoints |
| SQL injection | Low | Critical | SQLModel parameterized queries |
| XSS attacks | Low | High | React auto-escaping, CSP headers |

---

## Acceptance Criteria Summary

The Phase II system is considered complete when:

1. A new visitor can register an account with email/password
2. A registered user can log in and access their personalized dashboard
3. Authenticated users can create, view, update, and delete their tasks
4. Authenticated users can toggle task completion status
5. Users cannot see or modify other users' tasks (isolation verified)
6. All data persists across sessions and browser restarts
7. Invalid operations return appropriate error messages
8. All API endpoints are protected with JWT authentication
9. Frontend handles loading and error states gracefully
10. Application works correctly on mobile (320px) and desktop (1024px+) viewports
