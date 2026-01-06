"""Task model for todo items."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.user import User


class Task(SQLModel, table=True):
    """Task entity representing a todo item."""

    __tablename__ = "tasks"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
    )
    title: str = Field(max_length=200)
    description: str = Field(default="", max_length=2000)
    is_complete: bool = Field(default=False)
    user_id: uuid.UUID = Field(
        foreign_key="users.id",
        index=True,
        ondelete="CASCADE",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime, nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime, nullable=False),
    )

    # Relationships
    owner: "User" = Relationship(back_populates="tasks")
