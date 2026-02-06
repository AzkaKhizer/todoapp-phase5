"""Dapr Secrets helper for secure credential storage."""

import logging
from typing import Any

logger = logging.getLogger(__name__)

# Dapr component name (configured in infrastructure/dapr/components/)
SECRET_STORE_NAME = "kubernetes-secrets"


class DaprSecrets:
    """Dapr Secrets helper for retrieving secrets from secret stores.

    Supports multiple secret store backends:
    - Kubernetes secrets (local/Minikube)
    - Azure Key Vault (cloud)
    - HashiCorp Vault
    - AWS Secrets Manager
    - GCP Secret Manager

    Usage:
        secrets = DaprSecrets()

        # Get a single secret
        db_password = await secrets.get("database", "password")

        # Get all secrets from a key
        db_secrets = await secrets.get_bulk("database")
        # Returns: {"host": "...", "password": "...", "user": "..."}
    """

    def __init__(self, store_name: str = SECRET_STORE_NAME):
        """Initialize Dapr Secrets helper.

        Args:
            store_name: Name of the Dapr secret store component
        """
        self.store_name = store_name
        self._client = None
        self._cache: dict[str, dict[str, str]] = {}

    async def _get_client(self):
        """Get or create Dapr client (lazy initialization)."""
        if self._client is None:
            try:
                from dapr.clients import DaprClient

                self._client = DaprClient()
            except ImportError:
                logger.warning("Dapr SDK not available, using mock client")
                self._client = MockDaprSecretsClient()
        return self._client

    async def get(self, secret_name: str, key: str | None = None) -> str | dict[str, str] | None:
        """Get a secret from the store.

        Args:
            secret_name: Name of the secret
            key: Optional key within the secret (for multi-value secrets)

        Returns:
            Secret value as string, or dict if no key specified
        """
        # Check cache first
        if secret_name in self._cache:
            secrets = self._cache[secret_name]
            if key:
                return secrets.get(key)
            return secrets

        client = await self._get_client()

        try:
            response = await client.get_secret(
                store_name=self.store_name,
                key=secret_name,
            )

            if response.secret:
                self._cache[secret_name] = response.secret
                if key:
                    return response.secret.get(key)
                return response.secret

            return None
        except Exception as e:
            logger.error(f"Failed to get secret {secret_name}: {e}")
            raise

    async def get_bulk(self, secret_name: str) -> dict[str, str]:
        """Get all values from a secret.

        Args:
            secret_name: Name of the secret

        Returns:
            Dict of all key-value pairs in the secret
        """
        result = await self.get(secret_name)
        if isinstance(result, dict):
            return result
        if isinstance(result, str):
            return {secret_name: result}
        return {}

    def clear_cache(self) -> None:
        """Clear the secrets cache."""
        self._cache.clear()

    async def close(self) -> None:
        """Close the Dapr client connection."""
        if self._client is not None:
            try:
                await self._client.close()
            except Exception:
                pass
            self._client = None


class MockDaprSecretsClient:
    """Mock Dapr secrets client for local development."""

    def __init__(self):
        # Default mock secrets for local development
        self._secrets = {
            "database": {
                "host": "localhost",
                "user": "postgres",
                "password": "postgres",
            },
            "redis": {
                "host": "localhost",
                "port": "6379",
            },
            "kafka": {
                "brokers": "localhost:9092",
            },
        }

    async def get_secret(self, store_name: str, key: str):
        """Mock get that returns predefined secrets."""
        secret = self._secrets.get(key)
        logger.info(f"[MOCK] Getting secret: {key}")
        return MockSecretResponse(secret or {})

    async def close(self):
        """Mock close."""
        pass


class MockSecretResponse:
    """Mock secret response for testing."""

    def __init__(self, secret: dict[str, str]):
        self.secret = secret


# Global instance for convenience
_secrets: DaprSecrets | None = None


def get_secrets() -> DaprSecrets:
    """Get the global Dapr Secrets instance."""
    global _secrets
    if _secrets is None:
        _secrets = DaprSecrets()
    return _secrets
