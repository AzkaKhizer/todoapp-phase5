"""Pytest fixtures for backend tests."""

import asyncio
import uuid
from collections.abc import AsyncGenerator, Generator
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from app.config import get_settings
from app.database import get_session
from app.main import app
from app.models.task import Task

# Test database URL - use SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

settings = get_settings()


def create_test_token(user_id: str, email: str) -> str:
    """Create a JWT token for testing (mimics Better Auth tokens)."""
    payload = {
        "sub": user_id,
        "email": email,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
    }
    return jwt.encode(payload, settings.better_auth_secret, algorithm="HS256")


@dataclass
class MockUser:
    """Mock user for testing (Better Auth manages real users)."""
    id: str
    email: str


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def async_engine():
    """Create async engine for tests."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
    )
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def async_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create async session for tests."""
    async_session_factory = sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with async_session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def client(async_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with overridden database session."""

    async def get_test_session() -> AsyncGenerator[AsyncSession, None]:
        yield async_session

    app.dependency_overrides[get_session] = get_test_session

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user() -> MockUser:
    """Create a mock test user (Better Auth manages real users)."""
    return MockUser(
        id=str(uuid.uuid4()),
        email="test@example.com",
    )


@pytest_asyncio.fixture
async def test_user_token(test_user: MockUser) -> str:
    """Get auth token for test user."""
    return create_test_token(test_user.id, test_user.email)


@pytest_asyncio.fixture
async def auth_headers(test_user_token: str) -> dict[str, str]:
    """Get authorization headers for test user."""
    return {"Authorization": f"Bearer {test_user_token}"}


@pytest_asyncio.fixture
async def other_user() -> MockUser:
    """Create another mock test user for isolation tests."""
    return MockUser(
        id=str(uuid.uuid4()),
        email="other@example.com",
    )


@pytest_asyncio.fixture
async def other_user_token(other_user: MockUser) -> str:
    """Get auth token for other user."""
    return create_test_token(other_user.id, other_user.email)


@pytest_asyncio.fixture
async def other_auth_headers(other_user_token: str) -> dict[str, str]:
    """Get authorization headers for other user."""
    return {"Authorization": f"Bearer {other_user_token}"}


@pytest_asyncio.fixture
async def test_task(async_session: AsyncSession, test_user: MockUser) -> Task:
    """Create a test task for the test user."""
    task = Task(
        id=uuid.uuid4(),
        title="Test Task",
        description="Test Description",
        is_complete=False,
        user_id=test_user.id,
    )
    async_session.add(task)
    await async_session.commit()
    await async_session.refresh(task)
    return task


@pytest_asyncio.fixture
async def completed_task(async_session: AsyncSession, test_user: MockUser) -> Task:
    """Create a completed test task for the test user."""
    task = Task(
        id=uuid.uuid4(),
        title="Completed Task",
        description="This task is done",
        is_complete=True,
        user_id=test_user.id,
    )
    async_session.add(task)
    await async_session.commit()
    await async_session.refresh(task)
    return task


@pytest_asyncio.fixture
async def other_user_task(async_session: AsyncSession, other_user: MockUser) -> Task:
    """Create a task for the other user (for isolation tests)."""
    task = Task(
        id=uuid.uuid4(),
        title="Other User Task",
        description="Belongs to other user",
        is_complete=False,
        user_id=other_user.id,
    )
    async_session.add(task)
    await async_session.commit()
    await async_session.refresh(task)
    return task
