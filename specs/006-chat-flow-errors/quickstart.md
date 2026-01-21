# Quickstart: Testing AI-Powered Todo Chatbot - Part 3

**Feature**: 006-chat-flow-errors
**Date**: 2026-01-21

## Prerequisites

1. Backend running on `http://localhost:8000`
2. Frontend running on `http://localhost:3000`
3. Neon PostgreSQL database connected
4. OpenAI API key configured in `backend/.env`

## Start Servers

```bash
# Terminal 1 - Backend
cd backend
.venv/Scripts/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

## Test Scenarios

### Scenario 1: Authentication Flow

**Test**: Verify JWT authentication works for chat endpoints

1. Open http://localhost:3000/login
2. Login with valid credentials
3. Navigate to http://localhost:3000/chat
4. Open browser DevTools → Network tab
5. Look for requests to `/api/chat/conversations`

**Expected**:
- Request includes `Authorization: Bearer <token>` header
- Response is 200 OK with conversations array

**If 401 Error**:
- Check `/api/auth/token` endpoint returns a token
- Verify `BETTER_AUTH_SECRET` matches between frontend and backend

---

### Scenario 2: Send Task Commands

**Test**: Basic chat interaction with task operations

1. Go to chat page (logged in)
2. Type: "Show my tasks"
3. Type: "Add task: Test the chatbot"
4. Type: "Show my tasks"
5. Type: "Complete task 1"
6. Type: "Delete task 1"

**Expected**:
- Each command gets a response within 2-3 seconds
- Tasks are created, listed, completed, deleted
- Confirmation messages are shown

---

### Scenario 3: Error Handling - Invalid Operations

**Test**: User-friendly error messages for invalid inputs

1. With no tasks, type: "Complete task 1"
   - **Expected**: "You have no tasks yet. Would you like to add one?"

2. With 2 tasks, type: "Delete task 10"
   - **Expected**: "Task #10 not found. You have 2 tasks."

3. Type: "Add task" (without description)
   - **Expected**: "I need a title for the task."

4. Type: "Complete task abc"
   - **Expected**: "Please use a task number. Example: 'Complete task 1'"

5. Type: "Make me coffee"
   - **Expected**: Helpful response suggesting valid commands

---

### Scenario 4: Conversation Persistence

**Test**: Conversations are saved and can be resumed

1. Start a new conversation
2. Send a few messages
3. Note the conversation appears in sidebar
4. Close browser tab
5. Reopen http://localhost:3000/chat
6. Click on the conversation in sidebar

**Expected**:
- Previous conversation is visible in sidebar
- Clicking it loads all previous messages
- Can continue the conversation

---

### Scenario 5: New Chat

**Test**: Starting fresh conversation

1. Have an existing conversation
2. Click "New Chat" button
3. Send a new message

**Expected**:
- Chat window clears
- New conversation created
- New entry appears in sidebar

---

### Scenario 6: Service Errors

**Test**: Graceful handling of service issues

1. **Rate Limit**: Send many messages quickly
   - **Expected**: "AI service is busy. Please wait a moment and try again."

2. **Timeout**: (Hard to test manually)
   - **Expected**: "Request timed out. Please try again."

3. **Network Error**: Disconnect network mid-request
   - **Expected**: Error banner with "Retry" button

---

### Scenario 7: User Isolation

**Test**: Users only see their own data

1. Create tasks and conversations with User A
2. Logout
3. Register/Login as User B
4. Go to chat

**Expected**:
- User B sees no conversations (or only their own)
- User B's "Show my tasks" shows empty or their own tasks
- User B cannot access User A's data

---

## Quick Debug Commands

### Check Backend Health
```bash
curl http://localhost:8000/api/health
```

### Check Auth Token (in browser console)
```javascript
// On http://localhost:3000 after login
fetch('/api/auth/token', { credentials: 'include' })
  .then(r => r.json())
  .then(console.log)
```

### Check API Request Headers (DevTools)
1. Open Network tab
2. Make a request (e.g., "Show my tasks")
3. Click the request
4. Check "Request Headers" for `Authorization: Bearer ...`

---

## Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| 401 Unauthorized | Token not sent | Check `getAuthToken()` returns token |
| 401 Unauthorized | Secret mismatch | Verify `BETTER_AUTH_SECRET` matches `JWT_SECRET_KEY` |
| 503 Service Unavailable | Missing OPENAI_API_KEY | Add to `backend/.env` |
| 429 Too Many Requests | OpenAI rate limit | Wait and retry |
| CORS Error | Backend not allowing origin | Check `allow_origins` in `main.py` |
| Infinite Loading | Port conflict | Kill processes on port 8000/3000 |

---

## Acceptance Checklist

- [ ] Login → Chat page works without 401 errors
- [ ] "Add task: X" creates a task
- [ ] "Show my tasks" lists tasks with numbers
- [ ] "Complete task N" marks task complete
- [ ] "Delete task N" removes task
- [ ] Invalid task numbers show helpful errors
- [ ] Conversations persist in sidebar
- [ ] New Chat clears and creates new conversation
- [ ] Users only see their own tasks and conversations
