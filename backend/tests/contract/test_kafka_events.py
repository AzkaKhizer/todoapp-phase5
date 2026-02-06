"""Contract tests for Kafka event schemas.

These tests verify that event schemas conform to the CloudEvents specification
and maintain backward compatibility. They ensure that:

1. Events serialize to valid JSON
2. Required CloudEvents fields are present
3. Event data schemas are correct
4. Changes don't break existing consumers

Run with: pytest tests/contract/test_kafka_events.py -v
"""

import json
from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from app.events.schemas import (
    ActivityLogData,
    CloudEvent,
    NotificationData,
    NotificationEvent,
    ReminderDueData,
    ReminderDueEvent,
    SyncEvent,
    SyncEventData,
    TaskCreatedData,
    TaskDeletedData,
    TaskEvent,
    TaskEventData,
    TaskEventType,
    TaskUpdatedData,
)


class TestCloudEventBase:
    """Test CloudEvents base specification compliance."""

    def test_cloud_event_required_fields(self):
        """Test that CloudEvent has required fields per spec v1.0."""
        event = CloudEvent(
            type="test.event",
            source="/test",
        )

        # Required CloudEvents fields
        assert event.specversion == "1.0"
        assert event.type == "test.event"
        assert event.source == "/test"
        assert event.id is not None
        assert isinstance(event.id, UUID)
        assert event.time is not None
        assert event.datacontenttype == "application/json"

    def test_cloud_event_serialization(self):
        """Test CloudEvent serializes to valid JSON."""
        event = CloudEvent(
            type="test.event",
            source="/test",
        )

        json_data = event.model_dump_json()
        parsed = json.loads(json_data)

        assert "specversion" in parsed
        assert "type" in parsed
        assert "source" in parsed
        assert "id" in parsed
        assert "time" in parsed

    def test_cloud_event_id_is_unique(self):
        """Test that each CloudEvent gets a unique ID."""
        event1 = CloudEvent(type="test.event", source="/test")
        event2 = CloudEvent(type="test.event", source="/test")

        assert event1.id != event2.id


class TestReminderDueEvent:
    """Contract tests for reminder.due events."""

    def test_reminder_due_event_structure(self):
        """Test ReminderDueEvent has correct structure."""
        data = ReminderDueData(
            reminder_id=uuid4(),
            task_id=uuid4(),
            user_id="user-123",
            task_title="Test Task",
            task_due_date=datetime.now(timezone.utc),
            delivery_channel="in-app",
            attempt=1,
        )
        event = ReminderDueEvent(data=data)

        # CloudEvents fields
        assert event.specversion == "1.0"
        assert event.type == "reminder.due"
        assert event.source == "/scheduler/reminders"
        assert event.datacontenttype == "application/json"

        # Data fields
        assert event.data.reminder_id is not None
        assert event.data.task_id is not None
        assert event.data.user_id == "user-123"
        assert event.data.task_title == "Test Task"
        assert event.data.delivery_channel == "in-app"
        assert event.data.attempt == 1

    def test_reminder_due_event_serialization(self):
        """Test ReminderDueEvent serializes correctly."""
        data = ReminderDueData(
            reminder_id=uuid4(),
            task_id=uuid4(),
            user_id="user-123",
            task_title="Test Task",
            task_due_date=datetime(2024, 12, 31, 10, 0, 0, tzinfo=timezone.utc),
            delivery_channel="email",
            attempt=2,
        )
        event = ReminderDueEvent(data=data)

        json_str = event.model_dump_json()
        parsed = json.loads(json_str)

        assert parsed["type"] == "reminder.due"
        assert parsed["source"] == "/scheduler/reminders"
        assert "data" in parsed
        assert parsed["data"]["user_id"] == "user-123"
        assert parsed["data"]["delivery_channel"] == "email"
        assert parsed["data"]["attempt"] == 2

    def test_reminder_due_data_required_fields(self):
        """Test ReminderDueData requires all mandatory fields."""
        with pytest.raises(ValidationError):
            ReminderDueData(
                reminder_id=uuid4(),
                # Missing required fields
            )

    def test_reminder_due_data_default_values(self):
        """Test ReminderDueData default values."""
        data = ReminderDueData(
            reminder_id=uuid4(),
            task_id=uuid4(),
            user_id="user-123",
            task_title="Test",
            task_due_date=datetime.now(timezone.utc),
        )

        assert data.delivery_channel == "in-app"
        assert data.attempt == 1


class TestTaskEvents:
    """Contract tests for task lifecycle events."""

    def test_task_created_event_structure(self):
        """Test task.created event structure."""
        data = TaskCreatedData(
            task_id=uuid4(),
            user_id="user-123",
            title="New Task",
            description="Task description",
            priority="high",
            due_date=datetime.now(timezone.utc),
            tags=["work", "urgent"],
        )
        event = TaskEvent(
            type=TaskEventType.CREATED,
            data=data,
        )

        assert event.type == TaskEventType.CREATED
        assert event.source == "/api/tasks"
        assert event.data.title == "New Task"
        assert event.data.priority == "high"
        assert "work" in event.data.tags

    def test_task_updated_event_structure(self):
        """Test task.updated event structure."""
        data = TaskUpdatedData(
            task_id=uuid4(),
            user_id="user-123",
            changes={
                "title": {"old": "Old Title", "new": "New Title"},
                "priority": {"old": "low", "new": "high"},
            },
            current_state={"title": "New Title", "priority": "high"},
        )
        event = TaskEvent(
            type=TaskEventType.UPDATED,
            data=data,
        )

        assert event.type == TaskEventType.UPDATED
        assert "title" in event.data.changes
        assert event.data.changes["title"]["new"] == "New Title"

    def test_task_deleted_event_structure(self):
        """Test task.deleted event structure."""
        data = TaskDeletedData(
            task_id=uuid4(),
            user_id="user-123",
            title="Deleted Task",
        )
        event = TaskEvent(
            type=TaskEventType.DELETED,
            data=data,
        )

        assert event.type == TaskEventType.DELETED
        assert event.data.title == "Deleted Task"

    def test_task_event_types_enum(self):
        """Test TaskEventType enum values."""
        assert TaskEventType.CREATED.value == "task.created"
        assert TaskEventType.UPDATED.value == "task.updated"
        assert TaskEventType.COMPLETED.value == "task.completed"
        assert TaskEventType.DELETED.value == "task.deleted"

    def test_task_event_serialization(self):
        """Test TaskEvent serializes correctly."""
        data = TaskCreatedData(
            task_id=uuid4(),
            user_id="user-123",
            title="Test Task",
        )
        event = TaskEvent(
            type=TaskEventType.CREATED,
            data=data,
        )

        json_str = event.model_dump_json()
        parsed = json.loads(json_str)

        assert parsed["type"] == "task.created"
        assert parsed["data"]["title"] == "Test Task"
        assert parsed["data"]["user_id"] == "user-123"


class TestNotificationEvent:
    """Contract tests for notification events."""

    def test_notification_event_structure(self):
        """Test notification.send event structure."""
        data = NotificationData(
            user_id="user-123",
            channel="in-app",
            title="Notification Title",
            body="Notification body message",
            action_url="/tasks/123",
            metadata={"task_id": "123"},
        )
        event = NotificationEvent(data=data)

        assert event.type == "notification.send"
        assert event.source == "/notifications"
        assert event.data.user_id == "user-123"
        assert event.data.channel == "in-app"
        assert event.data.title == "Notification Title"
        assert event.data.action_url == "/tasks/123"

    def test_notification_data_defaults(self):
        """Test NotificationData default values."""
        data = NotificationData(
            user_id="user-123",
            title="Title",
            body="Body",
        )

        assert data.channel == "in-app"
        assert data.action_url is None
        assert data.metadata == {}
        assert data.notification_id is not None

    def test_notification_event_serialization(self):
        """Test NotificationEvent serializes correctly."""
        data = NotificationData(
            user_id="user-123",
            title="Test",
            body="Test message",
        )
        event = NotificationEvent(data=data)

        json_str = event.model_dump_json()
        parsed = json.loads(json_str)

        assert parsed["type"] == "notification.send"
        assert parsed["data"]["title"] == "Test"


class TestSyncEvent:
    """Contract tests for sync events."""

    def test_sync_event_structure(self):
        """Test sync.broadcast event structure."""
        data = SyncEventData(
            user_id="user-123",
            entity_type="task",
            entity_id=uuid4(),
            operation="create",
            payload={"title": "New Task"},
        )
        event = SyncEvent(data=data)

        assert event.type == "sync.broadcast"
        assert event.source == "/api"
        assert event.data.entity_type == "task"
        assert event.data.operation == "create"

    def test_sync_event_entity_types(self):
        """Test valid entity types for sync events."""
        for entity_type in ["task", "tag", "reminder"]:
            data = SyncEventData(
                user_id="user-123",
                entity_type=entity_type,
                entity_id=uuid4(),
                operation="create",
                payload={},
            )
            assert data.entity_type == entity_type

    def test_sync_event_operations(self):
        """Test valid operations for sync events."""
        for operation in ["create", "update", "delete"]:
            data = SyncEventData(
                user_id="user-123",
                entity_type="task",
                entity_id=uuid4(),
                operation=operation,
                payload={},
            )
            assert data.operation == operation


class TestActivityLogData:
    """Contract tests for activity log events."""

    def test_activity_log_data_structure(self):
        """Test ActivityLogData structure."""
        data = ActivityLogData(
            user_id="user-123",
            event_type="task.created",
            entity_type="task",
            entity_id=uuid4(),
            details={"title": "New Task"},
            correlation_id="corr-123",
        )

        assert data.user_id == "user-123"
        assert data.event_type == "task.created"
        assert data.entity_type == "task"
        assert data.timestamp is not None
        assert data.details["title"] == "New Task"
        assert data.correlation_id == "corr-123"

    def test_activity_log_data_defaults(self):
        """Test ActivityLogData default values."""
        data = ActivityLogData(
            user_id="user-123",
            event_type="task.created",
            entity_type="task",
            entity_id=uuid4(),
        )

        assert data.timestamp is not None
        assert data.details == {}
        assert data.correlation_id is None


class TestBackwardCompatibility:
    """Tests to ensure backward compatibility of event schemas."""

    def test_reminder_due_event_v1_compatibility(self):
        """Test ReminderDueEvent maintains v1 structure."""
        # Simulate receiving a v1 event from Kafka
        v1_event_json = {
            "specversion": "1.0",
            "type": "reminder.due",
            "source": "/scheduler/reminders",
            "id": str(uuid4()),
            "time": datetime.now(timezone.utc).isoformat(),
            "datacontenttype": "application/json",
            "data": {
                "reminder_id": str(uuid4()),
                "task_id": str(uuid4()),
                "user_id": "user-123",
                "task_title": "Test Task",
                "task_due_date": datetime.now(timezone.utc).isoformat(),
                "delivery_channel": "in-app",
                "attempt": 1,
            },
        }

        # Should be able to create ReminderDueData from v1 format
        data = ReminderDueData(**v1_event_json["data"])
        assert data.user_id == "user-123"

    def test_task_event_v1_compatibility(self):
        """Test TaskEvent maintains v1 structure."""
        # Simulate receiving a v1 task.created event
        v1_event_json = {
            "specversion": "1.0",
            "type": "task.created",
            "source": "/api/tasks",
            "id": str(uuid4()),
            "time": datetime.now(timezone.utc).isoformat(),
            "datacontenttype": "application/json",
            "data": {
                "task_id": str(uuid4()),
                "user_id": "user-123",
                "title": "Test Task",
                "due_date": None,
                "priority": "medium",
                "is_complete": False,
                "tags": [],
                "recurrence_id": None,
                "parent_task_id": None,
            },
        }

        # Should be able to create TaskEventData from v1 format
        data = TaskEventData(**v1_event_json["data"])
        assert data.title == "Test Task"
        assert data.priority == "medium"
