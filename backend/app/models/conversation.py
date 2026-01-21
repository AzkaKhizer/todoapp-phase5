"""Conversation model for chat sessions."""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String
from sqlmodel import Field, SQLModel


class Conversation(SQLModel, table=True):
    """Conversation entity representing a chat session.

    Note: user_id is a string to support Better Auth's nanoid format.
    """

    __tablename__ = "conversations"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
    )
    user_id: str = Field(
        sa_column=Column(String(64), index=True, nullable=False),
    )
    title: str | None = Field(default=None, max_length=200)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime, nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime, nullable=False),
    )
