# MCP Tools Implementation

## Tool Definitions

Define OpenAI function calling tools for task operations.

```python
# backend/app/mcp/tools.py
import json
from typing import Any
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.task import Task
from app.services.task import TaskService

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Create a new task for the user. Use this when the user wants to add, create, or make a new task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The title or name of the task"
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional detailed description of the task"
                    }
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "List all tasks for the user. Use this when the user wants to see, view, or show their tasks.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "complete_task",
            "description": "Mark a task as complete by its position number (1, 2, 3, etc). Use this when the user wants to mark, complete, finish, or check off a task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "position": {
                        "type": "integer",
                        "description": "The position number of the task (1 for first task, 2 for second, etc)"
                    }
                },
                "required": ["position"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Delete a task by its position number (1, 2, 3, etc). Use this when the user wants to remove, delete, or get rid of a task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "position": {
                        "type": "integer",
                        "description": "The position number of the task to delete"
                    }
                },
                "required": ["position"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Update a task's title or description. Use this when the user wants to change, edit, update, or rename a task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "position": {
                        "type": "integer",
                        "description": "The position number of the task to update"
                    },
                    "title": {
                        "type": "string",
                        "description": "New title for the task (optional)"
                    },
                    "description": {
                        "type": "string",
                        "description": "New description for the task (optional)"
                    }
                },
                "required": ["position"]
            }
        }
    }
]
```

## Tool Execution

```python
# backend/app/mcp/tools.py (continued)

async def execute_tool(
    tool_call: Any,
    user_id: str,
    session: AsyncSession
) -> str:
    """Execute a tool call and return the result as a string."""
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)

    task_service = TaskService(session)

    try:
        if name == "add_task":
            return await execute_add_task(task_service, user_id, args)
        elif name == "list_tasks":
            return await execute_list_tasks(task_service, user_id)
        elif name == "complete_task":
            return await execute_complete_task(task_service, user_id, args)
        elif name == "delete_task":
            return await execute_delete_task(task_service, user_id, args)
        elif name == "update_task":
            return await execute_update_task(task_service, user_id, args)
        else:
            return f"Unknown tool: {name}"
    except Exception as e:
        return f"Error executing {name}: {str(e)}"


async def execute_add_task(
    service: TaskService,
    user_id: str,
    args: dict
) -> str:
    """Create a new task."""
    task = await service.create_task(
        user_id=user_id,
        title=args["title"],
        description=args.get("description")
    )
    return f"Created task: {task.title}"


async def execute_list_tasks(
    service: TaskService,
    user_id: str
) -> str:
    """List all tasks with position numbers."""
    tasks = await service.get_user_tasks(user_id)

    if not tasks:
        return "No tasks found. The user has an empty task list."

    lines = []
    for i, task in enumerate(tasks, 1):
        status = "completed" if task.completed else "pending"
        lines.append(f"{i}. {task.title} ({status})")

    return "Tasks:\n" + "\n".join(lines)


async def execute_complete_task(
    service: TaskService,
    user_id: str,
    args: dict
) -> str:
    """Mark a task as complete by position."""
    position = args["position"]
    tasks = await service.get_user_tasks(user_id)

    if position < 1 or position > len(tasks):
        return f"Task #{position} not found. You have {len(tasks)} tasks."

    task = tasks[position - 1]
    await service.update_task(task.id, user_id, completed=True)
    return f"Marked '{task.title}' as complete."


async def execute_delete_task(
    service: TaskService,
    user_id: str,
    args: dict
) -> str:
    """Delete a task by position."""
    position = args["position"]
    tasks = await service.get_user_tasks(user_id)

    if position < 1 or position > len(tasks):
        return f"Task #{position} not found. You have {len(tasks)} tasks."

    task = tasks[position - 1]
    await service.delete_task(task.id, user_id)
    return f"Deleted '{task.title}'."


async def execute_update_task(
    service: TaskService,
    user_id: str,
    args: dict
) -> str:
    """Update a task's title or description."""
    position = args["position"]
    tasks = await service.get_user_tasks(user_id)

    if position < 1 or position > len(tasks):
        return f"Task #{position} not found. You have {len(tasks)} tasks."

    task = tasks[position - 1]
    updates = {}
    if "title" in args:
        updates["title"] = args["title"]
    if "description" in args:
        updates["description"] = args["description"]

    if not updates:
        return "No updates provided."

    await service.update_task(task.id, user_id, **updates)
    return f"Updated task: {args.get('title', task.title)}"
```

## Error Handling Patterns

```python
# User-friendly error messages
ERROR_MESSAGES = {
    "task_not_found": "I couldn't find that task. Try saying 'show my tasks' to see what's available.",
    "invalid_position": "Please use a number like 1, 2, or 3 to refer to tasks.",
    "empty_title": "I need a title for the task. What would you like to call it?",
    "api_error": "Something went wrong. Please try again.",
}
```

## Agent System Prompt

```python
SYSTEM_PROMPT = """You are a helpful task management assistant. Help users manage their todo list through natural conversation.

You have access to these tools:
- add_task: Create new tasks
- list_tasks: Show all tasks
- complete_task: Mark tasks as done
- delete_task: Remove tasks
- update_task: Change task details

Guidelines:
1. When users mention task numbers, use position-based references (1, 2, 3)
2. Always confirm actions: "I've added 'buy groceries' to your list"
3. If a task isn't found, suggest listing tasks first
4. Be conversational but concise
5. If unsure what the user wants, ask for clarification

Example interactions:
- "Add buy milk" -> Use add_task with title "buy milk"
- "Show my tasks" -> Use list_tasks
- "Done with 1" -> Use complete_task with position 1
- "Delete the second task" -> Use delete_task with position 2
- "Change task 1 to buy organic milk" -> Use update_task with position 1"""
```
