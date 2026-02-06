"""Recurrence service for managing recurring task patterns.

This service handles:
- Calculating the next occurrence date for recurring tasks
- Generating new task instances when recurring tasks are completed
- Handling edge cases (Feb 30, last day of month, etc.)
- Managing recurrence pattern lifecycle
"""

import calendar
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.recurrence import RecurrencePattern, RecurrenceType
from app.models.task import Task, TaskPriority

logger = logging.getLogger(__name__)


class RecurrenceService:
    """Service for managing recurring task patterns.

    The recurrence workflow:
    1. When a task with recurrence_id is marked complete, this service is called
    2. It calculates the next occurrence date based on the pattern
    3. A new task instance is created with the same properties but new due_date
    4. The new task maintains a link to the original via parent_task_id

    Supported patterns:
    - daily: Every N days
    - weekly: Every N weeks on specific days (Mon=0, Sun=6)
    - monthly: Every N months on specific day (handles last-day scenarios)
    - yearly: Every N years on specific date
    - custom: N-day intervals
    """

    def __init__(self, session: AsyncSession):
        """Initialize the recurrence service.

        Args:
            session: Database session for queries
        """
        self.session = session

    async def calculate_next_occurrence(
        self,
        pattern: RecurrencePattern,
        from_date: datetime,
    ) -> Optional[datetime]:
        """Calculate the next occurrence date based on the recurrence pattern.

        Args:
            pattern: The recurrence pattern
            from_date: The reference date (usually the previous due date)

        Returns:
            The next occurrence datetime, or None if recurrence has ended
        """
        # Check if we've passed the end date
        if pattern.end_date and from_date >= pattern.end_date:
            logger.info(f"Recurrence {pattern.id} has ended (end_date: {pattern.end_date})")
            return None

        next_date = self._calculate_next_date(pattern, from_date)

        # Check if calculated date exceeds end date
        if pattern.end_date and next_date > pattern.end_date:
            logger.info(f"Next occurrence {next_date} exceeds end_date {pattern.end_date}")
            return None

        return next_date

    def _calculate_next_date(
        self,
        pattern: RecurrencePattern,
        from_date: datetime,
    ) -> datetime:
        """Internal method to calculate the next date based on pattern type."""
        if pattern.type == RecurrenceType.DAILY:
            return self._next_daily(from_date, pattern.interval)

        elif pattern.type == RecurrenceType.WEEKLY:
            return self._next_weekly(from_date, pattern.interval, pattern.days_of_week)

        elif pattern.type == RecurrenceType.MONTHLY:
            return self._next_monthly(from_date, pattern.interval, pattern.day_of_month)

        elif pattern.type == RecurrenceType.YEARLY:
            return self._next_yearly(
                from_date,
                pattern.interval,
                pattern.month_of_year,
                pattern.day_of_month,
            )

        elif pattern.type == RecurrenceType.CUSTOM:
            # Custom is treated like daily with specified interval
            return self._next_daily(from_date, pattern.interval)

        else:
            raise ValueError(f"Unknown recurrence type: {pattern.type}")

    def _next_daily(self, from_date: datetime, interval: int) -> datetime:
        """Calculate next occurrence for daily recurrence."""
        return from_date + timedelta(days=interval)

    def _next_weekly(
        self,
        from_date: datetime,
        interval: int,
        days_of_week: list[int] | None,
    ) -> datetime:
        """Calculate next occurrence for weekly recurrence.

        Args:
            from_date: Reference date
            interval: Number of weeks between occurrences
            days_of_week: List of weekdays (0=Monday, 6=Sunday)

        Returns:
            Next occurrence date
        """
        if not days_of_week:
            # If no specific days, use same day of week
            return from_date + timedelta(weeks=interval)

        # Sort days to find next occurrence
        sorted_days = sorted(days_of_week)
        current_weekday = from_date.weekday()

        # Try to find next day in current week
        for day in sorted_days:
            if day > current_weekday:
                days_until = day - current_weekday
                return from_date + timedelta(days=days_until)

        # No more days this week, go to first day of next interval
        # Calculate days to next Monday
        days_until_monday = (7 - current_weekday) % 7 or 7
        # Add interval weeks minus 1 (since we're already advancing to next week)
        next_week_start = from_date + timedelta(days=days_until_monday + 7 * (interval - 1))
        # Add days to first occurrence in that week
        return next_week_start + timedelta(days=sorted_days[0])

    def _next_monthly(
        self,
        from_date: datetime,
        interval: int,
        day_of_month: int | None,
    ) -> datetime:
        """Calculate next occurrence for monthly recurrence.

        Handles edge cases like:
        - Feb 30 -> Feb 28/29
        - Jan 31 -> Feb 28/29 (last day of month)

        Args:
            from_date: Reference date
            interval: Number of months between occurrences
            day_of_month: Target day (1-31), or None for same day

        Returns:
            Next occurrence date
        """
        target_day = day_of_month or from_date.day

        # Calculate target month/year
        month = from_date.month + interval
        year = from_date.year

        # Handle year rollover
        while month > 12:
            month -= 12
            year += 1

        # Get the last day of target month
        last_day = calendar.monthrange(year, month)[1]

        # Handle "last day of month" logic
        # If target_day is > last day of month, use last day
        actual_day = min(target_day, last_day)

        # Preserve time component
        return from_date.replace(
            year=year,
            month=month,
            day=actual_day,
        )

    def _next_yearly(
        self,
        from_date: datetime,
        interval: int,
        month_of_year: int | None,
        day_of_month: int | None,
    ) -> datetime:
        """Calculate next occurrence for yearly recurrence.

        Handles edge cases like Feb 29 in non-leap years.

        Args:
            from_date: Reference date
            interval: Number of years between occurrences
            month_of_year: Target month (1-12), or None for same month
            day_of_month: Target day (1-31), or None for same day

        Returns:
            Next occurrence date
        """
        target_year = from_date.year + interval
        target_month = month_of_year or from_date.month
        target_day = day_of_month or from_date.day

        # Handle Feb 29 in non-leap years
        if target_month == 2 and target_day == 29:
            if not calendar.isleap(target_year):
                target_day = 28

        # Handle day overflow for any month
        last_day = calendar.monthrange(target_year, target_month)[1]
        actual_day = min(target_day, last_day)

        return from_date.replace(
            year=target_year,
            month=target_month,
            day=actual_day,
        )

    async def generate_next_task(
        self,
        completed_task: Task,
    ) -> Optional[Task]:
        """Generate the next task instance for a recurring task.

        Called when a task with recurrence_id is marked as complete.

        Args:
            completed_task: The task that was just completed

        Returns:
            The newly created task, or None if recurrence has ended
        """
        if not completed_task.recurrence_id:
            logger.debug(f"Task {completed_task.id} has no recurrence pattern")
            return None

        # Get the recurrence pattern
        pattern = await self._get_pattern(completed_task.recurrence_id)
        if not pattern:
            logger.warning(f"Recurrence pattern {completed_task.recurrence_id} not found")
            return None

        # Calculate next occurrence
        reference_date = completed_task.due_date or datetime.now(timezone.utc)
        next_due_date = await self.calculate_next_occurrence(pattern, reference_date)

        if not next_due_date:
            logger.info(f"No more occurrences for task {completed_task.id}")
            return None

        # Create new task instance
        new_task = Task(
            title=completed_task.title,
            description=completed_task.description,
            user_id=completed_task.user_id,
            due_date=next_due_date,
            priority=completed_task.priority,
            reminder_offset_minutes=completed_task.reminder_offset_minutes,
            recurrence_id=completed_task.recurrence_id,
            parent_task_id=completed_task.parent_task_id or completed_task.id,
            is_complete=False,
        )

        self.session.add(new_task)
        await self.session.commit()
        await self.session.refresh(new_task)

        logger.info(
            f"Generated next occurrence {new_task.id} for task {completed_task.id}, "
            f"due_date: {next_due_date}"
        )

        return new_task

    async def create_pattern(
        self,
        user_id: str,
        type: RecurrenceType,
        interval: int = 1,
        days_of_week: list[int] | None = None,
        day_of_month: int | None = None,
        month_of_year: int | None = None,
        end_date: datetime | None = None,
    ) -> RecurrencePattern:
        """Create a new recurrence pattern.

        Args:
            user_id: Owner of the pattern
            type: Type of recurrence
            interval: Number of units between occurrences
            days_of_week: For weekly, which days (0=Mon, 6=Sun)
            day_of_month: For monthly/yearly, which day
            month_of_year: For yearly, which month
            end_date: Optional end date

        Returns:
            The created RecurrencePattern
        """
        # Validate based on type
        if type == RecurrenceType.WEEKLY and not days_of_week:
            days_of_week = [0]  # Default to Monday

        if type == RecurrenceType.MONTHLY and not day_of_month:
            day_of_month = 1  # Default to 1st

        if type == RecurrenceType.YEARLY:
            if not month_of_year:
                month_of_year = 1  # Default to January
            if not day_of_month:
                day_of_month = 1  # Default to 1st

        pattern = RecurrencePattern(
            user_id=user_id,
            type=type,
            interval=interval,
            days_of_week=days_of_week,
            day_of_month=day_of_month,
            month_of_year=month_of_year,
            end_date=end_date,
        )

        self.session.add(pattern)
        await self.session.commit()
        await self.session.refresh(pattern)

        logger.info(f"Created recurrence pattern {pattern.id}: {type.value} every {interval}")
        return pattern

    async def get_pattern_by_id(self, pattern_id: UUID) -> Optional[RecurrencePattern]:
        """Get a recurrence pattern by its ID.

        Args:
            pattern_id: The pattern ID

        Returns:
            The pattern or None
        """
        return await self._get_pattern(pattern_id)

    async def delete_pattern(self, pattern_id: UUID, user_id: str) -> bool:
        """Delete a recurrence pattern.

        Note: This doesn't delete associated tasks, just removes the recurrence.
        Tasks will no longer generate new occurrences.

        Args:
            pattern_id: The pattern to delete
            user_id: Owner of the pattern (for authorization)

        Returns:
            True if deleted, False if not found or unauthorized
        """
        pattern = await self._get_pattern(pattern_id)

        if not pattern:
            return False

        if pattern.user_id != user_id:
            logger.warning(f"User {user_id} attempted to delete pattern {pattern_id} owned by {pattern.user_id}")
            return False

        await self.session.delete(pattern)
        await self.session.commit()

        logger.info(f"Deleted recurrence pattern {pattern_id}")
        return True

    async def get_patterns_for_user(
        self,
        user_id: str,
        limit: int = 50,
    ) -> list[RecurrencePattern]:
        """Get all recurrence patterns for a user.

        Args:
            user_id: The user ID
            limit: Maximum number to return

        Returns:
            List of patterns
        """
        statement = (
            select(RecurrencePattern)
            .where(RecurrencePattern.user_id == user_id)
            .order_by(RecurrencePattern.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    # Private helpers

    async def _get_pattern(self, pattern_id: UUID) -> Optional[RecurrencePattern]:
        """Get a recurrence pattern by ID."""
        statement = select(RecurrencePattern).where(RecurrencePattern.id == pattern_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()


def get_day_name(day: int) -> str:
    """Convert weekday number to name."""
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return days[day] if 0 <= day <= 6 else f"Day {day}"


def describe_pattern(pattern: RecurrencePattern) -> str:
    """Generate a human-readable description of a recurrence pattern."""
    interval = pattern.interval

    if pattern.type == RecurrenceType.DAILY:
        if interval == 1:
            return "Every day"
        return f"Every {interval} days"

    elif pattern.type == RecurrenceType.WEEKLY:
        if pattern.days_of_week:
            days = [get_day_name(d) for d in sorted(pattern.days_of_week)]
            days_str = ", ".join(days)
            if interval == 1:
                return f"Every {days_str}"
            return f"Every {interval} weeks on {days_str}"
        if interval == 1:
            return "Every week"
        return f"Every {interval} weeks"

    elif pattern.type == RecurrenceType.MONTHLY:
        day = pattern.day_of_month or 1
        suffix = "th"
        if day in (1, 21, 31):
            suffix = "st"
        elif day in (2, 22):
            suffix = "nd"
        elif day in (3, 23):
            suffix = "rd"
        if interval == 1:
            return f"Every month on the {day}{suffix}"
        return f"Every {interval} months on the {day}{suffix}"

    elif pattern.type == RecurrenceType.YEARLY:
        month = pattern.month_of_year or 1
        day = pattern.day_of_month or 1
        month_name = calendar.month_name[month]
        if interval == 1:
            return f"Every year on {month_name} {day}"
        return f"Every {interval} years on {month_name} {day}"

    elif pattern.type == RecurrenceType.CUSTOM:
        if interval == 1:
            return "Every day (custom)"
        return f"Every {interval} days (custom)"

    return f"Unknown pattern: {pattern.type}"


# Dependency injection helper
async def get_recurrence_service(session: AsyncSession) -> RecurrenceService:
    """Create a RecurrenceService instance."""
    return RecurrenceService(session)
