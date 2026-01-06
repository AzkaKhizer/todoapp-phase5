"""CLI module for Todo application.

Handles all console I/O, menu display, user prompts, and flow control.

Spec Reference: FR-014, FR-015
"""

from todo.services import TaskStore


def display_menu() -> None:
    """Display the main menu with numbered options.

    Spec Reference: FR-014, Console UX Requirements
    """
    print("========================================")
    print("          TODO APPLICATION")
    print("========================================")
    print()
    print("1. Add Task")
    print("2. View Tasks")
    print("3. Update Task")
    print("4. Delete Task")
    print("5. Toggle Complete")
    print("6. Exit")
    print()


def get_menu_choice() -> str:
    """Get and validate menu choice from user.

    Returns:
        User's input string (validated to be 1-6 or invalid)

    Spec Reference: FR-014
    """
    return input("Enter your choice (1-6): ").strip()


def add_task_handler(store: TaskStore) -> None:
    """Handle the add task flow.

    Prompts user for title (required) and description (optional),
    creates the task, and displays success/error messages.

    Args:
        store: TaskStore instance to add the task to

    Spec Reference: FR-001, FR-002, FR-003, FR-004, FR-013
    """
    title = input("Enter task title: ").strip()

    if not title:
        print("Error: Title is required.")
        return

    description = input("Enter task description (press Enter to skip): ")

    try:
        task = store.add(title, description)
        print(f"Task added successfully! (ID: {task.id})")
    except ValueError as e:
        print(f"Error: {e}")


def view_tasks_handler(store: TaskStore) -> None:
    """Handle the view tasks flow.

    Displays all tasks with ID, title, description, and status indicator.
    Shows appropriate message if no tasks exist.

    Args:
        store: TaskStore instance to get tasks from

    Spec Reference: FR-005, FR-006
    """
    tasks = store.get_all()

    print("========================================")
    print("             YOUR TASKS")
    print("========================================")
    print()

    if not tasks:
        print("No tasks found. Add a task to get started!")
    else:
        for task in tasks:
            status = "[X]" if task.is_complete else "[ ]"
            print(f"ID: {task.id}")
            print(f"{status} {task.title}")
            if task.description:
                print(f"    {task.description}")
            print()

        complete_count = sum(1 for t in tasks if t.is_complete)
        incomplete_count = len(tasks) - complete_count
        print("========================================")
        print(f"Total: {len(tasks)} tasks ({complete_count} complete, {incomplete_count} incomplete)")


def update_task_handler(store: TaskStore) -> None:
    """Handle the update task flow.

    Prompts user for task ID and new values for title/description.
    Empty input preserves the current value.

    Args:
        store: TaskStore instance to update task in

    Spec Reference: FR-007, FR-008, FR-009, FR-012, FR-013
    """
    id_input = input("Enter task ID to update: ").strip()

    try:
        task_id = int(id_input)
    except ValueError:
        print("Error: Invalid ID format. Please enter a number.")
        return

    if task_id <= 0:
        print(f"Error: Task not found with ID: {task_id}")
        return

    task = store.get_by_id(task_id)
    if task is None:
        print(f"Error: Task not found with ID: {task_id}")
        return

    new_title = input("Enter new title (press Enter to keep current): ").strip()
    new_description = input("Enter new description (press Enter to keep current): ")

    # Use None to indicate "keep current"
    title_arg = new_title if new_title else None
    # For description, empty string after strip means keep current
    # but we need to differentiate between "entered nothing" and "wants empty"
    # Per spec: empty input preserves current value
    description_arg = new_description if new_description else None

    try:
        updated_task = store.update(task_id, title=title_arg, description=description_arg)
        if updated_task:
            print("Task updated successfully!")
        else:
            print(f"Error: Task not found with ID: {task_id}")
    except ValueError as e:
        print(f"Error: {e}")


def delete_task_handler(store: TaskStore) -> None:
    """Handle the delete task flow.

    Prompts user for task ID and removes the task.

    Args:
        store: TaskStore instance to delete task from

    Spec Reference: FR-010, FR-012, FR-013
    """
    id_input = input("Enter task ID to delete: ").strip()

    try:
        task_id = int(id_input)
    except ValueError:
        print("Error: Invalid ID format. Please enter a number.")
        return

    if task_id <= 0:
        print(f"Error: Task not found with ID: {task_id}")
        return

    if store.delete(task_id):
        print("Task deleted successfully!")
    else:
        print(f"Error: Task not found with ID: {task_id}")


def toggle_complete_handler(store: TaskStore) -> None:
    """Handle the toggle complete flow.

    Prompts user for task ID and toggles the completion status.

    Args:
        store: TaskStore instance to toggle task in

    Spec Reference: FR-011, FR-012, FR-013
    """
    id_input = input("Enter task ID to toggle: ").strip()

    try:
        task_id = int(id_input)
    except ValueError:
        print("Error: Invalid ID format. Please enter a number.")
        return

    if task_id <= 0:
        print(f"Error: Task not found with ID: {task_id}")
        return

    task = store.toggle_complete(task_id)
    if task:
        if task.is_complete:
            print("Task marked as complete!")
        else:
            print("Task marked as incomplete!")
    else:
        print(f"Error: Task not found with ID: {task_id}")


def exit_handler() -> None:
    """Handle the exit flow.

    Displays goodbye message.

    Spec Reference: FR-017
    """
    print("Thank you for using Todo App. Goodbye!")
