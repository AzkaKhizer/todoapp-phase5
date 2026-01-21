# MCP Tool Definitions

Complete OpenAI function calling tool definitions for task management.

## Full Tool Definitions

```python
# backend/app/mcp/tools.py

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Create a new task for the user. Use when the user wants to add, create, or make a new task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The title or name of the task (required)"
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
            "description": "List all tasks for the user. Use when the user wants to see, view, show, or check their tasks.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filter": {
                        "type": "string",
                        "enum": ["all", "pending", "completed"],
                        "description": "Filter tasks by status. Defaults to 'all'."
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "complete_task",
            "description": "Mark a task as complete by its position number (1, 2, 3, etc). Use when the user wants to mark, complete, finish, done, or check off a task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "position": {
                        "type": "integer",
                        "description": "The position number of the task (1 for first, 2 for second, etc)"
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
            "description": "Delete/remove a task by its position number. Use when the user wants to delete, remove, or get rid of a task.",
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
            "description": "Update a task's title or description. Use when the user wants to change, edit, update, rename, or modify a task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "position": {
                        "type": "integer",
                        "description": "The position number of the task to update"
                    },
                    "title": {
                        "type": "string",
                        "description": "New title for the task"
                    },
                    "description": {
                        "type": "string",
                        "description": "New description for the task"
                    }
                },
                "required": ["position"]
            }
        }
    }
]
```

## Tool Parameter Reference

| Tool | Required Params | Optional Params | Returns |
|------|----------------|-----------------|---------|
| `add_task` | `title` | `description` | Created task confirmation |
| `list_tasks` | - | `filter` (all/pending/completed) | Numbered task list |
| `complete_task` | `position` | - | Completion confirmation |
| `delete_task` | `position` | - | Deletion confirmation |
| `update_task` | `position` | `title`, `description` | Update confirmation |

## Intent Mapping

Map natural language to tools:

| User Says | Tool | Parameters |
|-----------|------|------------|
| "Add buy milk" | `add_task` | `{"title": "buy milk"}` |
| "Create a task for meeting" | `add_task` | `{"title": "meeting"}` |
| "Show my tasks" | `list_tasks` | `{}` |
| "What's on my list?" | `list_tasks` | `{}` |
| "Show pending tasks" | `list_tasks` | `{"filter": "pending"}` |
| "Mark 1 as done" | `complete_task` | `{"position": 1}` |
| "Complete the first task" | `complete_task` | `{"position": 1}` |
| "Delete task 2" | `delete_task` | `{"position": 2}` |
| "Remove the second one" | `delete_task` | `{"position": 2}` |
| "Change task 1 to grocery shopping" | `update_task` | `{"position": 1, "title": "grocery shopping"}` |
| "Rename task 3" | `update_task` | `{"position": 3, ...}` |

## Exporting Tools

```python
# backend/app/mcp/__init__.py
from app.mcp.tools import TOOL_DEFINITIONS, execute_tool

__all__ = ["TOOL_DEFINITIONS", "execute_tool"]
```
