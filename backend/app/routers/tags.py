"""Tag endpoints for CRUD operations."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import func

from app.database import get_session
from app.dependencies.auth import get_current_user_id
from app.models import Tag, TaskTag
from app.services.tag_service import TagService

router = APIRouter(prefix="/tags", tags=["Tags"])


class TagCreate(BaseModel):
    """Schema for creating a new tag."""

    name: str = Field(min_length=1, max_length=50)
    color: str | None = Field(
        default=None,
        max_length=7,
        pattern=r"^#[0-9A-Fa-f]{6}$",
        description="Hex color code (e.g., #3B82F6)",
    )


class TagWithCount(BaseModel):
    """Schema for tag response with task count."""

    id: uuid.UUID
    name: str
    color: str | None = None
    task_count: int = 0

    model_config = {"from_attributes": True}


class TagListResponse(BaseModel):
    """Schema for tag list response."""

    data: list[TagWithCount]


async def get_task_count_for_tag(session: AsyncSession, tag_id: uuid.UUID) -> int:
    """Get the number of tasks associated with a tag."""
    result = await session.execute(
        select(func.count()).select_from(TaskTag).where(TaskTag.tag_id == tag_id)
    )
    return result.scalar_one()


@router.get("", response_model=TagListResponse)
async def list_tags(
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> TagListResponse:
    """List all tags for the current user with task counts."""
    tag_service = TagService(session)
    tags = await tag_service.get_tags(user_id)

    tags_with_counts = []
    for tag in tags:
        task_count = await get_task_count_for_tag(session, tag.id)
        tags_with_counts.append(
            TagWithCount(
                id=tag.id,
                name=tag.name,
                color=tag.color,
                task_count=task_count,
            )
        )

    return TagListResponse(data=tags_with_counts)


@router.post("", response_model=TagWithCount, status_code=status.HTTP_201_CREATED)
async def create_tag(
    data: TagCreate,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> TagWithCount:
    """Create a new tag."""
    tag_service = TagService(session)

    # Check if tag with this name already exists
    existing = await tag_service.get_tag_by_name(data.name, user_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Tag with name '{data.name}' already exists",
        )

    tag = await tag_service.create_tag(data.name, user_id, data.color)
    return TagWithCount(
        id=tag.id,
        name=tag.name,
        color=tag.color,
        task_count=0,
    )


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> None:
    """Delete a tag (removes from all tasks)."""
    tag_service = TagService(session)
    deleted = await tag_service.delete_tag(tag_id, user_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )
