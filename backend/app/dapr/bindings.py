"""Dapr Bindings helper for cron triggers and external integrations."""

import logging
from typing import Any, Callable

logger = logging.getLogger(__name__)


class DaprBindings:
    """Dapr Bindings helper for input/output bindings.

    Input bindings (triggers):
    - Cron binding: Triggers handlers at specified intervals

    Output bindings:
    - Email binding: Sends emails via SMTP
    - HTTP binding: Makes HTTP calls to external services

    Usage (input binding with FastAPI):
        from fastapi import FastAPI, Request

        @app.post("/reminder-scheduler")
        async def handle_cron_trigger(request: Request):
            # This endpoint is called by Dapr cron binding
            await check_due_reminders()
            return {"status": "ok"}

    Usage (output binding):
        bindings = DaprBindings()
        await bindings.invoke("email-binding", "send", {"to": "user@example.com", "subject": "Reminder"})
    """

    def __init__(self):
        """Initialize Dapr Bindings helper."""
        self._client = None

    async def _get_client(self):
        """Get or create Dapr client (lazy initialization)."""
        if self._client is None:
            try:
                from dapr.clients import DaprClient

                self._client = DaprClient()
            except ImportError:
                logger.warning("Dapr SDK not available, using mock client")
                self._client = MockDaprBindingsClient()
        return self._client

    async def invoke(
        self,
        binding_name: str,
        operation: str,
        data: dict[str, Any],
        metadata: dict[str, str] | None = None,
    ) -> bytes | None:
        """Invoke an output binding.

        Args:
            binding_name: Name of the Dapr binding component
            operation: Operation to perform (e.g., "create", "send")
            data: Data to send to the binding
            metadata: Optional metadata for the binding call

        Returns:
            Response data from the binding, if any
        """
        client = await self._get_client()

        try:
            response = await client.invoke_binding(
                binding_name=binding_name,
                operation=operation,
                data=data,
                binding_metadata=metadata or {},
            )
            logger.info(f"Invoked binding {binding_name}.{operation}")
            return response.data if hasattr(response, "data") else None
        except Exception as e:
            logger.error(f"Failed to invoke binding {binding_name}.{operation}: {e}")
            raise

    async def close(self) -> None:
        """Close the Dapr client connection."""
        if self._client is not None:
            try:
                await self._client.close()
            except Exception:
                pass
            self._client = None


class MockDaprBindingsClient:
    """Mock Dapr bindings client for local development."""

    async def invoke_binding(self, binding_name: str, operation: str, data: dict, **kwargs):
        """Mock binding invocation that logs the call."""
        logger.info(f"[MOCK] Invoking binding {binding_name}.{operation}: {data}")
        return MockBindingResponse(b"")

    async def close(self):
        """Mock close."""
        pass


class MockBindingResponse:
    """Mock binding response for testing."""

    def __init__(self, data: bytes):
        self.data = data


# Cron binding endpoint handler decorator
def cron_handler(binding_name: str) -> Callable:
    """Decorator to mark a function as a cron binding handler.

    This is informational only - the actual binding is configured
    in infrastructure/dapr/components/ and triggers a POST endpoint.

    Args:
        binding_name: Name of the cron binding component

    Usage:
        @cron_handler("reminder-scheduler")
        async def check_due_reminders():
            # Called every minute by Dapr cron binding
            pass
    """

    def decorator(func: Callable) -> Callable:
        func._dapr_cron_binding = binding_name
        return func

    return decorator


# Global instance for convenience
_bindings: DaprBindings | None = None


def get_bindings() -> DaprBindings:
    """Get the global Dapr Bindings instance."""
    global _bindings
    if _bindings is None:
        _bindings = DaprBindings()
    return _bindings
