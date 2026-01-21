---
name: mcp-task-operations
description: |
  MCP server implementation for task management operations. Provides OpenAI function calling tools that interface with FastAPI backend and Neon PostgreSQL. Use when implementing:
  (1) MCP tool definitions for add_task, update_task, delete_task, complete_task, list_tasks
  (2) Tool execution handlers with database operations
  (3) Position-based task references for natural language interaction
  (4) User-scoped task operations with authentication
---

# MCP Task Operations

Implement MCP (Model Context Protocol) tools for task management that integrate with OpenAI's function calling API.

## Architecture

```
OpenAI Agent -> MCP Tool Definitions -> Tool Executor -> TaskService -> Neon PostgreSQL
```

## File Structure

```
backend/app/
├── mcp/
│   ├── __init__.py           # Package init, exports tools
│   └── tools.py              # Tool definitions and executors
├── services/
│   └── task.py               # TaskService (existing)
└── models/
    └── task.py               # Task model (existing)
```

## Quick Implementation

### 1. Create MCP Package

```python
# backend/app/mcp/__init__.py
from app.mcp.tools import TOOL_DEFINITIONS, execute_tool

__all__ = ["TOOL_DEFINITIONS", "execute_tool"]
```

### 2. Define Tools

```python
# backend/app/mcp/tools.py
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Create a new task",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"}
                },
                "required": ["title"]
            }
        }
    },
    # ... other tools
]
```

### 3. Execute Tools

```python
async def execute_tool(tool_call, user_id: str, session: AsyncSession) -> str:
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)

    if name == "add_task":
        task = await task_service.create_task(user_id, args["title"])
        return f"Created: {task.title}"
```

## Key Patterns

### Position-Based References

Users reference tasks by position (1, 2, 3) not UUID:

```python
tasks = await service.get_user_tasks(user_id)
task = tasks[position - 1]  # Convert 1-indexed to 0-indexed
```

### User Isolation

All operations are scoped to the authenticated user:

```python
async def get_user_tasks(user_id: str) -> list[Task]:
    return await session.exec(
        select(Task).where(Task.user_id == user_id)
    )
```

## Reference Files

- **Tool definitions**: See `references/tool-definitions.md` for complete OpenAI function schemas
- **Tool executors**: See `references/tool-executors.md` for implementation of each tool
- **Error handling**: See `references/error-handling.md` for user-friendly error responses
