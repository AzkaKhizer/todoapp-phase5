"""RecurrencePattern model for recurring task definitions."""

import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, String
from sqlalchemy.types import JSON
from sqlmodel import Field, SQLModel

if TYPE_CHECKING:
    from app.models.task import Task


class RecurrenceType(str, Enum):
    """Types of recurrence patterns."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class RecurrencePattern(SQLModel, table=True):
    """Recurrence pattern for recurring tasks.

    Defines how tasks repeat:
    - daily: Every N days
    - weekly: Every N weeks on specific days
    - monthly: Every N months on specific day
    - yearly: Every N years on specific date
    - custom: Custom interval with base unit

    Examples:
    - Daily at 9am: type=daily, interval=1
    - Every Monday: type=weekly, interval=1, days_of_week=[0]
    - Every 2 weeks on Mon/Wed/Fri: type=weekly, interval=2, days_of_week=[0,2,4]
    - 15th of every month: type=monthly, interval=1, day_of_month=15
    - Every year on March 1st: type=yearly, interval=1, month_of_year=3, day_of_month=1
    """

    __tablename__ = "recurrence_patterns"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
    )
    type: RecurrenceType = Field(nullable=False)
    interval: int = Field(default=1, ge=1, le=365)
    # For weekly recurrence: 0=Monday, 6=Sunday (stored as JSON array for SQLite compatibility)
    days_of_week: list[int] | None = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
    )
    # For monthly recurrence: 1-31
    day_of_month: int | None = Field(default=None, ge=1, le=31)
    # For yearly recurrence: 1-12
    month_of_year: int | None = Field(default=None, ge=1, le=12)
    end_date: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime, nullable=True),
    )
    user_id: str = Field(
        sa_column=Column(String(64), nullable=False),
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime, nullable=False),
    )

    # Relationships (defined later to avoid circular imports)
    # tasks: list["Task"] = Relationship(back_populates="recurrence")
