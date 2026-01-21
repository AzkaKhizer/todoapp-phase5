"""Message model for chat messages."""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String, Text
from sqlmodel import Field, SQLModel


class Message(SQLModel, table=True):
    """Message entity representing a chat message.

    Stores user messages, assistant responses, and tool call results.
    """

    __tablename__ = "messages"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
    )
    conversation_id: uuid.UUID = Field(
        foreign_key="conversations.id",
        index=True,
    )
    user_id: str = Field(
        sa_column=Column(String(64), index=True, nullable=False),
    )
    role: str = Field(
        sa_column=Column(String(20), nullable=False),
    )  # "user", "assistant", "tool"
    content: str = Field(
        sa_column=Column(Text, nullable=False),
    )
    tool_calls: str | None = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
    )  # JSON string of tool calls
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime, nullable=False),
    )
