"""Dapr integration module for distributed application runtime.

This module provides wrappers for Dapr building blocks:
- Pub/Sub: Kafka integration for event publishing/subscribing
- State: Redis state store for distributed state management
- Bindings: Cron triggers and external integrations
- Secrets: Secure credential storage
"""

from app.dapr.pubsub import DaprPubSub
from app.dapr.state import DaprState
from app.dapr.bindings import DaprBindings
from app.dapr.secrets import DaprSecrets

__all__ = [
    "DaprPubSub",
    "DaprState",
    "DaprBindings",
    "DaprSecrets",
]
