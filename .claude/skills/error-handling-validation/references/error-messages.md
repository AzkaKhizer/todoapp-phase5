# Error Message Templates

User-friendly error messages for all task operations.

## Message Registry

```python
# backend/app/mcp/errors.py
from typing import Any, Dict

class ErrorMessages:
    """Centralized error message templates."""

    # === Input Validation Errors ===

    EMPTY_TITLE = "I need a title for the task. What would you like to call it?"

    TITLE_TOO_LONG = "That title is too long ({length} characters). Please keep it under 200 characters."

    DESCRIPTION_TOO_LONG = "That description is too long ({length} characters). Please keep it under 1000 characters."

    INVALID_POSITION_TYPE = "Please use a number (1, 2, 3) to refer to tasks."

    POSITION_TOO_LOW = "Task numbers start at 1."

    INVALID_FILTER = "Unknown filter '{filter}'. Use: all, pending, or completed."

    NO_UPDATES_PROVIDED = "No changes specified. What would you like to update? You can change the title or description."

    # === Task Not Found Errors ===

    NO_TASKS = "You have no tasks yet. Would you like to add one?"

    NO_TASKS_FOR_OPERATION = "You have no tasks to {operation}. Would you like to add one?"

    TASK_NOT_FOUND = "Task #{position} not found. You have {total} task(s). Try 'show my tasks' to see the list."

    NO_FILTERED_TASKS = "No {filter} tasks found."

    # === State Errors ===

    ALREADY_COMPLETED = "'{title}' is already marked as complete."

    ALREADY_PENDING = "'{title}' is not completed yet."

    # === System Errors ===

    UNKNOWN_TOOL = "I don't know how to do that."

    PARSE_ERROR = "I couldn't understand that request. Could you rephrase?"

    DATABASE_ERROR = "I couldn't save that change. Please try again in a moment."

    API_ERROR = "Something went wrong with the AI service. Please try again."

    TIMEOUT_ERROR = "That took too long. Please try again."

    SYSTEM_ERROR = "Something went wrong. Please try again."

    @classmethod
    def format(cls, template: str, **kwargs) -> str:
        """Format a template with provided values."""
        try:
            return template.format(**kwargs)
        except KeyError:
            return template


def get_error_message(error_type: str, **context) -> str:
    """
    Get formatted error message by type.

    Args:
        error_type: Key for the error message
        **context: Values to format into the message

    Returns:
        Formatted error message string
    """
    messages = {
        # Input validation
        "empty_title": ErrorMessages.EMPTY_TITLE,
        "title_too_long": ErrorMessages.TITLE_TOO_LONG,
        "description_too_long": ErrorMessages.DESCRIPTION_TOO_LONG,
        "invalid_position": ErrorMessages.INVALID_POSITION_TYPE,
        "position_too_low": ErrorMessages.POSITION_TOO_LOW,
        "invalid_filter": ErrorMessages.INVALID_FILTER,
        "no_updates": ErrorMessages.NO_UPDATES_PROVIDED,

        # Task not found
        "no_tasks": ErrorMessages.NO_TASKS,
        "no_tasks_operation": ErrorMessages.NO_TASKS_FOR_OPERATION,
        "task_not_found": ErrorMessages.TASK_NOT_FOUND,
        "no_filtered_tasks": ErrorMessages.NO_FILTERED_TASKS,

        # State errors
        "already_completed": ErrorMessages.ALREADY_COMPLETED,
        "already_pending": ErrorMessages.ALREADY_PENDING,

        # System errors
        "unknown_tool": ErrorMessages.UNKNOWN_TOOL,
        "parse_error": ErrorMessages.PARSE_ERROR,
        "database_error": ErrorMessages.DATABASE_ERROR,
        "api_error": ErrorMessages.API_ERROR,
        "timeout_error": ErrorMessages.TIMEOUT_ERROR,
        "system_error": ErrorMessages.SYSTEM_ERROR,
    }

    template = messages.get(error_type, ErrorMessages.SYSTEM_ERROR)
    return ErrorMessages.format(template, **context)
```

## Usage Examples

```python
from app.mcp.errors import get_error_message

# Empty title
msg = get_error_message("empty_title")
# "I need a title for the task. What would you like to call it?"

# Title too long
msg = get_error_message("title_too_long", length=250)
# "That title is too long (250 characters). Please keep it under 200 characters."

# Task not found
msg = get_error_message("task_not_found", position=5, total=3)
# "Task #5 not found. You have 3 task(s). Try 'show my tasks' to see the list."

# No tasks for operation
msg = get_error_message("no_tasks_operation", operation="delete")
# "You have no tasks to delete. Would you like to add one?"

# Already completed
msg = get_error_message("already_completed", title="Buy groceries")
# "'Buy groceries' is already marked as complete."

# No filtered tasks
msg = get_error_message("no_filtered_tasks", filter="completed")
# "No completed tasks found."
```

## Message Design Principles

### 1. Be Specific

```python
# Bad - vague
"Invalid input"

# Good - specific
"Task #5 not found. You have 3 task(s)."
```

### 2. Suggest Next Action

```python
# Bad - no guidance
"No tasks found."

# Good - actionable
"You have no tasks yet. Would you like to add one?"
```

### 3. Use Natural Language

```python
# Bad - technical
"ValidationError: position must be integer"

# Good - natural
"Please use a number (1, 2, 3) to refer to tasks."
```

### 4. Confirm Understanding

```python
# Bad - assuming
"Task deleted."

# Good - confirming
"Deleted 'Buy groceries'."
```

### 5. Handle Edge Cases Gracefully

```python
# Singular/plural handling
if total == 1:
    return f"Task #{position} not found. You have 1 task."
else:
    return f"Task #{position} not found. You have {total} tasks."
```

## Error Categories

| Category | Examples | Tone |
|----------|----------|------|
| Input Validation | Empty title, too long | Helpful, instructive |
| Not Found | Task #5 not found | Informative, suggest alternatives |
| State | Already completed | Neutral, factual |
| System | Database error | Apologetic, retry suggestion |

## Internationalization Ready

```python
# For future i18n support
ERROR_MESSAGES = {
    "en": {
        "empty_title": "I need a title for the task...",
    },
    "es": {
        "empty_title": "Necesito un título para la tarea...",
    }
}

def get_localized_error(error_type: str, locale: str = "en", **context) -> str:
    messages = ERROR_MESSAGES.get(locale, ERROR_MESSAGES["en"])
    template = messages.get(error_type, "Something went wrong.")
    return template.format(**context)
```
