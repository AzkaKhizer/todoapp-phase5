---
name: neon-database-management
description: |
  Database management for Todo AI Chatbot using SQLModel ORM with Neon PostgreSQL. Use when implementing:
  (1) Task, Conversation, and Message SQLModel definitions
  (2) Database queries for user-scoped CRUD operations
  (3) Async database sessions with connection pooling
  (4) Model relationships and foreign key constraints
---

# Neon Database Management

Manage database models and operations for the Todo AI Chatbot using SQLModel with Neon PostgreSQL.

## Architecture

```
FastAPI -> AsyncSession -> SQLModel -> asyncpg -> Neon PostgreSQL
```

## Models Overview

| Model | Purpose | Key Fields |
|-------|---------|------------|
| Task | User's todo items | id, user_id, title, description, completed |
| Conversation | Chat sessions | id, user_id, title, created_at |
| Message | Chat messages | id, conversation_id, role, content |

## Quick Setup

### 1. Database Configuration

```python
# backend/app/database.py
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL").replace("postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
```

### 2. Model Registration

```python
# backend/app/models/__init__.py
from app.models.task import Task
from app.models.conversation import Conversation
from app.models.message import Message

__all__ = ["Task", "Conversation", "Message"]
```

### 3. Table Creation

```python
# backend/app/main.py
from sqlmodel import SQLModel
from app.database import engine

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
```

## Key Patterns

### User-Scoped Queries

All queries filter by user_id for data isolation:

```python
async def get_user_tasks(session: AsyncSession, user_id: str) -> list[Task]:
    result = await session.exec(
        select(Task).where(Task.user_id == user_id).order_by(Task.created_at)
    )
    return result.all()
```

### Async Session Usage

```python
async def create_task(session: AsyncSession, user_id: str, title: str) -> Task:
    task = Task(user_id=user_id, title=title)
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task
```

## Reference Files

- **Models**: See `references/models.md` for complete SQLModel definitions
- **Queries**: See `references/queries.md` for CRUD operations
- **Migration**: See `references/migration.md` for schema migration SQL
