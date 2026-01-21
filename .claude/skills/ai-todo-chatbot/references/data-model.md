# Data Models for AI Todo Chatbot

## Conversation Model

```python
# backend/app/models/conversation.py
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.message import Message

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    title: Optional[str] = Field(default=None, max_length=200)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    messages: list["Message"] = Relationship(back_populates="conversation")
```

## Message Model

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
    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    user_id: str = Field(index=True, nullable=False)
    role: str = Field(max_length=20)  # "user", "assistant", "system", "tool"
    content: str = Field(sa_column=Column(Text))
    tool_calls: Optional[str] = Field(default=None, sa_column=Column(Text))  # JSON string
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    conversation: Optional["Conversation"] = Relationship(back_populates="messages")
```

## Chat Schemas

```python
# backend/app/schemas/chat.py
from typing import Optional
from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    message: str
    conversation_id: str

class MessageResponse(BaseModel):
    role: str
    content: str
    created_at: str

class ConversationResponse(BaseModel):
    id: str
    title: Optional[str]
    created_at: str
    messages: list[MessageResponse] = []

class ConversationListResponse(BaseModel):
    conversations: list[ConversationResponse]
```

## Database Migration SQL

```sql
-- Create conversations table
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR NOT NULL,
    title VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);

-- Create messages table
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id VARCHAR NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    tool_calls TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_user_id ON messages(user_id);
```

## Query Patterns

### Get or Create Conversation

```python
async def get_or_create_conversation(
    session: AsyncSession,
    user_id: str,
    conversation_id: Optional[str] = None
) -> Conversation:
    if conversation_id:
        result = await session.exec(
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
    session.add(conversation)
    await session.commit()
    await session.refresh(conversation)
    return conversation
```

### Get Conversation History (Last 20 Messages)

```python
async def get_conversation_history(
    session: AsyncSession,
    conversation_id: UUID,
    limit: int = 20
) -> list[dict]:
    result = await session.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    messages = result.all()
    # Reverse to get chronological order
    return [
        {"role": m.role, "content": m.content}
        for m in reversed(messages)
    ]
```

### Save Message

```python
async def save_message(
    session: AsyncSession,
    conversation_id: UUID,
    user_id: str,
    role: str,
    content: str,
    tool_calls: Optional[str] = None
) -> Message:
    message = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role=role,
        content=content,
        tool_calls=tool_calls
    )
    session.add(message)
    await session.commit()
    await session.refresh(message)
    return message
```
