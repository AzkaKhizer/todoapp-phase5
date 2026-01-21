# Protected Routes

Patterns for protecting FastAPI endpoints with JWT authentication.

## Basic Protected Endpoint

```python
# backend/app/routers/chat.py
from fastapi import APIRouter, Depends
from app.dependencies.auth import get_current_user, User

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("")
async def send_message(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Protected endpoint - requires valid JWT token.
    current_user.id is automatically extracted from token.
    """
    # Use current_user.id for all database operations
    response = await chat_service.process_message(
        user_id=current_user.id,
        message=request.message
    )
    return response
```

## Chat Router (Complete)

```python
# backend/app/routers/chat.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from app.database import get_session
from app.dependencies.auth import get_current_user, User
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ConversationResponse,
    ConversationListResponse,
)
from app.services.chat import ChatService
from app.services.agent import process_message

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Send a message and get AI response."""
    chat_service = ChatService(session)

    # Get or create conversation (user-scoped)
    conversation = await chat_service.get_or_create_conversation(
        user_id=current_user.id,
        conversation_id=request.conversation_id
    )

    # Get conversation history for context
    history = await chat_service.get_conversation_history(conversation.id)

    # Process message with AI agent
    response = await process_message(
        user_id=current_user.id,
        message=request.message,
        conversation_history=history,
        session=session
    )

    # Save messages
    await chat_service.save_message(
        conversation.id, current_user.id, "user", request.message
    )
    await chat_service.save_message(
        conversation.id, current_user.id, "assistant", response
    )

    return ChatResponse(
        message=response,
        conversation_id=str(conversation.id)
    )


@router.get("/conversations", response_model=ConversationListResponse)
async def list_conversations(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """List user's conversations."""
    chat_service = ChatService(session)
    conversations = await chat_service.get_user_conversations(current_user.id)

    return ConversationListResponse(
        conversations=[
            ConversationResponse(
                id=str(c.id),
                title=c.title,
                created_at=c.created_at.isoformat()
            )
            for c in conversations
        ]
    )


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Get a specific conversation with messages."""
    chat_service = ChatService(session)
    conversation = await chat_service.get_conversation_by_id(
        UUID(conversation_id),
        current_user.id  # Ensures user can only access their own conversations
    )

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = await chat_service.get_conversation_messages(
        conversation.id,
        current_user.id
    )

    return ConversationResponse(
        id=str(conversation.id),
        title=conversation.title,
        created_at=conversation.created_at.isoformat(),
        messages=[
            MessageResponse(
                role=m.role,
                content=m.content,
                created_at=m.created_at.isoformat()
            )
            for m in messages
        ]
    )


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Delete a conversation."""
    chat_service = ChatService(session)
    deleted = await chat_service.delete_conversation(
        UUID(conversation_id),
        current_user.id
    )

    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {"message": "Conversation deleted"}
```

## Task Router (Protected)

```python
# backend/app/routers/tasks.py
from fastapi import APIRouter, Depends, HTTPException
from app.dependencies.auth import get_current_user, User

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("")
async def list_tasks(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """List all tasks for the authenticated user."""
    task_service = TaskService(session)
    tasks = await task_service.get_user_tasks(current_user.id)
    return {"tasks": tasks}


@router.post("")
async def create_task(
    request: CreateTaskRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Create a new task for the authenticated user."""
    task_service = TaskService(session)
    task = await task_service.create_task(
        user_id=current_user.id,  # Always use authenticated user's ID
        title=request.title,
        description=request.description
    )
    return task


@router.put("/{task_id}")
async def update_task(
    task_id: str,
    request: UpdateTaskRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Update a task (only if owned by authenticated user)."""
    task_service = TaskService(session)
    task = await task_service.update_task(
        task_id=UUID(task_id),
        user_id=current_user.id,  # Ensures ownership check
        **request.dict(exclude_unset=True)
    )

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


@router.delete("/{task_id}")
async def delete_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Delete a task (only if owned by authenticated user)."""
    task_service = TaskService(session)
    deleted = await task_service.delete_task(
        task_id=UUID(task_id),
        user_id=current_user.id
    )

    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")

    return {"message": "Task deleted"}
```

## Register Routers

```python
# backend/app/main.py
from app.routers import auth, tasks, chat

app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(chat.router)
```

## Security Checklist

- [ ] All endpoints use `Depends(get_current_user)`
- [ ] All database queries include `user_id` filter
- [ ] Task/conversation access verified by ownership
- [ ] No endpoint exposes data across users
- [ ] 404 returned for resources user doesn't own (not 403)
