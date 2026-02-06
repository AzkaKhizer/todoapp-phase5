"""Task endpoints for CRUD operations."""

import uuid
from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.dependencies.auth import get_current_user_id
from app.models.task import TaskPriority
from app.schemas.auth import MessageResponse
from app.schemas.task import (
    PaginationInfo,
    TaskCreate,
    TaskFilterParams,
    TaskListResponse,
    TaskPatch,
    TaskResponse,
    TaskUpdate,
)
from app.services import task as task_service

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    page: int = Query(default=1, ge=1, description="Page number"),
    limit: int = Query(default=20, ge=1, le=100, description="Items per page"),
    search: str | None = Query(default=None, description="Full-text search on title/description"),
    priority: str | None = Query(default=None, description="Filter by priority (comma-separated: low,medium,high,urgent)"),
    due_before: datetime | None = Query(default=None, description="Tasks due before this date (ISO 8601)"),
    due_after: datetime | None = Query(default=None, description="Tasks due after this date (ISO 8601)"),
    tags: str | None = Query(default=None, description="Filter by tag names (comma-separated)"),
    is_complete: bool | None = Query(default=None, description="Filter by completion status"),
    sort_by: Literal["due_date", "priority", "created_at", "title"] = Query(default="created_at", description="Sort field"),
    sort_order: Literal["asc", "desc"] = Query(default="desc", description="Sort direction"),
    include_overdue: bool = Query(default=True, description="Include overdue indicator in response"),
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> TaskListResponse:
    """List tasks with filtering, sorting, and pagination."""
    # Parse comma-separated priority values
    priority_list: list[TaskPriority] | None = None
    if priority:
        priority_list = [TaskPriority(p.strip()) for p in priority.split(",")]

    # Parse comma-separated tag names
    tags_list: list[str] | None = None
    if tags:
        tags_list = [t.strip() for t in tags.split(",")]

    # Build filter params
    filters = TaskFilterParams(
        search=search,
        priority=priority_list,
        due_before=due_before,
        due_after=due_after,
        tags=tags_list,
        is_complete=is_complete,
        sort_by=sort_by,
        sort_order=sort_order,
        include_overdue=include_overdue,
    )

    tasks, total = await task_service.get_tasks(session, user_id, filters, page, limit)

    # Build task responses with details
    task_responses = []
    for task in tasks:
        response_dict = await task_service.build_task_response(session, task)
        task_responses.append(TaskResponse(**response_dict))

    # Calculate pagination
    total_pages = (total + limit - 1) // limit if total > 0 else 1

    return TaskListResponse(
        data=task_responses,
        pagination=PaginationInfo(
            page=page,
            limit=limit,
            total_items=total,
            total_pages=total_pages,
        ),
    )


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    data: TaskCreate,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> TaskResponse:
    """Create a new task."""
    task = await task_service.create_task(session, user_id, data)
    return TaskResponse.model_validate(task)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> TaskResponse:
    """Get a specific task."""
    task = await task_service.get_task_by_id(session, task_id, user_id)
    return TaskResponse.model_validate(task)


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: uuid.UUID,
    data: TaskUpdate,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> TaskResponse:
    """Full update of a task."""
    task = await task_service.update_task(session, task_id, user_id, data)
    return TaskResponse.model_validate(task)


@router.patch("/{task_id}", response_model=TaskResponse)
async def patch_task(
    task_id: uuid.UUID,
    data: TaskPatch,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> TaskResponse:
    """Partial update of a task."""
    task = await task_service.patch_task(session, task_id, user_id, data)
    return TaskResponse.model_validate(task)


@router.delete("/{task_id}", response_model=MessageResponse)
async def delete_task(
    task_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> MessageResponse:
    """Delete a task."""
    await task_service.delete_task(session, task_id, user_id)
    return MessageResponse(message="Task deleted successfully")


@router.patch("/{task_id}/toggle", response_model=TaskResponse)
async def toggle_task(
    task_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> TaskResponse:
    """Toggle task completion status."""
    task = await task_service.toggle_task(session, task_id, user_id)
    return TaskResponse.model_validate(task)
