"""Task request/response schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    """Schema for creating a new task."""

    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)


class TaskUpdate(BaseModel):
    """Schema for full task update."""

    title: str = Field(min_length=1, max_length=200)
    description: str = Field(max_length=2000)


class TaskPatch(BaseModel):
    """Schema for partial task update."""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    is_complete: bool | None = None


class TaskResponse(BaseModel):
    """Schema for task in responses."""

    id: uuid.UUID
    title: str
    description: str
    is_complete: bool
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TaskListResponse(BaseModel):
    """Schema for paginated task list."""

    tasks: list[TaskResponse]
    total: int
    limit: int
    offset: int
