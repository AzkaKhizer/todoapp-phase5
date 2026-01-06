"""Authentication endpoints for registration, login, and user info."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.database import get_session
from app.dependencies.auth import get_current_user
from app.exceptions import AuthenticationError, ConflictError
from app.models.user import User
from app.schemas.auth import (
    AuthResponse,
    LoginRequest,
    MessageResponse,
    UserCreate,
    UserResponse,
)
from app.services.auth import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: UserCreate,
    session: AsyncSession = Depends(get_session),
) -> AuthResponse:
    """Register a new user."""
    # Check if email already exists
    result = await session.execute(select(User).where(User.email == data.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise ConflictError("Email already registered")

    # Create new user
    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    # Generate token
    token = create_access_token(user.id, user.email)

    return AuthResponse(
        user=UserResponse.model_validate(user),
        token=token,
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    data: LoginRequest,
    session: AsyncSession = Depends(get_session),
) -> AuthResponse:
    """Login a user and return a token."""
    # Find user by email
    result = await session.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.password_hash):
        raise AuthenticationError("Invalid email or password")

    # Generate token
    token = create_access_token(user.id, user.email)

    return AuthResponse(
        user=UserResponse.model_validate(user),
        token=token,
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    current_user: User = Depends(get_current_user),
) -> MessageResponse:
    """Logout the current user."""
    # JWT is stateless, so logout is handled client-side
    # This endpoint exists for API completeness
    return MessageResponse(message="Successfully logged out")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Get the current authenticated user's information."""
    return UserResponse.model_validate(current_user)
