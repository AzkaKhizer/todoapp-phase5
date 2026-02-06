"""Integration tests for the recurring task system.

These tests verify the complete recurring task workflow:
1. Creating a task with a recurrence pattern
2. Completing the task
3. Verifying the next occurrence is generated
4. Verifying recurrence end dates are respected

Run with: pytest tests/integration/test_recurrence.py -v
"""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.recurrence import RecurrencePattern, RecurrenceType
from app.models.task import Task, TaskPriority
from app.services.recurrence_service import RecurrenceService


@pytest_asyncio.fixture
async def test_user_id():
    """Generate a test user ID."""
    return f"test-user-{uuid4().hex[:8]}"


@pytest_asyncio.fixture
async def recurrence_service(async_session: AsyncSession):
    """Create a RecurrenceService instance."""
    return RecurrenceService(async_session)


@pytest_asyncio.fixture
async def daily_pattern(
    async_session: AsyncSession,
    test_user_id: str,
) -> RecurrencePattern:
    """Create a daily recurrence pattern."""
    pattern = RecurrencePattern(
        type=RecurrenceType.DAILY,
        interval=1,
        user_id=test_user_id,
    )
    async_session.add(pattern)
    await async_session.commit()
    await async_session.refresh(pattern)
    return pattern


@pytest_asyncio.fixture
async def weekly_pattern(
    async_session: AsyncSession,
    test_user_id: str,
) -> RecurrencePattern:
    """Create a weekly recurrence pattern."""
    pattern = RecurrencePattern(
        type=RecurrenceType.WEEKLY,
        interval=1,
        days_of_week=[0, 2, 4],  # Mon, Wed, Fri
        user_id=test_user_id,
    )
    async_session.add(pattern)
    await async_session.commit()
    await async_session.refresh(pattern)
    return pattern


@pytest_asyncio.fixture
async def monthly_pattern(
    async_session: AsyncSession,
    test_user_id: str,
) -> RecurrencePattern:
    """Create a monthly recurrence pattern."""
    pattern = RecurrencePattern(
        type=RecurrenceType.MONTHLY,
        interval=1,
        day_of_month=15,
        user_id=test_user_id,
    )
    async_session.add(pattern)
    await async_session.commit()
    await async_session.refresh(pattern)
    return pattern


@pytest_asyncio.fixture
async def recurring_task(
    async_session: AsyncSession,
    test_user_id: str,
    daily_pattern: RecurrencePattern,
) -> Task:
    """Create a task with daily recurrence."""
    due_date = datetime.now(timezone.utc) + timedelta(hours=1)
    task = Task(
        title="Daily Standup",
        description="Daily standup meeting",
        user_id=test_user_id,
        due_date=due_date,
        priority=TaskPriority.HIGH,
        recurrence_id=daily_pattern.id,
    )
    async_session.add(task)
    await async_session.commit()
    await async_session.refresh(task)
    return task


class TestRecurrencePatternCreation:
    """Test creating recurrence patterns."""

    @pytest.mark.asyncio
    async def test_create_daily_pattern(
        self,
        recurrence_service: RecurrenceService,
        test_user_id: str,
    ):
        """Test creating a daily recurrence pattern."""
        pattern = await recurrence_service.create_pattern(
            user_id=test_user_id,
            type=RecurrenceType.DAILY,
            interval=1,
        )

        assert pattern.id is not None
        assert pattern.type == RecurrenceType.DAILY
        assert pattern.interval == 1
        assert pattern.user_id == test_user_id

    @pytest.mark.asyncio
    async def test_create_weekly_pattern(
        self,
        recurrence_service: RecurrenceService,
        test_user_id: str,
    ):
        """Test creating a weekly recurrence pattern with specific days."""
        pattern = await recurrence_service.create_pattern(
            user_id=test_user_id,
            type=RecurrenceType.WEEKLY,
            interval=2,
            days_of_week=[0, 4],  # Mon, Fri
        )

        assert pattern.type == RecurrenceType.WEEKLY
        assert pattern.interval == 2
        assert pattern.days_of_week == [0, 4]

    @pytest.mark.asyncio
    async def test_create_monthly_pattern(
        self,
        recurrence_service: RecurrenceService,
        test_user_id: str,
    ):
        """Test creating a monthly recurrence pattern."""
        pattern = await recurrence_service.create_pattern(
            user_id=test_user_id,
            type=RecurrenceType.MONTHLY,
            interval=1,
            day_of_month=15,
        )

        assert pattern.type == RecurrenceType.MONTHLY
        assert pattern.day_of_month == 15

    @pytest.mark.asyncio
    async def test_create_yearly_pattern_with_end_date(
        self,
        recurrence_service: RecurrenceService,
        test_user_id: str,
    ):
        """Test creating a yearly recurrence pattern with end date."""
        end_date = datetime.now(timezone.utc) + timedelta(days=365 * 5)
        pattern = await recurrence_service.create_pattern(
            user_id=test_user_id,
            type=RecurrenceType.YEARLY,
            interval=1,
            month_of_year=12,
            day_of_month=25,
            end_date=end_date,
        )

        assert pattern.type == RecurrenceType.YEARLY
        assert pattern.month_of_year == 12
        assert pattern.day_of_month == 25
        assert pattern.end_date == end_date


class TestNextOccurrenceGeneration:
    """Test generating next task occurrences."""

    @pytest.mark.asyncio
    async def test_generate_next_daily_task(
        self,
        recurrence_service: RecurrenceService,
        recurring_task: Task,
    ):
        """Test generating next occurrence for daily recurring task."""
        # Mark original task as complete
        recurring_task.is_complete = True

        # Generate next occurrence
        new_task = await recurrence_service.generate_next_task(recurring_task)

        assert new_task is not None
        assert new_task.id != recurring_task.id
        assert new_task.title == recurring_task.title
        assert new_task.user_id == recurring_task.user_id
        assert new_task.recurrence_id == recurring_task.recurrence_id
        assert new_task.is_complete is False

        # Verify due date is next day
        assert new_task.due_date > recurring_task.due_date
        expected_due = recurring_task.due_date + timedelta(days=1)
        assert abs((new_task.due_date - expected_due).total_seconds()) < 1

    @pytest.mark.asyncio
    async def test_generate_next_task_preserves_properties(
        self,
        recurrence_service: RecurrenceService,
        recurring_task: Task,
    ):
        """Test that generated task preserves original properties."""
        recurring_task.is_complete = True
        recurring_task.description = "Important meeting"
        recurring_task.priority = TaskPriority.URGENT
        recurring_task.reminder_offset_minutes = 30

        new_task = await recurrence_service.generate_next_task(recurring_task)

        assert new_task.description == "Important meeting"
        assert new_task.priority == TaskPriority.URGENT
        assert new_task.reminder_offset_minutes == 30

    @pytest.mark.asyncio
    async def test_generate_sets_parent_task_id(
        self,
        recurrence_service: RecurrenceService,
        recurring_task: Task,
    ):
        """Test that generated task has parent_task_id set."""
        recurring_task.is_complete = True

        new_task = await recurrence_service.generate_next_task(recurring_task)

        # First generation links to original
        assert new_task.parent_task_id == recurring_task.id

        # Second generation links to original (not the previous occurrence)
        new_task.is_complete = True
        third_task = await recurrence_service.generate_next_task(new_task)

        assert third_task.parent_task_id == recurring_task.id

    @pytest.mark.asyncio
    async def test_no_generation_for_non_recurring_task(
        self,
        recurrence_service: RecurrenceService,
        async_session: AsyncSession,
        test_user_id: str,
    ):
        """Test that non-recurring tasks don't generate new instances."""
        task = Task(
            title="One-time task",
            user_id=test_user_id,
            recurrence_id=None,
        )
        async_session.add(task)
        await async_session.commit()
        await async_session.refresh(task)

        task.is_complete = True
        new_task = await recurrence_service.generate_next_task(task)

        assert new_task is None


class TestEndDateHandling:
    """Test recurrence end date handling."""

    @pytest.mark.asyncio
    async def test_no_generation_after_end_date(
        self,
        recurrence_service: RecurrenceService,
        async_session: AsyncSession,
        test_user_id: str,
    ):
        """Test that no task is generated after end date."""
        # Create pattern with end date in the past
        pattern = RecurrencePattern(
            type=RecurrenceType.DAILY,
            interval=1,
            end_date=datetime.now(timezone.utc) - timedelta(days=1),
            user_id=test_user_id,
        )
        async_session.add(pattern)
        await async_session.commit()

        task = Task(
            title="Ended recurring task",
            user_id=test_user_id,
            due_date=datetime.now(timezone.utc),
            recurrence_id=pattern.id,
            is_complete=True,
        )
        async_session.add(task)
        await async_session.commit()
        await async_session.refresh(task)

        new_task = await recurrence_service.generate_next_task(task)

        assert new_task is None


class TestPatternManagement:
    """Test pattern CRUD operations."""

    @pytest.mark.asyncio
    async def test_get_pattern_by_id(
        self,
        recurrence_service: RecurrenceService,
        daily_pattern: RecurrencePattern,
    ):
        """Test retrieving a pattern by ID."""
        pattern = await recurrence_service.get_pattern_by_id(daily_pattern.id)

        assert pattern is not None
        assert pattern.id == daily_pattern.id

    @pytest.mark.asyncio
    async def test_delete_pattern(
        self,
        recurrence_service: RecurrenceService,
        async_session: AsyncSession,
        test_user_id: str,
    ):
        """Test deleting a pattern."""
        pattern = await recurrence_service.create_pattern(
            user_id=test_user_id,
            type=RecurrenceType.DAILY,
            interval=1,
        )

        deleted = await recurrence_service.delete_pattern(pattern.id, test_user_id)
        assert deleted is True

        # Verify deletion
        found = await recurrence_service.get_pattern_by_id(pattern.id)
        assert found is None

    @pytest.mark.asyncio
    async def test_delete_pattern_unauthorized(
        self,
        recurrence_service: RecurrenceService,
        daily_pattern: RecurrencePattern,
    ):
        """Test that users can't delete other users' patterns."""
        deleted = await recurrence_service.delete_pattern(
            daily_pattern.id,
            "different-user",
        )
        assert deleted is False

    @pytest.mark.asyncio
    async def test_get_patterns_for_user(
        self,
        recurrence_service: RecurrenceService,
        daily_pattern: RecurrencePattern,
        weekly_pattern: RecurrencePattern,
        test_user_id: str,
    ):
        """Test retrieving all patterns for a user."""
        patterns = await recurrence_service.get_patterns_for_user(test_user_id)

        assert len(patterns) >= 2
        pattern_ids = [p.id for p in patterns]
        assert daily_pattern.id in pattern_ids
        assert weekly_pattern.id in pattern_ids


class TestEdgeCases:
    """Test edge cases in recurrence calculations."""

    @pytest.mark.asyncio
    async def test_monthly_feb_30_to_feb_28(
        self,
        recurrence_service: RecurrenceService,
        async_session: AsyncSession,
        test_user_id: str,
    ):
        """Test monthly recurrence from Jan 30 to Feb (non-leap year)."""
        pattern = RecurrencePattern(
            type=RecurrenceType.MONTHLY,
            interval=1,
            day_of_month=30,
            user_id=test_user_id,
        )
        async_session.add(pattern)
        await async_session.commit()

        # January 30, 2023 (non-leap year)
        task = Task(
            title="Monthly task",
            user_id=test_user_id,
            due_date=datetime(2023, 1, 30, 10, 0, 0, tzinfo=timezone.utc),
            recurrence_id=pattern.id,
            is_complete=True,
        )
        async_session.add(task)
        await async_session.commit()
        await async_session.refresh(task)

        new_task = await recurrence_service.generate_next_task(task)

        # Feb 2023 has 28 days
        assert new_task.due_date.month == 2
        assert new_task.due_date.day == 28

    @pytest.mark.asyncio
    async def test_monthly_feb_30_leap_year(
        self,
        recurrence_service: RecurrenceService,
        async_session: AsyncSession,
        test_user_id: str,
    ):
        """Test monthly recurrence from Jan 30 to Feb (leap year)."""
        pattern = RecurrencePattern(
            type=RecurrenceType.MONTHLY,
            interval=1,
            day_of_month=30,
            user_id=test_user_id,
        )
        async_session.add(pattern)
        await async_session.commit()

        # January 30, 2024 (leap year)
        task = Task(
            title="Monthly task",
            user_id=test_user_id,
            due_date=datetime(2024, 1, 30, 10, 0, 0, tzinfo=timezone.utc),
            recurrence_id=pattern.id,
            is_complete=True,
        )
        async_session.add(task)
        await async_session.commit()
        await async_session.refresh(task)

        new_task = await recurrence_service.generate_next_task(task)

        # Feb 2024 has 29 days
        assert new_task.due_date.month == 2
        assert new_task.due_date.day == 29
