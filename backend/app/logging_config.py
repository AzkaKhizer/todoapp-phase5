"""Structured logging configuration with correlation IDs.

This module provides:
- Structured JSON logging with structlog
- Request correlation ID tracking
- Context-aware logging
- Log level configuration
"""

import logging
import sys
import uuid
from contextvars import ContextVar
from typing import Any

import structlog

# Context variable for correlation ID
correlation_id_ctx: ContextVar[str | None] = ContextVar("correlation_id", default=None)


def get_correlation_id() -> str:
    """Get the current correlation ID or generate a new one."""
    cid = correlation_id_ctx.get()
    if cid is None:
        cid = str(uuid.uuid4())
        correlation_id_ctx.set(cid)
    return cid


def set_correlation_id(cid: str | None) -> None:
    """Set the correlation ID for the current context."""
    correlation_id_ctx.set(cid)


def add_correlation_id(
    logger: logging.Logger,
    method_name: str,
    event_dict: dict[str, Any],
) -> dict[str, Any]:
    """Add correlation ID to log events."""
    cid = correlation_id_ctx.get()
    if cid:
        event_dict["correlation_id"] = cid
    return event_dict


def add_service_context(
    logger: logging.Logger,
    method_name: str,
    event_dict: dict[str, Any],
) -> dict[str, Any]:
    """Add service context to log events."""
    event_dict["service"] = "todo-backend"
    return event_dict


def setup_logging(
    log_level: str = "INFO",
    json_logs: bool = True,
    development: bool = False,
) -> None:
    """Configure structured logging with structlog.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_logs: If True, output JSON formatted logs
        development: If True, use development-friendly formatting
    """
    # Shared processors for all loggers
    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
        add_correlation_id,
        add_service_context,
    ]

    if development:
        # Development: colorful console output
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True),
        ]
    elif json_logs:
        # Production: JSON output
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]
    else:
        # Plain text output
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer(colors=False),
        ]

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )

    # Set log levels for third-party libraries
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)


# =============================================================================
# Logging Context Manager
# =============================================================================


class LogContext:
    """Context manager for adding temporary context to logs."""

    def __init__(self, **kwargs: Any):
        """Initialize with context values.

        Args:
            **kwargs: Key-value pairs to add to log context
        """
        self.context = kwargs
        self._token = None

    def __enter__(self) -> "LogContext":
        """Enter the context and bind values."""
        structlog.contextvars.bind_contextvars(**self.context)
        return self

    def __exit__(self, *args: Any) -> None:
        """Exit the context and unbind values."""
        structlog.contextvars.unbind_contextvars(*self.context.keys())


# =============================================================================
# Request Logging Helpers
# =============================================================================


def log_request(
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    user_id: str | None = None,
    client_ip: str | None = None,
) -> None:
    """Log an HTTP request.

    Args:
        method: HTTP method
        path: Request path
        status_code: Response status code
        duration_ms: Request duration in milliseconds
        user_id: Authenticated user ID
        client_ip: Client IP address
    """
    logger = get_logger("http")

    level = "info"
    if status_code >= 500:
        level = "error"
    elif status_code >= 400:
        level = "warning"

    log_method = getattr(logger, level)
    log_method(
        "http_request",
        method=method,
        path=path,
        status_code=status_code,
        duration_ms=round(duration_ms, 2),
        user_id=user_id,
        client_ip=client_ip,
    )


def log_kafka_event(
    topic: str,
    event_type: str,
    success: bool,
    duration_ms: float | None = None,
    error: str | None = None,
) -> None:
    """Log a Kafka event.

    Args:
        topic: Kafka topic
        event_type: Event type (e.g., "task.created")
        success: Whether the operation succeeded
        duration_ms: Processing duration in milliseconds
        error: Error message if failed
    """
    logger = get_logger("kafka")

    if success:
        logger.info(
            "kafka_event",
            topic=topic,
            event_type=event_type,
            status="success",
            duration_ms=round(duration_ms, 2) if duration_ms else None,
        )
    else:
        logger.error(
            "kafka_event",
            topic=topic,
            event_type=event_type,
            status="error",
            error=error,
            duration_ms=round(duration_ms, 2) if duration_ms else None,
        )


def log_database_operation(
    operation: str,
    table: str,
    success: bool,
    duration_ms: float,
    rows_affected: int | None = None,
    error: str | None = None,
) -> None:
    """Log a database operation.

    Args:
        operation: Operation type (SELECT, INSERT, UPDATE, DELETE)
        table: Table name
        success: Whether the operation succeeded
        duration_ms: Query duration in milliseconds
        rows_affected: Number of rows affected
        error: Error message if failed
    """
    logger = get_logger("database")

    if success:
        logger.debug(
            "db_operation",
            operation=operation,
            table=table,
            status="success",
            duration_ms=round(duration_ms, 2),
            rows_affected=rows_affected,
        )
    else:
        logger.error(
            "db_operation",
            operation=operation,
            table=table,
            status="error",
            error=error,
            duration_ms=round(duration_ms, 2),
        )
