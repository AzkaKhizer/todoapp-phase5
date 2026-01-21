# Edge Case Handling

Handle special scenarios and edge cases in task operations.

## Edge Cases by Operation

### add_task

```python
async def execute_add_task(service, user_id: str, args: dict) -> str:
    """
    Edge cases:
    - Empty/whitespace title
    - Very long title (>200 chars)
    - Unicode/emoji in title
    - Duplicate title (allowed - not an error)
    """
    title = args.get("title", "")

    # Edge: Empty or whitespace-only
    if not title or not title.strip():
        return "I need a title for the task. What would you like to call it?"

    title = title.strip()

    # Edge: Too long
    if len(title) > 200:
        return f"That title is too long ({len(title)} chars). Please keep it under 200 characters."

    # Edge: Unicode/emoji - allowed, just create it
    # "Add task 🎉 Party planning" is valid

    # Edge: Duplicate title - allowed, create anyway
    # User might want multiple "Call mom" tasks

    task = await service.create_task(user_id=user_id, title=title)
    return f"Created task: '{task.title}'"
```

### list_tasks

```python
async def execute_list_tasks(service, user_id: str, args: dict) -> str:
    """
    Edge cases:
    - Empty task list
    - All tasks completed (when filtering pending)
    - All tasks pending (when filtering completed)
    - Very long task list (pagination consideration)
    - Task titles with special characters
    """
    filter_value = args.get("filter", "all")
    tasks = await service.get_user_tasks(user_id)

    # Apply filter
    if filter_value == "pending":
        tasks = [t for t in tasks if not t.completed]
    elif filter_value == "completed":
        tasks = [t for t in tasks if t.completed]

    # Edge: Empty list
    if not tasks:
        if filter_value == "all":
            return "You have no tasks yet. Would you like to add one?"
        elif filter_value == "pending":
            return "No pending tasks. All caught up! 🎉"
        else:  # completed
            return "No completed tasks yet. Keep going!"

    # Edge: Very long list - show all but mention count
    lines = []
    for i, task in enumerate(tasks, 1):
        status = "✓" if task.completed else "○"
        # Edge: Truncate very long titles in display
        title = task.title[:50] + "..." if len(task.title) > 50 else task.title
        lines.append(f"{i}. {status} {title}")

    result = "\n".join(lines)

    # Edge: If many tasks, add helpful note
    if len(tasks) > 10:
        result += f"\n\n({len(tasks)} tasks total)"

    return result
```

### complete_task

```python
async def execute_complete_task(service, user_id: str, args: dict) -> str:
    """
    Edge cases:
    - Position is None
    - Position is not a number (string "one")
    - Position is 0 or negative
    - Position exceeds task count
    - Task already completed
    - Empty task list
    """
    position = args.get("position")

    # Edge: Position not provided
    if position is None:
        return "Which task would you like to complete? Use a number like 'complete task 1'."

    # Edge: Position not an integer
    if not isinstance(position, int):
        return "Please use a number (1, 2, 3) to refer to tasks."

    tasks = await service.get_user_tasks(user_id)

    # Edge: No tasks
    if not tasks:
        return "You have no tasks to complete. Would you like to add one?"

    # Edge: Position out of range
    if position < 1:
        return "Task numbers start at 1."

    if position > len(tasks):
        return f"Task #{position} not found. You have {len(tasks)} task(s). Try 'show my tasks' to see the list."

    task = tasks[position - 1]

    # Edge: Already completed
    if task.completed:
        return f"'{task.title}' is already marked as complete. Would you like to see your pending tasks?"

    await service.update_task(task.id, user_id, completed=True)

    # Edge: Was the last pending task
    remaining = [t for t in tasks if not t.completed and t.id != task.id]
    if not remaining:
        return f"Marked '{task.title}' as complete. You've finished all your tasks! 🎉"

    return f"Marked '{task.title}' as complete. {len(remaining)} task(s) remaining."
```

### delete_task

```python
async def execute_delete_task(service, user_id: str, args: dict) -> str:
    """
    Edge cases:
    - Position not provided
    - Position out of range
    - Empty task list
    - Deleting completed task (allowed)
    - Last task in list
    """
    position = args.get("position")

    if position is None:
        return "Which task would you like to delete? Use a number like 'delete task 2'."

    if not isinstance(position, int):
        return "Please use a number (1, 2, 3) to refer to tasks."

    tasks = await service.get_user_tasks(user_id)

    if not tasks:
        return "You have no tasks to delete."

    if position < 1 or position > len(tasks):
        return f"Task #{position} not found. You have {len(tasks)} task(s)."

    task = tasks[position - 1]
    title = task.title

    await service.delete_task(task.id, user_id)

    # Edge: Was last task
    if len(tasks) == 1:
        return f"Deleted '{title}'. Your task list is now empty."

    return f"Deleted '{title}'. {len(tasks) - 1} task(s) remaining."
```

### update_task

```python
async def execute_update_task(service, user_id: str, args: dict) -> str:
    """
    Edge cases:
    - Position not provided
    - Position out of range
    - No fields to update
    - Only whitespace in new title
    - New title same as old
    - Clearing description (setting to empty)
    """
    position = args.get("position")

    if position is None:
        return "Which task would you like to update? Use a number like 'update task 1'."

    if not isinstance(position, int):
        return "Please use a number (1, 2, 3) to refer to tasks."

    tasks = await service.get_user_tasks(user_id)

    if not tasks:
        return "You have no tasks to update."

    if position < 1 or position > len(tasks):
        return f"Task #{position} not found. You have {len(tasks)} task(s)."

    task = tasks[position - 1]
    old_title = task.title

    # Collect valid updates
    updates = {}

    if "title" in args:
        new_title = args["title"]
        if new_title:
            new_title = new_title.strip()
            if not new_title:
                return "The new title can't be empty. What would you like to rename it to?"
            if len(new_title) > 200:
                return f"That title is too long ({len(new_title)} chars). Please keep it under 200 characters."
            # Edge: Same as old title
            if new_title == old_title:
                return f"'{old_title}' already has that title."
            updates["title"] = new_title

    if "description" in args:
        # Edge: Allow clearing description with empty string
        updates["description"] = args["description"] if args["description"] else None

    # Edge: No actual updates
    if not updates:
        return "No changes specified. What would you like to update? You can change the title or description."

    await service.update_task(task.id, user_id, **updates)

    new_title = updates.get("title", old_title)
    if "title" in updates and "description" in updates:
        return f"Updated '{old_title}' -> '{new_title}' with new description."
    elif "title" in updates:
        return f"Renamed '{old_title}' to '{new_title}'."
    else:
        return f"Updated description for '{old_title}'."
```

## System-Level Edge Cases

### Database Connection Issues

```python
async def execute_with_retry(func, *args, max_retries=3):
    """Retry database operations on transient failures."""
    for attempt in range(max_retries):
        try:
            return await func(*args)
        except OperationalError as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(0.5 * (attempt + 1))
            else:
                return "I'm having trouble connecting. Please try again in a moment."
    return "Something went wrong. Please try again."
```

### OpenAI API Failures

```python
async def process_with_fallback(message: str, user_id: str):
    """Handle OpenAI API failures gracefully."""
    try:
        return await call_openai_agent(message, user_id)
    except openai.RateLimitError:
        return "I'm getting too many requests right now. Please wait a moment and try again."
    except openai.APITimeoutError:
        return "That took too long. Please try again with a simpler request."
    except openai.APIError:
        return "I'm having trouble with the AI service. Please try again."
```

### Malformed Tool Arguments

```python
async def execute_tool(tool_call, user_id: str, session) -> str:
    """Handle malformed tool arguments."""
    try:
        args = json.loads(tool_call.function.arguments)
    except json.JSONDecodeError:
        return "I couldn't understand that request. Could you rephrase?"

    # Validate args is a dict
    if not isinstance(args, dict):
        return "I received an unexpected format. Please try again."

    # Continue with execution...
```

## Edge Case Checklist

- [ ] Empty/null input handling
- [ ] Whitespace-only strings
- [ ] Maximum length validation
- [ ] Out of range numbers
- [ ] Type mismatches
- [ ] Empty collections
- [ ] Already in target state
- [ ] Last item scenarios
- [ ] Unicode/special characters
- [ ] Concurrent modifications
- [ ] Network timeouts
- [ ] Database connection issues
