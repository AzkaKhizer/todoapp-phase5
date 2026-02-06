"""Unit tests for ActivityService.

Tests cover:
- Logging activity entries
- Querying activities with filters
- Getting activity by ID
- Getting entity history
- Productivity summary calculations
- Activity type counts
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest
import pytest_asyncio

from app.models.activity_log import ActivityLogEntry
from app.services.activity_service import ActivityService


@pytest.fixture
def mock_session():
    """Create a mock async session."""
    session = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    return session


@pytest.fixture
def test_user_id():
    """Generate a test user ID."""
    return f"test-user-{uuid4().hex[:8]}"


@pytest.fixture
def activity_service(mock_session):
    """Create an ActivityService instance with mock session."""
    return ActivityService(mock_session)


class TestLogActivity:
    """Tests for logging activity entries."""

    @pytest.mark.asyncio
    async def test_log_activity_basic(
        self,
        activity_service: ActivityService,
        mock_session: AsyncMock,
        test_user_id: str,
    ):
        """Test basic activity logging."""
        entity_id = uuid4()

        # Configure mock to refresh the entry
        async def mock_refresh(entry):
            entry.id = uuid4()

        mock_session.refresh.side_effect = mock_refresh

        entry = await activity_service.log_activity(
            user_id=test_user_id,
            event_type="task.created",
            entity_type="task",
            entity_id=entity_id,
        )

        # Verify session methods were called
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

        # Verify entry attributes
        assert entry.user_id == test_user_id
        assert entry.event_type == "task.created"
        assert entry.entity_type == "task"
        assert entry.entity_id == entity_id

    @pytest.mark.asyncio
    async def test_log_activity_with_details(
        self,
        activity_service: ActivityService,
        mock_session: AsyncMock,
        test_user_id: str,
    ):
        """Test logging activity with additional details."""
        entity_id = uuid4()
        details = {"title": "Test Task", "priority": "high"}

        async def mock_refresh(entry):
            entry.id = uuid4()

        mock_session.refresh.side_effect = mock_refresh

        entry = await activity_service.log_activity(
            user_id=test_user_id,
            event_type="task.created",
            entity_type="task",
            entity_id=entity_id,
            details=details,
        )

        assert entry.details == details

    @pytest.mark.asyncio
    async def test_log_activity_with_correlation_id(
        self,
        activity_service: ActivityService,
        mock_session: AsyncMock,
        test_user_id: str,
    ):
        """Test logging activity with correlation ID."""
        entity_id = uuid4()
        correlation_id = "req-12345"

        async def mock_refresh(entry):
            entry.id = uuid4()

        mock_session.refresh.side_effect = mock_refresh

        entry = await activity_service.log_activity(
            user_id=test_user_id,
            event_type="task.updated",
            entity_type="task",
            entity_id=entity_id,
            correlation_id=correlation_id,
        )

        assert entry.correlation_id == correlation_id

    @pytest.mark.asyncio
    async def test_log_activity_with_custom_timestamp(
        self,
        activity_service: ActivityService,
        mock_session: AsyncMock,
        test_user_id: str,
    ):
        """Test logging activity with custom timestamp."""
        entity_id = uuid4()
        custom_time = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)

        async def mock_refresh(entry):
            entry.id = uuid4()

        mock_session.refresh.side_effect = mock_refresh

        entry = await activity_service.log_activity(
            user_id=test_user_id,
            event_type="task.completed",
            entity_type="task",
            entity_id=entity_id,
            timestamp=custom_time,
        )

        assert entry.timestamp == custom_time


class TestGetActivities:
    """Tests for querying activities with filtering."""

    @pytest.mark.asyncio
    async def test_get_activities_basic(
        self,
        activity_service: ActivityService,
        mock_session: AsyncMock,
        test_user_id: str,
    ):
        """Test basic activity listing."""
        # Setup mock results
        mock_activities = [
            ActivityLogEntry(
                id=uuid4(),
                user_id=test_user_id,
                event_type="task.created",
                entity_type="task",
                entity_id=uuid4(),
                timestamp=datetime.now(timezone.utc),
            ),
        ]

        # Mock count query
        count_result = MagicMock()
        count_result.scalar_one.return_value = 1

        # Mock data query
        data_result = MagicMock()
        data_result.scalars.return_value.all.return_value = mock_activities

        mock_session.execute.side_effect = [count_result, data_result]

        activities, total = await activity_service.get_activities(user_id=test_user_id)

        assert len(activities) == 1
        assert total == 1

    @pytest.mark.asyncio
    async def test_get_activities_with_entity_filter(
        self,
        activity_service: ActivityService,
        mock_session: AsyncMock,
        test_user_id: str,
    ):
        """Test filtering activities by entity type."""
        count_result = MagicMock()
        count_result.scalar_one.return_value = 0

        data_result = MagicMock()
        data_result.scalars.return_value.all.return_value = []

        mock_session.execute.side_effect = [count_result, data_result]

        activities, total = await activity_service.get_activities(
            user_id=test_user_id,
            entity_type="task",
        )

        # Verify execute was called twice (count + data)
        assert mock_session.execute.call_count == 2

    @pytest.mark.asyncio
    async def test_get_activities_with_date_range(
        self,
        activity_service: ActivityService,
        mock_session: AsyncMock,
        test_user_id: str,
    ):
        """Test filtering activities by date range."""
        start_date = datetime.now(timezone.utc) - timedelta(days=7)
        end_date = datetime.now(timezone.utc)

        count_result = MagicMock()
        count_result.scalar_one.return_value = 0

        data_result = MagicMock()
        data_result.scalars.return_value.all.return_value = []

        mock_session.execute.side_effect = [count_result, data_result]

        activities, total = await activity_service.get_activities(
            user_id=test_user_id,
            start_date=start_date,
            end_date=end_date,
        )

        assert mock_session.execute.call_count == 2

    @pytest.mark.asyncio
    async def test_get_activities_pagination(
        self,
        activity_service: ActivityService,
        mock_session: AsyncMock,
        test_user_id: str,
    ):
        """Test activity pagination."""
        count_result = MagicMock()
        count_result.scalar_one.return_value = 100

        data_result = MagicMock()
        data_result.scalars.return_value.all.return_value = []

        mock_session.execute.side_effect = [count_result, data_result]

        activities, total = await activity_service.get_activities(
            user_id=test_user_id,
            page=2,
            limit=10,
        )

        assert total == 100


class TestGetActivityById:
    """Tests for getting a specific activity."""

    @pytest.mark.asyncio
    async def test_get_activity_found(
        self,
        activity_service: ActivityService,
        mock_session: AsyncMock,
        test_user_id: str,
    ):
        """Test getting an existing activity."""
        activity_id = uuid4()
        mock_activity = ActivityLogEntry(
            id=activity_id,
            user_id=test_user_id,
            event_type="task.created",
            entity_type="task",
            entity_id=uuid4(),
            timestamp=datetime.now(timezone.utc),
        )

        result = MagicMock()
        result.scalar_one_or_none.return_value = mock_activity
        mock_session.execute.return_value = result

        activity = await activity_service.get_activity_by_id(activity_id, test_user_id)

        assert activity is not None
        assert activity.id == activity_id

    @pytest.mark.asyncio
    async def test_get_activity_not_found(
        self,
        activity_service: ActivityService,
        mock_session: AsyncMock,
        test_user_id: str,
    ):
        """Test getting a non-existent activity."""
        activity_id = uuid4()

        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = result

        activity = await activity_service.get_activity_by_id(activity_id, test_user_id)

        assert activity is None


class TestGetEntityHistory:
    """Tests for getting entity history."""

    @pytest.mark.asyncio
    async def test_get_entity_history(
        self,
        activity_service: ActivityService,
        mock_session: AsyncMock,
        test_user_id: str,
    ):
        """Test getting history for a specific entity."""
        entity_id = uuid4()
        mock_activities = [
            ActivityLogEntry(
                id=uuid4(),
                user_id=test_user_id,
                event_type="task.created",
                entity_type="task",
                entity_id=entity_id,
                timestamp=datetime.now(timezone.utc) - timedelta(hours=2),
            ),
            ActivityLogEntry(
                id=uuid4(),
                user_id=test_user_id,
                event_type="task.updated",
                entity_type="task",
                entity_id=entity_id,
                timestamp=datetime.now(timezone.utc) - timedelta(hours=1),
            ),
            ActivityLogEntry(
                id=uuid4(),
                user_id=test_user_id,
                event_type="task.completed",
                entity_type="task",
                entity_id=entity_id,
                timestamp=datetime.now(timezone.utc),
            ),
        ]

        result = MagicMock()
        result.scalars.return_value.all.return_value = mock_activities
        mock_session.execute.return_value = result

        history = await activity_service.get_entity_history(
            entity_type="task",
            entity_id=entity_id,
            user_id=test_user_id,
        )

        assert len(history) == 3
        assert all(h.entity_id == entity_id for h in history)


class TestGetProductivitySummary:
    """Tests for productivity summary calculations."""

    @pytest.mark.asyncio
    async def test_get_productivity_summary(
        self,
        activity_service: ActivityService,
        mock_session: AsyncMock,
        test_user_id: str,
    ):
        """Test productivity summary calculation."""
        # Mock completed count
        completed_result = MagicMock()
        completed_result.scalar_one.return_value = 10

        # Mock created count
        created_result = MagicMock()
        created_result.scalar_one.return_value = 15

        # Mock deleted count
        deleted_result = MagicMock()
        deleted_result.scalar_one.return_value = 2

        # Mock completions by day
        day_result = MagicMock()
        day_result.all.return_value = [
            (datetime.now(timezone.utc) - timedelta(days=1),),
            (datetime.now(timezone.utc) - timedelta(days=1),),
            (datetime.now(timezone.utc),),
        ]

        mock_session.execute.side_effect = [
            completed_result,
            created_result,
            deleted_result,
            day_result,
        ]

        summary = await activity_service.get_productivity_summary(
            user_id=test_user_id,
            days=7,
        )

        assert summary["period_days"] == 7
        assert summary["tasks_completed"] == 10
        assert summary["tasks_created"] == 15
        assert summary["tasks_deleted"] == 2
        assert summary["net_tasks"] == 13  # 15 - 2
        assert "completion_rate" in summary
        assert "completions_by_day" in summary

    @pytest.mark.asyncio
    async def test_get_productivity_summary_empty(
        self,
        activity_service: ActivityService,
        mock_session: AsyncMock,
        test_user_id: str,
    ):
        """Test productivity summary with no activity."""
        # All counts are zero
        for _ in range(3):
            result = MagicMock()
            result.scalar_one.return_value = 0
            mock_session.execute.return_value = result

        # Empty completions
        day_result = MagicMock()
        day_result.all.return_value = []

        mock_session.execute.side_effect = [
            MagicMock(scalar_one=MagicMock(return_value=0)),
            MagicMock(scalar_one=MagicMock(return_value=0)),
            MagicMock(scalar_one=MagicMock(return_value=0)),
            day_result,
        ]

        summary = await activity_service.get_productivity_summary(
            user_id=test_user_id,
            days=7,
        )

        assert summary["tasks_completed"] == 0
        assert summary["tasks_created"] == 0
        assert summary["completion_rate"] == 0


class TestGetRecentActivityTypes:
    """Tests for getting activity type counts."""

    @pytest.mark.asyncio
    async def test_get_recent_activity_types(
        self,
        activity_service: ActivityService,
        mock_session: AsyncMock,
        test_user_id: str,
    ):
        """Test getting activity type counts."""
        mock_types = [
            ("task.created", 25),
            ("task.completed", 20),
            ("task.updated", 15),
        ]

        result = MagicMock()
        result.all.return_value = mock_types
        mock_session.execute.return_value = result

        types = await activity_service.get_recent_activity_types(
            user_id=test_user_id,
            limit=10,
        )

        assert len(types) == 3
        assert types[0]["event_type"] == "task.created"
        assert types[0]["count"] == 25
