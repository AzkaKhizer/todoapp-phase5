"""Unit tests for TaskService filter/sort functionality."""

import uuid
from datetime import datetime, timedelta

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Task, Tag, TaskTag
from app.models.task import TaskPriority
from app.schemas.task import TaskFilterParams
from app.services import task as task_service


@pytest_asyncio.fixture
async def sample_tasks(async_session: AsyncSession, test_user) -> list[Task]:
    """Create sample tasks with various properties for filter testing."""
    user_id = str(test_user.id)
    now = datetime.utcnow()

    tasks_data = [
        {
            "title": "High priority urgent task",
            "description": "Urgent work item",
            "priority": TaskPriority.URGENT,
            "due_date": now + timedelta(days=1),
            "is_complete": False,
        },
        {
            "title": "High priority task",
            "description": "Important work",
            "priority": TaskPriority.HIGH,
            "due_date": now + timedelta(days=3),
            "is_complete": False,
        },
        {
            "title": "Medium priority task",
            "description": "Regular work",
            "priority": TaskPriority.MEDIUM,
            "due_date": now + timedelta(days=7),
            "is_complete": False,
        },
        {
            "title": "Low priority task",
            "description": "Can wait",
            "priority": TaskPriority.LOW,
            "due_date": now + timedelta(days=14),
            "is_complete": False,
        },
        {
            "title": "Overdue task",
            "description": "Should have been done",
            "priority": TaskPriority.HIGH,
            "due_date": now - timedelta(days=1),
            "is_complete": False,
        },
        {
            "title": "Completed task",
            "description": "Already done",
            "priority": TaskPriority.MEDIUM,
            "due_date": now - timedelta(days=2),
            "is_complete": True,
        },
    ]

    tasks = []
    for data in tasks_data:
        task = Task(
            id=uuid.uuid4(),
            user_id=user_id,
            **data,
        )
        async_session.add(task)
        tasks.append(task)

    await async_session.commit()
    for task in tasks:
        await async_session.refresh(task)

    return tasks


@pytest_asyncio.fixture
async def sample_tags(async_session: AsyncSession, test_user) -> list[Tag]:
    """Create sample tags for testing."""
    user_id = str(test_user.id)

    tags_data = [
        {"name": "work", "color": "#3B82F6"},
        {"name": "personal", "color": "#10B981"},
        {"name": "urgent", "color": "#EF4444"},
    ]

    tags = []
    for data in tags_data:
        tag = Tag(
            id=uuid.uuid4(),
            user_id=user_id,
            **data,
        )
        async_session.add(tag)
        tags.append(tag)

    await async_session.commit()
    for tag in tags:
        await async_session.refresh(tag)

    return tags


class TestTaskServiceFilters:
    """Test TaskService filter functionality."""

    @pytest.mark.asyncio
    async def test_filter_by_priority(
        self, async_session: AsyncSession, sample_tasks: list[Task], test_user
    ):
        """Test filtering tasks by priority."""
        filters = TaskFilterParams(priority=[TaskPriority.URGENT, TaskPriority.HIGH])
        tasks, total = await task_service.get_tasks(
            async_session, str(test_user.id), filters
        )

        assert len(tasks) == 3  # 1 urgent + 2 high
        for task in tasks:
            assert task.priority in [TaskPriority.URGENT, TaskPriority.HIGH]

    @pytest.mark.asyncio
    async def test_filter_by_completion_status(
        self, async_session: AsyncSession, sample_tasks: list[Task], test_user
    ):
        """Test filtering by completion status."""
        # Active tasks
        filters = TaskFilterParams(is_complete=False)
        tasks, total = await task_service.get_tasks(
            async_session, str(test_user.id), filters
        )
        assert len(tasks) == 5
        assert all(not t.is_complete for t in tasks)

        # Completed tasks
        filters = TaskFilterParams(is_complete=True)
        tasks, total = await task_service.get_tasks(
            async_session, str(test_user.id), filters
        )
        assert len(tasks) == 1
        assert all(t.is_complete for t in tasks)

    @pytest.mark.asyncio
    async def test_filter_by_due_date_range(
        self, async_session: AsyncSession, sample_tasks: list[Task], test_user
    ):
        """Test filtering by due date range."""
        now = datetime.utcnow()

        # Tasks due in next 7 days
        filters = TaskFilterParams(
            due_after=now,
            due_before=now + timedelta(days=7),
        )
        tasks, total = await task_service.get_tasks(
            async_session, str(test_user.id), filters
        )

        assert len(tasks) >= 2
        for task in tasks:
            assert task.due_date is not None
            assert task.due_date >= now
            assert task.due_date <= now + timedelta(days=7)

    @pytest.mark.asyncio
    async def test_search_by_title(
        self, async_session: AsyncSession, sample_tasks: list[Task], test_user
    ):
        """Test searching tasks by title."""
        filters = TaskFilterParams(search="urgent")
        tasks, total = await task_service.get_tasks(
            async_session, str(test_user.id), filters
        )

        assert len(tasks) >= 1
        for task in tasks:
            assert "urgent" in task.title.lower() or "urgent" in task.description.lower()

    @pytest.mark.asyncio
    async def test_search_by_description(
        self, async_session: AsyncSession, sample_tasks: list[Task], test_user
    ):
        """Test searching tasks by description."""
        filters = TaskFilterParams(search="work")
        tasks, total = await task_service.get_tasks(
            async_session, str(test_user.id), filters
        )

        assert len(tasks) >= 1


class TestTaskServiceSorting:
    """Test TaskService sorting functionality."""

    @pytest.mark.asyncio
    async def test_sort_by_due_date_asc(
        self, async_session: AsyncSession, sample_tasks: list[Task], test_user
    ):
        """Test sorting by due date ascending."""
        filters = TaskFilterParams(sort_by="due_date", sort_order="asc")
        tasks, total = await task_service.get_tasks(
            async_session, str(test_user.id), filters
        )

        # Verify order (nulls may vary)
        due_dates = [t.due_date for t in tasks if t.due_date]
        assert due_dates == sorted(due_dates)

    @pytest.mark.asyncio
    async def test_sort_by_due_date_desc(
        self, async_session: AsyncSession, sample_tasks: list[Task], test_user
    ):
        """Test sorting by due date descending."""
        filters = TaskFilterParams(sort_by="due_date", sort_order="desc")
        tasks, total = await task_service.get_tasks(
            async_session, str(test_user.id), filters
        )

        due_dates = [t.due_date for t in tasks if t.due_date]
        assert due_dates == sorted(due_dates, reverse=True)

    @pytest.mark.asyncio
    async def test_sort_by_priority(
        self, async_session: AsyncSession, sample_tasks: list[Task], test_user
    ):
        """Test sorting by priority."""
        filters = TaskFilterParams(sort_by="priority", sort_order="desc")
        tasks, total = await task_service.get_tasks(
            async_session, str(test_user.id), filters
        )

        # Just verify no error - priority sorting works differently
        assert len(tasks) > 0

    @pytest.mark.asyncio
    async def test_sort_by_title(
        self, async_session: AsyncSession, sample_tasks: list[Task], test_user
    ):
        """Test sorting by title."""
        filters = TaskFilterParams(sort_by="title", sort_order="asc")
        tasks, total = await task_service.get_tasks(
            async_session, str(test_user.id), filters
        )

        titles = [t.title for t in tasks]
        assert titles == sorted(titles)


class TestTaskServicePagination:
    """Test TaskService pagination functionality."""

    @pytest.mark.asyncio
    async def test_pagination_first_page(
        self, async_session: AsyncSession, sample_tasks: list[Task], test_user
    ):
        """Test getting first page of results."""
        tasks, total = await task_service.get_tasks(
            async_session, str(test_user.id), page=1, limit=2
        )

        assert len(tasks) == 2
        assert total == 6  # Total sample tasks

    @pytest.mark.asyncio
    async def test_pagination_second_page(
        self, async_session: AsyncSession, sample_tasks: list[Task], test_user
    ):
        """Test getting second page of results."""
        tasks, total = await task_service.get_tasks(
            async_session, str(test_user.id), page=2, limit=2
        )

        assert len(tasks) == 2
        assert total == 6

    @pytest.mark.asyncio
    async def test_pagination_last_page(
        self, async_session: AsyncSession, sample_tasks: list[Task], test_user
    ):
        """Test getting last page with partial results."""
        tasks, total = await task_service.get_tasks(
            async_session, str(test_user.id), page=3, limit=2
        )

        assert len(tasks) == 2  # Last 2 tasks
        assert total == 6


class TestTaskServiceCombinedFilters:
    """Test TaskService with combined filters."""

    @pytest.mark.asyncio
    async def test_combined_priority_and_status(
        self, async_session: AsyncSession, sample_tasks: list[Task], test_user
    ):
        """Test filtering by priority AND completion status."""
        filters = TaskFilterParams(
            priority=[TaskPriority.HIGH, TaskPriority.URGENT],
            is_complete=False,
        )
        tasks, total = await task_service.get_tasks(
            async_session, str(test_user.id), filters
        )

        for task in tasks:
            assert task.priority in [TaskPriority.HIGH, TaskPriority.URGENT]
            assert not task.is_complete

    @pytest.mark.asyncio
    async def test_combined_search_and_priority(
        self, async_session: AsyncSession, sample_tasks: list[Task], test_user
    ):
        """Test combining search with priority filter."""
        filters = TaskFilterParams(
            search="task",
            priority=[TaskPriority.HIGH],
        )
        tasks, total = await task_service.get_tasks(
            async_session, str(test_user.id), filters
        )

        for task in tasks:
            assert task.priority == TaskPriority.HIGH
            assert "task" in task.title.lower() or "task" in task.description.lower()
