# Chat Service Implementation

Complete ChatService for conversation and message management.

## ChatService Class

```python
# backend/app/services/chat.py
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.conversation import Conversation
from app.models.message import Message


class ChatService:
    """
    Service for managing conversations and messages.

    Provides stateless chat by persisting all state in the database.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    # ==================== Conversation Operations ====================

    async def get_or_create_conversation(
        self,
        user_id: str,
        conversation_id: Optional[str] = None
    ) -> Conversation:
        """
        Get existing conversation or create a new one.

        Args:
            user_id: Authenticated user's ID
            conversation_id: Optional existing conversation ID

        Returns:
            Conversation object (existing or newly created)
        """
        # Try to find existing conversation
        if conversation_id:
            try:
                conv_uuid = UUID(conversation_id)
                result = await self.session.exec(
                    select(Conversation).where(
                        Conversation.id == conv_uuid,
                        Conversation.user_id == user_id  # Security: user isolation
                    )
                )
                conversation = result.first()
                if conversation:
                    return conversation
            except ValueError:
                pass  # Invalid UUID, create new

        # Create new conversation
        conversation = Conversation(user_id=user_id)
        self.session.add(conversation)
        await self.session.commit()
        await self.session.refresh(conversation)
        return conversation

    async def get_conversation_by_id(
        self,
        conversation_id: UUID,
        user_id: str
    ) -> Optional[Conversation]:
        """Get a specific conversation, ensuring user ownership."""
        result = await self.session.exec(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
        )
        return result.first()

    async def get_user_conversations(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[Conversation]:
        """Get user's conversations, most recent first."""
        result = await self.session.exec(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(result.all())

    async def update_conversation_title(
        self,
        conversation_id: UUID,
        user_id: str,
        title: str
    ) -> Optional[Conversation]:
        """Update conversation title (e.g., from first message)."""
        conversation = await self.get_conversation_by_id(conversation_id, user_id)
        if not conversation:
            return None

        conversation.title = title[:200]  # Truncate if needed
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
        """Delete conversation and all its messages (cascade)."""
        conversation = await self.get_conversation_by_id(conversation_id, user_id)
        if not conversation:
            return False

        await self.session.delete(conversation)
        await self.session.commit()
        return True

    # ==================== Message Operations ====================

    async def save_message(
        self,
        conversation_id: UUID,
        user_id: str,
        role: str,
        content: str,
        tool_calls: Optional[str] = None
    ) -> Message:
        """
        Save a message to the conversation.

        Args:
            conversation_id: ID of the conversation
            user_id: User who owns the message
            role: Message role (user, assistant, system, tool)
            content: Message content
            tool_calls: Optional JSON string of tool calls

        Returns:
            Created Message object
        """
        message = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role=role,
            content=content,
            tool_calls=tool_calls
        )
        self.session.add(message)

        # Update conversation's updated_at timestamp
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

        Args:
            conversation_id: ID of the conversation
            limit: Maximum number of messages to return

        Returns:
            List of message dicts with 'role' and 'content' keys
        """
        result = await self.session.exec(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        messages = list(result.all())

        # Reverse to get chronological order (oldest first)
        return [
            {"role": m.role, "content": m.content}
            for m in reversed(messages)
        ]

    async def get_conversation_messages(
        self,
        conversation_id: UUID,
        user_id: str
    ) -> List[Message]:
        """Get all messages for a conversation (for API response)."""
        # Verify ownership first
        conversation = await self.get_conversation_by_id(conversation_id, user_id)
        if not conversation:
            return []

        result = await self.session.exec(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        )
        return list(result.all())

    async def get_last_message(
        self,
        conversation_id: UUID
    ) -> Optional[Message]:
        """Get the most recent message in a conversation."""
        result = await self.session.exec(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(1)
        )
        return result.first()

    # ==================== Utility Methods ====================

    async def auto_title_conversation(
        self,
        conversation_id: UUID,
        user_id: str,
        first_message: str
    ) -> None:
        """
        Automatically set conversation title from first message.

        Truncates to first 50 chars or first sentence.
        """
        conversation = await self.get_conversation_by_id(conversation_id, user_id)
        if not conversation or conversation.title:
            return  # Already has title

        # Generate title from first message
        title = first_message.strip()

        # Take first sentence or first 50 chars
        for delimiter in ['.', '!', '?', '\n']:
            if delimiter in title:
                title = title.split(delimiter)[0]
                break

        title = title[:50]
        if len(first_message) > 50:
            title += "..."

        conversation.title = title
        self.session.add(conversation)
        await self.session.commit()

    async def count_user_conversations(self, user_id: str) -> int:
        """Count total conversations for a user."""
        from sqlalchemy import func
        result = await self.session.exec(
            select(func.count(Conversation.id))
            .where(Conversation.user_id == user_id)
        )
        return result.one()

    async def count_conversation_messages(self, conversation_id: UUID) -> int:
        """Count total messages in a conversation."""
        from sqlalchemy import func
        result = await self.session.exec(
            select(func.count(Message.id))
            .where(Message.conversation_id == conversation_id)
        )
        return result.one()
```

## Usage in Chat Router

```python
# backend/app/routers/chat.py
from app.services.chat import ChatService

@router.post("/api/chat")
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    chat_service = ChatService(session)

    # Get or create conversation
    conversation = await chat_service.get_or_create_conversation(
        user_id=current_user.id,
        conversation_id=request.conversation_id
    )

    # Load history for context
    history = await chat_service.get_conversation_history(conversation.id)

    # Process with AI agent
    response = await process_message(current_user.id, request.message, history, session)

    # Save messages
    await chat_service.save_message(conversation.id, current_user.id, "user", request.message)
    await chat_service.save_message(conversation.id, current_user.id, "assistant", response)

    # Auto-title if first message
    if len(history) == 0:
        await chat_service.auto_title_conversation(
            conversation.id, current_user.id, request.message
        )

    return ChatResponse(
        message=response,
        conversation_id=str(conversation.id)
    )
```
