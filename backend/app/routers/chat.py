"""Chat router for AI chatbot endpoints."""

import asyncio
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from openai import APIError, APITimeoutError, RateLimitError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.dependencies.auth import get_current_user_id
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ConversationDetailResponse,
    ConversationListResponse,
    ConversationResponse,
    MessageResponse,
)
from app.services import chat as chat_service
from app.services.agent import process_chat_message

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def send_chat_message(
    request: ChatRequest,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ChatResponse:
    """Send a chat message and get AI response.

    If conversation_id is provided, continues that conversation.
    Otherwise, creates a new conversation.
    """
    conversation = None

    # Get or create conversation
    if request.conversation_id:
        conversation = await chat_service.get_conversation(
            session, request.conversation_id, user_id
        )
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )
    else:
        # Create new conversation with first message as title
        title = request.message[:50] + "..." if len(request.message) > 50 else request.message
        conversation = await chat_service.create_conversation(
            session, user_id, title=title
        )

    # Get conversation history for context
    history = await chat_service.get_conversation_history_for_agent(
        session, conversation.id, user_id
    )

    # Process the message with the AI agent (30s timeout)
    try:
        response_text, messages_to_store = await asyncio.wait_for(
            process_chat_message(
                request.message,
                user_id,
                session,
                conversation_history=history,
            ),
            timeout=30.0,
        )
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Request timed out. Please try again with a shorter message.",
        )
    except APITimeoutError:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="AI service timed out. Please try again.",
        )
    except RateLimitError:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="AI service is busy. Please wait a moment and try again.",
        )
    except APIError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service temporarily unavailable. Please try again.",
        )
    except ValueError as e:
        # Missing OPENAI_API_KEY
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service not configured.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again.",
        )

    # Store the messages
    for msg in messages_to_store:
        await chat_service.add_message(
            session,
            conversation.id,
            user_id,
            role=msg["role"],
            content=msg["content"],
            tool_calls=msg.get("tool_calls"),
        )

    # Update conversation timestamp
    await chat_service.update_conversation_timestamp(session, conversation)

    return ChatResponse(
        message=response_text,
        conversation_id=conversation.id,
    )


@router.get("/conversations", response_model=ConversationListResponse)
async def list_conversations(
    limit: int = 20,
    offset: int = 0,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ConversationListResponse:
    """Get list of user's conversations."""
    conversations, total = await chat_service.get_conversations(
        session, user_id, limit=limit, offset=offset
    )

    return ConversationListResponse(
        conversations=[
            ConversationResponse(
                id=c.id,
                title=c.title,
                created_at=c.created_at,
                updated_at=c.updated_at,
            )
            for c in conversations
        ],
        total=total,
    )


@router.get("/conversations/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conversation_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ConversationDetailResponse:
    """Get a conversation with its messages."""
    conversation = await chat_service.get_conversation(
        session, conversation_id, user_id
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    messages = await chat_service.get_conversation_messages(
        session, conversation_id, user_id
    )

    return ConversationDetailResponse(
        id=conversation.id,
        title=conversation.title,
        messages=[
            MessageResponse(
                id=m.id,
                role=m.role,
                content=m.content,
                created_at=m.created_at,
            )
            for m in messages
        ],
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
    )


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> None:
    """Delete a conversation and all its messages."""
    deleted = await chat_service.delete_conversation(
        session, conversation_id, user_id
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )
