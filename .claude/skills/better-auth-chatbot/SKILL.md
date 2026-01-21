---
name: better-auth-chatbot
description: |
  Better Auth integration for Todo AI Chatbot with JWT authentication. Use when implementing:
  (1) JWT token verification in FastAPI middleware
  (2) User-scoped task and chat operations
  (3) Protected API endpoints requiring authentication
  (4) Extracting user_id from JWT for database queries
---

# Better Auth for AI Chatbot

Integrate Better Auth JWT authentication to secure chat and task endpoints.

## Architecture

```
Frontend (Better Auth) -> JWT Token -> FastAPI Middleware -> Verify JWT -> Extract user_id -> Database Query
```

## Existing Authentication Setup

The project already has Better Auth configured:
- Frontend: `frontend/src/lib/auth-client.ts`
- Backend: `backend/app/dependencies/auth.py`
- Token endpoint: `POST /api/auth/token`

## Quick Integration

### 1. Protect Chat Endpoint

```python
# backend/app/routers/chat.py
from fastapi import APIRouter, Depends
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.post("")
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    # current_user.id is the authenticated user's ID
    response = await process_chat(current_user.id, request.message)
    return response
```

### 2. User-Scoped Database Queries

```python
# All queries filter by user_id
tasks = await task_service.get_user_tasks(current_user.id)
conversation = await chat_service.get_or_create_conversation(current_user.id)
```

### 3. Frontend Token Attachment

```typescript
// frontend/src/lib/chat-api.ts
import { authClient } from '@/lib/auth-client';

async function getAuthHeaders() {
  const session = await authClient.getSession();
  const token = session?.token;
  return {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  };
}
```

## Key Patterns

### JWT Verification Dependency

```python
# backend/app/dependencies/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        return User(id=user_id)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### User Isolation Pattern

Every database operation MUST include user_id:

```python
# Good - user isolated
await session.exec(select(Task).where(Task.user_id == user_id))

# Bad - security vulnerability
await session.exec(select(Task).where(Task.id == task_id))
```

## Reference Files

- **JWT Verification**: See `references/jwt-verification.md` for complete middleware
- **Protected Routes**: See `references/protected-routes.md` for endpoint patterns
- **Frontend Auth**: See `references/frontend-auth.md` for token handling
