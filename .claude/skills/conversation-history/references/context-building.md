# Context Building for OpenAI

Build message arrays for OpenAI API with conversation history.

## Message Array Structure

OpenAI expects messages in this format:

```python
messages = [
    {"role": "system", "content": "System prompt..."},
    {"role": "user", "content": "Previous user message"},
    {"role": "assistant", "content": "Previous assistant response"},
    {"role": "user", "content": "Current user message"},
]
```

## Context Builder

```python
# backend/app/services/agent.py
from typing import List, Optional
from uuid import UUID
from app.services.chat import ChatService

# Configuration
HISTORY_LIMIT = 20  # Max messages to include
MAX_CONTEXT_TOKENS = 4000  # Approximate token budget for history

SYSTEM_PROMPT = """You are a helpful task management assistant. Help users manage their todo list through natural conversation.

You have access to these tools:
- add_task: Create new tasks
- list_tasks: Show all tasks
- complete_task: Mark tasks as done
- delete_task: Remove tasks
- update_task: Change task details

Guidelines:
1. Use position numbers (1, 2, 3) when referring to tasks
2. Always confirm actions with the task title
3. If a task isn't found, suggest listing tasks first
4. Be conversational but concise
5. If unsure what the user wants, ask for clarification"""


async def build_openai_messages(
    chat_service: ChatService,
    conversation_id: UUID,
    current_message: str,
    include_system: bool = True
) -> List[dict]:
    """
    Build complete message array for OpenAI API.

    Args:
        chat_service: ChatService instance
        conversation_id: ID of current conversation
        current_message: The new user message
        include_system: Whether to include system prompt

    Returns:
        List of message dicts ready for OpenAI API
    """
    messages = []

    # 1. System prompt (always first)
    if include_system:
        messages.append({
            "role": "system",
            "content": SYSTEM_PROMPT
        })

    # 2. Conversation history (oldest to newest)
    history = await chat_service.get_conversation_history(
        conversation_id,
        limit=HISTORY_LIMIT
    )
    messages.extend(history)

    # 3. Current user message (always last)
    messages.append({
        "role": "user",
        "content": current_message
    })

    return messages


async def build_messages_with_tool_results(
    base_messages: List[dict],
    assistant_message: dict,
    tool_results: List[dict]
) -> List[dict]:
    """
    Build messages including tool call results for follow-up.

    Used when the assistant made tool calls and we need to
    send the results back for a final response.

    Args:
        base_messages: Original messages sent to OpenAI
        assistant_message: Assistant's response with tool_calls
        tool_results: Results from executing the tools

    Returns:
        Extended message list with tool results
    """
    messages = base_messages.copy()

    # Add assistant's response (with tool_calls)
    messages.append(assistant_message)

    # Add tool results
    for result in tool_results:
        messages.append({
            "role": "tool",
            "tool_call_id": result["tool_call_id"],
            "content": result["content"]
        })

    return messages
```

## Complete Agent Processing

```python
# backend/app/services/agent.py
import json
from openai import AsyncOpenAI
from sqlmodel.ext.asyncio.session import AsyncSession
from app.mcp.tools import TOOL_DEFINITIONS, execute_tool
from app.services.chat import ChatService

client = AsyncOpenAI()


async def process_message(
    user_id: str,
    message: str,
    conversation_history: List[dict],
    session: AsyncSession
) -> str:
    """
    Process a user message through the OpenAI agent.

    Args:
        user_id: Authenticated user's ID
        message: User's input message
        conversation_history: Previous messages for context
        session: Database session for tool execution

    Returns:
        Assistant's response text
    """
    # Build initial messages
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *conversation_history,
        {"role": "user", "content": message}
    ]

    # First API call
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=TOOL_DEFINITIONS,
        tool_choice="auto"
    )

    assistant_message = response.choices[0].message

    # Check if tool calls were made
    if assistant_message.tool_calls:
        # Execute each tool
        tool_results = []
        for tool_call in assistant_message.tool_calls:
            result = await execute_tool(tool_call, user_id, session)
            tool_results.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "content": result
            })

        # Build messages with tool results
        messages.append(assistant_message.model_dump())
        messages.extend(tool_results)

        # Second API call for final response
        final_response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )

        return final_response.choices[0].message.content

    # No tool calls - return direct response
    return assistant_message.content or "I'm not sure how to help with that."
```

## Context Window Management

### Token Estimation

```python
def estimate_tokens(text: str) -> int:
    """Rough estimate: ~4 chars per token for English."""
    return len(text) // 4


def estimate_message_tokens(messages: List[dict]) -> int:
    """Estimate total tokens in message array."""
    total = 0
    for msg in messages:
        # Role overhead (~4 tokens)
        total += 4
        # Content
        total += estimate_tokens(msg.get("content", ""))
    return total
```

### Truncation Strategy

```python
async def get_truncated_history(
    chat_service: ChatService,
    conversation_id: UUID,
    max_tokens: int = 3000
) -> List[dict]:
    """
    Get history that fits within token budget.

    Keeps most recent messages, drops oldest if needed.
    """
    # Start with max messages
    history = await chat_service.get_conversation_history(
        conversation_id,
        limit=HISTORY_LIMIT
    )

    # Truncate if over budget
    while history and estimate_message_tokens(history) > max_tokens:
        history = history[1:]  # Remove oldest message

    return history
```

### Summarization (Advanced)

```python
async def summarize_old_history(
    client: AsyncOpenAI,
    old_messages: List[dict]
) -> str:
    """
    Summarize older conversation history to save tokens.

    Use for very long conversations.
    """
    if not old_messages:
        return ""

    summary_prompt = """Summarize this conversation briefly, focusing on:
1. Tasks mentioned or created
2. Key decisions made
3. User preferences expressed

Conversation:
"""
    for msg in old_messages:
        summary_prompt += f"{msg['role']}: {msg['content']}\n"

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": summary_prompt}],
        max_tokens=200
    )

    return response.choices[0].message.content
```

## Message Role Reference

| Role | Description | When Used |
|------|-------------|-----------|
| `system` | Instructions for the AI | First message, always |
| `user` | User's input | Every user turn |
| `assistant` | AI's response | After each AI turn |
| `tool` | Tool execution result | After tool calls |

## Best Practices

1. **Always include system prompt** - Provides consistent behavior
2. **Chronological order** - Oldest to newest for history
3. **Limit history** - 20 messages or ~3000 tokens
4. **Current message last** - User's new message at the end
5. **Handle empty history** - First message of conversation
