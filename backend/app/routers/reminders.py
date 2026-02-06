"""Reminder API endpoints for managing task reminders.

This router provides endpoints for:
- Listing pending reminders for the current user
- Getting reminders for a specific task
- Updating reminder settings (delivery channel, scheduled time)
- Deleting/cancelling reminders
"""

import logging
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models.reminder import Reminder, ReminderStatus
from app.dependencies.auth import get_current_user_id
from app.services.reminder_service import ReminderService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/reminders", tags=["reminders"])


# =============================================================================
# Schemas
# =============================================================================


class ReminderResponse(BaseModel):
    """Response schema for a reminder."""

    id: UUID
    task_id: UUID
    user_id: str
    scheduled_time: datetime
    status: ReminderStatus
    delivery_channel: str
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class ReminderListResponse(BaseModel):
    """Response schema for listing reminders."""

    data: list[ReminderResponse]
    total: int


class ReminderUpdate(BaseModel):
    """Schema for updating a reminder."""

    scheduled_time: Optional[datetime] = None
    delivery_channel: Optional[str] = Field(None, max_length=20)


# =============================================================================
# Endpoints
# =============================================================================


@router.get("", response_model=ReminderListResponse)
async def list_reminders(
    status_filter: Optional[ReminderStatus] = Query(
        default=ReminderStatus.PENDING,
        alias="status",
        description="Filter by reminder status",
    ),
    limit: int = Query(default=50, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ReminderListResponse:
    """List reminders for the current user.

    Returns pending reminders by default. Use status query param to filter.
    """
    service = ReminderService(session)

    if status_filter == ReminderStatus.PENDING:
        reminders = await service.get_pending_reminders_for_user(user_id, limit)
    else:
        # For other statuses, we need a more general query
        from sqlalchemy import and_
        from sqlmodel import select

        statement = (
            select(Reminder)
            .where(
                and_(
                    Reminder.user_id == user_id,
                    Reminder.status == status_filter,
                )
            )
            .order_by(Reminder.scheduled_time.desc())
            .limit(limit)
        )
        result = await session.execute(statement)
        reminders = list(result.scalars().all())

    return ReminderListResponse(
        data=[ReminderResponse.model_validate(r) for r in reminders],
        total=len(reminders),
    )


@router.get("/task/{task_id}", response_model=ReminderListResponse)
async def get_reminders_for_task(
    task_id: UUID,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ReminderListResponse:
    """Get all reminders for a specific task.

    Returns reminders in descending order by creation date.
    """
    service = ReminderService(session)
    reminders = await service.get_reminders_for_task(task_id)

    # Filter to only return user's reminders (security check)
    user_reminders = [r for r in reminders if r.user_id == user_id]

    if not user_reminders and reminders:
        # Task exists but belongs to another user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this task's reminders",
        )

    return ReminderListResponse(
        data=[ReminderResponse.model_validate(r) for r in user_reminders],
        total=len(user_reminders),
    )


@router.get("/{reminder_id}", response_model=ReminderResponse)
async def get_reminder(
    reminder_id: UUID,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ReminderResponse:
    """Get a specific reminder by ID."""
    service = ReminderService(session)
    reminder = await service.get_reminder_by_id(reminder_id)

    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found",
        )

    if reminder.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this reminder",
        )

    return ReminderResponse.model_validate(reminder)


@router.put("/{reminder_id}", response_model=ReminderResponse)
async def update_reminder(
    reminder_id: UUID,
    update_data: ReminderUpdate,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ReminderResponse:
    """Update a reminder's scheduled time or delivery channel.

    Only pending reminders can be updated.
    """
    service = ReminderService(session)
    reminder = await service.get_reminder_by_id(reminder_id)

    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found",
        )

    if reminder.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this reminder",
        )

    if reminder.status != ReminderStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot update reminder with status '{reminder.status}'",
        )

    # Apply updates
    if update_data.scheduled_time is not None:
        reminder.scheduled_time = update_data.scheduled_time

    if update_data.delivery_channel is not None:
        reminder.delivery_channel = update_data.delivery_channel

    session.add(reminder)
    await session.commit()
    await session.refresh(reminder)

    logger.info(f"Updated reminder {reminder_id} for user {user_id}")
    return ReminderResponse.model_validate(reminder)


@router.delete("/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reminder(
    reminder_id: UUID,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> None:
    """Cancel/delete a pending reminder.

    This sets the reminder status to CANCELLED rather than deleting the record,
    preserving audit trail.
    """
    service = ReminderService(session)
    reminder = await service.get_reminder_by_id(reminder_id)

    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found",
        )

    if reminder.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this reminder",
        )

    if reminder.status == ReminderStatus.SENT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete a reminder that has already been sent",
        )

    reminder.status = ReminderStatus.CANCELLED
    session.add(reminder)
    await session.commit()

    logger.info(f"Cancelled reminder {reminder_id} for user {user_id}")


@router.post("/task/{task_id}/cancel", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_task_reminders(
    task_id: UUID,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> None:
    """Cancel all pending reminders for a specific task.

    Useful when a task is completed or the user wants to stop all reminders.
    """
    service = ReminderService(session)

    # Verify user owns the task's reminders
    reminders = await service.get_reminders_for_task(task_id)
    if reminders and reminders[0].user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to cancel reminders for this task",
        )

    cancelled = await service.cancel_reminder(task_id)

    if cancelled:
        logger.info(f"Cancelled reminders for task {task_id} by user {user_id}")
    else:
        logger.debug(f"No pending reminders to cancel for task {task_id}")
