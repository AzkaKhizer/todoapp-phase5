"""OpenAI agent service for chat processing."""

import json
import os
from typing import Any

from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.mcp.tools import TOOL_DEFINITIONS, execute_tool


def get_openai_client() -> AsyncOpenAI:
    """Get OpenAI client with API key from environment."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    # Debug: log first/last 4 chars of API key
    print(f"[DEBUG] Using API key: {api_key[:7]}...{api_key[-4:]}")
    return AsyncOpenAI(api_key=api_key)

# System prompt for the task management assistant
SYSTEM_PROMPT = """You are a helpful task management assistant. Help users manage their todo list.

When users want to:
- Add a task: Use add_task with the title (and optionally a description)
- View tasks: Use list_tasks (optionally filter by status: all, pending, completed)
- Complete a task: Use complete_task with the position number (1, 2, 3, etc.)
- Delete a task: Use delete_task with the position number
- Update a task: Use update_task with the position number and the new title/description

Always confirm actions with the task title. Be concise and friendly.
When listing tasks, the position number is shown before each task - users reference tasks by these numbers."""


async def process_chat_message(
    user_message: str,
    user_id: str,
    session: AsyncSession,
    conversation_history: list[dict[str, Any]] | None = None,
) -> tuple[str, list[dict[str, Any]]]:
    """Process a chat message and return the assistant's response.

    Args:
        user_message: The user's input message
        user_id: The authenticated user's ID
        session: Database session for task operations
        conversation_history: Previous messages for context

    Returns:
        Tuple of (assistant_response, updated_messages_for_storage)
    """
    # Get OpenAI client
    client = get_openai_client()

    # Build messages list
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Add conversation history if provided (last 20 messages for context)
    if conversation_history:
        messages.extend(conversation_history[-20:])

    # Add the new user message
    messages.append({"role": "user", "content": user_message})

    # Track messages to store
    messages_to_store = [{"role": "user", "content": user_message}]

    # Call OpenAI API with tools
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=TOOL_DEFINITIONS,
        tool_choice="auto",
        max_tokens=1000,
        timeout=30.0,
    )

    assistant_message = response.choices[0].message

    # Handle tool calls if present
    if assistant_message.tool_calls:
        # Add assistant message with tool calls
        tool_calls_data = [
            {
                "id": tc.id,
                "type": "function",
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments,
                },
            }
            for tc in assistant_message.tool_calls
        ]

        messages.append({
            "role": "assistant",
            "content": assistant_message.content or "",
            "tool_calls": tool_calls_data,
        })

        # Execute each tool call
        for tool_call in assistant_message.tool_calls:
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            # Execute the tool
            tool_result = await execute_tool(
                function_name,
                arguments,
                user_id,
                session,
            )

            # Add tool result to messages
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": tool_result,
            })

        # Get final response from the model
        final_response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=1000,
            timeout=30.0,
        )

        final_message = final_response.choices[0].message.content or ""

        # Store assistant response with tool calls info
        messages_to_store.append({
            "role": "assistant",
            "content": final_message,
            "tool_calls": json.dumps(tool_calls_data),
        })

        return final_message, messages_to_store

    # No tool calls - direct response
    assistant_content = assistant_message.content or ""
    messages_to_store.append({
        "role": "assistant",
        "content": assistant_content,
    })

    return assistant_content, messages_to_store
