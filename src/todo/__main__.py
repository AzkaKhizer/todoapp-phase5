"""Entry point for the Todo application.

Run with: python -m todo

Spec Reference: FR-014, FR-015, FR-017
"""

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


def main() -> None:
    """Main entry point - runs the menu loop.

    Creates a TaskStore instance and loops through the menu
    until user selects exit.

    Spec Reference: FR-015, FR-016
    """
    store = TaskStore()

    while True:
        display_menu()
        choice = get_menu_choice()

        if choice == "1":
            add_task_handler(store)
        elif choice == "2":
            view_tasks_handler(store)
        elif choice == "3":
            update_task_handler(store)
        elif choice == "4":
            delete_task_handler(store)
        elif choice == "5":
            toggle_complete_handler(store)
        elif choice == "6":
            exit_handler()
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 6.")

        print()  # Add blank line before next menu


if __name__ == "__main__":
    main()
