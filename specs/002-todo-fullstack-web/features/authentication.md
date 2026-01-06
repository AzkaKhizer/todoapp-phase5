# Feature Specification: Authentication

**Parent Spec**: @specs/002-todo-fullstack-web/spec.md
**Feature Branch**: `002-todo-fullstack-web`
**Created**: 2026-01-05

---

## Overview

This document specifies the authentication system for the Todo Full-Stack Web Application, including user registration, login, logout, and session management using JWT tokens with Better Auth.

---

## Authentication Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Browser   │     │   Backend   │     │  Database   │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       │ POST /auth/register                   │
       │ (email, password) │                   │
       │──────────────────►│                   │
       │                   │ Hash password     │
       │                   │ INSERT user       │
       │                   │──────────────────►│
       │                   │◄──────────────────│
       │                   │ Generate JWT      │
       │◄──────────────────│                   │
       │ { token, user }   │                   │
       │                   │                   │
       │ Store token       │                   │
       │ (localStorage)    │                   │
       │                   │                   │
       │ GET /api/tasks    │                   │
       │ Authorization:    │                   │
       │ Bearer <token>    │                   │
       │──────────────────►│                   │
       │                   │ Verify JWT        │
       │                   │ Extract user_id   │
       │                   │ Query tasks       │
       │                   │──────────────────►│
       │                   │◄──────────────────│
       │◄──────────────────│                   │
       │ { tasks: [...] }  │                   │
```

---

## User Stories

### US-AUTH-1: User Registration (Priority: P1)

**As a** visitor,
**I want to** create an account,
**So that** I can save and access my tasks.

**Acceptance Criteria**:

| AC ID | Scenario | Given | When | Then |
|-------|----------|-------|------|------|
| AC-1.1 | Valid registration | I am on /register | I enter valid email/password and submit | Account created, redirected to dashboard |
| AC-1.2 | Invalid email format | I am on /register | I enter "notanemail" | Validation error "Please enter a valid email" |
| AC-1.3 | Short password | I am on /register | I enter password "short" | Validation error "Password must be at least 8 characters" |
| AC-1.4 | Duplicate email | Email already exists | I try to register with it | Error "Email already registered" |
| AC-1.5 | Auto-login after register | Registration succeeds | Response received | JWT token issued, user logged in |
| AC-1.6 | Redirect if logged in | I am already logged in | I visit /register | Redirected to dashboard |

**Validation Rules**:
- Email: Required, valid format (contains @, valid domain)
- Password: Required, minimum 8 characters

---

### US-AUTH-2: User Login (Priority: P1)

**As a** registered user,
**I want to** log in,
**So that** I can access my saved tasks.

**Acceptance Criteria**:

| AC ID | Scenario | Given | When | Then |
|-------|----------|-------|------|------|
| AC-2.1 | Valid login | I have an account | I enter correct credentials | JWT issued, redirected to dashboard |
| AC-2.2 | Wrong password | I have an account | I enter wrong password | Error "Invalid email or password" |
| AC-2.3 | Non-existent email | Email not registered | I try to login | Error "Invalid email or password" (same message) |
| AC-2.4 | Session persistence | I log in successfully | I refresh the page | Remain logged in |
| AC-2.5 | Token expiry | My token expires | I make an API request | Redirected to login |
| AC-2.6 | Redirect if logged in | I am already logged in | I visit /login | Redirected to dashboard |

**Security Notes**:
- Same error message for wrong email and wrong password (prevents enumeration)
- Tokens stored in localStorage or httpOnly cookie
- Token expiry: 24 hours

---

### US-AUTH-3: User Logout (Priority: P2)

**As a** logged-in user,
**I want to** log out,
**So that** I can secure my account on shared devices.

**Acceptance Criteria**:

| AC ID | Scenario | Given | When | Then |
|-------|----------|-------|------|------|
| AC-3.1 | Logout clears session | I am logged in | I click "Logout" | Token removed, redirected to /login |
| AC-3.2 | Protected routes blocked | I have logged out | I visit /dashboard | Redirected to /login |
| AC-3.3 | Back button blocked | I have logged out | I press browser back | Cannot see protected content |
| AC-3.4 | API calls fail | I have logged out | I make an API request | 401 Unauthorized |

---

### US-AUTH-4: Session Management (Priority: P1)

**As a** user,
**I want to** my session to persist,
**So that** I don't have to log in repeatedly.

**Acceptance Criteria**:

| AC ID | Scenario | Given | When | Then |
|-------|----------|-------|------|------|
| AC-4.1 | Session survives refresh | I am logged in | I refresh the page | Remain logged in |
| AC-4.2 | Session survives close | I am logged in | I close and reopen browser | Remain logged in (if within 24h) |
| AC-4.3 | Token auto-attached | I am logged in | I make API request | JWT automatically included |
| AC-4.4 | Expired token handled | Token has expired | I make API request | Redirected to login with message |

---

## JWT Token Specification

### Token Structure

```
Header:
{
  "alg": "HS256",
  "typ": "JWT"
}

Payload:
{
  "sub": "<user_uuid>",           // User ID
  "email": "<user_email>",        // User email
  "iat": <issued_at_timestamp>,   // Issued at
  "exp": <expiry_timestamp>       // Expires (iat + 24h)
}

Signature:
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  SECRET_KEY
)
```

### Token Lifecycle

| Event | Action |
|-------|--------|
| Registration | Issue new token |
| Login | Issue new token |
| Logout | Remove token from client |
| Expiry | Token becomes invalid after 24 hours |
| API Request | Verify token, extract user_id |

---

## Input/Output Specifications

### Register

**Endpoint**: `POST /api/auth/register`

**Input**:
| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| email | string | Yes | Valid email format, unique |
| password | string | Yes | 8+ characters |

**Output** (Success - 201):
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "created_at": "2026-01-05T10:00:00Z"
  },
  "token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Output** (Error - 400):
```json
{
  "error": "VALIDATION_ERROR",
  "message": "Email already registered"
}
```

---

### Login

**Endpoint**: `POST /api/auth/login`

**Input**:
| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| email | string | Yes | Valid email format |
| password | string | Yes | Non-empty |

**Output** (Success - 200):
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com"
  },
  "token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Output** (Error - 401):
```json
{
  "error": "INVALID_CREDENTIALS",
  "message": "Invalid email or password"
}
```

---

### Logout

**Endpoint**: `POST /api/auth/logout`

**Input**: Authorization header with Bearer token

**Output** (Success - 200):
```json
{
  "message": "Logged out successfully"
}
```

**Notes**:
- Logout is primarily client-side (remove token from storage)
- Backend logout endpoint is optional but recommended for audit logging

---

### Get Current User

**Endpoint**: `GET /api/auth/me`

**Input**: Authorization header with Bearer token

**Output** (Success - 200):
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "created_at": "2026-01-05T10:00:00Z"
}
```

**Output** (Error - 401):
```json
{
  "error": "UNAUTHORIZED",
  "message": "Authentication required"
}
```

---

## Error Responses

| Error Code | HTTP Status | Message | Trigger |
|------------|-------------|---------|---------|
| VALIDATION_ERROR | 400 | "Please enter a valid email address" | Invalid email format |
| VALIDATION_ERROR | 400 | "Password must be at least 8 characters" | Short password |
| VALIDATION_ERROR | 400 | "Email already registered" | Duplicate email on register |
| INVALID_CREDENTIALS | 401 | "Invalid email or password" | Wrong credentials on login |
| UNAUTHORIZED | 401 | "Authentication required" | Missing JWT on protected route |
| TOKEN_EXPIRED | 401 | "Session expired. Please log in again" | Expired JWT |
| TOKEN_INVALID | 401 | "Invalid authentication token" | Malformed/tampered JWT |

---

## Security Requirements

### Password Storage
- Hash with bcrypt, cost factor 12+
- Never store plaintext passwords
- Never log passwords

### Token Security
- Sign with strong secret key (256-bit minimum)
- Store in localStorage (SPA) or httpOnly cookie
- Transmit only over HTTPS in production
- Short expiry (24 hours)

### Rate Limiting
- Login: 5 attempts per minute per IP
- Registration: 3 attempts per minute per IP
- After limit: 429 Too Many Requests with retry-after header

### Enumeration Prevention
- Same error message for wrong email vs wrong password
- Consistent response time for valid vs invalid emails

---

## Frontend Token Handling

### Token Storage
```
localStorage.setItem('auth_token', token)
localStorage.getItem('auth_token')
localStorage.removeItem('auth_token')
```

### API Request Pattern
```
All authenticated requests include:
Authorization: Bearer <token>
```

### Auth State Check
1. On app load, check for token in storage
2. If token exists, call GET /api/auth/me
3. If valid, user is authenticated
4. If 401, clear token and redirect to login

---

## Route Protection

### Frontend Routes

| Route | Access | Redirect |
|-------|--------|----------|
| / | Public | Landing page |
| /login | Public (guest only) | /dashboard if logged in |
| /register | Public (guest only) | /dashboard if logged in |
| /dashboard | Authenticated only | /login if not logged in |

### API Routes

| Route Pattern | Authentication |
|---------------|----------------|
| /api/auth/* | None (public) |
| /api/tasks/* | Required (JWT) |

---

## Related Documents

- @specs/002-todo-fullstack-web/api/rest-endpoints.md - Auth endpoint details
- @specs/002-todo-fullstack-web/database/schema.md - Users table
- @specs/002-todo-fullstack-web/ui/pages.md - Login/Register pages
