---
name: ai-todo-chatbot
description: |
  AI-powered chatbot for managing tasks using natural language. Integrates with OpenAI Agents SDK, MCP tools, and Neon PostgreSQL for task management. Use when implementing:
  (1) Natural language task operations (add, update, delete, complete, list tasks)
  (2) Chat interface with conversation persistence
  (3) OpenAI function calling with MCP tool definitions
  (4) Authenticated chat endpoints with Better Auth JWT
---

# AI Todo Chatbot

Build an AI-powered chatbot that manages tasks through natural language using OpenAI Agents SDK and MCP tools.

## Architecture

```
Frontend (Vercel AI SDK) -> POST /api/chat -> OpenAI Agent -> MCP Tools -> Task Service -> Database
```

## Backend Implementation

### 1. MCP Tool Definitions

Create tools in `backend/app/mcp/tools.py`:

```python
from typing import Any
from app.services.task import TaskService

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Create a new task for the user",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Task title"},
                    "description": {"type": "string", "description": "Optional task description"}
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "List all tasks for the user",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "complete_task",
            "description": "Mark a task as complete by position number",
            "parameters": {
                "type": "object",
                "properties": {
                    "position": {"type": "integer", "description": "Task position (1, 2, 3...)"}
                },
                "required": ["position"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Delete a task by position number",
            "parameters": {
                "type": "object",
                "properties": {
                    "position": {"type": "integer", "description": "Task position (1, 2, 3...)"}
                },
                "required": ["position"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Update a task's title or description",
            "parameters": {
                "type": "object",
                "properties": {
                    "position": {"type": "integer", "description": "Task position"},
                    "title": {"type": "string", "description": "New title"},
                    "description": {"type": "string", "description": "New description"}
                },
                "required": ["position"]
            }
        }
    }
]
```

### 2. OpenAI Agent Service

Create agent in `backend/app/services/agent.py`:

```python
from openai import AsyncOpenAI
from app.mcp.tools import TOOL_DEFINITIONS, execute_tool

SYSTEM_PROMPT = """You are a helpful task management assistant. Help users manage their tasks through natural language.

When users want to:
- Add a task: Use add_task tool
- View tasks: Use list_tasks tool
- Complete a task: Use complete_task tool with position number
- Delete a task: Use delete_task tool with position number
- Update a task: Use update_task tool

Always confirm actions and provide friendly responses."""

async def process_message(
    client: AsyncOpenAI,
    user_id: str,
    message: str,
    conversation_history: list[dict]
) -> str:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(conversation_history)
    messages.append({"role": "user", "content": message})

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=TOOL_DEFINITIONS
    )

    # Handle tool calls
    if response.choices[0].message.tool_calls:
        tool_results = []
        for tool_call in response.choices[0].message.tool_calls:
            result = await execute_tool(tool_call, user_id)
            tool_results.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "content": result
            })

        # Get final response with tool results
        messages.append(response.choices[0].message)
        messages.extend(tool_results)

        final_response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        return final_response.choices[0].message.content

    return response.choices[0].message.content
```

### 3. Chat Router

Create router in `backend/app/routers/chat.py`:

```python
from fastapi import APIRouter, Depends
from app.dependencies.auth import get_current_user
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.agent import process_message
from app.services.chat import get_or_create_conversation, save_message

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user = Depends(get_current_user)
):
    conversation = await get_or_create_conversation(
        user_id=user.id,
        conversation_id=request.conversation_id
    )

    history = await get_conversation_history(conversation.id)

    response = await process_message(
        client=openai_client,
        user_id=user.id,
        message=request.message,
        conversation_history=history
    )

    await save_message(conversation.id, user.id, "user", request.message)
    await save_message(conversation.id, user.id, "assistant", response)

    return ChatResponse(
        message=response,
        conversation_id=str(conversation.id)
    )
```

## Frontend Implementation

### Chat Hook with Vercel AI SDK

Create hook in `frontend/src/hooks/useChat.ts`:

```typescript
import { useState } from 'react';
import { chatApi } from '@/lib/chat-api';

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);

  const sendMessage = async (content: string) => {
    setIsLoading(true);
    setMessages(prev => [...prev, { role: 'user', content }]);

    try {
      const response = await chatApi.send(content, conversationId);
      setMessages(prev => [...prev, { role: 'assistant', content: response.message }]);
      setConversationId(response.conversation_id);
    } catch (error) {
      console.error('Chat error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return { messages, sendMessage, isLoading };
}
```

## Database Models

See `references/data-model.md` for Conversation and Message SQLModel definitions.

## Key Patterns

### Position-Based Task References

Use position numbers (1, 2, 3) instead of UUIDs for user-friendly references:

```python
async def get_task_by_position(user_id: str, position: int) -> Task | None:
    tasks = await get_user_tasks(user_id)
    if 0 < position <= len(tasks):
        return tasks[position - 1]
    return None
```

### Error Handling

Provide friendly error messages:
- "I couldn't find task #3. You only have 2 tasks."
- "Something went wrong. Please try again."

### Conversation Persistence

Store messages in database for context across sessions. Load last 20 messages for context window management.
