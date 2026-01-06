# REST API Specification

**Parent Spec**: @specs/002-todo-fullstack-web/spec.md
**Feature Branch**: `002-todo-fullstack-web`
**Created**: 2026-01-05

---

## Overview

This document specifies all REST API endpoints for the Todo Full-Stack Web Application backend. The API follows RESTful conventions with JSON request/response bodies.

---

## Base URL

- Development: `http://localhost:8000/api`
- Production: `https://<domain>/api`

---

## Common Headers

### Request Headers

| Header | Value | Required | Description |
|--------|-------|----------|-------------|
| Content-Type | application/json | Yes (POST/PUT/PATCH) | Request body format |
| Authorization | Bearer \<token\> | Yes (protected routes) | JWT authentication |

### Response Headers

| Header | Value | Description |
|--------|-------|-------------|
| Content-Type | application/json | Response body format |
| X-Request-ID | UUID | Request tracking ID |

---

## Authentication Endpoints

### POST /api/auth/register

Create a new user account.

**Authentication**: None

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Validation**:
| Field | Rules |
|-------|-------|
| email | Required, valid email format, unique |
| password | Required, minimum 8 characters |

**Response 201 Created**:
```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "created_at": "2026-01-05T10:30:00Z"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Error Responses**:
| Status | Code | Message | Condition |
|--------|------|---------|-----------|
| 400 | VALIDATION_ERROR | "Please enter a valid email address" | Invalid email format |
| 400 | VALIDATION_ERROR | "Password must be at least 8 characters" | Password too short |
| 400 | EMAIL_EXISTS | "Email already registered" | Duplicate email |

---

### POST /api/auth/login

Authenticate user and issue JWT token.

**Authentication**: None

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response 200 OK**:
```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Error Responses**:
| Status | Code | Message | Condition |
|--------|------|---------|-----------|
| 401 | INVALID_CREDENTIALS | "Invalid email or password" | Wrong email or password |

---

### POST /api/auth/logout

Log out current user (optional endpoint for audit).

**Authentication**: Required

**Request Body**: None

**Response 200 OK**:
```json
{
  "message": "Logged out successfully"
}
```

---

### GET /api/auth/me

Get current authenticated user's profile.

**Authentication**: Required

**Response 200 OK**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "created_at": "2026-01-05T10:30:00Z"
}
```

**Error Responses**:
| Status | Code | Message | Condition |
|--------|------|---------|-----------|
| 401 | UNAUTHORIZED | "Authentication required" | Missing/invalid token |

---

## Task Endpoints

### GET /api/tasks

Retrieve all tasks for the authenticated user.

**Authentication**: Required

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| limit | integer | 100 | Max tasks to return |
| offset | integer | 0 | Pagination offset |

**Response 200 OK**:
```json
{
  "tasks": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "title": "Buy groceries",
      "description": "Milk, bread, eggs",
      "is_complete": false,
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "created_at": "2026-01-05T10:30:00Z",
      "updated_at": "2026-01-05T10:30:00Z"
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440002",
      "title": "Call mom",
      "description": "",
      "is_complete": true,
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "created_at": "2026-01-05T09:00:00Z",
      "updated_at": "2026-01-05T11:00:00Z"
    }
  ],
  "total": 2,
  "limit": 100,
  "offset": 0
}
```

**Notes**:
- Returns only tasks where `user_id` matches authenticated user
- Ordered by `created_at` descending (newest first)

---

### GET /api/tasks/{id}

Retrieve a specific task by ID.

**Authentication**: Required

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| id | UUID | Task identifier |

**Response 200 OK**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "title": "Buy groceries",
  "description": "Milk, bread, eggs",
  "is_complete": false,
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-01-05T10:30:00Z",
  "updated_at": "2026-01-05T10:30:00Z"
}
```

**Error Responses**:
| Status | Code | Message | Condition |
|--------|------|---------|-----------|
| 404 | TASK_NOT_FOUND | "Task not found" | Task doesn't exist |
| 403 | FORBIDDEN | "You don't have permission to access this task" | Task belongs to another user |

---

### POST /api/tasks

Create a new task.

**Authentication**: Required

**Request Body**:
```json
{
  "title": "Buy groceries",
  "description": "Milk, bread, eggs"
}
```

**Validation**:
| Field | Rules |
|-------|-------|
| title | Required, 1-200 characters (trimmed) |
| description | Optional, 0-2000 characters |

**Response 201 Created**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "title": "Buy groceries",
  "description": "Milk, bread, eggs",
  "is_complete": false,
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-01-05T10:30:00Z",
  "updated_at": "2026-01-05T10:30:00Z"
}
```

**Error Responses**:
| Status | Code | Message | Condition |
|--------|------|---------|-----------|
| 400 | VALIDATION_ERROR | "Title is required" | Empty/whitespace title |
| 400 | VALIDATION_ERROR | "Title must be 200 characters or less" | Title too long |
| 400 | VALIDATION_ERROR | "Description must be 2000 characters or less" | Description too long |

---

### PUT /api/tasks/{id}

Update a task (full update).

**Authentication**: Required

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| id | UUID | Task identifier |

**Request Body**:
```json
{
  "title": "Buy groceries today",
  "description": "Milk, bread, eggs, butter"
}
```

**Validation**:
| Field | Rules |
|-------|-------|
| title | Required, 1-200 characters |
| description | Required (can be empty string), 0-2000 characters |

**Response 200 OK**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "title": "Buy groceries today",
  "description": "Milk, bread, eggs, butter",
  "is_complete": false,
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-01-05T10:30:00Z",
  "updated_at": "2026-01-05T12:00:00Z"
}
```

**Error Responses**:
| Status | Code | Message | Condition |
|--------|------|---------|-----------|
| 404 | TASK_NOT_FOUND | "Task not found" | Task doesn't exist |
| 403 | FORBIDDEN | "You don't have permission to modify this task" | Task belongs to another user |
| 400 | VALIDATION_ERROR | "Title is required" | Empty title |

---

### PATCH /api/tasks/{id}

Partially update a task.

**Authentication**: Required

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| id | UUID | Task identifier |

**Request Body** (all fields optional):
```json
{
  "title": "Updated title",
  "description": "Updated description",
  "is_complete": true
}
```

**Validation**:
| Field | Rules |
|-------|-------|
| title | If provided: 1-200 characters |
| description | If provided: 0-2000 characters |
| is_complete | If provided: boolean |

**Response 200 OK**: Updated task object

**Error Responses**: Same as PUT

---

### PATCH /api/tasks/{id}/toggle

Toggle task completion status.

**Authentication**: Required

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| id | UUID | Task identifier |

**Request Body**: None

**Response 200 OK**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "title": "Buy groceries",
  "description": "Milk, bread, eggs",
  "is_complete": true,
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-01-05T10:30:00Z",
  "updated_at": "2026-01-05T12:30:00Z"
}
```

**Error Responses**:
| Status | Code | Message | Condition |
|--------|------|---------|-----------|
| 404 | TASK_NOT_FOUND | "Task not found" | Task doesn't exist |
| 403 | FORBIDDEN | "You don't have permission to modify this task" | Task belongs to another user |

---

### DELETE /api/tasks/{id}

Delete a task.

**Authentication**: Required

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| id | UUID | Task identifier |

**Response 200 OK**:
```json
{
  "message": "Task deleted successfully"
}
```

**Error Responses**:
| Status | Code | Message | Condition |
|--------|------|---------|-----------|
| 404 | TASK_NOT_FOUND | "Task not found" | Task doesn't exist |
| 403 | FORBIDDEN | "You don't have permission to delete this task" | Task belongs to another user |

---

## Health Check

### GET /api/health

Check API availability.

**Authentication**: None

**Response 200 OK**:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-05T10:30:00Z"
}
```

---

## Common Error Response Format

All errors follow this format:

```json
{
  "error": "ERROR_CODE",
  "message": "Human-readable message",
  "details": {}  // Optional, additional error details
}
```

---

## HTTP Status Code Summary

| Status | Meaning | Usage |
|--------|---------|-------|
| 200 | OK | Successful GET, PUT, PATCH, DELETE |
| 201 | Created | Successful POST (resource created) |
| 400 | Bad Request | Validation error |
| 401 | Unauthorized | Missing/invalid authentication |
| 403 | Forbidden | Access denied to resource |
| 404 | Not Found | Resource doesn't exist |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Unexpected server error |

---

## Rate Limiting

| Endpoint Pattern | Limit | Window |
|------------------|-------|--------|
| POST /api/auth/login | 5 requests | 1 minute |
| POST /api/auth/register | 3 requests | 1 minute |
| All other endpoints | 100 requests | 1 minute |

**Response when limited (429)**:
```json
{
  "error": "RATE_LIMITED",
  "message": "Too many requests. Please try again later.",
  "retry_after": 45
}
```

---

## CORS Configuration

**Allowed Origins**:
- Development: `http://localhost:3000`
- Production: `https://<frontend-domain>`

**Allowed Methods**: GET, POST, PUT, PATCH, DELETE, OPTIONS

**Allowed Headers**: Content-Type, Authorization

---

## Related Documents

- @specs/002-todo-fullstack-web/features/task-crud.md - Task operation details
- @specs/002-todo-fullstack-web/features/authentication.md - Auth flow details
- @specs/002-todo-fullstack-web/database/schema.md - Data models
