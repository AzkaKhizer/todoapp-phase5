"""Task service for CRUD operations with filtering, sorting, and search."""

import uuid
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import func, select

from app.exceptions import AuthorizationError, NotFoundError
from app.models import RecurrencePattern, Reminder, Tag, Task, TaskTag
from app.models.task import TaskPriority
from app.schemas.task import TaskCreate, TaskFilterParams, TaskPatch, TaskUpdate
from app.services.tag_service import TagService


async def create_task(
    session: AsyncSession,
    user_id: str,
    data: TaskCreate,
) -> Task:
    """Create a new task for a user with optional tags, reminder, and recurrence."""
    # Create recurrence pattern if provided
    recurrence_id = None
    if data.recurrence:
        recurrence = RecurrencePattern(
            type=data.recurrence.type,
            interval=data.recurrence.interval,
            days_of_week=data.recurrence.days_of_week,
            day_of_month=data.recurrence.day_of_month,
            end_date=data.recurrence.end_date,
            user_id=user_id,
        )
        session.add(recurrence)
        await session.flush()
        recurrence_id = recurrence.id

    task = Task(
        title=data.title,
        description=data.description,
        user_id=user_id,
        due_date=data.due_date,
        priority=data.priority,
        reminder_offset_minutes=data.reminder_offset_minutes,
        recurrence_id=recurrence_id,
    )
    session.add(task)
    await session.flush()

    # Handle tags
    if data.tags:
        tag_service = TagService(session)
        tags = await tag_service.get_tags_by_names(data.tags, user_id)
        for tag in tags:
            task_tag = TaskTag(task_id=task.id, tag_id=tag.id)
            session.add(task_tag)

    # Create reminder if due_date and reminder_offset are set
    if data.due_date and data.reminder_offset_minutes is not None:
        scheduled_time = data.due_date - timedelta(minutes=data.reminder_offset_minutes)
        reminder = Reminder(
            task_id=task.id,
            user_id=user_id,
            scheduled_time=scheduled_time,
        )
        session.add(reminder)

    await session.commit()
    await session.refresh(task)
    return task


async def get_tasks(
    session: AsyncSession,
    user_id: str,
    filters: TaskFilterParams | None = None,
    page: int = 1,
    limit: int = 20,
) -> tuple[list[Task], int]:
    """Get paginated tasks for a user with filtering and sorting."""
    if filters is None:
        filters = TaskFilterParams()

    # Build base query
    query = select(Task).where(Task.user_id == user_id)
    count_query = select(func.count()).select_from(Task).where(Task.user_id == user_id)

    # Apply filters
    conditions = []

    # Search filter (title or description)
    if filters.search:
        search_term = f"%{filters.search}%"
        conditions.append(
            or_(
                Task.title.ilike(search_term),
                Task.description.ilike(search_term),
            )
        )

    # Priority filter
    if filters.priority:
        conditions.append(Task.priority.in_(filters.priority))

    # Due date filters
    if filters.due_before:
        conditions.append(Task.due_date <= filters.due_before)
    if filters.due_after:
        conditions.append(Task.due_date >= filters.due_after)

    # Completion status filter
    if filters.is_complete is not None:
        conditions.append(Task.is_complete == filters.is_complete)

    # Apply all conditions
    if conditions:
        query = query.where(and_(*conditions))
        count_query = count_query.where(and_(*conditions))

    # Apply sorting
    sort_column = getattr(Task, filters.sort_by)
    if filters.sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Get total count
    total_result = await session.execute(count_query)
    total = total_result.scalar_one()

    # Apply pagination
    offset = (page - 1) * limit
    query = query.limit(limit).offset(offset)

    # Execute query
    result = await session.execute(query)
    tasks = list(result.scalars().all())

    # Filter by tags if specified (post-query filter for now)
    if filters.tags:
        filtered_tasks = []
        for task in tasks:
            task_tags = await get_task_tags(session, task.id)
            tag_names = [t.name for t in task_tags]
            if any(tag in tag_names for tag in filters.tags):
                filtered_tasks.append(task)
        tasks = filtered_tasks

    return tasks, total


async def get_task_tags(session: AsyncSession, task_id: uuid.UUID) -> list[Tag]:
    """Get tags for a task."""
    query = (
        select(Tag)
        .join(TaskTag, Tag.id == TaskTag.tag_id)
        .where(TaskTag.task_id == task_id)
    )
    result = await session.execute(query)
    return list(result.scalars().all())


async def get_task_by_id(
    session: AsyncSession,
    task_id: uuid.UUID,
    user_id: str,
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


async def get_task_with_details(
    session: AsyncSession,
    task_id: uuid.UUID,
    user_id: str,
) -> dict[str, Any]:
    """Get a task with tags, reminder, and recurrence details."""
    task = await get_task_by_id(session, task_id, user_id)

    # Get tags
    tags = await get_task_tags(session, task_id)

    # Get reminder
    reminder_query = select(Reminder).where(
        Reminder.task_id == task_id,
        Reminder.status == "pending",
    )
    reminder_result = await session.execute(reminder_query)
    reminder = reminder_result.scalar_one_or_none()

    # Get recurrence
    recurrence = None
    if task.recurrence_id:
        recurrence_query = select(RecurrencePattern).where(
            RecurrencePattern.id == task.recurrence_id
        )
        recurrence_result = await session.execute(recurrence_query)
        recurrence = recurrence_result.scalar_one_or_none()

    return {
        "task": task,
        "tags": tags,
        "reminder": reminder,
        "recurrence": recurrence,
    }


async def update_task(
    session: AsyncSession,
    task_id: uuid.UUID,
    user_id: str,
    data: TaskUpdate,
) -> Task:
    """Full update of a task."""
    task = await get_task_by_id(session, task_id, user_id)

    task.title = data.title
    task.description = data.description
    task.due_date = data.due_date
    task.priority = data.priority
    task.updated_at = datetime.utcnow()

    # Update reminder_offset_minutes
    task.reminder_offset_minutes = data.reminder_offset_minutes

    # Update tags: remove existing, add new
    delete_query = TaskTag.__table__.delete().where(TaskTag.task_id == task_id)
    await session.execute(delete_query)

    if data.tags:
        tag_service = TagService(session)
        tags = await tag_service.get_tags_by_names(data.tags, user_id)
        for tag in tags:
            task_tag = TaskTag(task_id=task.id, tag_id=tag.id)
            session.add(task_tag)

    # Update or create reminder
    if data.due_date and data.reminder_offset_minutes is not None:
        scheduled_time = data.due_date - timedelta(minutes=data.reminder_offset_minutes)
        # Cancel existing reminder
        existing_reminder = await session.execute(
            select(Reminder).where(Reminder.task_id == task_id, Reminder.status == "pending")
        )
        existing = existing_reminder.scalar_one_or_none()
        if existing:
            existing.scheduled_time = scheduled_time
        else:
            reminder = Reminder(
                task_id=task.id,
                user_id=user_id,
                scheduled_time=scheduled_time,
            )
            session.add(reminder)

    session.add(task)
    await session.commit()
    await session.refresh(task)

    return task


async def patch_task(
    session: AsyncSession,
    task_id: uuid.UUID,
    user_id: str,
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
    if data.due_date is not None:
        task.due_date = data.due_date
    if data.priority is not None:
        task.priority = data.priority
    if data.reminder_offset_minutes is not None:
        task.reminder_offset_minutes = data.reminder_offset_minutes

    # Update tags if provided
    if data.tags is not None:
        delete_query = TaskTag.__table__.delete().where(TaskTag.task_id == task_id)
        await session.execute(delete_query)

        if data.tags:
            tag_service = TagService(session)
            tags = await tag_service.get_tags_by_names(data.tags, user_id)
            for tag in tags:
                task_tag = TaskTag(task_id=task.id, tag_id=tag.id)
                session.add(task_tag)

    task.updated_at = datetime.utcnow()

    session.add(task)
    await session.commit()
    await session.refresh(task)

    return task


async def delete_task(
    session: AsyncSession,
    task_id: uuid.UUID,
    user_id: str,
) -> None:
    """Delete a task."""
    task = await get_task_by_id(session, task_id, user_id)
    await session.delete(task)
    await session.commit()


async def toggle_task(
    session: AsyncSession,
    task_id: uuid.UUID,
    user_id: str,
) -> Task:
    """Toggle task completion status."""
    task = await get_task_by_id(session, task_id, user_id)

    task.is_complete = not task.is_complete
    task.updated_at = datetime.utcnow()

    # If completing a task, cancel pending reminders
    if task.is_complete:
        reminder_query = select(Reminder).where(
            Reminder.task_id == task_id,
            Reminder.status == "pending",
        )
        result = await session.execute(reminder_query)
        for reminder in result.scalars().all():
            reminder.status = "cancelled"
            session.add(reminder)

    session.add(task)
    await session.commit()
    await session.refresh(task)

    return task


async def build_task_response(
    session: AsyncSession,
    task: Task,
) -> dict[str, Any]:
    """Build task response with tags, reminder, and recurrence."""
    tags = await get_task_tags(session, task.id)

    # Get reminder
    reminder_query = select(Reminder).where(
        Reminder.task_id == task.id,
        Reminder.status == "pending",
    )
    reminder_result = await session.execute(reminder_query)
    reminder = reminder_result.scalar_one_or_none()

    # Get recurrence
    recurrence = None
    if task.recurrence_id:
        recurrence_query = select(RecurrencePattern).where(
            RecurrencePattern.id == task.recurrence_id
        )
        recurrence_result = await session.execute(recurrence_query)
        recurrence = recurrence_result.scalar_one_or_none()

    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "is_complete": task.is_complete,
        "user_id": task.user_id,
        "due_date": task.due_date,
        "priority": task.priority,
        "tags": [{"id": t.id, "name": t.name, "color": t.color} for t in tags],
        "reminder": {
            "id": reminder.id,
            "scheduled_time": reminder.scheduled_time,
            "status": reminder.status,
        } if reminder else None,
        "recurrence": {
            "id": recurrence.id,
            "type": recurrence.type,
            "interval": recurrence.interval,
            "days_of_week": recurrence.days_of_week,
            "day_of_month": recurrence.day_of_month,
            "end_date": recurrence.end_date,
        } if recurrence else None,
        "is_overdue": task.is_overdue,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
    }
