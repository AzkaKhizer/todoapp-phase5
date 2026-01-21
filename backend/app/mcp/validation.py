"""Input validation for MCP tool operations."""


def validate_title(title: str | None) -> tuple[str | None, str | None]:
    """Validate task title.

    Returns (cleaned_title, error_message).
    If error, cleaned_title is None.
    """
    if title is None:
        return None, None  # Optional field, no validation needed

    title = title.strip()

    if not title:
        return None, "Title cannot be empty."

    if len(title) > 200:
        return None, "Title is too long. Please keep it under 200 characters."

    return title, None


def validate_position(
    position: int | None,
    task_count: int,
) -> tuple[int | None, str | None]:
    """Validate task position.

    Returns (position, error_message).
    If error, position is None.
    """
    if position is None:
        return None, "Please specify which task number."

    if position < 1:
        return None, "Position must be at least 1."

    if position > task_count:
        if task_count == 0:
            return None, "You have no tasks yet. Would you like to add one?"
        return None, f"Task #{position} not found. You have {task_count} tasks."

    return position, None


def validate_description(description: str | None) -> tuple[str | None, str | None]:
    """Validate task description.

    Returns (cleaned_description, error_message).
    If error, cleaned_description is None.
    """
    if description is None:
        return None, None  # Optional field

    description = description.strip()

    if len(description) > 2000:
        return None, "Description is too long. Please keep it under 2000 characters."

    return description, None
