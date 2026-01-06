"""Unit tests for TaskStore service.

Spec Reference: FR-003, FR-005, FR-007, FR-008, FR-009, FR-010, FR-011, FR-016, NFR-006
"""

import pytest
from todo.models import Task
from todo.services import TaskStore


class TestTaskStoreAdd:
    """Tests for TaskStore.add() method."""

    def test_add_task_returns_task_with_id(self) -> None:
        """Add returns Task with auto-generated ID (FR-003)."""
        store = TaskStore()
        task = store.add("Buy groceries")
        assert isinstance(task, Task)
        assert task.id == 1
        assert task.title == "Buy groceries"

    def test_add_task_with_description(self) -> None:
        """Add accepts optional description (FR-002)."""
        store = TaskStore()
        task = store.add("Call doctor", "Schedule annual checkup")
        assert task.description == "Schedule annual checkup"

    def test_add_task_default_incomplete(self) -> None:
        """New tasks default to incomplete status (FR-004)."""
        store = TaskStore()
        task = store.add("Test task")
        assert task.is_complete is False

    def test_add_multiple_tasks_unique_ids(self) -> None:
        """Each task gets unique sequential ID (FR-003)."""
        store = TaskStore()
        task1 = store.add("Task 1")
        task2 = store.add("Task 2")
        task3 = store.add("Task 3")
        assert task1.id == 1
        assert task2.id == 2
        assert task3.id == 3

    def test_add_task_increments_id_counter(self) -> None:
        """ID counter increments even after deletion."""
        store = TaskStore()
        store.add("Task 1")
        store.add("Task 2")
        store.delete(1)
        task3 = store.add("Task 3")
        # ID should be 3, not reusing 1
        assert task3.id == 3

    def test_add_empty_title_raises_error(self) -> None:
        """Empty title raises ValueError (FR-001)."""
        store = TaskStore()
        with pytest.raises(ValueError, match="Title is required"):
            store.add("")


class TestTaskStoreGetAll:
    """Tests for TaskStore.get_all() method."""

    def test_get_all_empty_store(self) -> None:
        """Get all from empty store returns empty list."""
        store = TaskStore()
        tasks = store.get_all()
        assert tasks == []

    def test_get_all_returns_all_tasks(self) -> None:
        """Get all returns all added tasks (FR-005)."""
        store = TaskStore()
        store.add("Task 1")
        store.add("Task 2")
        store.add("Task 3")
        tasks = store.get_all()
        assert len(tasks) == 3

    def test_get_all_returns_list(self) -> None:
        """Get all returns a list type."""
        store = TaskStore()
        store.add("Task 1")
        tasks = store.get_all()
        assert isinstance(tasks, list)


class TestTaskStoreGetById:
    """Tests for TaskStore.get_by_id() method."""

    def test_get_by_id_found(self) -> None:
        """Get by ID returns task when found."""
        store = TaskStore()
        store.add("Task 1")
        task = store.get_by_id(1)
        assert task is not None
        assert task.id == 1
        assert task.title == "Task 1"

    def test_get_by_id_not_found(self) -> None:
        """Get by ID returns None when not found (FR-012)."""
        store = TaskStore()
        task = store.get_by_id(99)
        assert task is None

    def test_get_by_id_after_delete(self) -> None:
        """Get by ID returns None for deleted task."""
        store = TaskStore()
        store.add("Task 1")
        store.delete(1)
        task = store.get_by_id(1)
        assert task is None


class TestTaskStoreUpdate:
    """Tests for TaskStore.update() method."""

    def test_update_title(self) -> None:
        """Update changes title (FR-007)."""
        store = TaskStore()
        store.add("Old title")
        task = store.update(1, title="New title")
        assert task is not None
        assert task.title == "New title"

    def test_update_description(self) -> None:
        """Update changes description (FR-008)."""
        store = TaskStore()
        store.add("Task", "Old description")
        task = store.update(1, description="New description")
        assert task is not None
        assert task.description == "New description"

    def test_update_preserves_id(self) -> None:
        """Update preserves task ID (FR-009)."""
        store = TaskStore()
        store.add("Task")
        task = store.update(1, title="Updated")
        assert task is not None
        assert task.id == 1

    def test_update_none_title_keeps_current(self) -> None:
        """Update with None title keeps current title."""
        store = TaskStore()
        store.add("Original title")
        task = store.update(1, title=None, description="New desc")
        assert task is not None
        assert task.title == "Original title"
        assert task.description == "New desc"

    def test_update_none_description_keeps_current(self) -> None:
        """Update with None description keeps current description."""
        store = TaskStore()
        store.add("Title", "Original desc")
        task = store.update(1, title="New title", description=None)
        assert task is not None
        assert task.title == "New title"
        assert task.description == "Original desc"

    def test_update_not_found(self) -> None:
        """Update returns None for non-existent ID (FR-012)."""
        store = TaskStore()
        task = store.update(99, title="New")
        assert task is None

    def test_update_empty_title_raises_error(self) -> None:
        """Update with empty title raises ValueError."""
        store = TaskStore()
        store.add("Task")
        with pytest.raises(ValueError, match="Title is required"):
            store.update(1, title="")


class TestTaskStoreDelete:
    """Tests for TaskStore.delete() method."""

    def test_delete_existing_task(self) -> None:
        """Delete removes task and returns True (FR-010)."""
        store = TaskStore()
        store.add("Task 1")
        result = store.delete(1)
        assert result is True
        assert store.get_by_id(1) is None

    def test_delete_non_existent_task(self) -> None:
        """Delete returns False for non-existent ID (FR-012)."""
        store = TaskStore()
        result = store.delete(99)
        assert result is False

    def test_delete_does_not_affect_other_tasks(self) -> None:
        """Delete only removes specified task."""
        store = TaskStore()
        store.add("Task 1")
        store.add("Task 2")
        store.delete(1)
        tasks = store.get_all()
        assert len(tasks) == 1
        assert tasks[0].id == 2


class TestTaskStoreToggleComplete:
    """Tests for TaskStore.toggle_complete() method."""

    def test_toggle_incomplete_to_complete(self) -> None:
        """Toggle changes incomplete to complete (FR-011)."""
        store = TaskStore()
        store.add("Task")
        task = store.toggle_complete(1)
        assert task is not None
        assert task.is_complete is True

    def test_toggle_complete_to_incomplete(self) -> None:
        """Toggle changes complete to incomplete (FR-011)."""
        store = TaskStore()
        store.add("Task")
        store.toggle_complete(1)  # Now complete
        task = store.toggle_complete(1)  # Now incomplete
        assert task is not None
        assert task.is_complete is False

    def test_toggle_not_found(self) -> None:
        """Toggle returns None for non-existent ID (FR-012)."""
        store = TaskStore()
        task = store.toggle_complete(99)
        assert task is None

    def test_toggle_preserves_other_fields(self) -> None:
        """Toggle only changes is_complete, preserves other fields."""
        store = TaskStore()
        store.add("Task", "Description")
        task = store.toggle_complete(1)
        assert task is not None
        assert task.title == "Task"
        assert task.description == "Description"
        assert task.id == 1


class TestTaskStoreIsolation:
    """Tests for TaskStore state isolation (NFR-006)."""

    def test_separate_instances_independent(self) -> None:
        """Different TaskStore instances have independent state."""
        store1 = TaskStore()
        store2 = TaskStore()
        store1.add("Task in store 1")
        assert len(store1.get_all()) == 1
        assert len(store2.get_all()) == 0

    def test_new_instance_starts_fresh(self) -> None:
        """New TaskStore instance starts with empty state and ID=1."""
        store = TaskStore()
        store.add("Task")
        store.add("Another task")

        new_store = TaskStore()
        task = new_store.add("Fresh task")
        assert len(new_store.get_all()) == 1
        assert task.id == 1  # Starts from 1 again
