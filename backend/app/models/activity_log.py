"""ActivityLogEntry model for audit trail."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, Index, String
from sqlalchemy.types import JSON
from sqlmodel import Field, SQLModel


class ActivityLogEntry(SQLModel, table=True):
    """Activity log entry for audit trail.

    Records all significant operations on tasks, reminders, and tags.
    Consumed from Kafka events and persisted to the database.

    Event types:
    - task.created, task.updated, task.completed, task.deleted
    - reminder.scheduled, reminder.sent, reminder.cancelled
    - tag.created, tag.deleted
    """

    __tablename__ = "activity_log"
    __table_args__ = (
        Index("idx_activity_user_time", "user_id", "timestamp"),
        Index("idx_activity_entity", "entity_type", "entity_id"),
    )

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
    )
    user_id: str = Field(
        sa_column=Column(String(64), index=True, nullable=False),
    )
    event_type: str = Field(
        max_length=50,
        description="Event type (e.g., task.created, task.completed)",
    )
    entity_type: str = Field(
        max_length=20,
        description="Type of entity (task, reminder, tag)",
    )
    entity_id: uuid.UUID = Field(
        description="ID of the affected entity",
    )
    timestamp: datetime = Field(
        sa_column=Column(DateTime, nullable=False, index=True),
    )
    details: dict[str, Any] | None = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
    )
    correlation_id: str | None = Field(
        default=None,
        max_length=64,
        description="Request correlation ID for tracing",
    )
