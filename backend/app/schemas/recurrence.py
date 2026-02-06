"""Pydantic schemas for recurrence pattern API requests and responses."""

from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


RecurrenceTypeValue = Literal["daily", "weekly", "monthly", "yearly", "custom"]


class RecurrenceCreate(BaseModel):
    """Schema for creating a recurrence pattern."""

    type: RecurrenceTypeValue = Field(
        description="Type of recurrence pattern"
    )
    interval: int = Field(
        default=1,
        ge=1,
        le=365,
        description="Number of units (days/weeks/months/years) between occurrences",
    )
    days_of_week: Optional[list[int]] = Field(
        default=None,
        description="For weekly: days of week (0=Monday, 6=Sunday)",
    )
    day_of_month: Optional[int] = Field(
        default=None,
        ge=1,
        le=31,
        description="For monthly/yearly: day of month (1-31)",
    )
    month_of_year: Optional[int] = Field(
        default=None,
        ge=1,
        le=12,
        description="For yearly: month (1-12)",
    )
    end_date: Optional[datetime] = Field(
        default=None,
        description="Optional end date for the recurrence",
    )

    @field_validator("days_of_week")
    @classmethod
    def validate_days_of_week(cls, v):
        if v is not None:
            for day in v:
                if day < 0 or day > 6:
                    raise ValueError("days_of_week must be between 0 (Monday) and 6 (Sunday)")
        return v


class RecurrenceResponse(BaseModel):
    """Schema for recurrence pattern response."""

    id: UUID
    type: RecurrenceTypeValue
    interval: int
    days_of_week: Optional[list[int]] = None
    day_of_month: Optional[int] = None
    month_of_year: Optional[int] = None
    end_date: Optional[datetime] = None
    created_at: datetime
    description: Optional[str] = Field(
        default=None,
        description="Human-readable description of the pattern",
    )

    class Config:
        from_attributes = True


class RecurrenceUpdate(BaseModel):
    """Schema for updating a recurrence pattern."""

    interval: Optional[int] = Field(
        default=None,
        ge=1,
        le=365,
    )
    days_of_week: Optional[list[int]] = None
    day_of_month: Optional[int] = Field(default=None, ge=1, le=31)
    month_of_year: Optional[int] = Field(default=None, ge=1, le=12)
    end_date: Optional[datetime] = None

    @field_validator("days_of_week")
    @classmethod
    def validate_days_of_week(cls, v):
        if v is not None:
            for day in v:
                if day < 0 or day > 6:
                    raise ValueError("days_of_week must be between 0 (Monday) and 6 (Sunday)")
        return v


class RecurrenceListResponse(BaseModel):
    """Schema for listing recurrence patterns."""

    data: list[RecurrenceResponse]
    total: int
