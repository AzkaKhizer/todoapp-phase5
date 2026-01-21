# SQLModel Definitions

Complete model definitions for Task, Conversation, and Message.

## Task Model (Existing)

```python
# backend/app/models/task.py
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel


class Task(SQLModel, table=True):
    """User's todo task item."""
    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    title: str = Field(max_length=200, nullable=False)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat()
        }
```

## Conversation Model (New)

```python
# backend/app/models/conversation.py
from datetime import datetime
from typing import TYPE_CHECKING, Optional, List
from uuid import UUID, uuid4
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.message import Message


class Conversation(SQLModel, table=True):
    """Chat conversation session."""
    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    title: Optional[str] = Field(default=None, max_length=200)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to messages
    messages: List["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    class Config:
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat()
        }
```

## Message Model (New)

```python
# backend/app/models/message.py
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4
from sqlmodel import Field, Relationship, SQLModel, Column
from sqlalchemy import Text

if TYPE_CHECKING:
    from app.models.conversation import Conversation


class Message(SQLModel, table=True):
    """Individual message within a conversation."""
    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    user_id: str = Field(index=True, nullable=False)
    role: str = Field(max_length=20, nullable=False)  # "user", "assistant", "system", "tool"
    content: str = Field(sa_column=Column(Text, nullable=False))
    tool_calls: Optional[str] = Field(default=None, sa_column=Column(Text))  # JSON string
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to conversation
    conversation: Optional["Conversation"] = Relationship(back_populates="messages")

    class Config:
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat()
        }
```

## Model Registration

```python
# backend/app/models/__init__.py
from app.models.task import Task
from app.models.conversation import Conversation
from app.models.message import Message

__all__ = ["Task", "Conversation", "Message"]
```

## Import in Main

```python
# backend/app/main.py
from sqlmodel import SQLModel
from app.database import engine

# Import models to register them with SQLModel metadata
from app.models import Task, Conversation, Message  # noqa: F401

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
```

## Field Constraints Reference

| Model | Field | Type | Constraints |
|-------|-------|------|-------------|
| Task | id | UUID | PK, auto-generated |
| Task | user_id | str | indexed, not null |
| Task | title | str | max 200 chars, not null |
| Task | description | str | max 1000 chars, nullable |
| Task | completed | bool | default False |
| Conversation | id | UUID | PK, auto-generated |
| Conversation | user_id | str | indexed, not null |
| Conversation | title | str | max 200 chars, nullable |
| Message | id | UUID | PK, auto-generated |
| Message | conversation_id | UUID | FK to conversations.id, indexed |
| Message | user_id | str | indexed, not null |
| Message | role | str | max 20 chars, not null |
| Message | content | Text | not null |
| Message | tool_calls | Text | nullable, JSON string |

## Role Values for Messages

```python
class MessageRole:
    USER = "user"           # User's input message
    ASSISTANT = "assistant" # AI's response
    SYSTEM = "system"       # System prompt (optional)
    TOOL = "tool"           # Tool execution result
```
