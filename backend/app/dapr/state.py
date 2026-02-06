"""Dapr State Store helper for Redis integration."""

import json
import logging
from typing import Any, TypeVar

from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Dapr component name (configured in infrastructure/dapr/components/)
STATE_STORE_NAME = "statestore"

T = TypeVar("T", bound=BaseModel)


class DaprState:
    """Dapr State Store helper for distributed state management via Redis.

    Usage:
        state = DaprState()

        # Save state
        await state.save("user:123:session", {"token": "abc"})

        # Get state
        data = await state.get("user:123:session")

        # Delete state
        await state.delete("user:123:session")
    """

    def __init__(self, store_name: str = STATE_STORE_NAME):
        """Initialize Dapr State Store helper.

        Args:
            store_name: Name of the Dapr state store component
        """
        self.store_name = store_name
        self._client = None

    async def _get_client(self):
        """Get or create Dapr client (lazy initialization)."""
        if self._client is None:
            try:
                from dapr.clients import DaprClient

                self._client = DaprClient()
            except ImportError:
                logger.warning("Dapr SDK not available, using mock client")
                self._client = MockDaprStateClient()
        return self._client

    async def save(
        self,
        key: str,
        value: BaseModel | dict[str, Any],
        metadata: dict[str, str] | None = None,
    ) -> None:
        """Save state to the store.

        Args:
            key: State key
            value: State value (Pydantic model or dict)
            metadata: Optional metadata
        """
        client = await self._get_client()

        # Serialize Pydantic models
        if isinstance(value, BaseModel):
            data = value.model_dump()
        else:
            data = value

        try:
            await client.save_state(
                store_name=self.store_name,
                key=key,
                value=json.dumps(data),
                state_metadata=metadata or {},
            )
            logger.debug(f"Saved state for key: {key}")
        except Exception as e:
            logger.error(f"Failed to save state for key {key}: {e}")
            raise

    async def get(self, key: str) -> dict[str, Any] | None:
        """Get state from the store.

        Args:
            key: State key

        Returns:
            State value as dict, or None if not found
        """
        client = await self._get_client()

        try:
            response = await client.get_state(store_name=self.store_name, key=key)
            if response.data:
                return json.loads(response.data)
            return None
        except Exception as e:
            logger.error(f"Failed to get state for key {key}: {e}")
            raise

    async def get_typed(self, key: str, model: type[T]) -> T | None:
        """Get state from the store and parse to a Pydantic model.

        Args:
            key: State key
            model: Pydantic model class to parse into

        Returns:
            Parsed model instance, or None if not found
        """
        data = await self.get(key)
        if data is not None:
            return model.model_validate(data)
        return None

    async def delete(self, key: str) -> None:
        """Delete state from the store.

        Args:
            key: State key
        """
        client = await self._get_client()

        try:
            await client.delete_state(store_name=self.store_name, key=key)
            logger.debug(f"Deleted state for key: {key}")
        except Exception as e:
            logger.error(f"Failed to delete state for key {key}: {e}")
            raise

    async def close(self) -> None:
        """Close the Dapr client connection."""
        if self._client is not None:
            try:
                await self._client.close()
            except Exception:
                pass
            self._client = None


class MockDaprStateClient:
    """Mock Dapr state client for local development without Dapr sidecar."""

    def __init__(self):
        self._store: dict[str, str] = {}

    async def save_state(self, store_name: str, key: str, value: str, **kwargs):
        """Mock save that stores in memory."""
        self._store[key] = value
        logger.info(f"[MOCK] Saved state: {key}")

    async def get_state(self, store_name: str, key: str):
        """Mock get that retrieves from memory."""
        data = self._store.get(key)
        return MockStateResponse(data.encode() if data else b"")

    async def delete_state(self, store_name: str, key: str):
        """Mock delete that removes from memory."""
        self._store.pop(key, None)
        logger.info(f"[MOCK] Deleted state: {key}")

    async def close(self):
        """Mock close."""
        pass


class MockStateResponse:
    """Mock state response for testing."""

    def __init__(self, data: bytes):
        self.data = data


# Global instance for convenience
_state: DaprState | None = None


def get_state() -> DaprState:
    """Get the global Dapr State Store instance."""
    global _state
    if _state is None:
        _state = DaprState()
    return _state
