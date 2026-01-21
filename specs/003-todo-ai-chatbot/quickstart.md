# Quickstart: Todo AI Chatbot

**Feature**: 003-todo-ai-chatbot
**Date**: 2026-01-15

## Prerequisites

- Existing Phase II setup (backend + frontend running)
- OpenAI API key with access to GPT-4o-mini or GPT-4o
- Node.js 18+ and Python 3.11+

## Setup Steps

### 1. Backend Dependencies

```bash
cd backend

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# or: .venv\Scripts\activate  # Windows

# Install new dependencies
pip install openai
```

### 2. Frontend Dependencies

```bash
cd frontend

# Install Vercel AI SDK for chat functionality
npm install ai @ai-sdk/react
```

### 3. Environment Variables

Add to `backend/.env`:
```env
# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4o-mini
```

### 4. Database Migration

The new tables will be auto-created by SQLModel on startup. Verify by checking:

```bash
# After starting the backend, check tables exist
psql $DATABASE_URL -c "\dt"

# Expected new tables:
# - conversations
# - messages
```

### 5. Verify Setup

```bash
# Start backend (if not running)
cd backend
python -m uvicorn app.main:app --reload --port 8000

# Start frontend (if not running)
cd frontend
npm run dev

# Test the chat endpoint
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"message": "Show me all my tasks"}'
```

## Usage Examples

### Creating a Task

**User**: "Add a task to buy groceries"

**Bot Response**: "I've added 'buy groceries' to your task list."

### Viewing Tasks

**User**: "Show me all my tasks"

**Bot Response**:
```
Here are your tasks:
1. buy groceries (pending)
2. call mom (completed)
3. finish report (pending)
```

### Completing a Task

**User**: "Mark task 1 as complete"

**Bot Response**: "Done! I've marked 'buy groceries' as complete."

### Deleting a Task

**User**: "Delete task 3"

**Bot Response**: "I've removed 'finish report' from your list."

## File Structure After Implementation

```
backend/app/
├── models/
│   ├── conversation.py    # NEW
│   └── message.py         # NEW
├── routers/
│   └── chat.py            # NEW
├── services/
│   ├── chat.py            # NEW
│   └── agent.py           # NEW
├── schemas/
│   └── chat.py            # NEW
└── mcp/
    ├── __init__.py        # NEW
    └── tools.py           # NEW

frontend/src/
├── app/
│   └── chat/
│       └── page.tsx       # NEW
├── components/
│   └── chat/
│       ├── ChatWindow.tsx     # NEW
│       ├── MessageBubble.tsx  # NEW
│       └── ChatInput.tsx      # NEW
├── hooks/
│   └── useChat.ts         # NEW
└── lib/
    └── chat-api.ts        # NEW
```

## Troubleshooting

### "OpenAI API key not found"
- Verify `OPENAI_API_KEY` is set in `backend/.env`
- Restart the backend server after adding

### "CORS error when calling /api/chat"
- Verify CORS middleware includes `http://localhost:3000`
- Check `backend/app/main.py` CORS configuration

### "Conversation not found"
- Ensure you're passing a valid `conversation_id`
- Or omit it to create a new conversation

### "Tool execution failed"
- Check backend logs for detailed error
- Verify task exists when completing/deleting

## API Quick Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat` | POST | Send message, get AI response |
| `/api/chat/conversations` | GET | List user's conversations |
| `/api/chat/conversations/{id}` | GET | Get conversation + messages |
| `/api/chat/conversations/{id}` | DELETE | Delete conversation |

## Next Steps

After setup, run `/sp.tasks` to generate the implementation task list.
