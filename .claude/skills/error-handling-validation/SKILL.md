---
name: error-handling-validation
description: |
  Error handling and input validation for Todo AI Chatbot task operations. Use when implementing:
  (1) Input validation for task title, position, and description
  (2) User-friendly error messages for MCP tool operations
  (3) Edge case handling (empty lists, non-existent tasks, duplicates)
  (4) Graceful degradation for API and database failures
---

# Error Handling and Validation

Handle errors gracefully and validate user inputs for task operations in the AI chatbot.

## Principles

1. **User-Friendly Messages**: Technical errors become helpful suggestions
2. **Fail Fast**: Validate inputs before database operations
3. **Recovery Suggestions**: Always tell users what to do next
4. **Consistent Format**: Same error structure across all tools

## Quick Reference

### Common Validation Patterns

```python
# Title validation
if not title or not title.strip():
    return "I need a title for the task. What would you like to call it?"

# Position validation
if position < 1 or position > len(tasks):
    return f"Task #{position} not found. You have {len(tasks)} task(s)."

# Empty list handling
if not tasks:
    return "You have no tasks yet. Would you like to add one?"
```

### Error Response Pattern

```python
def create_error_response(error_type: str, context: dict) -> str:
    """Create user-friendly error message."""
    messages = {
        "empty_title": "I need a title for the task. What would you like to call it?",
        "task_not_found": f"Task #{context.get('position')} not found. You have {context.get('total', 0)} task(s).",
        "no_tasks": "You have no tasks yet. Would you like to add one?",
        "already_completed": f"'{context.get('title')}' is already complete.",
    }
    return messages.get(error_type, "Something went wrong. Please try again.")
```

## Validation Functions

### Title Validation

```python
def validate_title(title: str | None) -> tuple[bool, str]:
    if not title or not title.strip():
        return False, "I need a title for the task. What would you like to call it?"
    if len(title) > 200:
        return False, f"That title is too long ({len(title)} chars). Please keep it under 200 characters."
    return True, title.strip()
```

### Position Validation

```python
def validate_position(position: int | None, tasks: list) -> tuple[bool, str]:
    if position is None:
        return False, "Please specify a task number (e.g., 'complete task 1')."
    if not isinstance(position, int):
        return False, "Please use a number (1, 2, 3) to refer to tasks."
    if len(tasks) == 0:
        return False, "You have no tasks yet. Would you like to add one?"
    if position < 1 or position > len(tasks):
        return False, f"Task #{position} not found. You have {len(tasks)} task(s). Try 'show my tasks' to see them."
    return True, ""
```

## Reference Files

- **Validation**: See `references/validation.md` for complete validation functions
- **Error Messages**: See `references/error-messages.md` for message templates
- **Edge Cases**: See `references/edge-cases.md` for handling special scenarios
