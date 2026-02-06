"""Unit tests for RecurrenceService date calculations.

These tests verify the correctness of recurrence pattern calculations
without requiring database access.

Run with: pytest tests/unit/test_recurrence_service.py -v
"""

import calendar
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.recurrence import RecurrencePattern, RecurrenceType
from app.services.recurrence_service import (
    RecurrenceService,
    describe_pattern,
    get_day_name,
)


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def mock_session():
    """Create a mock database session."""
    return AsyncMock()


@pytest.fixture
def recurrence_service(mock_session):
    """Create a RecurrenceService with mock session."""
    return RecurrenceService(mock_session)


def create_pattern(
    type: RecurrenceType,
    interval: int = 1,
    days_of_week: list[int] | None = None,
    day_of_month: int | None = None,
    month_of_year: int | None = None,
    end_date: datetime | None = None,
) -> RecurrencePattern:
    """Helper to create a RecurrencePattern for testing."""
    pattern = MagicMock(spec=RecurrencePattern)
    pattern.type = type
    pattern.interval = interval
    pattern.days_of_week = days_of_week
    pattern.day_of_month = day_of_month
    pattern.month_of_year = month_of_year
    pattern.end_date = end_date
    return pattern


# =============================================================================
# Daily Recurrence Tests
# =============================================================================


class TestDailyRecurrence:
    """Tests for daily recurrence pattern."""

    def test_daily_next_day(self, recurrence_service):
        """Test daily recurrence with interval of 1."""
        pattern = create_pattern(RecurrenceType.DAILY, interval=1)
        from_date = datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc)

        result = recurrence_service._calculate_next_date(pattern, from_date)

        assert result == datetime(2024, 1, 16, 10, 0, 0, tzinfo=timezone.utc)

    def test_daily_every_3_days(self, recurrence_service):
        """Test daily recurrence with interval of 3."""
        pattern = create_pattern(RecurrenceType.DAILY, interval=3)
        from_date = datetime(2024, 1, 15, 9, 0, 0, tzinfo=timezone.utc)

        result = recurrence_service._calculate_next_date(pattern, from_date)

        assert result == datetime(2024, 1, 18, 9, 0, 0, tzinfo=timezone.utc)

    def test_daily_month_boundary(self, recurrence_service):
        """Test daily recurrence crossing month boundary."""
        pattern = create_pattern(RecurrenceType.DAILY, interval=1)
        from_date = datetime(2024, 1, 31, 12, 0, 0, tzinfo=timezone.utc)

        result = recurrence_service._calculate_next_date(pattern, from_date)

        assert result == datetime(2024, 2, 1, 12, 0, 0, tzinfo=timezone.utc)

    def test_daily_year_boundary(self, recurrence_service):
        """Test daily recurrence crossing year boundary."""
        pattern = create_pattern(RecurrenceType.DAILY, interval=1)
        from_date = datetime(2024, 12, 31, 12, 0, 0, tzinfo=timezone.utc)

        result = recurrence_service._calculate_next_date(pattern, from_date)

        assert result == datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


# =============================================================================
# Weekly Recurrence Tests
# =============================================================================


class TestWeeklyRecurrence:
    """Tests for weekly recurrence pattern."""

    def test_weekly_same_day(self, recurrence_service):
        """Test weekly recurrence with no specific days (same day next week)."""
        pattern = create_pattern(RecurrenceType.WEEKLY, interval=1, days_of_week=None)
        # Monday, Jan 15, 2024
        from_date = datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc)

        result = recurrence_service._calculate_next_date(pattern, from_date)

        # Should be next Monday, Jan 22
        assert result == datetime(2024, 1, 22, 10, 0, 0, tzinfo=timezone.utc)

    def test_weekly_next_day_same_week(self, recurrence_service):
        """Test weekly recurrence with next day later in same week."""
        pattern = create_pattern(RecurrenceType.WEEKLY, interval=1, days_of_week=[2, 4])
        # Monday (0), should go to Wednesday (2)
        from_date = datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc)  # Monday

        result = recurrence_service._calculate_next_date(pattern, from_date)

        # Should be Wednesday, Jan 17
        assert result == datetime(2024, 1, 17, 10, 0, 0, tzinfo=timezone.utc)

    def test_weekly_next_week(self, recurrence_service):
        """Test weekly recurrence when current day is after all specified days."""
        pattern = create_pattern(RecurrenceType.WEEKLY, interval=1, days_of_week=[0, 2])
        # Friday (4), should go to Monday next week
        from_date = datetime(2024, 1, 19, 10, 0, 0, tzinfo=timezone.utc)  # Friday

        result = recurrence_service._calculate_next_date(pattern, from_date)

        # Should be Monday, Jan 22
        assert result == datetime(2024, 1, 22, 10, 0, 0, tzinfo=timezone.utc)

    def test_weekly_every_2_weeks(self, recurrence_service):
        """Test bi-weekly recurrence."""
        pattern = create_pattern(RecurrenceType.WEEKLY, interval=2, days_of_week=[0])
        # Monday, Jan 15
        from_date = datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc)

        result = recurrence_service._calculate_next_date(pattern, from_date)

        # Should be Monday, Jan 29 (2 weeks later)
        assert result == datetime(2024, 1, 29, 10, 0, 0, tzinfo=timezone.utc)


# =============================================================================
# Monthly Recurrence Tests
# =============================================================================


class TestMonthlyRecurrence:
    """Tests for monthly recurrence pattern."""

    def test_monthly_same_day(self, recurrence_service):
        """Test monthly recurrence on same day number."""
        pattern = create_pattern(RecurrenceType.MONTHLY, interval=1, day_of_month=15)
        from_date = datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc)

        result = recurrence_service._calculate_next_date(pattern, from_date)

        assert result == datetime(2024, 2, 15, 10, 0, 0, tzinfo=timezone.utc)

    def test_monthly_jan_to_feb_28(self, recurrence_service):
        """Test monthly recurrence from Jan 30 to Feb (should use Feb 28)."""
        pattern = create_pattern(RecurrenceType.MONTHLY, interval=1, day_of_month=30)
        from_date = datetime(2024, 1, 30, 10, 0, 0, tzinfo=timezone.utc)

        result = recurrence_service._calculate_next_date(pattern, from_date)

        # 2024 is a leap year, so Feb has 29 days, but we want 30 -> 29
        assert result == datetime(2024, 2, 29, 10, 0, 0, tzinfo=timezone.utc)

    def test_monthly_feb_29_non_leap_year(self, recurrence_service):
        """Test monthly recurrence from Feb 29 in non-leap year."""
        pattern = create_pattern(RecurrenceType.MONTHLY, interval=1, day_of_month=29)
        from_date = datetime(2023, 1, 29, 10, 0, 0, tzinfo=timezone.utc)

        result = recurrence_service._calculate_next_date(pattern, from_date)

        # 2023 Feb has 28 days
        assert result == datetime(2023, 2, 28, 10, 0, 0, tzinfo=timezone.utc)

    def test_monthly_jan_31_to_feb(self, recurrence_service):
        """Test monthly recurrence from Jan 31 to Feb (last day handling)."""
        pattern = create_pattern(RecurrenceType.MONTHLY, interval=1, day_of_month=31)
        from_date = datetime(2024, 1, 31, 10, 0, 0, tzinfo=timezone.utc)

        result = recurrence_service._calculate_next_date(pattern, from_date)

        # Feb 2024 has 29 days (leap year)
        assert result == datetime(2024, 2, 29, 10, 0, 0, tzinfo=timezone.utc)

    def test_monthly_every_3_months(self, recurrence_service):
        """Test quarterly recurrence."""
        pattern = create_pattern(RecurrenceType.MONTHLY, interval=3, day_of_month=15)
        from_date = datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc)

        result = recurrence_service._calculate_next_date(pattern, from_date)

        assert result == datetime(2024, 4, 15, 10, 0, 0, tzinfo=timezone.utc)

    def test_monthly_year_rollover(self, recurrence_service):
        """Test monthly recurrence crossing year boundary."""
        pattern = create_pattern(RecurrenceType.MONTHLY, interval=1, day_of_month=15)
        from_date = datetime(2024, 12, 15, 10, 0, 0, tzinfo=timezone.utc)

        result = recurrence_service._calculate_next_date(pattern, from_date)

        assert result == datetime(2025, 1, 15, 10, 0, 0, tzinfo=timezone.utc)


# =============================================================================
# Yearly Recurrence Tests
# =============================================================================


class TestYearlyRecurrence:
    """Tests for yearly recurrence pattern."""

    def test_yearly_same_date(self, recurrence_service):
        """Test yearly recurrence on same date."""
        pattern = create_pattern(
            RecurrenceType.YEARLY,
            interval=1,
            month_of_year=3,
            day_of_month=15,
        )
        from_date = datetime(2024, 3, 15, 10, 0, 0, tzinfo=timezone.utc)

        result = recurrence_service._calculate_next_date(pattern, from_date)

        assert result == datetime(2025, 3, 15, 10, 0, 0, tzinfo=timezone.utc)

    def test_yearly_feb_29_to_non_leap_year(self, recurrence_service):
        """Test yearly recurrence from Feb 29 to non-leap year."""
        pattern = create_pattern(
            RecurrenceType.YEARLY,
            interval=1,
            month_of_year=2,
            day_of_month=29,
        )
        from_date = datetime(2024, 2, 29, 10, 0, 0, tzinfo=timezone.utc)  # Leap year

        result = recurrence_service._calculate_next_date(pattern, from_date)

        # 2025 is not a leap year, should use Feb 28
        assert result == datetime(2025, 2, 28, 10, 0, 0, tzinfo=timezone.utc)

    def test_yearly_every_2_years(self, recurrence_service):
        """Test biennial recurrence."""
        pattern = create_pattern(
            RecurrenceType.YEARLY,
            interval=2,
            month_of_year=6,
            day_of_month=1,
        )
        from_date = datetime(2024, 6, 1, 10, 0, 0, tzinfo=timezone.utc)

        result = recurrence_service._calculate_next_date(pattern, from_date)

        assert result == datetime(2026, 6, 1, 10, 0, 0, tzinfo=timezone.utc)


# =============================================================================
# End Date Tests
# =============================================================================


class TestEndDate:
    """Tests for recurrence end date handling."""

    @pytest.mark.asyncio
    async def test_no_occurrence_after_end_date(self, recurrence_service):
        """Test that no occurrence is returned after end date."""
        pattern = create_pattern(
            RecurrenceType.DAILY,
            interval=1,
            end_date=datetime(2024, 1, 20, 0, 0, 0, tzinfo=timezone.utc),
        )
        from_date = datetime(2024, 1, 21, 10, 0, 0, tzinfo=timezone.utc)

        result = await recurrence_service.calculate_next_occurrence(pattern, from_date)

        assert result is None

    @pytest.mark.asyncio
    async def test_occurrence_before_end_date(self, recurrence_service):
        """Test that occurrence is returned before end date."""
        pattern = create_pattern(
            RecurrenceType.DAILY,
            interval=1,
            end_date=datetime(2024, 1, 20, 0, 0, 0, tzinfo=timezone.utc),
        )
        from_date = datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc)

        result = await recurrence_service.calculate_next_occurrence(pattern, from_date)

        assert result == datetime(2024, 1, 16, 10, 0, 0, tzinfo=timezone.utc)


# =============================================================================
# Helper Function Tests
# =============================================================================


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_get_day_name(self):
        """Test day name conversion."""
        assert get_day_name(0) == "Monday"
        assert get_day_name(6) == "Sunday"
        assert get_day_name(3) == "Thursday"

    def test_describe_pattern_daily(self):
        """Test daily pattern description."""
        pattern = create_pattern(RecurrenceType.DAILY, interval=1)
        assert describe_pattern(pattern) == "Every day"

        pattern = create_pattern(RecurrenceType.DAILY, interval=3)
        assert describe_pattern(pattern) == "Every 3 days"

    def test_describe_pattern_weekly(self):
        """Test weekly pattern description."""
        pattern = create_pattern(
            RecurrenceType.WEEKLY,
            interval=1,
            days_of_week=[0, 2, 4],
        )
        result = describe_pattern(pattern)
        assert "Monday" in result
        assert "Wednesday" in result
        assert "Friday" in result

    def test_describe_pattern_monthly(self):
        """Test monthly pattern description."""
        pattern = create_pattern(RecurrenceType.MONTHLY, interval=1, day_of_month=15)
        assert "15th" in describe_pattern(pattern)

        pattern = create_pattern(RecurrenceType.MONTHLY, interval=1, day_of_month=1)
        assert "1st" in describe_pattern(pattern)

        pattern = create_pattern(RecurrenceType.MONTHLY, interval=1, day_of_month=2)
        assert "2nd" in describe_pattern(pattern)

        pattern = create_pattern(RecurrenceType.MONTHLY, interval=1, day_of_month=3)
        assert "3rd" in describe_pattern(pattern)

    def test_describe_pattern_yearly(self):
        """Test yearly pattern description."""
        pattern = create_pattern(
            RecurrenceType.YEARLY,
            interval=1,
            month_of_year=3,
            day_of_month=15,
        )
        result = describe_pattern(pattern)
        assert "March" in result
        assert "15" in result
