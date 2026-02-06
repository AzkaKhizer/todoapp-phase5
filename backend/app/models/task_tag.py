"""TaskTag junction table for many-to-many relationship between tasks and tags."""

import uuid

from sqlalchemy import Column, ForeignKey
from sqlmodel import Field, SQLModel


class TaskTag(SQLModel, table=True):
    """Junction table for Task-Tag many-to-many relationship.

    This table enables tasks to have multiple tags and tags to be
    associated with multiple tasks.

    CASCADE delete ensures:
    - When a task is deleted, its tag associations are removed
    - When a tag is deleted, its task associations are removed
    """

    __tablename__ = "task_tags"

    task_id: uuid.UUID = Field(
        sa_column=Column(
            ForeignKey("tasks.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )
    tag_id: uuid.UUID = Field(
        sa_column=Column(
            ForeignKey("tags.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )
