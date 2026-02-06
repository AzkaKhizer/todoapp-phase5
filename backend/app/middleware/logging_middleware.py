"""Request logging middleware with correlation ID tracking.

This middleware:
- Generates or extracts correlation IDs from requests
- Logs all HTTP requests with timing and context
- Adds correlation ID to response headers
"""

import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.logging_config import (
    get_logger,
    log_request,
    set_correlation_id,
)

logger = get_logger(__name__)

# Headers for correlation ID
CORRELATION_ID_HEADER = "X-Correlation-ID"
REQUEST_ID_HEADER = "X-Request-ID"


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request logging and correlation ID tracking."""

    def __init__(
        self,
        app: ASGIApp,
        exclude_paths: list[str] | None = None,
    ):
        """Initialize the logging middleware.

        Args:
            app: The ASGI application
            exclude_paths: Paths to exclude from logging (e.g., /health, /metrics)
        """
        super().__init__(app)
        self.exclude_paths = exclude_paths or ["/health", "/api/health", "/metrics"]

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        """Process the request and log it.

        Args:
            request: The incoming request
            call_next: The next middleware/handler in the chain

        Returns:
            The response from the handler
        """
        # Check if path should be excluded from logging
        if self._should_exclude(request.url.path):
            return await call_next(request)

        # Extract or generate correlation ID
        correlation_id = self._get_correlation_id(request)
        set_correlation_id(correlation_id)

        # Extract client IP
        client_ip = self._get_client_ip(request)

        # Record start time
        start_time = time.perf_counter()

        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            # Log error and re-raise
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.error(
                "request_error",
                method=request.method,
                path=request.url.path,
                error=str(e),
                duration_ms=round(duration_ms, 2),
                client_ip=client_ip,
            )
            raise

        # Calculate duration
        duration_ms = (time.perf_counter() - start_time) * 1000

        # Add correlation ID to response headers
        response.headers[CORRELATION_ID_HEADER] = correlation_id

        # Extract user ID from request state if available
        user_id = getattr(request.state, "user_id", None)

        # Log the request
        log_request(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
            user_id=user_id,
            client_ip=client_ip,
        )

        return response

    def _get_correlation_id(self, request: Request) -> str:
        """Extract correlation ID from request or generate a new one.

        Args:
            request: The incoming request

        Returns:
            Correlation ID string
        """
        # Check for existing correlation ID in headers
        correlation_id = request.headers.get(CORRELATION_ID_HEADER)
        if correlation_id:
            return correlation_id

        # Check for request ID header
        request_id = request.headers.get(REQUEST_ID_HEADER)
        if request_id:
            return request_id

        # Generate new correlation ID
        return str(uuid.uuid4())

    def _get_client_ip(self, request: Request) -> str | None:
        """Extract client IP from request.

        Args:
            request: The incoming request

        Returns:
            Client IP address or None
        """
        # Check for forwarded header (behind proxy/load balancer)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP in the chain
            return forwarded_for.split(",")[0].strip()

        # Check for real IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fall back to client host
        if request.client:
            return request.client.host

        return None

    def _should_exclude(self, path: str) -> bool:
        """Check if the path should be excluded from logging.

        Args:
            path: The request path

        Returns:
            True if the path should be excluded
        """
        return any(path.startswith(excluded) for excluded in self.exclude_paths)


def get_logging_middleware(
    exclude_paths: list[str] | None = None,
) -> type[LoggingMiddleware]:
    """Factory function to create logging middleware with configuration.

    Args:
        exclude_paths: Paths to exclude from logging

    Returns:
        Configured LoggingMiddleware class
    """

    class ConfiguredLoggingMiddleware(LoggingMiddleware):
        def __init__(self, app: ASGIApp):
            super().__init__(app, exclude_paths=exclude_paths)

    return ConfiguredLoggingMiddleware
