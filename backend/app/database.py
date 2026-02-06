"""Database connection and session management."""

import ssl
from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from app.config import get_settings

# Import all models to ensure they are registered with SQLModel metadata
# This is required for create_tables() to create all tables
from app.models import (  # noqa: F401
    ActivityLogEntry,
    Conversation,
    Message,
    RecurrencePattern,
    Reminder,
    Tag,
    Task,
    TaskTag,
)

settings = get_settings()

# Create SSL context for Neon PostgreSQL
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

engine = create_async_engine(
    settings.database_url,
    echo=False,
    future=True,
    connect_args={"ssl": ssl_context},
)

async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session."""
    async with async_session() as session:
        yield session


async def create_tables() -> None:
    """Create all database tables.

    Also handles migration from UUID to VARCHAR for user_id column
    to support Better Auth's nanoid format.
    """
    async with engine.begin() as conn:
        # First, check if tasks table exists and has old UUID user_id column
        # If so, alter it to VARCHAR to support Better Auth nanoid format
        try:
            result = await conn.execute(
                text("""
                    SELECT data_type
                    FROM information_schema.columns
                    WHERE table_name = 'tasks' AND column_name = 'user_id'
                """)
            )
            row = result.fetchone()
            if row and row[0] == 'uuid':
                print("Migrating tasks.user_id from UUID to VARCHAR for Better Auth compatibility...")
                # Drop foreign key constraint if exists
                await conn.execute(
                    text("""
                        ALTER TABLE tasks
                        DROP CONSTRAINT IF EXISTS tasks_user_id_fkey
                    """)
                )
                # Alter column type
                await conn.execute(
                    text("""
                        ALTER TABLE tasks
                        ALTER COLUMN user_id TYPE VARCHAR(64) USING user_id::text
                    """)
                )
                print("Migration complete: tasks.user_id is now VARCHAR(64)")
        except Exception as e:
            # Table might not exist yet, which is fine
            print(f"Migration check skipped: {e}")

        # Create tables if they don't exist
        await conn.run_sync(SQLModel.metadata.create_all)


async def drop_tables() -> None:
    """Drop all database tables (for testing)."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
