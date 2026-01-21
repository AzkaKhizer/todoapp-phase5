# Quickstart: AI-Powered Todo Chatbot Frontend UI

## Prerequisites

1. **Backend running** on `http://localhost:8000`
   ```bash
   cd backend
   uvicorn app.main:app --reload --port 8000
   ```

2. **Frontend running** on `http://localhost:3000`
   ```bash
   cd frontend
   npm run dev
   ```

3. **User account** created and logged in

---

## Test Scenarios

### Scenario 1: Send First Message (US1)

1. Navigate to `http://localhost:3000/chat`
2. Type "Hello, show me my tasks" in the input
3. Press Enter or click Send

**Expected**:
- Your message appears in the chat (right-aligned, user style)
- Loading indicator shows
- AI response appears (left-aligned, assistant style)
- If no tasks: "You have no tasks yet. Would you like to add one?"

---

### Scenario 2: Create Task via Chat (US1)

1. In the chat, type: "Add a task to buy groceries"
2. Press Enter

**Expected**:
- AI responds: "Created task: 'buy groceries'" (or similar)
- Task is actually created in database

**Verify**:
- Type "Show my tasks"
- The new task appears in the list

---

### Scenario 3: Complete Task via Chat (US3)

1. First create a task or have existing tasks
2. Type "Show my tasks" to see positions
3. Type "Mark task 1 as complete"

**Expected**:
- AI responds: "Marked 'task title' as complete."

---

### Scenario 4: View Chat History (US2)

1. Send several messages
2. Scroll up to see previous messages
3. Refresh the page

**Expected**:
- All messages remain visible in order
- After refresh, conversation continues

---

### Scenario 5: Start New Conversation (US4)

1. Send a few messages
2. Click "New Chat" button

**Expected**:
- Chat window clears
- New conversation begins on next message

---

### Scenario 6: Load Previous Conversation (US5)

1. Have multiple conversations (create some if needed)
2. Click on a conversation in the sidebar

**Expected**:
- Previous messages load
- Can continue chatting in that conversation

---

## Error Scenarios

### Network Error
1. Disconnect internet
2. Try to send a message

**Expected**: Error message with retry option

### Empty Message
1. Click Send with empty input

**Expected**: Validation prevents send, inline error

### Long Message
1. Try to paste >2000 characters

**Expected**: Character limit warning

### Unauthenticated
1. Clear cookies
2. Navigate to /chat

**Expected**: Redirect to login page

---

## API Verification

### Check Backend Health
```bash
curl http://localhost:8000/api/health
```

### Test Chat Endpoint (with auth token)
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"message": "Show my tasks"}'
```

### List Conversations
```bash
curl http://localhost:8000/api/chat/conversations \
  -H "Authorization: Bearer <token>"
```
