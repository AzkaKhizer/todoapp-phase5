# Input Validation Functions

Complete validation functions for task operations.

## Validation Module

```python
# backend/app/mcp/validation.py
from typing import Any, Optional, Tuple, List
from app.models.task import Task


class ValidationResult:
    """Result of a validation check."""

    def __init__(self, is_valid: bool, error: str = "", value: Any = None):
        self.is_valid = is_valid
        self.error = error
        self.value = value  # Cleaned/normalized value if valid

    @property
    def ok(self) -> bool:
        return self.is_valid


def validate_title(title: Any) -> ValidationResult:
    """
    Validate task title.

    Rules:
    - Required (not None, not empty)
    - Max 200 characters
    - Stripped of whitespace

    Returns:
        ValidationResult with cleaned title or error message
    """
    if title is None:
        return ValidationResult(
            False,
            "I need a title for the task. What would you like to call it?"
        )

    if not isinstance(title, str):
        return ValidationResult(
            False,
            "Task title must be text."
        )

    cleaned = title.strip()

    if not cleaned:
        return ValidationResult(
            False,
            "I need a title for the task. What would you like to call it?"
        )

    if len(cleaned) > 200:
        return ValidationResult(
            False,
            f"That title is too long ({len(cleaned)} characters). Please keep it under 200 characters."
        )

    return ValidationResult(True, value=cleaned)


def validate_description(description: Any) -> ValidationResult:
    """
    Validate task description (optional).

    Rules:
    - Optional (None is valid)
    - Max 1000 characters if provided

    Returns:
        ValidationResult with cleaned description or error message
    """
    if description is None:
        return ValidationResult(True, value=None)

    if not isinstance(description, str):
        return ValidationResult(
            False,
            "Task description must be text."
        )

    cleaned = description.strip()

    if not cleaned:
        return ValidationResult(True, value=None)

    if len(cleaned) > 1000:
        return ValidationResult(
            False,
            f"That description is too long ({len(cleaned)} characters). Please keep it under 1000 characters."
        )

    return ValidationResult(True, value=cleaned)


def validate_position(
    position: Any,
    tasks: List[Task],
    operation: str = "access"
) -> ValidationResult:
    """
    Validate task position number.

    Rules:
    - Required (not None)
    - Must be an integer
    - Must be >= 1
    - Must be <= len(tasks)

    Args:
        position: The position to validate
        tasks: List of user's tasks
        operation: What operation is being performed (for error messages)

    Returns:
        ValidationResult with task at position or error message
    """
    if position is None:
        return ValidationResult(
            False,
            f"Please specify a task number to {operation} (e.g., '{operation} task 1')."
        )

    if not isinstance(position, int):
        return ValidationResult(
            False,
            "Please use a number (1, 2, 3) to refer to tasks."
        )

    if len(tasks) == 0:
        return ValidationResult(
            False,
            f"You have no tasks to {operation}. Would you like to add one?"
        )

    if position < 1:
        return ValidationResult(
            False,
            "Task numbers start at 1."
        )

    if position > len(tasks):
        return ValidationResult(
            False,
            f"Task #{position} not found. You have {len(tasks)} task(s). "
            "Try 'show my tasks' to see the list."
        )

    # Return the task at that position
    return ValidationResult(True, value=tasks[position - 1])


def validate_filter(filter_value: Any) -> ValidationResult:
    """
    Validate task filter parameter.

    Rules:
    - Optional (None defaults to "all")
    - Must be one of: all, pending, completed

    Returns:
        ValidationResult with normalized filter value
    """
    valid_filters = {"all", "pending", "completed"}

    if filter_value is None:
        return ValidationResult(True, value="all")

    if not isinstance(filter_value, str):
        return ValidationResult(
            False,
            f"Filter must be one of: {', '.join(valid_filters)}"
        )

    normalized = filter_value.lower().strip()

    if normalized not in valid_filters:
        return ValidationResult(
            False,
            f"Unknown filter '{filter_value}'. Use: {', '.join(valid_filters)}"
        )

    return ValidationResult(True, value=normalized)


def validate_update_args(args: dict) -> ValidationResult:
    """
    Validate update operation has at least one field to update.

    Rules:
    - Must have at least one of: title, description
    - Individual fields validated separately

    Returns:
        ValidationResult with cleaned update dict
    """
    updates = {}

    if "title" in args and args["title"]:
        title_result = validate_title(args["title"])
        if not title_result.ok:
            return title_result
        updates["title"] = title_result.value

    if "description" in args:
        desc_result = validate_description(args["description"])
        if not desc_result.ok:
            return desc_result
        updates["description"] = desc_result.value

    if not updates:
        return ValidationResult(
            False,
            "No changes specified. What would you like to update? "
            "You can change the title or description."
        )

    return ValidationResult(True, value=updates)
```

## Using Validation in Tool Executors

```python
# backend/app/mcp/tools.py
from app.mcp.validation import (
    validate_title,
    validate_position,
    validate_description,
    validate_filter,
    validate_update_args,
)


async def execute_add_task(service, user_id: str, args: dict) -> str:
    # Validate title
    title_result = validate_title(args.get("title"))
    if not title_result.ok:
        return title_result.error

    # Validate optional description
    desc_result = validate_description(args.get("description"))
    if not desc_result.ok:
        return desc_result.error

    # Create task with validated values
    task = await service.create_task(
        user_id=user_id,
        title=title_result.value,
        description=desc_result.value
    )

    return f"Created task: '{task.title}'"


async def execute_complete_task(service, user_id: str, args: dict) -> str:
    tasks = await service.get_user_tasks(user_id)

    # Validate position
    pos_result = validate_position(args.get("position"), tasks, "complete")
    if not pos_result.ok:
        return pos_result.error

    task = pos_result.value

    # Check if already completed
    if task.completed:
        return f"'{task.title}' is already marked as complete."

    await service.update_task(task.id, user_id, completed=True)
    return f"Marked '{task.title}' as complete."


async def execute_list_tasks(service, user_id: str, args: dict) -> str:
    # Validate filter
    filter_result = validate_filter(args.get("filter"))
    if not filter_result.ok:
        return filter_result.error

    tasks = await service.get_user_tasks(user_id)

    # Apply filter
    filter_value = filter_result.value
    if filter_value == "pending":
        tasks = [t for t in tasks if not t.completed]
    elif filter_value == "completed":
        tasks = [t for t in tasks if t.completed]

    if not tasks:
        if filter_value == "all":
            return "You have no tasks yet. Would you like to add one?"
        return f"No {filter_value} tasks found."

    # Format task list
    lines = []
    for i, task in enumerate(tasks, 1):
        status = "completed" if task.completed else "pending"
        lines.append(f"{i}. {task.title} ({status})")

    return "\n".join(lines)


async def execute_update_task(service, user_id: str, args: dict) -> str:
    tasks = await service.get_user_tasks(user_id)

    # Validate position
    pos_result = validate_position(args.get("position"), tasks, "update")
    if not pos_result.ok:
        return pos_result.error

    task = pos_result.value

    # Validate update fields
    update_result = validate_update_args(args)
    if not update_result.ok:
        return update_result.error

    updates = update_result.value
    old_title = task.title

    await service.update_task(task.id, user_id, **updates)

    new_title = updates.get("title", old_title)
    if "title" in updates:
        return f"Renamed '{old_title}' to '{new_title}'."
    else:
        return f"Updated description for '{old_title}'."
```

## Validation Summary

| Field | Required | Max Length | Default |
|-------|----------|------------|---------|
| title | Yes | 200 chars | - |
| description | No | 1000 chars | None |
| position | Yes* | - | - |
| filter | No | - | "all" |

*Required for complete, delete, update operations
