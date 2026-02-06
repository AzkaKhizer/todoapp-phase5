"""FastAPI application for the Todo backend."""

from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database import create_tables
from app.exceptions import TodoException
# Import models before create_tables() to register them with SQLModel.metadata
from app.models.task import Task  # noqa: F401
from app.models.conversation import Conversation  # noqa: F401
from app.models.message import Message  # noqa: F401
from app.models.tag import Tag  # noqa: F401
from app.models.task_tag import TaskTag  # noqa: F401
from app.models.recurrence import RecurrencePattern  # noqa: F401
from app.models.reminder import Reminder  # noqa: F401
from app.models.activity_log import ActivityLogEntry  # noqa: F401
from app.events.handlers import router as dapr_router
from app.routers.activity import router as activity_router
from app.routers.auth import router as auth_router
from app.routers.chat import router as chat_router
from app.routers.reminders import router as reminders_router
from app.routers.tags import router as tags_router
from app.routers.tasks import router as tasks_router
from app.routers.websocket import router as websocket_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown events."""
    # Startup
    await create_tables()
    yield
    # Shutdown
    pass


app = FastAPI(
    title="Todo Full-Stack API",
    description="REST API for Phase II Todo application",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.exception_handler(TodoException)
async def todo_exception_handler(request: Request, exc: TodoException):
    """Handle custom Todo exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
        },
    )


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# Include routers
app.include_router(activity_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(reminders_router)  # Already has /api prefix
app.include_router(tags_router, prefix="/api")
app.include_router(tasks_router, prefix="/api")

# WebSocket router for real-time sync
app.include_router(websocket_router)

# Dapr event handlers (bindings and subscriptions)
app.include_router(dapr_router)
