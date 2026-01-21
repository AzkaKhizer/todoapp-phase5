"""MCP tool definitions and executors for task management."""

import json
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskPatch
from app.services import task as task_service


# OpenAI function calling tool definitions
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Create a new task for the user",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The title of the task (required)",
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional description for the task",
                    },
                },
                "required": ["title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "List all tasks for the user with position numbers",
            "parameters": {
                "type": "object",
                "properties": {
                    "filter": {
                        "type": "string",
                        "enum": ["all", "pending", "completed"],
                        "description": "Filter tasks by status (default: all)",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "complete_task",
            "description": "Mark a task as complete by its position number",
            "parameters": {
                "type": "object",
                "properties": {
                    "position": {
                        "type": "integer",
                        "description": "The position number of the task (1, 2, 3, etc.)",
                    },
                },
                "required": ["position"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Delete a task by its position number",
            "parameters": {
                "type": "object",
                "properties": {
                    "position": {
                        "type": "integer",
                        "description": "The position number of the task (1, 2, 3, etc.)",
                    },
                },
                "required": ["position"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Update a task's title or description by its position number",
            "parameters": {
                "type": "object",
                "properties": {
                    "position": {
                        "type": "integer",
                        "description": "The position number of the task (1, 2, 3, etc.)",
                    },
                    "title": {
                        "type": "string",
                        "description": "New title for the task (optional)",
                    },
                    "description": {
                        "type": "string",
                        "description": "New description for the task (optional)",
                    },
                },
                "required": ["position"],
            },
        },
    },
]


async def get_task_by_position(
    session: AsyncSession,
    user_id: str,
    position: int,
) -> tuple[Task | None, str | None]:
    """Get task by 1-indexed position number.

    Returns (task, error_message). If error, task is None.
    """
    tasks, total = await task_service.get_tasks(session, user_id, limit=1000)

    if position < 1:
        return None, f"Invalid position. Position must be at least 1."

    if position > len(tasks):
        if len(tasks) == 0:
            return None, "You have no tasks yet. Would you like to add one?"
        return None, f"Task #{position} not found. You have {len(tasks)} tasks."

    return tasks[position - 1], None


async def execute_tool(
    tool_name: str,
    arguments: dict[str, Any],
    user_id: str,
    session: AsyncSession,
) -> str:
    """Execute an MCP tool and return a string result.

    All tools return user-friendly string messages for the AI to relay.
    """
    try:
        if tool_name == "add_task":
            return await execute_add_task(session, user_id, arguments)
        elif tool_name == "list_tasks":
            return await execute_list_tasks(session, user_id, arguments)
        elif tool_name == "complete_task":
            return await execute_complete_task(session, user_id, arguments)
        elif tool_name == "delete_task":
            return await execute_delete_task(session, user_id, arguments)
        elif tool_name == "update_task":
            return await execute_update_task(session, user_id, arguments)
        else:
            return f"Unknown tool: {tool_name}"
    except Exception as e:
        return f"An error occurred: {str(e)}"


async def execute_add_task(
    session: AsyncSession,
    user_id: str,
    arguments: dict[str, Any],
) -> str:
    """Execute add_task tool."""
    title = arguments.get("title", "").strip()
    description = arguments.get("description", "").strip()

    if not title:
        return "I need a title for the task. What would you like to call it?"

    if len(title) > 200:
        return "The title is too long. Please keep it under 200 characters."

    task_data = TaskCreate(title=title, description=description)
    task = await task_service.create_task(session, user_id, task_data)

    return f"Created task: '{task.title}'"


async def execute_list_tasks(
    session: AsyncSession,
    user_id: str,
    arguments: dict[str, Any],
) -> str:
    """Execute list_tasks tool."""
    filter_status = arguments.get("filter", "all")

    tasks, _ = await task_service.get_tasks(session, user_id, limit=1000)

    # Apply filter
    if filter_status == "pending":
        tasks = [t for t in tasks if not t.is_complete]
    elif filter_status == "completed":
        tasks = [t for t in tasks if t.is_complete]

    if not tasks:
        if filter_status == "pending":
            return "You have no pending tasks."
        elif filter_status == "completed":
            return "You have no completed tasks."
        return "You have no tasks yet. Would you like to add one?"

    # Format with position numbers
    lines = []
    for i, task in enumerate(tasks, 1):
        status = "completed" if task.is_complete else "pending"
        lines.append(f"{i}. {task.title} ({status})")

    return "Your tasks:\n" + "\n".join(lines)


async def execute_complete_task(
    session: AsyncSession,
    user_id: str,
    arguments: dict[str, Any],
) -> str:
    """Execute complete_task tool."""
    position = arguments.get("position")

    if position is None:
        return "Please specify which task number to complete."

    task, error = await get_task_by_position(session, user_id, position)
    if error:
        return error

    if task.is_complete:
        return f"'{task.title}' is already marked as complete."

    patch_data = TaskPatch(is_complete=True)
    await task_service.patch_task(session, task.id, user_id, patch_data)

    return f"Marked '{task.title}' as complete."


async def execute_delete_task(
    session: AsyncSession,
    user_id: str,
    arguments: dict[str, Any],
) -> str:
    """Execute delete_task tool."""
    position = arguments.get("position")

    if position is None:
        return "Please specify which task number to delete."

    task, error = await get_task_by_position(session, user_id, position)
    if error:
        return error

    title = task.title
    await task_service.delete_task(session, task.id, user_id)

    return f"Deleted task: '{title}'"


async def execute_update_task(
    session: AsyncSession,
    user_id: str,
    arguments: dict[str, Any],
) -> str:
    """Execute update_task tool."""
    position = arguments.get("position")
    new_title = arguments.get("title")
    new_description = arguments.get("description")

    if position is None:
        return "Please specify which task number to update."

    if new_title is None and new_description is None:
        return "What would you like to change? You can update the title or description."

    task, error = await get_task_by_position(session, user_id, position)
    if error:
        return error

    # Validate title length
    if new_title is not None and len(new_title.strip()) > 200:
        return "The title is too long. Please keep it under 200 characters."

    patch_data = TaskPatch(
        title=new_title.strip() if new_title else None,
        description=new_description.strip() if new_description else None,
    )
    updated_task = await task_service.patch_task(session, task.id, user_id, patch_data)

    changes = []
    if new_title:
        changes.append(f"title to '{updated_task.title}'")
    if new_description:
        changes.append("description")

    return f"Updated {' and '.join(changes)} for task #{position}."
