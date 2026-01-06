---
id: 001
title: Phase II Full-Stack Web Specification
stage: spec
date: 2026-01-05
surface: agent
model: claude-opus-4-5-20251101
feature: 002-todo-fullstack-web
branch: 002-todo-fullstack-web
user: TOSHIBA
command: /sp.specify
labels: ["specification", "fullstack", "nextjs", "fastapi", "postgresql", "phase-II"]
links:
  spec: specs/002-todo-fullstack-web/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-todo-fullstack-web/spec.md
  - specs/002-todo-fullstack-web/features/task-crud.md
  - specs/002-todo-fullstack-web/features/authentication.md
  - specs/002-todo-fullstack-web/api/rest-endpoints.md
  - specs/002-todo-fullstack-web/database/schema.md
  - specs/002-todo-fullstack-web/ui/components.md
  - specs/002-todo-fullstack-web/ui/pages.md
  - specs/002-todo-fullstack-web/checklists/requirements.md
tests:
  - N/A (specification phase)
---

## Prompt

/sp.specify Phase II — Todo Full-Stack Web Application

Produce a complete specification that covers:

1. **Frontend**: Pages, components, layouts, API integration patterns, User interactions and UI states, Responsive design rules

2. **Backend**: FastAPI endpoints (GET, POST, PUT, DELETE, PATCH), JWT authentication & middleware, User filtering & task ownership enforcement, Error handling & validation

3. **Database**: PostgreSQL schema (users, tasks, indexes), Relationships & constraints, Timestamps and default values

4. **Authentication**: Better Auth configuration, JWT token issuing and verification, Frontend token attachment to API calls

5. **Acceptance Criteria**: Each feature should have testable outcomes, API response formats, Frontend displays & validation, Multi-user isolation

6. **Project Structure**: Monorepo folder layout, /frontend, /backend, /specs, /.spec-kit

Tech stack: Next.js 16+ (App Router), TypeScript, Tailwind CSS, FastAPI, SQLModel, Neon PostgreSQL, Better Auth with JWT

## Response snapshot

Created comprehensive Phase II specification consisting of 7 specification documents:

1. **spec.md** - Main specification with:
   - 8 user stories (registration, login, CRUD tasks, logout)
   - 13 authentication requirements (FR-AUTH-001 to FR-AUTH-010)
   - 13 task management requirements (FR-TASK-001 to FR-TASK-013)
   - 13 UI requirements (FR-UI-001 to FR-UI-013)
   - 10 success criteria
   - 15 non-functional requirements

2. **features/task-crud.md** - Detailed task operations:
   - Create, Read, Update, Delete, Toggle specifications
   - 35+ acceptance criteria
   - Input/output formats
   - Error responses
   - Data isolation requirements

3. **features/authentication.md** - Auth flow specification:
   - Registration, login, logout flows
   - JWT token structure and lifecycle
   - Session management
   - Security requirements
   - Rate limiting

4. **api/rest-endpoints.md** - Complete REST API:
   - 10 endpoints fully specified
   - Request/response formats
   - Error codes and messages
   - CORS configuration

5. **database/schema.md** - PostgreSQL schema:
   - Users table with fields and constraints
   - Tasks table with foreign keys
   - Indexes for performance
   - Query patterns

6. **ui/components.md** - React components:
   - 15+ components specified
   - Props and visual states
   - Accessibility requirements

7. **ui/pages.md** - Page layouts:
   - 4 main pages (Landing, Login, Register, Dashboard)
   - Mobile layouts
   - Navigation flow
   - Authentication guards

## Outcome

- Impact: Complete Phase II specification ready for planning
- Tests: N/A (specification phase)
- Files: 8 specification files created
- Next prompts: /sp.clarify or /sp.plan
- Reflection: Specification covers all required aspects including frontend, backend, database, authentication, and UI. Multi-user isolation requirements well-documented.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Checklist PASS (all items complete)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
