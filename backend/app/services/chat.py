"""Chat service for conversation and message management."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import func, select

from app.models.conversation import Conversation
from app.models.message import Message


async def create_conversation(
    session: AsyncSession,
    user_id: str,
    title: str | None = None,
) -> Conversation:
    """Create a new conversation for a user."""
    conversation = Conversation(
        user_id=user_id,
        title=title,
    )
    session.add(conversation)
    await session.commit()
    await session.refresh(conversation)
    return conversation


async def get_conversation(
    session: AsyncSession,
    conversation_id: uuid.UUID,
    user_id: str,
) -> Conversation | None:
    """Get a conversation by ID, ensuring user ownership."""
    query = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id,
    )
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def get_conversations(
    session: AsyncSession,
    user_id: str,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[Conversation], int]:
    """Get paginated conversations for a user."""
    # Get total count
    count_query = (
        select(func.count())
        .select_from(Conversation)
        .where(Conversation.user_id == user_id)
    )
    total_result = await session.execute(count_query)
    total = total_result.scalar_one()

    # Get conversations ordered by most recent first
    query = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(query)
    conversations = list(result.scalars().all())

    return conversations, total


async def delete_conversation(
    session: AsyncSession,
    conversation_id: uuid.UUID,
    user_id: str,
) -> bool:
    """Delete a conversation and its messages."""
    conversation = await get_conversation(session, conversation_id, user_id)
    if not conversation:
        return False

    # Delete all messages in the conversation
    delete_messages_query = select(Message).where(
        Message.conversation_id == conversation_id
    )
    result = await session.execute(delete_messages_query)
    messages = result.scalars().all()
    for msg in messages:
        await session.delete(msg)

    # Delete the conversation
    await session.delete(conversation)
    await session.commit()
    return True


async def update_conversation_timestamp(
    session: AsyncSession,
    conversation: Conversation,
) -> None:
    """Update the conversation's updated_at timestamp."""
    conversation.updated_at = datetime.utcnow()
    session.add(conversation)
    await session.commit()


async def add_message(
    session: AsyncSession,
    conversation_id: uuid.UUID,
    user_id: str,
    role: str,
    content: str,
    tool_calls: str | None = None,
) -> Message:
    """Add a message to a conversation."""
    message = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role=role,
        content=content,
        tool_calls=tool_calls,
    )
    session.add(message)
    await session.commit()
    await session.refresh(message)
    return message


async def get_conversation_messages(
    session: AsyncSession,
    conversation_id: uuid.UUID,
    user_id: str,
    limit: int = 50,
) -> list[Message]:
    """Get messages for a conversation, ordered by creation time."""
    # Verify user owns the conversation
    conversation = await get_conversation(session, conversation_id, user_id)
    if not conversation:
        return []

    query = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .limit(limit)
    )
    result = await session.execute(query)
    return list(result.scalars().all())


async def get_conversation_history_for_agent(
    session: AsyncSession,
    conversation_id: uuid.UUID,
    user_id: str,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Get conversation history formatted for the OpenAI agent.

    Returns messages in the format expected by the OpenAI API.
    """
    messages = await get_conversation_messages(
        session, conversation_id, user_id, limit=limit
    )

    history = []
    for msg in messages:
        entry = {"role": msg.role, "content": msg.content}
        # Note: tool_calls are stored but not reconstructed for history
        # The agent will re-execute tools if needed based on context
        history.append(entry)

    return history
