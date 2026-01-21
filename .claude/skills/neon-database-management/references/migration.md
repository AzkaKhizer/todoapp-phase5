# Database Migration

SQL migration scripts and SQLModel auto-creation for Neon PostgreSQL.

## Auto-Creation (Development)

SQLModel creates tables automatically on startup:

```python
# backend/app/main.py
from sqlmodel import SQLModel
from app.database import engine
from app.models import Task, Conversation, Message  # noqa: F401

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
```

## Manual Migration SQL

For production or explicit control, use these SQL scripts.

### Create Tasks Table

```sql
-- Already exists from Phase II, but here for reference
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR NOT NULL,
    title VARCHAR(200) NOT NULL,
    description VARCHAR(1000),
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id);
```

### Create Conversations Table

```sql
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR NOT NULL,
    title VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_updated_at ON conversations(updated_at DESC);
```

### Create Messages Table

```sql
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id VARCHAR NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    tool_calls TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);
```

## Complete Migration Script

```sql
-- Migration: Add AI Chatbot tables
-- Version: 003
-- Date: 2026-01-15

BEGIN;

-- Create conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR NOT NULL,
    title VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_updated_at ON conversations(updated_at DESC);

-- Create messages table
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id VARCHAR NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    tool_calls TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);

COMMIT;
```

## Rollback Script

```sql
-- Rollback: Remove AI Chatbot tables
-- WARNING: This will delete all conversation data

BEGIN;

DROP TABLE IF EXISTS messages;
DROP TABLE IF EXISTS conversations;

COMMIT;
```

## Verification Queries

After migration, verify tables exist:

```sql
-- List all tables
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public';

-- Check table columns
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'conversations';

-- Check indexes
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename IN ('tasks', 'conversations', 'messages');

-- Check foreign keys
SELECT
    tc.constraint_name,
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY';
```

## Neon-Specific Notes

### Connection String

```python
# Neon requires SSL, asyncpg driver
DATABASE_URL = "postgresql+asyncpg://user:pass@host/db?sslmode=require"
```

### Connection Pooling

```python
# backend/app/database.py
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

# Use NullPool for serverless (Neon handles pooling)
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    poolclass=NullPool,  # Recommended for Neon serverless
)
```

### Auto-Suspend Handling

Neon databases auto-suspend after inactivity. Handle cold starts:

```python
from sqlalchemy.exc import OperationalError
import asyncio

async def execute_with_retry(session, query, max_retries=3):
    """Execute query with retry for cold start."""
    for attempt in range(max_retries):
        try:
            return await session.exec(query)
        except OperationalError:
            if attempt < max_retries - 1:
                await asyncio.sleep(1)  # Wait for Neon to wake up
            else:
                raise
```

## Schema Evolution

For future schema changes, add migration scripts:

```
backend/migrations/
├── 001_initial_tasks.sql
├── 002_add_timestamps.sql
└── 003_add_chatbot_tables.sql
```

Each migration should be idempotent (use IF NOT EXISTS).
