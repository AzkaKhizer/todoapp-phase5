# MCP Tool Executors

Implementation of tool execution handlers for task operations.

## Main Executor

```python
# backend/app/mcp/tools.py

import json
from typing import Any, Optional
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.task import Task
from app.services.task import TaskService


async def execute_tool(
    tool_call: Any,
    user_id: str,
    session: AsyncSession
) -> str:
    """
    Execute an MCP tool call and return the result as a string.

    Args:
        tool_call: OpenAI tool call object with function.name and function.arguments
        user_id: Authenticated user's ID for scoping operations
        session: Database session for task operations

    Returns:
        String result to be sent back to the AI for response generation
    """
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)

    task_service = TaskService(session)

    executors = {
        "add_task": lambda: execute_add_task(task_service, user_id, args),
        "list_tasks": lambda: execute_list_tasks(task_service, user_id, args),
        "complete_task": lambda: execute_complete_task(task_service, user_id, args),
        "delete_task": lambda: execute_delete_task(task_service, user_id, args),
        "update_task": lambda: execute_update_task(task_service, user_id, args),
    }

    executor = executors.get(name)
    if not executor:
        return f"Unknown tool: {name}"

    try:
        return await executor()
    except Exception as e:
        return f"Error: {str(e)}"
```

## Individual Tool Executors

### add_task

```python
async def execute_add_task(
    service: TaskService,
    user_id: str,
    args: dict
) -> str:
    """Create a new task for the user."""
    title = args.get("title", "").strip()
    if not title:
        return "Error: Task title is required."

    description = args.get("description")

    task = await service.create_task(
        user_id=user_id,
        title=title,
        description=description
    )

    return f"Created task: '{task.title}'"
```

### list_tasks

```python
async def execute_list_tasks(
    service: TaskService,
    user_id: str,
    args: dict
) -> str:
    """List all tasks with position numbers."""
    filter_status = args.get("filter", "all")

    tasks = await service.get_user_tasks(user_id)

    # Apply filter
    if filter_status == "pending":
        tasks = [t for t in tasks if not t.completed]
    elif filter_status == "completed":
        tasks = [t for t in tasks if t.completed]

    if not tasks:
        if filter_status == "all":
            return "You have no tasks. Would you like to add one?"
        return f"No {filter_status} tasks found."

    lines = []
    for i, task in enumerate(tasks, 1):
        status = "completed" if task.completed else "pending"
        desc = f" - {task.description}" if task.description else ""
        lines.append(f"{i}. {task.title} ({status}){desc}")

    header = f"Your tasks ({filter_status}):" if filter_status != "all" else "Your tasks:"
    return header + "\n" + "\n".join(lines)
```

### complete_task

```python
async def execute_complete_task(
    service: TaskService,
    user_id: str,
    args: dict
) -> str:
    """Mark a task as complete by position number."""
    position = args.get("position")
    if not position or not isinstance(position, int):
        return "Error: Please specify a task number (e.g., 'complete task 1')."

    tasks = await service.get_user_tasks(user_id)

    if position < 1 or position > len(tasks):
        if len(tasks) == 0:
            return "You have no tasks to complete."
        return f"Task #{position} not found. You have {len(tasks)} task(s). Try 'show my tasks' to see them."

    task = tasks[position - 1]

    if task.completed:
        return f"'{task.title}' is already marked as complete."

    await service.update_task(task.id, user_id, completed=True)
    return f"Marked '{task.title}' as complete."
```

### delete_task

```python
async def execute_delete_task(
    service: TaskService,
    user_id: str,
    args: dict
) -> str:
    """Delete a task by position number."""
    position = args.get("position")
    if not position or not isinstance(position, int):
        return "Error: Please specify a task number (e.g., 'delete task 2')."

    tasks = await service.get_user_tasks(user_id)

    if position < 1 or position > len(tasks):
        if len(tasks) == 0:
            return "You have no tasks to delete."
        return f"Task #{position} not found. You have {len(tasks)} task(s)."

    task = tasks[position - 1]
    title = task.title  # Store before deletion

    await service.delete_task(task.id, user_id)
    return f"Deleted '{title}'."
```

### update_task

```python
async def execute_update_task(
    service: TaskService,
    user_id: str,
    args: dict
) -> str:
    """Update a task's title or description."""
    position = args.get("position")
    if not position or not isinstance(position, int):
        return "Error: Please specify a task number (e.g., 'update task 1')."

    tasks = await service.get_user_tasks(user_id)

    if position < 1 or position > len(tasks):
        if len(tasks) == 0:
            return "You have no tasks to update."
        return f"Task #{position} not found. You have {len(tasks)} task(s)."

    task = tasks[position - 1]
    old_title = task.title

    # Collect updates
    updates = {}
    if "title" in args and args["title"]:
        updates["title"] = args["title"].strip()
    if "description" in args:
        updates["description"] = args["description"]

    if not updates:
        return "No changes specified. What would you like to update?"

    await service.update_task(task.id, user_id, **updates)

    new_title = updates.get("title", old_title)
    if "title" in updates and "description" in updates:
        return f"Updated '{old_title}' -> '{new_title}' with new description."
    elif "title" in updates:
        return f"Renamed '{old_title}' to '{new_title}'."
    else:
        return f"Updated description for '{old_title}'."
```

## Helper: Get Task by Position

```python
async def get_task_by_position(
    service: TaskService,
    user_id: str,
    position: int
) -> tuple[Optional[Task], Optional[str]]:
    """
    Get a task by position number with error handling.

    Returns:
        tuple: (task, error_message) - task is None if error
    """
    tasks = await service.get_user_tasks(user_id)

    if not tasks:
        return None, "You have no tasks."

    if position < 1 or position > len(tasks):
        return None, f"Task #{position} not found. You have {len(tasks)} task(s)."

    return tasks[position - 1], None
```

## Complete File

```python
# backend/app/mcp/tools.py
"""
MCP Tool definitions and executors for task management.
"""

import json
from typing import Any, Optional
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.task import Task
from app.services.task import TaskService

# Tool definitions (see tool-definitions.md)
TOOL_DEFINITIONS = [...]  # As defined in tool-definitions.md


async def execute_tool(
    tool_call: Any,
    user_id: str,
    session: AsyncSession
) -> str:
    """Execute an MCP tool call."""
    # Implementation as shown above


async def execute_add_task(...) -> str:
    # Implementation as shown above


async def execute_list_tasks(...) -> str:
    # Implementation as shown above


async def execute_complete_task(...) -> str:
    # Implementation as shown above


async def execute_delete_task(...) -> str:
    # Implementation as shown above


async def execute_update_task(...) -> str:
    # Implementation as shown above
```
