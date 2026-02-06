"""Activity log API routes.

This module provides REST endpoints for:
- Querying activity logs with filtering and pagination
- Viewing activity history for specific entities
- Getting productivity summaries

All endpoints require authentication and return only the
authenticated user's activity data.
"""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.dependencies.auth import get_current_user_id
from app.services.activity_service import ActivityService

router = APIRouter(prefix="/activities", tags=["activities"])


# =============================================================================
# Response Schemas
# =============================================================================


class ActivityLogResponse(BaseModel):
    """Activity log entry response."""

    id: UUID
    user_id: str
    event_type: str
    entity_type: str
    entity_id: UUID
    timestamp: datetime
    details: dict[str, Any]
    correlation_id: Optional[str] = None

    class Config:
        from_attributes = True


class ActivityListResponse(BaseModel):
    """Paginated activity list response."""

    data: list[ActivityLogResponse]
    pagination: dict[str, Any]


class ProductivitySummaryResponse(BaseModel):
    """Productivity summary response."""

    period_days: int
    start_date: str
    end_date: str
    tasks_completed: int
    tasks_created: int
    tasks_deleted: int
    net_tasks: int
    completion_rate: float
    completions_by_day: list[dict[str, Any]]


class ActivityTypeCount(BaseModel):
    """Activity type with count."""

    event_type: str
    count: int


# =============================================================================
# Endpoints
# =============================================================================


@router.get("", response_model=ActivityListResponse)
async def list_activities(
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    entity_id: Optional[UUID] = Query(None, description="Filter by entity ID"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    start_date: Optional[datetime] = Query(None, description="Filter activities after this date"),
    end_date: Optional[datetime] = Query(None, description="Filter activities before this date"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id),
) -> ActivityListResponse:
    """List activity log entries with filtering and pagination.

    Returns activities for the authenticated user only, with optional filters
    for entity type, entity ID, event type, and date range.

    Args:
        entity_type: Filter by entity type (task, reminder, tag)
        entity_id: Filter by specific entity ID
        event_type: Filter by event type (e.g., task.created)
        start_date: Filter activities after this date
        end_date: Filter activities before this date
        page: Page number (1-indexed)
        limit: Items per page (max 100)

    Returns:
        Paginated list of activity log entries
    """
    service = ActivityService(session)
    activities, total = await service.get_activities(
        user_id=user_id,
        entity_type=entity_type,
        entity_id=entity_id,
        event_type=event_type,
        start_date=start_date,
        end_date=end_date,
        page=page,
        limit=limit,
    )

    return ActivityListResponse(
        data=[ActivityLogResponse.model_validate(a) for a in activities],
        pagination={
            "page": page,
            "limit": limit,
            "total_items": total,
            "total_pages": (total + limit - 1) // limit,
        },
    )


@router.get("/productivity", response_model=ProductivitySummaryResponse)
async def get_productivity_summary(
    days: int = Query(7, ge=1, le=365, description="Number of days to include"),
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id),
) -> ProductivitySummaryResponse:
    """Get productivity summary for the authenticated user.

    Returns metrics including:
    - Tasks completed in the period
    - Tasks created in the period
    - Net tasks (created - deleted)
    - Completion rate
    - Daily breakdown of completions

    Args:
        days: Number of days to include in the summary (default: 7)

    Returns:
        Productivity summary with metrics and daily breakdown
    """
    service = ActivityService(session)
    summary = await service.get_productivity_summary(user_id=user_id, days=days)
    return ProductivitySummaryResponse(**summary)


@router.get("/types", response_model=list[ActivityTypeCount])
async def get_activity_types(
    limit: int = Query(10, ge=1, le=50, description="Maximum types to return"),
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id),
) -> list[ActivityTypeCount]:
    """Get activity types with counts for the authenticated user.

    Returns the most common activity types for the user, useful for
    filtering the activity log.

    Args:
        limit: Maximum number of activity types to return

    Returns:
        List of activity types with their counts
    """
    service = ActivityService(session)
    types = await service.get_recent_activity_types(user_id=user_id, limit=limit)
    return [ActivityTypeCount(**t) for t in types]


@router.get("/{activity_id}", response_model=ActivityLogResponse)
async def get_activity(
    activity_id: UUID,
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id),
) -> ActivityLogResponse:
    """Get a specific activity log entry.

    Args:
        activity_id: The activity ID to retrieve

    Returns:
        The activity log entry

    Raises:
        404: If activity not found or doesn't belong to user
    """
    service = ActivityService(session)
    activity = await service.get_activity_by_id(activity_id, user_id)

    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    return ActivityLogResponse.model_validate(activity)


@router.get("/entity/{entity_type}/{entity_id}", response_model=list[ActivityLogResponse])
async def get_entity_history(
    entity_type: str,
    entity_id: UUID,
    limit: int = Query(100, ge=1, le=500, description="Maximum entries to return"),
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id),
) -> list[ActivityLogResponse]:
    """Get the complete activity history for a specific entity.

    Useful for viewing the audit trail of a task, reminder, or tag.

    Args:
        entity_type: Type of entity (task, reminder, tag)
        entity_id: The entity ID
        limit: Maximum entries to return

    Returns:
        List of activity log entries for the entity
    """
    service = ActivityService(session)
    activities = await service.get_entity_history(
        entity_type=entity_type,
        entity_id=entity_id,
        user_id=user_id,
        limit=limit,
    )

    return [ActivityLogResponse.model_validate(a) for a in activities]
