"""Unit tests for Task model.

Spec Reference: FR-001, FR-002, FR-003, FR-004
"""

import pytest
from todo.models import Task


class TestTaskCreation:
    """Tests for Task creation with valid data."""

    def test_create_task_with_required_fields(self) -> None:
        """Task can be created with id and title."""
        task = Task(id=1, title="Buy groceries")
        assert task.id == 1
        assert task.title == "Buy groceries"
        assert task.description == ""
        assert task.is_complete is False

    def test_create_task_with_all_fields(self) -> None:
        """Task can be created with all fields specified."""
        task = Task(
            id=2,
            title="Call doctor",
            description="Schedule annual checkup",
            is_complete=True
        )
        assert task.id == 2
        assert task.title == "Call doctor"
        assert task.description == "Schedule annual checkup"
        assert task.is_complete is True

    def test_create_task_with_empty_description(self) -> None:
        """Task accepts empty description."""
        task = Task(id=3, title="Test task", description="")
        assert task.description == ""

    def test_task_default_status_incomplete(self) -> None:
        """New tasks default to incomplete status (FR-004)."""
        task = Task(id=1, title="New task")
        assert task.is_complete is False


class TestTaskTitleValidation:
    """Tests for Task title validation (FR-001, FR-013)."""

    def test_empty_title_raises_error(self) -> None:
        """Empty title raises ValueError."""
        with pytest.raises(ValueError, match="Title is required"):
            Task(id=1, title="")

    def test_whitespace_only_title_raises_error(self) -> None:
        """Whitespace-only title raises ValueError."""
        with pytest.raises(ValueError, match="Title is required"):
            Task(id=1, title="   ")

    def test_whitespace_only_tabs_raises_error(self) -> None:
        """Tab-only title raises ValueError."""
        with pytest.raises(ValueError, match="Title is required"):
            Task(id=1, title="\t\t")

    def test_whitespace_only_newlines_raises_error(self) -> None:
        """Newline-only title raises ValueError."""
        with pytest.raises(ValueError, match="Title is required"):
            Task(id=1, title="\n\n")

    def test_valid_title_with_leading_whitespace(self) -> None:
        """Title with leading/trailing whitespace is valid if non-empty after strip."""
        task = Task(id=1, title="  Valid title  ")
        assert task.title == "  Valid title  "

    def test_special_characters_in_title(self) -> None:
        """Title with special characters is valid."""
        task = Task(id=1, title="Task @#$%^&*()!")
        assert task.title == "Task @#$%^&*()!"
