"""Authentication dependencies for protected routes."""

import uuid

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.database import get_session
from app.exceptions import AuthenticationError
from app.models.user import User
from app.services.auth import get_user_id_from_token


async def get_current_user(
    authorization: str = Header(..., description="Bearer token"),
    session: AsyncSession = Depends(get_session),
) -> User:
    """Dependency to get the current authenticated user."""
    if not authorization.startswith("Bearer "):
        raise AuthenticationError("Invalid authorization header format")

    token = authorization[7:]  # Remove "Bearer " prefix

    try:
        user_id = get_user_id_from_token(token)
    except Exception as e:
        raise AuthenticationError("Invalid or expired token") from e

    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise AuthenticationError("User not found")

    return user


async def get_current_user_id(
    authorization: str = Header(..., description="Bearer token"),
) -> uuid.UUID:
    """Dependency to get just the current user's ID from token."""
    if not authorization.startswith("Bearer "):
        raise AuthenticationError("Invalid authorization header format")

    token = authorization[7:]  # Remove "Bearer " prefix
    return get_user_id_from_token(token)
