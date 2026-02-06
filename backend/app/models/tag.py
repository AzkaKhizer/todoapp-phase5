"""Tag model for task categorization."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, String, UniqueConstraint
from sqlmodel import Field, SQLModel

if TYPE_CHECKING:
    from app.models.task import Task


class Tag(SQLModel, table=True):
    """Tag entity for categorizing tasks.

    Tags are user-scoped, meaning each user has their own set of tags.
    A task can have multiple tags (many-to-many relationship via TaskTag).
    """

    __tablename__ = "tags"
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_tag_user_name"),
    )

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
    )
    name: str = Field(max_length=50)
    color: str | None = Field(
        default=None,
        max_length=7,
        description="Hex color code (e.g., #3B82F6)",
    )
    user_id: str = Field(
        sa_column=Column(String(64), index=True, nullable=False),
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime, nullable=False),
    )

    # Relationships (defined in TaskTag to avoid circular imports)
    # tasks: list["Task"] = Relationship(back_populates="tags", link_model=TaskTag)
