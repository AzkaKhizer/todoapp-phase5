# Research: Todo Full-Stack Web Application (Phase II)

**Feature Branch**: `002-todo-fullstack-web`
**Created**: 2026-01-05
**Spec**: @specs/002-todo-fullstack-web/spec.md

---

## Purpose

Document technology decisions, patterns, and best practices for implementing Phase II of the Todo application. All clarifications resolved here inform the implementation plan.

---

## Technology Decisions

### 1. Frontend Framework: Next.js 16+ with App Router

**Decision**: Use Next.js 16 with App Router and React Server Components

**Rationale**:
- App Router provides better routing patterns and layouts
- Server Components reduce client-side JavaScript bundle
- TypeScript integration is first-class
- Built-in API route support (though we use external FastAPI)
- Strong Tailwind CSS integration

**Alternatives Considered**:
- Vite + React: Simpler but lacks SSR/SSG capabilities
- Remix: Good alternative but less ecosystem support
- SvelteKit: Different paradigm, team familiarity with React

**Pattern**: Client-side state management with React hooks, server-side data fetching where possible

---

### 2. Backend Framework: FastAPI

**Decision**: Use FastAPI 0.100+ with async endpoints

**Rationale**:
- High performance async Python framework
- Automatic OpenAPI documentation
- Pydantic integration for validation
- Native async/await support for database operations
- Strong typing with Python 3.13+

**Alternatives Considered**:
- Django REST Framework: Heavier, more opinionated
- Flask: Less structured, manual validation
- Starlette: Lower-level than needed

**Pattern**: Router-based organization with dependency injection for auth

---

### 3. ORM: SQLModel

**Decision**: Use SQLModel 0.0.14+ for database models

**Rationale**:
- Combines Pydantic and SQLAlchemy
- Single model definition for API and database
- Native async support with asyncpg
- Type hints throughout

**Alternatives Considered**:
- SQLAlchemy 2.0 alone: More complex, separate schemas needed
- Tortoise ORM: Less mature, different API
- Prisma: Better for Node.js, Python support limited

**Pattern**: Models define both database schema and API schemas

---

### 4. Database: PostgreSQL on Neon

**Decision**: Use PostgreSQL 15+ on Neon serverless

**Rationale**:
- Neon provides serverless PostgreSQL with branching
- Connection pooling built-in
- Free tier sufficient for hackathon
- Full PostgreSQL compatibility

**Alternatives Considered**:
- Supabase: More features than needed
- PlanetScale (MySQL): PostgreSQL preferred for SQLModel
- Self-hosted: Operational overhead

**Pattern**: Connection pooling with environment-based configuration

---

### 5. Authentication: Better Auth with JWT

**Decision**: Use Better Auth library for JWT-based authentication

**Rationale**:
- Lightweight JWT implementation
- Works with any backend framework
- Simple token issuance and verification
- No external service dependencies

**Alternatives Considered**:
- Auth0: External dependency, complexity
- NextAuth: Tied to Next.js, separate from FastAPI
- Firebase Auth: Google dependency

**Pattern**:
- Backend issues JWT on login/register
- Frontend stores token in localStorage
- All authenticated requests include Authorization header
- Token expiry: 24 hours

---

### 6. Password Hashing: bcrypt

**Decision**: Use bcrypt with cost factor 12

**Rationale**:
- Industry standard for password hashing
- Automatic salt generation
- Configurable work factor
- Widely audited

**Alternatives Considered**:
- Argon2: Newer but less library support
- scrypt: Good but bcrypt is more common
- PBKDF2: Older, bcrypt preferred

**Pattern**: Hash on registration, verify on login, never store plaintext

---

### 7. API Communication: REST with JSON

**Decision**: RESTful API with JSON request/response bodies

**Rationale**:
- Simple and well-understood
- Good browser support (fetch API)
- Easy to test and debug
- Matches spec requirements

**Alternatives Considered**:
- GraphQL: Overkill for simple CRUD
- gRPC: Not browser-friendly without proxy
- tRPC: Ties frontend and backend too closely

**Pattern**: Standard REST verbs (GET, POST, PUT, PATCH, DELETE) with proper status codes

---

### 8. Frontend State Management

**Decision**: React hooks (useState, useEffect) with custom hooks for API

**Rationale**:
- Simple state needs (auth token, task list)
- No complex state relationships
- Avoids external library overhead

**Alternatives Considered**:
- Redux: Overkill for this scope
- Zustand: Nice but unnecessary
- Jotai/Recoil: Atomic state not needed

**Pattern**: Custom useAuth and useTasks hooks encapsulating API calls

---

### 9. Form Handling

**Decision**: React Hook Form with client-side validation

**Rationale**:
- Performant form handling
- Built-in validation
- Good TypeScript support
- Minimal re-renders

**Alternatives Considered**:
- Formik: More verbose
- Native forms: Less structured validation
- Final Form: Similar but less popular

**Pattern**: Controlled forms with immediate validation feedback

---

### 10. Styling: Tailwind CSS

**Decision**: Tailwind CSS 3+ with utility classes

**Rationale**:
- Rapid prototyping
- Consistent design system
- No CSS file management
- Responsive utilities built-in

**Alternatives Considered**:
- CSS Modules: More setup, less rapid
- Styled Components: Runtime overhead
- Chakra UI: Component library overhead

**Pattern**: Utility-first with custom components abstracting common patterns

---

## Integration Patterns

### Frontend-Backend Communication

```
Frontend (Next.js)
    │
    │ HTTP/JSON with JWT in Authorization header
    ▼
Backend (FastAPI)
    │
    │ SQLModel ORM
    ▼
Database (PostgreSQL/Neon)
```

### Authentication Flow

1. **Registration**:
   - Frontend: POST email/password to /api/auth/register
   - Backend: Hash password, create user, issue JWT
   - Frontend: Store JWT, redirect to dashboard

2. **Login**:
   - Frontend: POST email/password to /api/auth/login
   - Backend: Verify password, issue JWT
   - Frontend: Store JWT, redirect to dashboard

3. **Authenticated Request**:
   - Frontend: Include `Authorization: Bearer <token>` header
   - Backend: Verify JWT, extract user_id, proceed with request

4. **Logout**:
   - Frontend: Remove JWT from localStorage
   - Redirect to login page

### Error Handling Pattern

- All API errors return JSON with `error` code and `message`
- HTTP status codes: 400 (validation), 401 (auth), 403 (forbidden), 404 (not found)
- Frontend displays user-friendly error messages
- Network errors show generic "Connection error" message

---

## Security Considerations

### JWT Security

- Sign with HS256 algorithm
- Store secret in environment variable (minimum 256-bit)
- Token expiry: 24 hours
- No sensitive data in token payload (only user_id, email)

### Data Isolation

- All task queries filtered by authenticated user_id
- Ownership check before update/delete operations
- No task IDs leak cross-user information (UUIDs)

### Input Validation

- Backend validates all inputs with Pydantic
- Frontend validates for UX (backend is source of truth)
- SQL injection prevented by parameterized queries (SQLModel)
- XSS prevented by React's default escaping

---

## Performance Considerations

### Database

- Index on users.email for login
- Index on tasks.user_id for filtering
- Connection pooling via Neon
- Pagination for task lists (default 100)

### Frontend

- Static assets cached
- API responses not cached (real-time data)
- Optimistic updates for better perceived performance

### Backend

- Async endpoints for non-blocking I/O
- Database connection pooling
- No N+1 queries (single query for task list)

---

## Development Environment

### Backend

```
Python 3.13+
UV for package management
FastAPI + Uvicorn for development server
pytest for testing
```

### Frontend

```
Node.js 20+
pnpm for package management
Next.js dev server (port 3000)
Vitest or Jest for testing
```

### Database

```
Neon PostgreSQL (cloud)
Connection string in .env
No local database needed
```

---

## Environment Variables

### Backend (.env)

```
DATABASE_URL=postgresql://...@neon.tech/...
JWT_SECRET=<256-bit-random-string>
JWT_EXPIRY_HOURS=24
CORS_ORIGINS=http://localhost:3000
```

### Frontend (.env.local)

```
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

---

## Testing Strategy

### Backend Tests

- Unit tests for models and services
- Integration tests for API endpoints
- Auth tests for protected routes
- User isolation tests

### Frontend Tests

- Component tests for UI components
- Integration tests for forms and API calls
- E2E tests for critical flows (login, task CRUD)

---

## Related Documents

- @specs/002-todo-fullstack-web/spec.md - Feature specification
- @specs/002-todo-fullstack-web/api/rest-endpoints.md - API details
- @specs/002-todo-fullstack-web/database/schema.md - Database schema
