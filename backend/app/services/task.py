"""Task service for CRUD operations."""

import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import func, select

from app.exceptions import AuthorizationError, NotFoundError
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskPatch, TaskUpdate


async def create_task(
    session: AsyncSession,
    user_id: uuid.UUID,
    data: TaskCreate,
) -> Task:
    """Create a new task for a user."""
    task = Task(
        title=data.title,
        description=data.description,
        user_id=user_id,
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


async def get_tasks(
    session: AsyncSession,
    user_id: uuid.UUID,
    limit: int = 100,
    offset: int = 0,
) -> tuple[list[Task], int]:
    """Get paginated tasks for a user."""
    # Get total count
    count_query = select(func.count()).select_from(Task).where(Task.user_id == user_id)
    total_result = await session.execute(count_query)
    total = total_result.scalar_one()

    # Get tasks
    query = (
        select(Task)
        .where(Task.user_id == user_id)
        .order_by(Task.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(query)
    tasks = list(result.scalars().all())

    return tasks, total


async def get_task_by_id(
    session: AsyncSession,
    task_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Task:
    """Get a task by ID, ensuring user ownership."""
    query = select(Task).where(Task.id == task_id)
    result = await session.execute(query)
    task = result.scalar_one_or_none()

    if not task:
        raise NotFoundError("Task not found")

    if task.user_id != user_id:
        raise AuthorizationError("You don't have permission to access this task")

    return task


async def update_task(
    session: AsyncSession,
    task_id: uuid.UUID,
    user_id: uuid.UUID,
    data: TaskUpdate,
) -> Task:
    """Full update of a task."""
    task = await get_task_by_id(session, task_id, user_id)

    task.title = data.title
    task.description = data.description
    task.updated_at = datetime.utcnow()

    session.add(task)
    await session.commit()
    await session.refresh(task)

    return task


async def patch_task(
    session: AsyncSession,
    task_id: uuid.UUID,
    user_id: uuid.UUID,
    data: TaskPatch,
) -> Task:
    """Partial update of a task."""
    task = await get_task_by_id(session, task_id, user_id)

    if data.title is not None:
        task.title = data.title
    if data.description is not None:
        task.description = data.description
    if data.is_complete is not None:
        task.is_complete = data.is_complete

    task.updated_at = datetime.utcnow()

    session.add(task)
    await session.commit()
    await session.refresh(task)

    return task


async def delete_task(
    session: AsyncSession,
    task_id: uuid.UUID,
    user_id: uuid.UUID,
) -> None:
    """Delete a task."""
    task = await get_task_by_id(session, task_id, user_id)
    await session.delete(task)
    await session.commit()


async def toggle_task(
    session: AsyncSession,
    task_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Task:
    """Toggle task completion status."""
    task = await get_task_by_id(session, task_id, user_id)

    task.is_complete = not task.is_complete
    task.updated_at = datetime.utcnow()

    session.add(task)
    await session.commit()
    await session.refresh(task)

    return task
