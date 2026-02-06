"""Reminder model for task notifications."""

import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlmodel import Field, SQLModel

if TYPE_CHECKING:
    from app.models.task import Task


class ReminderStatus(str, Enum):
    """Status of a reminder."""

    PENDING = "pending"
    SENT = "sent"
    CANCELLED = "cancelled"
    FAILED = "failed"


class Reminder(SQLModel, table=True):
    """Reminder entity for task notifications.

    Reminders are scheduled based on task due dates and reminder offsets.
    The reminder scheduler (Dapr cron binding) checks for due reminders
    every minute and publishes them to Kafka for delivery.

    Delivery channels:
    - in-app: WebSocket notification to connected clients
    - email: Email notification (future)
    - push: Push notification (future)
    """

    __tablename__ = "reminders"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
    )
    task_id: uuid.UUID = Field(
        sa_column=Column(
            ForeignKey("tasks.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
    )
    user_id: str = Field(
        sa_column=Column(String(64), index=True, nullable=False),
    )
    scheduled_time: datetime = Field(
        sa_column=Column(DateTime, nullable=False, index=True),
    )
    status: ReminderStatus = Field(default=ReminderStatus.PENDING)
    delivery_channel: str = Field(default="in-app", max_length=20)
    sent_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime, nullable=True),
    )
    error_message: str | None = Field(default=None, max_length=500)
    retry_count: int = Field(default=0)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime, nullable=False),
    )

    # Relationships (defined later to avoid circular imports)
    # task: "Task" = Relationship(back_populates="reminders")
