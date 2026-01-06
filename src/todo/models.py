"""Task model for the Todo application.

Spec Reference: FR-001, FR-002, FR-003, FR-004
"""

from dataclasses import dataclass, field


@dataclass
class Task:
    """Represents a single todo item.

    Attributes:
        id: Positive integer, unique identifier, immutable after creation
        title: Non-empty string, required
        description: String (may be empty), optional
        is_complete: Boolean, default False, toggleable
    """
    id: int
    title: str
    description: str = ""
    is_complete: bool = False

    def __post_init__(self) -> None:
        """Validate task fields after initialization."""
        self._validate_title(self.title)

    @staticmethod
    def _validate_title(title: str) -> None:
        """Validate that title is non-empty and not whitespace-only.

        Args:
            title: The title to validate

        Raises:
            ValueError: If title is empty or whitespace-only
        """
        if not title or not title.strip():
            raise ValueError("Title is required")
