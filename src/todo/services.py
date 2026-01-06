"""TaskStore service for in-memory task management.

Spec Reference: FR-003, FR-005, FR-007, FR-008, FR-009, FR-010, FR-011, FR-016, NFR-006
"""

from todo.models import Task


class TaskStore:
    """In-memory collection managing all Task instances.

    Attributes:
        _tasks: Internal storage mapping ID -> Task
        _next_id: Counter for ID generation, starts at 1
    """

    def __init__(self) -> None:
        """Initialize empty TaskStore with ID counter starting at 1."""
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1

    def add(self, title: str, description: str = "") -> Task:
        """Create a new task with auto-generated ID.

        Args:
            title: Task title (must be non-empty after strip)
            description: Task description (default: empty string)

        Returns:
            The newly created Task with ID assigned

        Spec Reference: FR-001, FR-002, FR-003, FR-004
        """
        task = Task(
            id=self._next_id,
            title=title,
            description=description,
            is_complete=False
        )
        self._tasks[self._next_id] = task
        self._next_id += 1
        return task

    def get_all(self) -> list[Task]:
        """Return all tasks in the store.

        Returns:
            List of all tasks (may be empty), ordered by ID

        Spec Reference: FR-005
        """
        return list(self._tasks.values())

    def get_by_id(self, task_id: int) -> Task | None:
        """Retrieve a task by its ID.

        Args:
            task_id: The task ID to look up

        Returns:
            Task if found, None if not found

        Spec Reference: FR-005, FR-012
        """
        return self._tasks.get(task_id)

    def update(
        self,
        task_id: int,
        title: str | None = None,
        description: str | None = None
    ) -> Task | None:
        """Update a task's title and/or description.

        Only non-None values are applied. Empty string for title is NOT allowed
        (title must be non-empty if provided).

        Args:
            task_id: The task ID to update
            title: New title (None = keep current)
            description: New description (None = keep current)

        Returns:
            Updated Task if found, None if task not found

        Spec Reference: FR-007, FR-008, FR-009, FR-012
        """
        task = self._tasks.get(task_id)
        if task is None:
            return None

        if title is not None:
            # Validate new title
            Task._validate_title(title)
            task.title = title

        if description is not None:
            task.description = description

        return task

    def delete(self, task_id: int) -> bool:
        """Remove a task from the store.

        Args:
            task_id: The task ID to delete

        Returns:
            True if task was deleted, False if task not found

        Spec Reference: FR-010, FR-012
        """
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False

    def toggle_complete(self, task_id: int) -> Task | None:
        """Toggle the completion status of a task.

        Args:
            task_id: The task ID to toggle

        Returns:
            Updated Task if found (with is_complete flipped), None if not found

        Spec Reference: FR-011, FR-012
        """
        task = self._tasks.get(task_id)
        if task is None:
            return None

        task.is_complete = not task.is_complete
        return task
