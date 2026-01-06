# Data Model: Todo Full-Stack Web Application (Phase II)

**Feature Branch**: `002-todo-fullstack-web`
**Created**: 2026-01-05
**Spec**: @specs/002-todo-fullstack-web/spec.md

---

## Overview

This document defines the data entities, their relationships, and validation rules for the Phase II Todo application. Models are implemented using SQLModel (Python) and TypeScript interfaces (frontend).

---

## Entity Relationship Diagram

```
┌─────────────────────────────────────┐
│              User                   │
├─────────────────────────────────────┤
│ id          UUID      PK            │
│ email       String    UNIQUE        │
│ password    String    (hashed)      │
│ created_at  DateTime                │
└─────────────────────────────────────┘
                 │
                 │ 1:N (one user, many tasks)
                 │
                 ▼
┌─────────────────────────────────────┐
│              Task                   │
├─────────────────────────────────────┤
│ id          UUID      PK            │
│ title       String                  │
│ description String    (nullable)    │
│ is_complete Boolean                 │
│ user_id     UUID      FK → User     │
│ created_at  DateTime                │
│ updated_at  DateTime                │
└─────────────────────────────────────┘
```

---

## Entity: User

Represents a registered user account.

### Fields

| Field | Type | Constraints | Default | Description |
|-------|------|-------------|---------|-------------|
| id | UUID | Primary Key | auto-generated | Unique identifier |
| email | String(255) | Unique, Not Null | - | User's email address |
| password_hash | String(255) | Not Null | - | Bcrypt hashed password |
| created_at | DateTime (TZ) | Not Null | CURRENT_TIMESTAMP | Account creation time |

### Validation Rules

| Field | Rule | Error Message |
|-------|------|---------------|
| email | Required | "Email is required" |
| email | Valid format (contains @, domain) | "Please enter a valid email address" |
| email | Unique in database | "Email already registered" |
| password | Required | "Password is required" |
| password | Minimum 8 characters | "Password must be at least 8 characters" |

### Relationships

| Relationship | Target | Type | Cascade |
|--------------|--------|------|---------|
| tasks | Task | One-to-Many | Delete tasks on user deletion |

### Indexes

| Index | Columns | Type | Purpose |
|-------|---------|------|---------|
| users_pkey | id | Primary | PK lookup |
| users_email_idx | email | Unique | Email lookup for auth |

---

## Entity: Task

Represents a todo item owned by a user.

### Fields

| Field | Type | Constraints | Default | Description |
|-------|------|-------------|---------|-------------|
| id | UUID | Primary Key | auto-generated | Unique identifier |
| title | String(200) | Not Null | - | Task title |
| description | Text | Nullable | "" (empty) | Optional description |
| is_complete | Boolean | Not Null | false | Completion status |
| user_id | UUID | Foreign Key, Not Null | - | Owner reference |
| created_at | DateTime (TZ) | Not Null | CURRENT_TIMESTAMP | Creation time |
| updated_at | DateTime (TZ) | Not Null | CURRENT_TIMESTAMP | Last modification |

### Validation Rules

| Field | Rule | Error Message |
|-------|------|---------------|
| title | Required | "Title is required" |
| title | Non-empty after trim | "Title is required" |
| title | Max 200 characters | "Title must be 200 characters or less" |
| description | Max 2000 characters | "Description must be 2000 characters or less" |
| user_id | Must exist in users table | - (DB constraint) |

### Relationships

| Relationship | Target | Type | On Delete |
|--------------|--------|------|-----------|
| owner | User | Many-to-One | CASCADE (delete task) |

### Indexes

| Index | Columns | Type | Purpose |
|-------|---------|------|---------|
| tasks_pkey | id | Primary | PK lookup |
| tasks_user_id_idx | user_id | B-tree | User's tasks lookup |
| tasks_user_created_idx | (user_id, created_at DESC) | Composite | Sorted task list |

---

## State Transitions

### Task Completion State

```
          ┌─────────────────┐
          │   is_complete   │
          │    = false      │
          │   (Incomplete)  │
          └────────┬────────┘
                   │
                   │ toggle_complete()
                   ▼
          ┌─────────────────┐
          │   is_complete   │
          │    = true       │
          │   (Complete)    │
          └────────┬────────┘
                   │
                   │ toggle_complete()
                   ▼
          ┌─────────────────┐
          │   is_complete   │
          │    = false      │
          │   (Incomplete)  │
          └─────────────────┘
```

### Task Lifecycle

```
[Create] → [Active/Incomplete] → [Complete] → [Delete]
                  ↑                   │
                  └───────────────────┘
                     (toggle back)
```

---

## API Data Transfer Objects

### UserCreate (Registration Input)

| Field | Type | Required |
|-------|------|----------|
| email | string | Yes |
| password | string | Yes |

### UserResponse (API Output)

| Field | Type | Description |
|-------|------|-------------|
| id | string (UUID) | User ID |
| email | string | Email address |
| created_at | string (ISO 8601) | Creation timestamp |

### LoginRequest

| Field | Type | Required |
|-------|------|----------|
| email | string | Yes |
| password | string | Yes |

### AuthResponse

| Field | Type | Description |
|-------|------|-------------|
| user | UserResponse | User data |
| token | string | JWT token |

### TaskCreate (Input)

| Field | Type | Required |
|-------|------|----------|
| title | string | Yes |
| description | string | No |

### TaskUpdate (Input)

| Field | Type | Required |
|-------|------|----------|
| title | string | No |
| description | string | No |
| is_complete | boolean | No |

### TaskResponse (API Output)

| Field | Type | Description |
|-------|------|-------------|
| id | string (UUID) | Task ID |
| title | string | Task title |
| description | string | Description (may be empty) |
| is_complete | boolean | Completion status |
| user_id | string (UUID) | Owner ID |
| created_at | string (ISO 8601) | Creation timestamp |
| updated_at | string (ISO 8601) | Last update timestamp |

### TaskListResponse

| Field | Type | Description |
|-------|------|-------------|
| tasks | TaskResponse[] | Array of tasks |
| total | number | Total task count |
| limit | number | Page size |
| offset | number | Pagination offset |

---

## Data Constraints Summary

### Business Rules

1. **Email Uniqueness**: Each email can only be registered once
2. **Task Ownership**: Tasks belong to exactly one user
3. **User Isolation**: Users can only access their own tasks
4. **Title Required**: Tasks must have a non-empty title
5. **Default Incomplete**: New tasks default to is_complete = false

### Database Constraints

1. **Primary Keys**: UUIDs auto-generated
2. **Foreign Keys**: task.user_id → users.id with CASCADE delete
3. **Not Null**: id, email, password_hash, title, is_complete, user_id, timestamps
4. **Unique**: users.email
5. **Check**: title length >= 1

---

## Timestamps

### Auto-Management

| Entity | Field | Behavior |
|--------|-------|----------|
| User | created_at | Set on insert |
| Task | created_at | Set on insert |
| Task | updated_at | Set on insert, updated on modification |

### Timezone

- Store: UTC (TIMESTAMP WITH TIME ZONE)
- Display: Convert to user's local timezone in frontend
- API: ISO 8601 format with timezone

---

## Related Documents

- @specs/002-todo-fullstack-web/database/schema.md - Database implementation
- @specs/002-todo-fullstack-web/api/rest-endpoints.md - API using these models
- @specs/002-todo-fullstack-web/spec.md - Feature requirements
