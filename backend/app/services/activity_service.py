"""Activity service for managing the activity log.

This service handles:
- Persisting activity log entries from Kafka events
- Querying activity logs with filtering and pagination
- Generating productivity summaries (tasks completed per day/week)
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.activity_log import ActivityLogEntry

logger = logging.getLogger(__name__)


class ActivityService:
    """Service for managing activity log entries.

    The activity log provides:
    - Audit trail for all task operations
    - Productivity tracking and analytics
    - Historical record for compliance
    """

    def __init__(self, session: AsyncSession):
        """Initialize the activity service.

        Args:
            session: Database session for queries
        """
        self.session = session

    async def log_activity(
        self,
        user_id: str,
        event_type: str,
        entity_type: str,
        entity_id: UUID,
        timestamp: datetime | None = None,
        details: dict[str, Any] | None = None,
        correlation_id: str | None = None,
    ) -> ActivityLogEntry:
        """Log an activity entry.

        Args:
            user_id: The user who performed the action
            event_type: Type of event (e.g., "task.created")
            entity_type: Type of entity (task, reminder, tag)
            entity_id: ID of the affected entity
            timestamp: When the event occurred (defaults to now)
            details: Additional event details
            correlation_id: Request correlation ID for tracing

        Returns:
            The created ActivityLogEntry
        """
        entry = ActivityLogEntry(
            user_id=user_id,
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            timestamp=timestamp or datetime.now(timezone.utc),
            details=details,
            correlation_id=correlation_id,
        )

        self.session.add(entry)
        await self.session.commit()
        await self.session.refresh(entry)

        logger.debug(f"Logged activity: {event_type} for {entity_type}/{entity_id}")
        return entry

    async def get_activities(
        self,
        user_id: str,
        entity_type: str | None = None,
        entity_id: UUID | None = None,
        event_type: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        page: int = 1,
        limit: int = 50,
    ) -> tuple[list[ActivityLogEntry], int]:
        """Get activity log entries with filtering and pagination.

        Args:
            user_id: Filter by user
            entity_type: Filter by entity type (task, reminder, tag)
            entity_id: Filter by specific entity
            event_type: Filter by event type
            start_date: Filter activities after this date
            end_date: Filter activities before this date
            page: Page number (1-indexed)
            limit: Items per page

        Returns:
            Tuple of (activities, total_count)
        """
        # Build base query
        query = select(ActivityLogEntry).where(ActivityLogEntry.user_id == user_id)
        count_query = (
            select(func.count())
            .select_from(ActivityLogEntry)
            .where(ActivityLogEntry.user_id == user_id)
        )

        # Apply filters
        conditions = []

        if entity_type:
            conditions.append(ActivityLogEntry.entity_type == entity_type)

        if entity_id:
            conditions.append(ActivityLogEntry.entity_id == entity_id)

        if event_type:
            conditions.append(ActivityLogEntry.event_type == event_type)

        if start_date:
            conditions.append(ActivityLogEntry.timestamp >= start_date)

        if end_date:
            conditions.append(ActivityLogEntry.timestamp <= end_date)

        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))

        # Get total count
        count_result = await self.session.execute(count_query)
        total = count_result.scalar_one()

        # Apply ordering and pagination
        query = query.order_by(ActivityLogEntry.timestamp.desc())
        offset = (page - 1) * limit
        query = query.limit(limit).offset(offset)

        # Execute query
        result = await self.session.execute(query)
        activities = list(result.scalars().all())

        return activities, total

    async def get_activity_by_id(
        self,
        activity_id: UUID,
        user_id: str,
    ) -> Optional[ActivityLogEntry]:
        """Get a specific activity log entry.

        Args:
            activity_id: The activity ID
            user_id: The user ID (for authorization)

        Returns:
            The activity entry or None
        """
        statement = select(ActivityLogEntry).where(
            and_(
                ActivityLogEntry.id == activity_id,
                ActivityLogEntry.user_id == user_id,
            )
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_entity_history(
        self,
        entity_type: str,
        entity_id: UUID,
        user_id: str,
        limit: int = 100,
    ) -> list[ActivityLogEntry]:
        """Get the complete history for a specific entity.

        Args:
            entity_type: Type of entity
            entity_id: Entity ID
            user_id: User ID (for authorization)
            limit: Maximum entries to return

        Returns:
            List of activity entries for the entity
        """
        statement = (
            select(ActivityLogEntry)
            .where(
                and_(
                    ActivityLogEntry.entity_type == entity_type,
                    ActivityLogEntry.entity_id == entity_id,
                    ActivityLogEntry.user_id == user_id,
                )
            )
            .order_by(ActivityLogEntry.timestamp.desc())
            .limit(limit)
        )

        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get_productivity_summary(
        self,
        user_id: str,
        days: int = 7,
    ) -> dict[str, Any]:
        """Get productivity summary for a user.

        Args:
            user_id: The user ID
            days: Number of days to include (default: 7)

        Returns:
            Dictionary with productivity metrics
        """
        start_date = datetime.now(timezone.utc) - timedelta(days=days)

        # Count tasks completed
        completed_query = (
            select(func.count())
            .select_from(ActivityLogEntry)
            .where(
                and_(
                    ActivityLogEntry.user_id == user_id,
                    ActivityLogEntry.event_type == "task.completed",
                    ActivityLogEntry.timestamp >= start_date,
                )
            )
        )
        completed_result = await self.session.execute(completed_query)
        tasks_completed = completed_result.scalar_one()

        # Count tasks created
        created_query = (
            select(func.count())
            .select_from(ActivityLogEntry)
            .where(
                and_(
                    ActivityLogEntry.user_id == user_id,
                    ActivityLogEntry.event_type == "task.created",
                    ActivityLogEntry.timestamp >= start_date,
                )
            )
        )
        created_result = await self.session.execute(created_query)
        tasks_created = created_result.scalar_one()

        # Count tasks deleted
        deleted_query = (
            select(func.count())
            .select_from(ActivityLogEntry)
            .where(
                and_(
                    ActivityLogEntry.user_id == user_id,
                    ActivityLogEntry.event_type == "task.deleted",
                    ActivityLogEntry.timestamp >= start_date,
                )
            )
        )
        deleted_result = await self.session.execute(deleted_query)
        tasks_deleted = deleted_result.scalar_one()

        # Get completions by day
        completions_by_day = await self._get_completions_by_day(user_id, days)

        return {
            "period_days": days,
            "start_date": start_date.isoformat(),
            "end_date": datetime.now(timezone.utc).isoformat(),
            "tasks_completed": tasks_completed,
            "tasks_created": tasks_created,
            "tasks_deleted": tasks_deleted,
            "net_tasks": tasks_created - tasks_deleted,
            "completion_rate": (
                round(tasks_completed / tasks_created * 100, 1)
                if tasks_created > 0
                else 0
            ),
            "completions_by_day": completions_by_day,
        }

    async def _get_completions_by_day(
        self,
        user_id: str,
        days: int,
    ) -> list[dict[str, Any]]:
        """Get task completions grouped by day.

        Args:
            user_id: The user ID
            days: Number of days to include

        Returns:
            List of {date, count} dictionaries
        """
        start_date = datetime.now(timezone.utc) - timedelta(days=days)

        # Get all completions in the period
        statement = (
            select(ActivityLogEntry.timestamp)
            .where(
                and_(
                    ActivityLogEntry.user_id == user_id,
                    ActivityLogEntry.event_type == "task.completed",
                    ActivityLogEntry.timestamp >= start_date,
                )
            )
            .order_by(ActivityLogEntry.timestamp)
        )

        result = await self.session.execute(statement)
        timestamps = [row[0] for row in result.all()]

        # Group by date
        date_counts: dict[str, int] = {}
        for ts in timestamps:
            date_key = ts.strftime("%Y-%m-%d")
            date_counts[date_key] = date_counts.get(date_key, 0) + 1

        # Fill in missing days with zeros
        completions = []
        current_date = start_date.date()
        end_date = datetime.now(timezone.utc).date()

        while current_date <= end_date:
            date_key = current_date.strftime("%Y-%m-%d")
            completions.append({
                "date": date_key,
                "count": date_counts.get(date_key, 0),
            })
            current_date += timedelta(days=1)

        return completions

    async def get_recent_activity_types(
        self,
        user_id: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Get recent activity types with counts.

        Args:
            user_id: The user ID
            limit: Maximum number of event types to return

        Returns:
            List of {event_type, count} dictionaries
        """
        statement = (
            select(
                ActivityLogEntry.event_type,
                func.count().label("count"),
            )
            .where(ActivityLogEntry.user_id == user_id)
            .group_by(ActivityLogEntry.event_type)
            .order_by(func.count().desc())
            .limit(limit)
        )

        result = await self.session.execute(statement)
        return [{"event_type": row[0], "count": row[1]} for row in result.all()]


# Dependency injection helper
async def get_activity_service(session: AsyncSession) -> ActivityService:
    """Create an ActivityService instance."""
    return ActivityService(session)
