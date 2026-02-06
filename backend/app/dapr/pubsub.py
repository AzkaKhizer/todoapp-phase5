"""Dapr Pub/Sub helper for Kafka integration."""

import json
import logging
from typing import Any

from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Dapr component names (configured in infrastructure/dapr/components/)
PUBSUB_NAME = "kafka-pubsub"


class DaprPubSub:
    """Dapr Pub/Sub helper for publishing and subscribing to Kafka topics.

    Usage:
        # Publishing events
        pubsub = DaprPubSub()
        await pubsub.publish("task.events", task_event)

        # Subscribing (via FastAPI endpoint with Dapr SDK)
        from dapr.ext.fastapi import DaprApp
        dapr_app = DaprApp(app)

        @dapr_app.subscribe(pubsub=PUBSUB_NAME, topic="task.events")
        async def handle_task_event(event: dict):
            pass
    """

    def __init__(self, pubsub_name: str = PUBSUB_NAME):
        """Initialize Dapr Pub/Sub helper.

        Args:
            pubsub_name: Name of the Dapr pub/sub component
        """
        self.pubsub_name = pubsub_name
        self._client = None

    async def _get_client(self):
        """Get or create Dapr client (lazy initialization)."""
        if self._client is None:
            try:
                from dapr.clients import DaprClient

                self._client = DaprClient()
            except ImportError:
                logger.warning("Dapr SDK not available, using mock client")
                self._client = MockDaprClient()
        return self._client

    async def publish(
        self,
        topic: str,
        data: BaseModel | dict[str, Any],
        metadata: dict[str, str] | None = None,
    ) -> None:
        """Publish an event to a Kafka topic via Dapr.

        Args:
            topic: Kafka topic name
            data: Event data (Pydantic model or dict)
            metadata: Optional metadata for the message
        """
        client = await self._get_client()

        # Serialize Pydantic models
        if isinstance(data, BaseModel):
            payload = data.model_dump_json()
        else:
            payload = json.dumps(data)

        try:
            await client.publish_event(
                pubsub_name=self.pubsub_name,
                topic_name=topic,
                data=payload,
                data_content_type="application/json",
                publish_metadata=metadata or {},
            )
            logger.info(f"Published event to {topic}")
        except Exception as e:
            logger.error(f"Failed to publish event to {topic}: {e}")
            raise

    async def close(self) -> None:
        """Close the Dapr client connection."""
        if self._client is not None:
            try:
                await self._client.close()
            except Exception:
                pass
            self._client = None


class MockDaprClient:
    """Mock Dapr client for local development without Dapr sidecar."""

    async def publish_event(self, **kwargs):
        """Mock publish that logs the event."""
        logger.info(f"[MOCK] Publishing event: {kwargs}")

    async def close(self):
        """Mock close."""
        pass


# Global instance for convenience
_pubsub: DaprPubSub | None = None


def get_pubsub() -> DaprPubSub:
    """Get the global Dapr Pub/Sub instance."""
    global _pubsub
    if _pubsub is None:
        _pubsub = DaprPubSub()
    return _pubsub
