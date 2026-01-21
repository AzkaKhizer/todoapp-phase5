# JWT Verification

Complete JWT verification middleware for FastAPI with Better Auth.

## Auth Dependency

```python
# backend/app/dependencies/auth.py
import os
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from pydantic import BaseModel

# Security scheme
security = HTTPBearer(auto_error=False)

# Configuration
SECRET_KEY = os.getenv("BETTER_AUTH_SECRET", os.getenv("AUTH_SECRET"))
ALGORITHM = "HS256"


class User(BaseModel):
    """Authenticated user from JWT token."""
    id: str
    email: Optional[str] = None
    name: Optional[str] = None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    Extract and verify JWT token from Authorization header.

    Returns authenticated User with id from token's 'sub' claim.
    Raises 401 if token is missing, invalid, or expired.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        # Decode JWT token
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        # Extract user ID from 'sub' claim
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID",
            )

        # Build user object
        return User(
            id=user_id,
            email=payload.get("email"),
            name=payload.get("name"),
        )

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Optional[User]:
    """
    Optional authentication - returns None if no token provided.
    Use for endpoints that work with or without auth.
    """
    if not credentials:
        return None

    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None
```

## Token Issuance Endpoint

```python
# backend/app/routers/auth.py
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException
from jose import jwt
from pydantic import BaseModel

router = APIRouter(prefix="/api/auth", tags=["auth"])


class TokenRequest(BaseModel):
    user_id: str
    email: Optional[str] = None
    name: Optional[str] = None


class TokenResponse(BaseModel):
    token: str
    expires_at: str


@router.post("/token", response_model=TokenResponse)
async def create_token(request: TokenRequest):
    """
    Issue JWT token for authenticated user.
    Called by frontend after Better Auth session verification.
    """
    expires_at = datetime.utcnow() + timedelta(days=7)

    payload = {
        "sub": request.user_id,
        "email": request.email,
        "name": request.name,
        "exp": expires_at,
        "iat": datetime.utcnow(),
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return TokenResponse(
        token=token,
        expires_at=expires_at.isoformat()
    )
```

## JWT Claims Reference

| Claim | Description | Required |
|-------|-------------|----------|
| `sub` | User ID (Better Auth nanoid) | Yes |
| `email` | User's email address | No |
| `name` | User's display name | No |
| `exp` | Expiration timestamp | Yes |
| `iat` | Issued at timestamp | Yes |

## Error Responses

| Status | Detail | Cause |
|--------|--------|-------|
| 401 | Missing authentication token | No Authorization header |
| 401 | Invalid token: missing user ID | Token has no 'sub' claim |
| 401 | Invalid token: Signature has expired | Token expired |
| 401 | Invalid token: Invalid signature | Wrong secret key |

## Environment Variables

```env
# backend/.env
BETTER_AUTH_SECRET=your-secret-key-here
# or
AUTH_SECRET=your-secret-key-here
```

The secret must match the one used by Better Auth in the frontend.
