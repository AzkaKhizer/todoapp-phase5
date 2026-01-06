"""Integration tests for CLI module.

Spec Reference: All User Stories
"""

import pytest
from io import StringIO
from unittest.mock import patch

from todo.services import TaskStore
from todo.cli import (
    display_menu,
    get_menu_choice,
    add_task_handler,
    view_tasks_handler,
    update_task_handler,
    delete_task_handler,
    toggle_complete_handler,
    exit_handler,
)


class TestDisplayMenu:
    """Tests for display_menu function."""

    def test_display_menu_shows_all_options(self, capsys) -> None:
        """Menu displays all 6 options."""
        display_menu()
        captured = capsys.readouterr()
        assert "1. Add Task" in captured.out
        assert "2. View Tasks" in captured.out
        assert "3. Update Task" in captured.out
        assert "4. Delete Task" in captured.out
        assert "5. Toggle Complete" in captured.out
        assert "6. Exit" in captured.out

    def test_display_menu_shows_header(self, capsys) -> None:
        """Menu displays application header."""
        display_menu()
        captured = capsys.readouterr()
        assert "TODO APPLICATION" in captured.out


class TestGetMenuChoice:
    """Tests for get_menu_choice function."""

    def test_get_menu_choice_returns_input(self) -> None:
        """Returns user input stripped."""
        with patch("builtins.input", return_value="1"):
            choice = get_menu_choice()
            assert choice == "1"

    def test_get_menu_choice_strips_whitespace(self) -> None:
        """Strips whitespace from input."""
        with patch("builtins.input", return_value="  2  "):
            choice = get_menu_choice()
            assert choice == "2"


class TestAddTaskHandler:
    """Tests for add_task_handler function (User Story 1)."""

    def test_add_task_with_title_only(self, capsys) -> None:
        """Add task with title creates task and shows success."""
        store = TaskStore()
        with patch("builtins.input", side_effect=["Buy groceries", ""]):
            add_task_handler(store)

        captured = capsys.readouterr()
        assert "Task added successfully!" in captured.out
        assert "(ID: 1)" in captured.out
        assert len(store.get_all()) == 1
        assert store.get_by_id(1).title == "Buy groceries"

    def test_add_task_with_title_and_description(self, capsys) -> None:
        """Add task with title and description."""
        store = TaskStore()
        with patch("builtins.input", side_effect=["Call doctor", "Schedule annual checkup"]):
            add_task_handler(store)

        captured = capsys.readouterr()
        assert "Task added successfully!" in captured.out
        task = store.get_by_id(1)
        assert task.title == "Call doctor"
        assert task.description == "Schedule annual checkup"

    def test_add_task_empty_title_shows_error(self, capsys) -> None:
        """Empty title shows error message."""
        store = TaskStore()
        with patch("builtins.input", side_effect=["", ""]):
            add_task_handler(store)

        captured = capsys.readouterr()
        assert "Error: Title is required." in captured.out
        assert len(store.get_all()) == 0

    def test_add_task_whitespace_title_shows_error(self, capsys) -> None:
        """Whitespace-only title shows error."""
        store = TaskStore()
        with patch("builtins.input", side_effect=["   ", ""]):
            add_task_handler(store)

        captured = capsys.readouterr()
        assert "Error: Title is required." in captured.out
        assert len(store.get_all()) == 0

    def test_add_multiple_tasks_unique_ids(self, capsys) -> None:
        """Multiple tasks get unique IDs."""
        store = TaskStore()
        with patch("builtins.input", side_effect=["Task 1", "", "Task 2", "", "Task 3", ""]):
            add_task_handler(store)
            add_task_handler(store)
            add_task_handler(store)

        captured = capsys.readouterr()
        assert "(ID: 1)" in captured.out
        assert "(ID: 2)" in captured.out
        assert "(ID: 3)" in captured.out


class TestViewTasksHandler:
    """Tests for view_tasks_handler function (User Story 2)."""

    def test_view_empty_list(self, capsys) -> None:
        """Empty list shows appropriate message."""
        store = TaskStore()
        view_tasks_handler(store)

        captured = capsys.readouterr()
        assert "No tasks found. Add a task to get started!" in captured.out

    def test_view_tasks_shows_all_tasks(self, capsys) -> None:
        """All tasks are displayed."""
        store = TaskStore()
        store.add("Task 1", "Description 1")
        store.add("Task 2", "Description 2")

        view_tasks_handler(store)

        captured = capsys.readouterr()
        assert "Task 1" in captured.out
        assert "Task 2" in captured.out
        assert "Description 1" in captured.out
        assert "Description 2" in captured.out

    def test_view_tasks_shows_status_indicators(self, capsys) -> None:
        """Status indicators shown correctly."""
        store = TaskStore()
        store.add("Incomplete task")
        store.add("Complete task")
        store.toggle_complete(2)

        view_tasks_handler(store)

        captured = capsys.readouterr()
        assert "[ ] Incomplete task" in captured.out
        assert "[X] Complete task" in captured.out

    def test_view_tasks_shows_count_summary(self, capsys) -> None:
        """Summary count shown at bottom."""
        store = TaskStore()
        store.add("Task 1")
        store.add("Task 2")
        store.toggle_complete(1)

        view_tasks_handler(store)

        captured = capsys.readouterr()
        assert "Total: 2 tasks (1 complete, 1 incomplete)" in captured.out


class TestUpdateTaskHandler:
    """Tests for update_task_handler function (User Story 3)."""

    def test_update_task_title(self, capsys) -> None:
        """Update changes title."""
        store = TaskStore()
        store.add("Old title")

        with patch("builtins.input", side_effect=["1", "New title", ""]):
            update_task_handler(store)

        captured = capsys.readouterr()
        assert "Task updated successfully!" in captured.out
        assert store.get_by_id(1).title == "New title"

    def test_update_task_description(self, capsys) -> None:
        """Update changes description."""
        store = TaskStore()
        store.add("Title", "Old description")

        with patch("builtins.input", side_effect=["1", "", "New description"]):
            update_task_handler(store)

        captured = capsys.readouterr()
        assert "Task updated successfully!" in captured.out
        assert store.get_by_id(1).description == "New description"

    def test_update_task_not_found(self, capsys) -> None:
        """Update non-existent task shows error."""
        store = TaskStore()

        with patch("builtins.input", side_effect=["99", "", ""]):
            update_task_handler(store)

        captured = capsys.readouterr()
        assert "Error: Task not found with ID: 99" in captured.out

    def test_update_task_invalid_id(self, capsys) -> None:
        """Update with invalid ID format shows error."""
        store = TaskStore()

        with patch("builtins.input", side_effect=["abc"]):
            update_task_handler(store)

        captured = capsys.readouterr()
        assert "Error: Invalid ID format. Please enter a number." in captured.out

    def test_update_preserves_id(self, capsys) -> None:
        """ID preserved after update."""
        store = TaskStore()
        store.add("Task")

        with patch("builtins.input", side_effect=["1", "Updated", ""]):
            update_task_handler(store)

        assert store.get_by_id(1).id == 1


class TestDeleteTaskHandler:
    """Tests for delete_task_handler function (User Story 4)."""

    def test_delete_existing_task(self, capsys) -> None:
        """Delete removes task."""
        store = TaskStore()
        store.add("Task to delete")

        with patch("builtins.input", return_value="1"):
            delete_task_handler(store)

        captured = capsys.readouterr()
        assert "Task deleted successfully!" in captured.out
        assert store.get_by_id(1) is None

    def test_delete_task_not_found(self, capsys) -> None:
        """Delete non-existent task shows error."""
        store = TaskStore()

        with patch("builtins.input", return_value="99"):
            delete_task_handler(store)

        captured = capsys.readouterr()
        assert "Error: Task not found with ID: 99" in captured.out

    def test_delete_task_invalid_id(self, capsys) -> None:
        """Delete with invalid ID format shows error."""
        store = TaskStore()

        with patch("builtins.input", return_value="xyz"):
            delete_task_handler(store)

        captured = capsys.readouterr()
        assert "Error: Invalid ID format. Please enter a number." in captured.out


class TestToggleCompleteHandler:
    """Tests for toggle_complete_handler function (User Story 5)."""

    def test_toggle_incomplete_to_complete(self, capsys) -> None:
        """Toggle changes incomplete to complete."""
        store = TaskStore()
        store.add("Task")

        with patch("builtins.input", return_value="1"):
            toggle_complete_handler(store)

        captured = capsys.readouterr()
        assert "Task marked as complete!" in captured.out
        assert store.get_by_id(1).is_complete is True

    def test_toggle_complete_to_incomplete(self, capsys) -> None:
        """Toggle changes complete to incomplete."""
        store = TaskStore()
        store.add("Task")
        store.toggle_complete(1)

        with patch("builtins.input", return_value="1"):
            toggle_complete_handler(store)

        captured = capsys.readouterr()
        assert "Task marked as incomplete!" in captured.out
        assert store.get_by_id(1).is_complete is False

    def test_toggle_task_not_found(self, capsys) -> None:
        """Toggle non-existent task shows error."""
        store = TaskStore()

        with patch("builtins.input", return_value="99"):
            toggle_complete_handler(store)

        captured = capsys.readouterr()
        assert "Error: Task not found with ID: 99" in captured.out

    def test_toggle_task_invalid_id(self, capsys) -> None:
        """Toggle with invalid ID format shows error."""
        store = TaskStore()

        with patch("builtins.input", return_value="invalid"):
            toggle_complete_handler(store)

        captured = capsys.readouterr()
        assert "Error: Invalid ID format. Please enter a number." in captured.out


class TestExitHandler:
    """Tests for exit_handler function (User Story 6)."""

    def test_exit_shows_goodbye_message(self, capsys) -> None:
        """Exit displays goodbye message."""
        exit_handler()

        captured = capsys.readouterr()
        assert "Thank you for using Todo App. Goodbye!" in captured.out


class TestMainLoop:
    """Tests for main loop integration."""

    def test_invalid_choice_shows_error(self, capsys) -> None:
        """Invalid choice shows appropriate error."""
        from todo.__main__ import main

        with patch("builtins.input", side_effect=["7", "6"]):
            main()

        captured = capsys.readouterr()
        assert "Invalid choice. Please enter a number between 1 and 6." in captured.out

    def test_menu_loops_after_operation(self, capsys) -> None:
        """Menu loops after each operation."""
        from todo.__main__ import main

        with patch("builtins.input", side_effect=["1", "Test Task", "", "6"]):
            main()

        captured = capsys.readouterr()
        # Menu should be displayed twice (initially and after add)
        assert captured.out.count("TODO APPLICATION") == 2


class TestEdgeCasesInvalidIDs:
    """Edge case tests for invalid ID formats (T064)."""

    def test_negative_id_update(self, capsys) -> None:
        """Negative ID shows error for update."""
        store = TaskStore()
        store.add("Task")

        with patch("builtins.input", side_effect=["-1", "", ""]):
            update_task_handler(store)

        captured = capsys.readouterr()
        assert "Error: Task not found with ID: -1" in captured.out

    def test_zero_id_update(self, capsys) -> None:
        """Zero ID shows error for update."""
        store = TaskStore()
        store.add("Task")

        with patch("builtins.input", side_effect=["0", "", ""]):
            update_task_handler(store)

        captured = capsys.readouterr()
        assert "Error: Task not found with ID: 0" in captured.out

    def test_negative_id_delete(self, capsys) -> None:
        """Negative ID shows error for delete."""
        store = TaskStore()

        with patch("builtins.input", return_value="-5"):
            delete_task_handler(store)

        captured = capsys.readouterr()
        assert "Error: Task not found with ID: -5" in captured.out

    def test_zero_id_delete(self, capsys) -> None:
        """Zero ID shows error for delete."""
        store = TaskStore()

        with patch("builtins.input", return_value="0"):
            delete_task_handler(store)

        captured = capsys.readouterr()
        assert "Error: Task not found with ID: 0" in captured.out

    def test_negative_id_toggle(self, capsys) -> None:
        """Negative ID shows error for toggle."""
        store = TaskStore()

        with patch("builtins.input", return_value="-10"):
            toggle_complete_handler(store)

        captured = capsys.readouterr()
        assert "Error: Task not found with ID: -10" in captured.out

    def test_zero_id_toggle(self, capsys) -> None:
        """Zero ID shows error for toggle."""
        store = TaskStore()

        with patch("builtins.input", return_value="0"):
            toggle_complete_handler(store)

        captured = capsys.readouterr()
        assert "Error: Task not found with ID: 0" in captured.out

    def test_float_id_shows_error(self, capsys) -> None:
        """Float ID shows invalid format error."""
        store = TaskStore()

        with patch("builtins.input", return_value="1.5"):
            delete_task_handler(store)

        captured = capsys.readouterr()
        assert "Error: Invalid ID format. Please enter a number." in captured.out

    def test_special_chars_id_shows_error(self, capsys) -> None:
        """Special characters in ID show invalid format error."""
        store = TaskStore()

        with patch("builtins.input", return_value="!@#"):
            toggle_complete_handler(store)

        captured = capsys.readouterr()
        assert "Error: Invalid ID format. Please enter a number." in captured.out


class TestEdgeCasesWhitespaceTitle:
    """Edge case tests for whitespace-only titles (T065)."""

    def test_tabs_only_title_rejected(self, capsys) -> None:
        """Tab-only title shows error."""
        store = TaskStore()

        with patch("builtins.input", side_effect=["\t\t\t", ""]):
            add_task_handler(store)

        captured = capsys.readouterr()
        assert "Error: Title is required." in captured.out
        assert len(store.get_all()) == 0

    def test_newlines_only_title_rejected(self, capsys) -> None:
        """Newline-only title shows error."""
        store = TaskStore()

        with patch("builtins.input", side_effect=["\n\n", ""]):
            add_task_handler(store)

        captured = capsys.readouterr()
        assert "Error: Title is required." in captured.out
        assert len(store.get_all()) == 0

    def test_mixed_whitespace_title_rejected(self, capsys) -> None:
        """Mixed whitespace title shows error."""
        store = TaskStore()

        with patch("builtins.input", side_effect=["  \t  \n  ", ""]):
            add_task_handler(store)

        captured = capsys.readouterr()
        assert "Error: Title is required." in captured.out
        assert len(store.get_all()) == 0

    def test_title_with_leading_trailing_whitespace_accepted(self, capsys) -> None:
        """Title with content and surrounding whitespace is accepted."""
        store = TaskStore()

        with patch("builtins.input", side_effect=["  Valid Task  ", ""]):
            add_task_handler(store)

        captured = capsys.readouterr()
        assert "Task added successfully!" in captured.out
        assert len(store.get_all()) == 1
