# Technical Research: AI-Powered Todo Chatbot - Part 3

**Feature**: 006-chat-flow-errors
**Date**: 2026-01-21

## Current Implementation Analysis

### Backend (FastAPI)

#### Chat Router (`backend/app/routers/chat.py`)
- **Status**: Implemented with good error handling
- **Endpoints**:
  - `POST /api/chat` - Send message, get AI response
  - `GET /api/chat/conversations` - List user's conversations
  - `GET /api/chat/conversations/{id}` - Get conversation with messages
  - `DELETE /api/chat/conversations/{id}` - Delete conversation

- **Error Handling** (Already Implemented):
  - `asyncio.TimeoutError` → 504 Gateway Timeout
  - `APITimeoutError` → 504 Gateway Timeout
  - `RateLimitError` → 429 Too Many Requests
  - `APIError` → 503 Service Unavailable
  - `ValueError` (missing API key) → 503 Service Unavailable
  - Generic `Exception` → 500 Internal Server Error

#### MCP Tools (`backend/app/mcp/tools.py`)
- **Status**: Implemented with user-friendly messages
- **Tools**: add_task, list_tasks, complete_task, delete_task, update_task
- **Position-based**: Uses 1-indexed positions instead of UUIDs

**Error Messages** (Already Good):
- Empty tasks: "You have no tasks yet. Would you like to add one?"
- Invalid position: "Task #X not found. You have Y tasks."
- Missing title: "I need a title for the task."
- Already complete: "'Title' is already marked as complete."

### Frontend (Next.js)

#### Authentication Flow
```
User Login → Better Auth Session → /api/auth/token → HS256 JWT → Backend API
```

**Potential Issues**:
1. Token endpoint returns 401 if session invalid
2. API client may not be getting token correctly
3. CORS issues if credentials not included

#### Hooks
- `useChat.ts` - Chat state, sendMessage, error handling
- `useConversations.ts` - Conversation list fetching

## Identified Issues

### Issue 1: 401 on /api/chat/conversations

**Symptoms**:
```
GET /api/chat/conversations HTTP/1.1" 401 Unauthorized
```

**Possible Causes**:
1. Session not established before fetching conversations
2. Token not being retrieved/attached
3. Secret mismatch between frontend and backend

**Investigation**:
1. Check if `/api/auth/token` returns a token
2. Verify `Authorization: Bearer <token>` header is sent
3. Compare `BETTER_AUTH_SECRET` in both .env files

### Issue 2: Frontend Timing

**Symptoms**: Conversations fetch before session is ready

**Root Cause**: `useConversations` fetches on mount, but session may not be populated yet

**Solution**: Add session loading state check

## Recommendations

### 1. Debug Authentication Flow

Add console logging to trace auth:
```typescript
// In api.ts getAuthHeaders
console.log("Getting auth headers...");
const token = await getAuthToken();
console.log("Token:", token ? "Present" : "Missing");
```

### 2. Verify Environment Variables

**Frontend (.env.local)**:
```
BETTER_AUTH_SECRET=<same-as-backend>
```

**Backend (.env)**:
```
JWT_SECRET_KEY=<same-as-frontend>
```

### 3. Session State Check

```typescript
// In useConversations.ts
useEffect(() => {
  if (session?.user && !isPending) {
    fetchConversations();
  }
}, [session?.user, isPending, fetchConversations]);
```

### 4. Error Boundary for Chat

Add error boundary to catch and display auth failures gracefully.

## Dependencies Verified

| Package | Version | Status |
|---------|---------|--------|
| openai | 2.15.0 | ✅ Installed |
| better-auth | Latest | ✅ Configured |
| jose | Latest | ✅ JWT signing |
| SQLModel | Latest | ✅ Database ORM |

## Security Considerations

1. **JWT Expiration**: 7 days (appropriate for hackathon, reduce for production)
2. **User Scoping**: All queries filter by user_id
3. **Secret Sharing**: Same secret used for signing and verification
4. **CORS**: Configured for localhost:3000 only

## Next Steps

1. Add debug logging to identify auth failure point
2. Fix any environment variable mismatches
3. Add session loading guard to conversations hook
4. Test end-to-end flow after fixes
