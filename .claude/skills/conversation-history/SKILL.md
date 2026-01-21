---
name: conversation-history
description: |
  Conversation history management for Todo AI Chatbot. Stores chat messages in Neon PostgreSQL for stateless operation. Use when implementing:
  (1) Conversation creation and retrieval by user
  (2) Message persistence (user, assistant, tool messages)
  (3) History loading for OpenAI context window
  (4) Conversation continuation across sessions
---

# Conversation History Management

Manage stateless chat by persisting conversation history in the database.

## Architecture

```
User Message -> Save to DB -> Load History -> OpenAI Context -> Response -> Save to DB
```

## Stateless Design

The chat endpoint is stateless - all state is stored in the database:

```python
@router.post("/api/chat")
async def chat(request: ChatRequest, user = Depends(get_current_user)):
    # 1. Get or create conversation
    conversation = await get_or_create_conversation(user.id, request.conversation_id)

    # 2. Load history from database
    history = await get_conversation_history(conversation.id)

    # 3. Process with OpenAI (history provides context)
    response = await process_message(user.id, request.message, history)

    # 4. Save both messages to database
    await save_message(conversation.id, user.id, "user", request.message)
    await save_message(conversation.id, user.id, "assistant", response)

    # 5. Return response with conversation_id for continuation
    return {"message": response, "conversation_id": str(conversation.id)}
```

## Quick Implementation

### Save Message

```python
async def save_message(
    conversation_id: UUID,
    user_id: str,
    role: str,
    content: str
) -> Message:
    message = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role=role,
        content=content
    )
    session.add(message)
    await session.commit()
    return message
```

### Load History for OpenAI

```python
async def get_conversation_history(conversation_id: UUID, limit: int = 20) -> list[dict]:
    result = await session.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    messages = result.all()
    # Reverse for chronological order
    return [{"role": m.role, "content": m.content} for m in reversed(messages)]
```

## Key Patterns

### Conversation Continuation

Client sends `conversation_id` to continue existing conversation:

```typescript
// First message - no conversation_id
const response1 = await chatApi.send("Add a task to buy milk");
const convId = response1.conversation_id;

// Subsequent messages - include conversation_id
const response2 = await chatApi.send("Show my tasks", convId);
```

### Context Window Management

Limit history to last 20 messages to fit OpenAI context:

```python
HISTORY_LIMIT = 20  # Configurable based on model context size

async def build_messages_for_openai(conversation_id: UUID, new_message: str):
    history = await get_conversation_history(conversation_id, limit=HISTORY_LIMIT)
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        *history,
        {"role": "user", "content": new_message}
    ]
```

## Reference Files

- **Service**: See `references/chat-service.md` for complete ChatService implementation
- **Context**: See `references/context-building.md` for OpenAI message array construction
- **Persistence**: See `references/persistence-patterns.md` for database operations
