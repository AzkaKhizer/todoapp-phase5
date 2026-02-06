"""Task request/response schemas."""

import uuid
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

from app.models import TaskPriority


class RecurrenceCreate(BaseModel):
    """Schema for creating a recurrence pattern."""

    type: Literal["daily", "weekly", "monthly", "yearly", "custom"]
    interval: int = Field(default=1, ge=1, le=365)
    days_of_week: list[int] | None = Field(
        default=None,
        description="For weekly: 0=Monday, 6=Sunday",
    )
    day_of_month: int | None = Field(default=None, ge=1, le=31)
    end_date: datetime | None = None


class TagResponse(BaseModel):
    """Schema for tag in responses."""

    id: uuid.UUID
    name: str
    color: str | None = None

    model_config = {"from_attributes": True}


class ReminderResponse(BaseModel):
    """Schema for reminder in responses."""

    id: uuid.UUID
    scheduled_time: datetime
    status: str

    model_config = {"from_attributes": True}


class RecurrenceResponse(BaseModel):
    """Schema for recurrence pattern in responses."""

    id: uuid.UUID
    type: str
    interval: int
    days_of_week: list[int] | None = None
    day_of_month: int | None = None
    end_date: datetime | None = None

    model_config = {"from_attributes": True}


class TaskCreate(BaseModel):
    """Schema for creating a new task."""

    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)
    due_date: datetime | None = None
    priority: TaskPriority = TaskPriority.MEDIUM
    tags: list[str] = Field(default_factory=list, description="Tag names")
    reminder_offset_minutes: int | None = Field(
        default=None,
        ge=0,
        le=10080,  # Max 7 days
        description="Minutes before due_date for reminder",
    )
    recurrence: RecurrenceCreate | None = None


class TaskUpdate(BaseModel):
    """Schema for full task update."""

    title: str = Field(min_length=1, max_length=200)
    description: str = Field(max_length=2000)
    due_date: datetime | None = None
    priority: TaskPriority = TaskPriority.MEDIUM
    tags: list[str] = Field(default_factory=list)
    reminder_offset_minutes: int | None = Field(default=None, ge=0, le=10080)
    recurrence: RecurrenceCreate | None = None


class TaskPatch(BaseModel):
    """Schema for partial task update."""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    is_complete: bool | None = None
    due_date: datetime | None = None
    priority: TaskPriority | None = None
    tags: list[str] | None = None
    reminder_offset_minutes: int | None = Field(default=None, ge=0, le=10080)


class TaskResponse(BaseModel):
    """Schema for task in responses."""

    id: uuid.UUID
    title: str
    description: str
    is_complete: bool
    user_id: str  # Better Auth uses nanoid format, not UUID
    due_date: datetime | None = None
    priority: TaskPriority
    tags: list[TagResponse] = Field(default_factory=list)
    reminder: ReminderResponse | None = None
    recurrence: RecurrenceResponse | None = None
    is_overdue: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TaskFilterParams(BaseModel):
    """Schema for task filter/sort query parameters."""

    search: str | None = Field(default=None, description="Full-text search on title/description")
    priority: list[TaskPriority] | None = Field(default=None, description="Filter by priorities")
    due_before: datetime | None = Field(default=None, description="Tasks due before this date")
    due_after: datetime | None = Field(default=None, description="Tasks due after this date")
    tags: list[str] | None = Field(default=None, description="Filter by tag names")
    is_complete: bool | None = Field(default=None, description="Filter by completion status")
    sort_by: Literal["due_date", "priority", "created_at", "title"] = "created_at"
    sort_order: Literal["asc", "desc"] = "desc"
    include_overdue: bool = True


class PaginationInfo(BaseModel):
    """Schema for pagination metadata."""

    page: int
    limit: int
    total_items: int
    total_pages: int


class TaskListResponse(BaseModel):
    """Schema for paginated task list."""

    data: list[TaskResponse]
    pagination: PaginationInfo
