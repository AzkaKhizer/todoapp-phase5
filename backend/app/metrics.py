"""Prometheus metrics for the Todo application.

This module provides:
- FastAPI instrumentation with prometheus-fastapi-instrumentator
- Custom business metrics (task counts, Kafka lag, reminder latency)
- Health check metrics
"""

import logging
import time
from contextlib import contextmanager
from typing import Callable

from prometheus_client import Counter, Gauge, Histogram, Info
from prometheus_fastapi_instrumentator import Instrumentator, metrics
from prometheus_fastapi_instrumentator.metrics import Info as MetricInfo

logger = logging.getLogger(__name__)

# =============================================================================
# Application Info
# =============================================================================

APP_INFO = Info(
    "todo_app",
    "Todo application information",
)

# =============================================================================
# Business Metrics
# =============================================================================

# Task metrics
TASKS_CREATED = Counter(
    "todo_tasks_created_total",
    "Total number of tasks created",
    ["user_id", "priority"],
)

TASKS_COMPLETED = Counter(
    "todo_tasks_completed_total",
    "Total number of tasks completed",
    ["user_id"],
)

TASKS_DELETED = Counter(
    "todo_tasks_deleted_total",
    "Total number of tasks deleted",
    ["user_id"],
)

ACTIVE_TASKS = Gauge(
    "todo_active_tasks",
    "Number of active (incomplete) tasks",
    ["user_id"],
)

OVERDUE_TASKS = Gauge(
    "todo_overdue_tasks",
    "Number of overdue tasks",
    ["user_id"],
)

# Reminder metrics
REMINDERS_SCHEDULED = Counter(
    "todo_reminders_scheduled_total",
    "Total number of reminders scheduled",
)

REMINDERS_SENT = Counter(
    "todo_reminders_sent_total",
    "Total number of reminders successfully sent",
)

REMINDERS_FAILED = Counter(
    "todo_reminders_failed_total",
    "Total number of reminders that failed to send",
)

REMINDER_DELIVERY_LATENCY = Histogram(
    "todo_reminder_delivery_latency_seconds",
    "Latency between scheduled time and actual delivery",
    buckets=[1, 5, 10, 30, 60, 120, 300, 600],
)

# Kafka metrics
KAFKA_MESSAGES_PRODUCED = Counter(
    "todo_kafka_messages_produced_total",
    "Total Kafka messages produced",
    ["topic"],
)

KAFKA_MESSAGES_CONSUMED = Counter(
    "todo_kafka_messages_consumed_total",
    "Total Kafka messages consumed",
    ["topic", "consumer_group"],
)

KAFKA_CONSUMER_LAG = Gauge(
    "todo_kafka_consumer_lag",
    "Kafka consumer lag (messages behind)",
    ["topic", "partition", "consumer_group"],
)

KAFKA_PROCESSING_TIME = Histogram(
    "todo_kafka_message_processing_seconds",
    "Time to process Kafka messages",
    ["topic"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

# WebSocket metrics
WEBSOCKET_CONNECTIONS = Gauge(
    "todo_websocket_connections",
    "Current number of WebSocket connections",
)

WEBSOCKET_MESSAGES_SENT = Counter(
    "todo_websocket_messages_sent_total",
    "Total WebSocket messages sent",
    ["message_type"],
)

# Database metrics
DB_QUERY_TIME = Histogram(
    "todo_db_query_seconds",
    "Database query execution time",
    ["operation", "table"],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0],
)

DB_CONNECTION_POOL_SIZE = Gauge(
    "todo_db_connection_pool_size",
    "Current database connection pool size",
)

DB_CONNECTION_POOL_CHECKED_OUT = Gauge(
    "todo_db_connection_pool_checked_out",
    "Number of database connections currently in use",
)


# =============================================================================
# Metric Helper Functions
# =============================================================================


def record_task_created(user_id: str, priority: str) -> None:
    """Record a task creation metric."""
    TASKS_CREATED.labels(user_id=user_id, priority=priority).inc()


def record_task_completed(user_id: str) -> None:
    """Record a task completion metric."""
    TASKS_COMPLETED.labels(user_id=user_id).inc()


def record_task_deleted(user_id: str) -> None:
    """Record a task deletion metric."""
    TASKS_DELETED.labels(user_id=user_id).inc()


def record_reminder_scheduled() -> None:
    """Record a reminder scheduled metric."""
    REMINDERS_SCHEDULED.inc()


def record_reminder_sent(latency_seconds: float) -> None:
    """Record a successful reminder delivery."""
    REMINDERS_SENT.inc()
    REMINDER_DELIVERY_LATENCY.observe(latency_seconds)


def record_reminder_failed() -> None:
    """Record a failed reminder delivery."""
    REMINDERS_FAILED.inc()


def record_kafka_produced(topic: str) -> None:
    """Record a Kafka message production."""
    KAFKA_MESSAGES_PRODUCED.labels(topic=topic).inc()


def record_kafka_consumed(topic: str, consumer_group: str) -> None:
    """Record a Kafka message consumption."""
    KAFKA_MESSAGES_CONSUMED.labels(topic=topic, consumer_group=consumer_group).inc()


def update_kafka_lag(topic: str, partition: int, consumer_group: str, lag: int) -> None:
    """Update Kafka consumer lag metric."""
    KAFKA_CONSUMER_LAG.labels(
        topic=topic, partition=str(partition), consumer_group=consumer_group
    ).set(lag)


@contextmanager
def track_kafka_processing(topic: str):
    """Context manager to track Kafka message processing time."""
    start = time.perf_counter()
    try:
        yield
    finally:
        duration = time.perf_counter() - start
        KAFKA_PROCESSING_TIME.labels(topic=topic).observe(duration)


def update_websocket_connections(count: int) -> None:
    """Update WebSocket connection count."""
    WEBSOCKET_CONNECTIONS.set(count)


def record_websocket_message(message_type: str) -> None:
    """Record a WebSocket message sent."""
    WEBSOCKET_MESSAGES_SENT.labels(message_type=message_type).inc()


@contextmanager
def track_db_query(operation: str, table: str):
    """Context manager to track database query time."""
    start = time.perf_counter()
    try:
        yield
    finally:
        duration = time.perf_counter() - start
        DB_QUERY_TIME.labels(operation=operation, table=table).observe(duration)


# =============================================================================
# FastAPI Instrumentator Setup
# =============================================================================


def setup_metrics(app) -> Instrumentator:
    """Set up Prometheus metrics instrumentation for FastAPI.

    Args:
        app: FastAPI application instance

    Returns:
        Configured Instrumentator instance
    """
    # Set application info
    APP_INFO.info({
        "version": "1.0.0",
        "environment": "production",
    })

    # Create instrumentator
    instrumentator = Instrumentator(
        should_group_status_codes=True,
        should_ignore_untemplated=True,
        should_respect_env_var=True,
        should_instrument_requests_inprogress=True,
        excluded_handlers=["/metrics", "/health", "/api/health"],
        inprogress_name="todo_http_requests_inprogress",
        inprogress_labels=True,
    )

    # Add default metrics
    instrumentator.add(
        metrics.default(
            metric_namespace="todo",
            metric_subsystem="http",
            latency_lowr_buckets=[0.01, 0.025, 0.05],
        )
    )

    # Add request size metric
    instrumentator.add(
        metrics.request_size(
            metric_namespace="todo",
            metric_subsystem="http",
        )
    )

    # Add response size metric
    instrumentator.add(
        metrics.response_size(
            metric_namespace="todo",
            metric_subsystem="http",
        )
    )

    # Add custom metric for API endpoint latency by path
    def api_latency_by_path() -> Callable[[MetricInfo], None]:
        LATENCY = Histogram(
            "todo_api_endpoint_latency_seconds",
            "API endpoint latency by path",
            ["method", "path", "status"],
            buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
        )

        def instrumentation(info: MetricInfo) -> None:
            if info.modified_handler:
                path = info.modified_handler
            else:
                path = info.request.url.path

            LATENCY.labels(
                method=info.request.method,
                path=path,
                status=info.response.status_code if info.response else 0,
            ).observe(info.modified_duration)

        return instrumentation

    instrumentator.add(api_latency_by_path())

    # Instrument the app and expose metrics endpoint
    instrumentator.instrument(app).expose(
        app,
        endpoint="/metrics",
        include_in_schema=False,
        tags=["monitoring"],
    )

    logger.info("Prometheus metrics instrumentation enabled")
    return instrumentator
