"""Integration tests for Dapr Pub/Sub with Kafka.

These tests require a running Dapr sidecar with Kafka pub/sub configured.
Run with: dapr run --app-id test-app -- pytest tests/integration/test_dapr_pubsub.py

For local testing without Dapr, the mock client will be used automatically.
"""

import asyncio
import os
from datetime import datetime, timezone
from uuid import uuid4

import pytest
import pytest_asyncio

from app.dapr.pubsub import DaprPubSub, Topics, EventTypes, CloudEvent, get_pubsub


# Skip tests if not running with Dapr
DAPR_HTTP_PORT = os.environ.get("DAPR_HTTP_PORT")
SKIP_REASON = "Dapr sidecar not available (set DAPR_HTTP_PORT to run)"


@pytest.fixture
def pubsub():
    """Get a DaprPubSub instance."""
    return DaprPubSub()


class TestCloudEvent:
    """Test CloudEvent creation."""

    def test_create_cloud_event(self):
        """Test creating a CloudEvent with auto-generated fields."""
        event = CloudEvent.create(
            event_type="task.created",
            source="test",
            data={"task_id": "123", "title": "Test Task"},
        )

        assert event.specversion == "1.0"
        assert event.type == "task.created"
        assert event.source == "test"
        assert event.id is not None
        assert event.time is not None
        assert event.data == {"task_id": "123", "title": "Test Task"}

    def test_cloud_event_serialization(self):
        """Test CloudEvent serializes to valid JSON."""
        event = CloudEvent.create(
            event_type="task.updated",
            source="todo-backend",
            data={"changes": ["title"]},
        )

        json_data = event.model_dump()

        assert "specversion" in json_data
        assert "type" in json_data
        assert "source" in json_data
        assert "id" in json_data
        assert "time" in json_data
        assert "data" in json_data


class TestDaprPubSubMock:
    """Test DaprPubSub with mock client (no Dapr required)."""

    @pytest.mark.asyncio
    async def test_publish_dict_data(self, pubsub):
        """Test publishing dict data."""
        result = await pubsub.publish(
            topic=Topics.TASK_EVENTS,
            event_type=EventTypes.TASK_CREATED,
            data={"task_id": str(uuid4()), "title": "Test Task"},
        )

        # Mock client always succeeds
        assert result is True

    @pytest.mark.asyncio
    async def test_publish_with_metadata(self, pubsub):
        """Test publishing with metadata."""
        result = await pubsub.publish(
            topic=Topics.TASK_EVENTS,
            event_type=EventTypes.TASK_UPDATED,
            data={"task_id": str(uuid4())},
            metadata={"correlation_id": str(uuid4())},
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_publish_bulk(self, pubsub):
        """Test bulk publishing."""
        events = [
            (EventTypes.TASK_CREATED, {"task_id": str(uuid4())}),
            (EventTypes.TASK_UPDATED, {"task_id": str(uuid4())}),
            (EventTypes.TASK_COMPLETED, {"task_id": str(uuid4())}),
        ]

        count = await pubsub.publish_bulk(Topics.TASK_EVENTS, events)

        assert count == 3


@pytest.mark.skipif(not DAPR_HTTP_PORT, reason=SKIP_REASON)
class TestDaprPubSubIntegration:
    """Integration tests requiring Dapr sidecar with Kafka.

    Run these tests with:
    dapr run --app-id test-pubsub --dapr-http-port 3500 -- pytest tests/integration/test_dapr_pubsub.py -v -k Integration
    """

    @pytest.mark.asyncio
    async def test_publish_to_kafka(self, pubsub):
        """Test publishing a message to Kafka via Dapr."""
        task_id = str(uuid4())

        result = await pubsub.publish(
            topic=Topics.TASK_EVENTS,
            event_type=EventTypes.TASK_CREATED,
            data={
                "task_id": task_id,
                "title": "Integration Test Task",
                "user_id": "test-user",
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_publish_activity_log(self, pubsub):
        """Test publishing to activity log topic."""
        result = await pubsub.publish(
            topic=Topics.ACTIVITY_LOG,
            event_type="task.created",
            data={
                "user_id": "test-user",
                "event_type": "task.created",
                "entity_type": "task",
                "entity_id": str(uuid4()),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "details": {"title": "Test Task"},
            },
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_publish_reminder_due(self, pubsub):
        """Test publishing to reminder.due topic."""
        result = await pubsub.publish(
            topic=Topics.REMINDER_DUE,
            event_type=EventTypes.REMINDER_DUE,
            data={
                "reminder_id": str(uuid4()),
                "task_id": str(uuid4()),
                "user_id": "test-user",
                "scheduled_time": datetime.now(timezone.utc).isoformat(),
            },
        )

        assert result is True


class TestTopicsAndEventTypes:
    """Test topic and event type constants."""

    def test_all_topics_defined(self):
        """Verify all expected topics are defined."""
        expected_topics = [
            "task.events",
            "reminder.due",
            "notification.send",
            "sync.events",
            "activity.log",
            "dlq.notifications",
        ]

        for topic in expected_topics:
            assert hasattr(Topics, topic.replace(".", "_").upper())

    def test_all_event_types_defined(self):
        """Verify all expected event types are defined."""
        expected_types = [
            "task.created",
            "task.updated",
            "task.completed",
            "task.deleted",
            "reminder.scheduled",
            "reminder.due",
            "reminder.sent",
        ]

        for event_type in expected_types:
            assert hasattr(EventTypes, event_type.replace(".", "_").upper())


class TestGlobalInstance:
    """Test global pubsub instance."""

    def test_get_pubsub_returns_instance(self):
        """Test that get_pubsub returns a DaprPubSub instance."""
        pubsub = get_pubsub()
        assert isinstance(pubsub, DaprPubSub)

    def test_get_pubsub_returns_same_instance(self):
        """Test that get_pubsub returns the same instance."""
        pubsub1 = get_pubsub()
        pubsub2 = get_pubsub()
        assert pubsub1 is pubsub2
