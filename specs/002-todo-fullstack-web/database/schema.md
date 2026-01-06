# Database Schema Specification

**Parent Spec**: @specs/002-todo-fullstack-web/spec.md
**Feature Branch**: `002-todo-fullstack-web`
**Created**: 2026-01-05

---

## Overview

This document specifies the PostgreSQL database schema for the Todo Full-Stack Web Application. The database is hosted on Neon PostgreSQL and accessed via SQLModel ORM.

---

## Database Configuration

| Property | Value |
|----------|-------|
| Database | PostgreSQL 15+ |
| Hosting | Neon (serverless) |
| ORM | SQLModel (Python) |
| Connection | Async via asyncpg |
| Pooling | Neon's connection pooling |

---

## Entity Relationship Diagram

```
┌─────────────────────────────────────┐
│              users                  │
├─────────────────────────────────────┤
│ id          UUID      PK            │
│ email       VARCHAR   UNIQUE NOT NULL│
│ password    VARCHAR   NOT NULL      │
│ created_at  TIMESTAMP NOT NULL      │
└─────────────────────────────────────┘
                 │
                 │ 1
                 │
                 ▼ *
┌─────────────────────────────────────┐
│              tasks                  │
├─────────────────────────────────────┤
│ id          UUID      PK            │
│ title       VARCHAR   NOT NULL      │
│ description TEXT                    │
│ is_complete BOOLEAN   NOT NULL      │
│ user_id     UUID      FK NOT NULL   │
│ created_at  TIMESTAMP NOT NULL      │
│ updated_at  TIMESTAMP NOT NULL      │
└─────────────────────────────────────┘
```

---

## Table: users

Stores registered user accounts.

### Columns

| Column | Type | Constraints | Default | Description |
|--------|------|-------------|---------|-------------|
| id | UUID | PRIMARY KEY | gen_random_uuid() | Unique identifier |
| email | VARCHAR(255) | UNIQUE, NOT NULL | - | User's email address |
| password_hash | VARCHAR(255) | NOT NULL | - | Bcrypt hashed password |
| created_at | TIMESTAMP WITH TIME ZONE | NOT NULL | CURRENT_TIMESTAMP | Account creation time |

### Indexes

| Index Name | Columns | Type | Purpose |
|------------|---------|------|---------|
| users_pkey | id | PRIMARY | Primary key lookup |
| users_email_idx | email | UNIQUE | Email lookup for login |

### Constraints

| Constraint | Type | Description |
|------------|------|-------------|
| users_pkey | PRIMARY KEY | Ensures unique user ID |
| users_email_key | UNIQUE | Prevents duplicate emails |
| users_email_check | CHECK | email contains '@' |

---

## Table: tasks

Stores todo items associated with users.

### Columns

| Column | Type | Constraints | Default | Description |
|--------|------|-------------|---------|-------------|
| id | UUID | PRIMARY KEY | gen_random_uuid() | Unique identifier |
| title | VARCHAR(200) | NOT NULL | - | Task title |
| description | TEXT | NULL | '' | Optional description |
| is_complete | BOOLEAN | NOT NULL | FALSE | Completion status |
| user_id | UUID | FOREIGN KEY, NOT NULL | - | Owner reference |
| created_at | TIMESTAMP WITH TIME ZONE | NOT NULL | CURRENT_TIMESTAMP | Creation time |
| updated_at | TIMESTAMP WITH TIME ZONE | NOT NULL | CURRENT_TIMESTAMP | Last modification time |

### Indexes

| Index Name | Columns | Type | Purpose |
|------------|---------|------|---------|
| tasks_pkey | id | PRIMARY | Primary key lookup |
| tasks_user_id_idx | user_id | BTREE | User's tasks lookup |
| tasks_user_id_created_idx | (user_id, created_at DESC) | BTREE | User's tasks sorted by date |

### Constraints

| Constraint | Type | Description |
|------------|------|-------------|
| tasks_pkey | PRIMARY KEY | Ensures unique task ID |
| tasks_user_id_fkey | FOREIGN KEY | References users(id) |
| tasks_title_check | CHECK | LENGTH(title) >= 1 |

### Foreign Key Details

| Constraint | References | On Delete | On Update |
|------------|------------|-----------|-----------|
| tasks_user_id_fkey | users(id) | CASCADE | CASCADE |

**Note**: CASCADE delete means deleting a user also deletes all their tasks.

---

## Data Types

### UUID Generation

- Use PostgreSQL's `gen_random_uuid()` function
- Provides 122 bits of randomness
- Example: `550e8400-e29b-41d4-a716-446655440000`

### Timestamp Handling

- Store all timestamps in UTC (`TIMESTAMP WITH TIME ZONE`)
- Default to `CURRENT_TIMESTAMP`
- Frontend displays in user's local timezone

### Password Hashing

- Algorithm: bcrypt
- Cost factor: 12
- Output length: 60 characters
- Format: `$2b$12$...`

---

## SQLModel Definitions

### User Model

```
User:
  id: UUID (primary key)
  email: str (max 255, unique, indexed)
  password_hash: str (max 255)
  created_at: datetime (default: utcnow)

  Relationships:
    tasks: List[Task] (back_populates="owner")
```

### Task Model

```
Task:
  id: UUID (primary key)
  title: str (max 200, non-empty)
  description: str (default: "")
  is_complete: bool (default: False)
  user_id: UUID (foreign key -> users.id)
  created_at: datetime (default: utcnow)
  updated_at: datetime (default: utcnow, onupdate: utcnow)

  Relationships:
    owner: User (back_populates="tasks")
```

---

## Migration Strategy

### Initial Migration

1. Create `users` table
2. Create `tasks` table with foreign key
3. Create indexes
4. Add constraints

### Future Migrations

- Use Alembic for schema migrations
- Version control all migrations
- Support rollback capability

---

## Query Patterns

### Get User by Email (Login)

```sql
SELECT id, email, password_hash, created_at
FROM users
WHERE email = :email
LIMIT 1
```

### Get User's Tasks

```sql
SELECT id, title, description, is_complete, user_id, created_at, updated_at
FROM tasks
WHERE user_id = :user_id
ORDER BY created_at DESC
```

### Create Task

```sql
INSERT INTO tasks (id, title, description, is_complete, user_id, created_at, updated_at)
VALUES (gen_random_uuid(), :title, :description, FALSE, :user_id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
RETURNING *
```

### Update Task

```sql
UPDATE tasks
SET title = :title,
    description = :description,
    updated_at = CURRENT_TIMESTAMP
WHERE id = :task_id AND user_id = :user_id
RETURNING *
```

### Toggle Complete

```sql
UPDATE tasks
SET is_complete = NOT is_complete,
    updated_at = CURRENT_TIMESTAMP
WHERE id = :task_id AND user_id = :user_id
RETURNING *
```

### Delete Task

```sql
DELETE FROM tasks
WHERE id = :task_id AND user_id = :user_id
```

---

## Data Validation

### At Database Level

| Field | Validation |
|-------|------------|
| users.email | NOT NULL, UNIQUE, contains '@' |
| users.password_hash | NOT NULL |
| tasks.title | NOT NULL, LENGTH >= 1 |
| tasks.is_complete | NOT NULL |
| tasks.user_id | NOT NULL, valid FK |

### At Application Level

| Field | Validation |
|-------|------------|
| email | Valid email format |
| password | Minimum 8 characters |
| title | 1-200 characters, trimmed |
| description | 0-2000 characters |

---

## Performance Considerations

### Indexing Strategy

1. Primary keys indexed automatically
2. `user_id` indexed for task filtering
3. Composite index on `(user_id, created_at)` for sorted listing

### Connection Pooling

- Use Neon's connection pooler
- Min connections: 1
- Max connections: 10 (per serverless instance)

### Query Optimization

- Always filter by `user_id` first (uses index)
- Limit result sets (default 100)
- Use pagination for large lists

---

## Security Considerations

### Data Access

- All task queries MUST include `WHERE user_id = :authenticated_user_id`
- Never expose password_hash in API responses
- Use parameterized queries (SQLModel handles this)

### Encryption

- Passwords hashed with bcrypt
- Database connection encrypted (TLS)
- Neon provides encryption at rest

---

## Backup and Recovery

### Neon Features

- Automatic daily backups
- Point-in-time recovery
- Branching for development/testing

### Data Retention

- User data retained until account deletion
- Task data retained until task deletion or user deletion
- No soft deletes in Phase II (hard deletes only)

---

## Related Documents

- @specs/002-todo-fullstack-web/api/rest-endpoints.md - API using this schema
- @specs/002-todo-fullstack-web/features/task-crud.md - Task operations
- @specs/002-todo-fullstack-web/features/authentication.md - User operations
