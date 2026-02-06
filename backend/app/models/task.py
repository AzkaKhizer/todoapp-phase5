"""Task model for todo items."""

import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.recurrence import RecurrencePattern
    from app.models.reminder import Reminder
    from app.models.tag import Tag


class TaskPriority(str, Enum):
    """Task priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Task(SQLModel, table=True):
    """Task entity representing a todo item.

    Note: user_id is a string to support Better Auth's nanoid format.
    No foreign key relationship since users are managed by Better Auth.

    Extended fields for advanced features:
    - due_date: When the task is due
    - priority: Task priority level (low, medium, high, urgent)
    - reminder_offset_minutes: Minutes before due_date for reminder notification
    - recurrence_id: Link to recurrence pattern for recurring tasks
    - parent_task_id: Original task for recurring task instances
    """

    __tablename__ = "tasks"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
    )
    title: str = Field(max_length=200)
    description: str = Field(default="", max_length=2000)
    is_complete: bool = Field(default=False)
    # Better Auth uses nanoid format for user IDs (not UUID)
    user_id: str = Field(
        sa_column=Column(String(64), index=True, nullable=False),
    )

    # Extended fields for advanced task management
    due_date: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, index=True, nullable=True),
    )
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    reminder_offset_minutes: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, nullable=True),
        description="Minutes before due_date for reminder",
    )
    recurrence_id: Optional[uuid.UUID] = Field(
        default=None,
        sa_column=Column(
            ForeignKey("recurrence_patterns.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    parent_task_id: Optional[uuid.UUID] = Field(
        default=None,
        sa_column=Column(
            ForeignKey("tasks.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime, nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime, nullable=False),
    )

    # Relationships (defined later to avoid circular imports)
    # tags: list["Tag"] = Relationship(back_populates="tasks", link_model=TaskTag)
    # reminders: list["Reminder"] = Relationship(back_populates="task")
    # recurrence: Optional["RecurrencePattern"] = Relationship(back_populates="tasks")

    @property
    def is_overdue(self) -> bool:
        """Check if the task is overdue."""
        if self.due_date and not self.is_complete:
            return datetime.utcnow() > self.due_date
        return False

    @property
    def reminder_offset(self) -> Optional[timedelta]:
        """Get reminder offset as timedelta."""
        if self.reminder_offset_minutes is not None:
            return timedelta(minutes=self.reminder_offset_minutes)
        return None

    @property
    def reminder_time(self) -> Optional[datetime]:
        """Calculate the reminder notification time."""
        if self.due_date and self.reminder_offset_minutes:
            return self.due_date - timedelta(minutes=self.reminder_offset_minutes)
        return None
