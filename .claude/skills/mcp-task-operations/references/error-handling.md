# MCP Tool Error Handling

User-friendly error responses for task operations.

## Error Response Patterns

### Position Errors

```python
# Task not found by position
def task_not_found_error(position: int, total: int) -> str:
    if total == 0:
        return "You have no tasks yet. Would you like to add one?"
    return f"Task #{position} not found. You have {total} task(s). Try 'show my tasks' to see them."

# Invalid position type
def invalid_position_error() -> str:
    return "Please use a number to refer to tasks (e.g., 'complete task 1')."
```

### Validation Errors

```python
# Empty title
def empty_title_error() -> str:
    return "I need a title for the task. What would you like to call it?"

# No updates provided
def no_updates_error() -> str:
    return "No changes specified. What would you like to update?"

# Task already in desired state
def already_completed_error(title: str) -> str:
    return f"'{title}' is already marked as complete."
```

### System Errors

```python
# Generic error wrapper
def system_error() -> str:
    return "Something went wrong. Please try again."

# API/Database errors
def database_error() -> str:
    return "I couldn't save that change. Please try again in a moment."
```

## Error Handling in Executors

```python
async def execute_tool(
    tool_call: Any,
    user_id: str,
    session: AsyncSession
) -> str:
    """Execute tool with error handling."""
    try:
        name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)

        task_service = TaskService(session)

        # Route to appropriate executor
        if name == "add_task":
            return await execute_add_task(task_service, user_id, args)
        # ... other tools

    except json.JSONDecodeError:
        return "I couldn't understand that request. Could you rephrase?"
    except ValueError as e:
        return f"Invalid input: {str(e)}"
    except Exception as e:
        # Log the actual error for debugging
        logger.error(f"Tool execution error: {name} - {str(e)}")
        return "Something went wrong. Please try again."
```

## Logging for Debugging

```python
import logging

logger = logging.getLogger(__name__)

async def execute_tool(...) -> str:
    logger.info(f"Executing tool: {name} with args: {args} for user: {user_id}")

    try:
        result = await executor()
        logger.info(f"Tool {name} succeeded: {result[:100]}...")
        return result
    except Exception as e:
        logger.error(f"Tool {name} failed: {str(e)}", exc_info=True)
        return "Something went wrong. Please try again."
```

## Validation Helpers

```python
def validate_position(args: dict, tasks: list) -> tuple[bool, str]:
    """
    Validate position parameter.

    Returns:
        tuple: (is_valid, error_message)
    """
    position = args.get("position")

    if position is None:
        return False, "Please specify a task number."

    if not isinstance(position, int):
        return False, "Please use a number (1, 2, 3) to refer to tasks."

    if position < 1:
        return False, "Task numbers start at 1."

    if position > len(tasks):
        if len(tasks) == 0:
            return False, "You have no tasks yet."
        return False, f"Task #{position} not found. You have {len(tasks)} task(s)."

    return True, ""


def validate_title(args: dict) -> tuple[bool, str]:
    """
    Validate title parameter.

    Returns:
        tuple: (is_valid, error_message)
    """
    title = args.get("title", "").strip()

    if not title:
        return False, "I need a title for the task. What would you like to call it?"

    if len(title) > 200:
        return False, f"That title is too long ({len(title)} chars). Please keep it under 200 characters."

    return True, ""
```

## User-Friendly Messages Map

```python
ERROR_MESSAGES = {
    # Position errors
    "no_tasks": "You have no tasks yet. Would you like to add one?",
    "task_not_found": "Task #{position} not found. You have {total} task(s).",
    "invalid_position": "Please use a number (1, 2, 3) to refer to tasks.",

    # Validation errors
    "empty_title": "I need a title for the task. What would you like to call it?",
    "title_too_long": "That title is too long. Please keep it under 200 characters.",
    "no_updates": "No changes specified. What would you like to update?",

    # State errors
    "already_completed": "'{title}' is already marked as complete.",
    "already_pending": "'{title}' is already pending.",

    # System errors
    "unknown_tool": "I don't know how to do that.",
    "parse_error": "I couldn't understand that request. Could you rephrase?",
    "system_error": "Something went wrong. Please try again.",
}

def get_error_message(key: str, **kwargs) -> str:
    """Get formatted error message."""
    template = ERROR_MESSAGES.get(key, ERROR_MESSAGES["system_error"])
    return template.format(**kwargs)
```

## Recovery Suggestions

Always provide actionable next steps:

```python
def error_with_suggestion(error: str, suggestion: str) -> str:
    return f"{error} {suggestion}"

# Examples:
# "Task #5 not found. Try 'show my tasks' to see what's available."
# "I need a title. What would you like to call this task?"
# "That task is already complete. Want to see your pending tasks?"
```
