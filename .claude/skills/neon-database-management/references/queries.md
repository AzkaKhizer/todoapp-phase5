# Database Query Patterns

CRUD operations for Task, Conversation, and Message models.

## Task Queries

### TaskService Class

```python
# backend/app/services/task.py
from typing import Optional, List
from uuid import UUID
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.task import Task


class TaskService:
    """Service for task CRUD operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_task(
        self,
        user_id: str,
        title: str,
        description: Optional[str] = None
    ) -> Task:
        """Create a new task for a user."""
        task = Task(
            user_id=user_id,
            title=title,
            description=description
        )
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def get_user_tasks(self, user_id: str) -> List[Task]:
        """Get all tasks for a user, ordered by creation date."""
        result = await self.session.exec(
            select(Task)
            .where(Task.user_id == user_id)
            .order_by(Task.created_at)
        )
        return list(result.all())

    async def get_task_by_id(self, task_id: UUID, user_id: str) -> Optional[Task]:
        """Get a specific task by ID, scoped to user."""
        result = await self.session.exec(
            select(Task).where(
                Task.id == task_id,
                Task.user_id == user_id
            )
        )
        return result.first()

    async def update_task(
        self,
        task_id: UUID,
        user_id: str,
        **updates
    ) -> Optional[Task]:
        """Update a task's fields."""
        task = await self.get_task_by_id(task_id, user_id)
        if not task:
            return None

        for key, value in updates.items():
            if hasattr(task, key):
                setattr(task, key, value)

        task.updated_at = datetime.utcnow()
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def delete_task(self, task_id: UUID, user_id: str) -> bool:
        """Delete a task. Returns True if deleted."""
        task = await self.get_task_by_id(task_id, user_id)
        if not task:
            return False

        await self.session.delete(task)
        await self.session.commit()
        return True

    async def get_pending_tasks(self, user_id: str) -> List[Task]:
        """Get only pending (incomplete) tasks."""
        result = await self.session.exec(
            select(Task).where(
                Task.user_id == user_id,
                Task.completed == False
            ).order_by(Task.created_at)
        )
        return list(result.all())

    async def get_completed_tasks(self, user_id: str) -> List[Task]:
        """Get only completed tasks."""
        result = await self.session.exec(
            select(Task).where(
                Task.user_id == user_id,
                Task.completed == True
            ).order_by(Task.created_at)
        )
        return list(result.all())
```

## Conversation Queries

### ChatService Class

```python
# backend/app/services/chat.py
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.conversation import Conversation
from app.models.message import Message


class ChatService:
    """Service for conversation and message operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # === Conversation Operations ===

    async def get_or_create_conversation(
        self,
        user_id: str,
        conversation_id: Optional[str] = None
    ) -> Conversation:
        """Get existing conversation or create a new one."""
        if conversation_id:
            result = await self.session.exec(
                select(Conversation).where(
                    Conversation.id == UUID(conversation_id),
                    Conversation.user_id == user_id
                )
            )
            conversation = result.first()
            if conversation:
                return conversation

        # Create new conversation
        conversation = Conversation(user_id=user_id)
        self.session.add(conversation)
        await self.session.commit()
        await self.session.refresh(conversation)
        return conversation

    async def get_user_conversations(
        self,
        user_id: str,
        limit: int = 20
    ) -> List[Conversation]:
        """Get user's conversations, most recent first."""
        result = await self.session.exec(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
        )
        return list(result.all())

    async def get_conversation_by_id(
        self,
        conversation_id: UUID,
        user_id: str
    ) -> Optional[Conversation]:
        """Get a specific conversation by ID."""
        result = await self.session.exec(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
        )
        return result.first()

    async def update_conversation_title(
        self,
        conversation_id: UUID,
        user_id: str,
        title: str
    ) -> Optional[Conversation]:
        """Update conversation title."""
        conversation = await self.get_conversation_by_id(conversation_id, user_id)
        if not conversation:
            return None

        conversation.title = title
        conversation.updated_at = datetime.utcnow()
        self.session.add(conversation)
        await self.session.commit()
        await self.session.refresh(conversation)
        return conversation

    async def delete_conversation(
        self,
        conversation_id: UUID,
        user_id: str
    ) -> bool:
        """Delete a conversation and all its messages."""
        conversation = await self.get_conversation_by_id(conversation_id, user_id)
        if not conversation:
            return False

        await self.session.delete(conversation)
        await self.session.commit()
        return True

    # === Message Operations ===

    async def save_message(
        self,
        conversation_id: UUID,
        user_id: str,
        role: str,
        content: str,
        tool_calls: Optional[str] = None
    ) -> Message:
        """Save a message to a conversation."""
        message = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role=role,
            content=content,
            tool_calls=tool_calls
        )
        self.session.add(message)

        # Update conversation's updated_at
        result = await self.session.exec(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.first()
        if conversation:
            conversation.updated_at = datetime.utcnow()
            self.session.add(conversation)

        await self.session.commit()
        await self.session.refresh(message)
        return message

    async def get_conversation_history(
        self,
        conversation_id: UUID,
        limit: int = 20
    ) -> List[dict]:
        """
        Get conversation history formatted for OpenAI API.
        Returns last N messages in chronological order.
        """
        result = await self.session.exec(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        messages = list(result.all())

        # Reverse to get chronological order
        return [
            {"role": m.role, "content": m.content}
            for m in reversed(messages)
        ]

    async def get_conversation_messages(
        self,
        conversation_id: UUID,
        user_id: str
    ) -> List[Message]:
        """Get all messages for a conversation."""
        # First verify conversation belongs to user
        conversation = await self.get_conversation_by_id(conversation_id, user_id)
        if not conversation:
            return []

        result = await self.session.exec(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        )
        return list(result.all())
```

## Query Patterns Summary

### User-Scoped Queries

Always include `user_id` in WHERE clause:

```python
# Good - user scoped
select(Task).where(Task.user_id == user_id)

# Bad - no user scope (security risk)
select(Task).where(Task.id == task_id)
```

### Pagination

```python
async def get_paginated_tasks(
    session: AsyncSession,
    user_id: str,
    offset: int = 0,
    limit: int = 20
) -> List[Task]:
    result = await session.exec(
        select(Task)
        .where(Task.user_id == user_id)
        .order_by(Task.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return list(result.all())
```

### Count Queries

```python
async def count_user_tasks(session: AsyncSession, user_id: str) -> int:
    from sqlalchemy import func
    result = await session.exec(
        select(func.count(Task.id)).where(Task.user_id == user_id)
    )
    return result.one()
```
