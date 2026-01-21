# Data Model: Todo AI Chatbot

**Feature**: 003-todo-ai-chatbot
**Date**: 2026-01-15

## Entity Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│      User       │     │  Conversation   │     │    Message      │
│  (Better Auth)  │────<│                 │────<│                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │
        │               ┌─────────────────┐
        └──────────────<│      Task       │
                        │   (existing)    │
                        └─────────────────┘
```

## Entities

### 1. Conversation

Represents a chat session between a user and the AI assistant.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | `integer` | PK, auto-increment | Unique conversation identifier |
| `user_id` | `string(64)` | NOT NULL, indexed | Better Auth user ID (nanoid format) |
| `title` | `string(200)` | nullable | Optional conversation title |
| `created_at` | `timestamp` | NOT NULL, default now | When conversation started |
| `updated_at` | `timestamp` | NOT NULL, default now | Last activity timestamp |

**Indexes**:
- Primary key on `id`
- Index on `user_id` for user's conversation list
- Index on `updated_at` for sorting by recent

**Relationships**:
- Belongs to one User (via `user_id`)
- Has many Messages

---

### 2. Message

Represents a single message in a conversation (user or assistant).

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | `integer` | PK, auto-increment | Unique message identifier |
| `conversation_id` | `integer` | FK, NOT NULL | Parent conversation |
| `user_id` | `string(64)` | NOT NULL | Message owner (for security) |
| `role` | `string(20)` | NOT NULL | "user" or "assistant" |
| `content` | `text` | NOT NULL | Message text content |
| `tool_calls` | `jsonb` | nullable | List of MCP tools invoked |
| `created_at` | `timestamp` | NOT NULL, default now | When message was created |

**Indexes**:
- Primary key on `id`
- Index on `conversation_id` for message retrieval
- Index on `(conversation_id, created_at)` for ordered history

**Relationships**:
- Belongs to one Conversation
- Belongs to one User (via `user_id`)

**Tool Calls JSON Schema**:
```json
{
  "tool_calls": [
    {
      "tool": "add_task",
      "arguments": {"title": "Buy groceries"},
      "result": {"id": "uuid", "title": "Buy groceries"}
    }
  ]
}
```

---

### 3. Task (Existing - No Changes)

Reference to existing Task model for MCP tool operations.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | `uuid` | PK | Unique task identifier |
| `user_id` | `string(64)` | NOT NULL, indexed | Task owner |
| `title` | `string(200)` | NOT NULL | Task title |
| `description` | `string(2000)` | default "" | Task description |
| `is_complete` | `boolean` | default false | Completion status |
| `created_at` | `timestamp` | NOT NULL | Creation timestamp |
| `updated_at` | `timestamp` | NOT NULL | Last update timestamp |

---

## SQLModel Definitions

### Conversation Model

```python
# backend/app/models/conversation.py
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, String, Text
from sqlmodel import Field, SQLModel


class Conversation(SQLModel, table=True):
    """Chat conversation session."""

    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(
        sa_column=Column(String(64), index=True, nullable=False)
    )
    title: Optional[str] = Field(default=None, max_length=200)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime, nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime, nullable=False),
    )
```

### Message Model

```python
# backend/app/models/message.py
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class Message(SQLModel, table=True):
    """Individual message in a conversation."""

    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("conversations.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )
    )
    user_id: str = Field(
        sa_column=Column(String(64), nullable=False)
    )
    role: str = Field(max_length=20)  # "user" or "assistant"
    content: str = Field(sa_column=Column(Text, nullable=False))
    tool_calls: Optional[dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSONB, nullable=True),
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime, nullable=False),
    )
```

---

## Validation Rules

### Conversation
- `user_id` must be non-empty string (validated by auth middleware)
- `title` max 200 characters if provided
- `created_at` and `updated_at` auto-managed

### Message
- `role` must be one of: "user", "assistant"
- `content` must be non-empty string
- `conversation_id` must reference existing conversation
- `user_id` must match conversation owner (security check)
- `tool_calls` must be valid JSON if provided

---

## State Transitions

### Conversation Lifecycle
```
[Created] → [Active] → [Archived (future)]
     │          │
     └──────────┴──────────────────────────────────
              Messages added over time
```

### Message Creation Flow
```
User Input → Store Message (role=user) → AI Processing → Store Message (role=assistant)
```

---

## Database Migrations

### Migration: Add Conversations Table

```sql
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    title VARCHAR(200),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_updated_at ON conversations(updated_at);
```

### Migration: Add Messages Table

```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id VARCHAR(64) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    tool_calls JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_conversation_created ON messages(conversation_id, created_at);
```

---

## Query Patterns

### Get User's Conversations (most recent first)
```sql
SELECT * FROM conversations
WHERE user_id = :user_id
ORDER BY updated_at DESC
LIMIT 20;
```

### Get Conversation Messages (for AI context)
```sql
SELECT * FROM messages
WHERE conversation_id = :conversation_id
ORDER BY created_at ASC
LIMIT 20;
```

### Create New Message
```sql
INSERT INTO messages (conversation_id, user_id, role, content, tool_calls)
VALUES (:conversation_id, :user_id, :role, :content, :tool_calls)
RETURNING id, created_at;
```

### Update Conversation Timestamp
```sql
UPDATE conversations
SET updated_at = NOW()
WHERE id = :conversation_id;
```
