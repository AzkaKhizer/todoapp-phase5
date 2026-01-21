# Implementation Plan: AI-Powered Todo Chatbot - Part 2 (Frontend Chat UI)

**Feature**: Frontend Chat UI for AI Task Management
**Spec**: [spec.md](./spec.md)
**Branch**: `005-chatbot-frontend-ui`
**Created**: 2026-01-20

---

## Technical Context

### Existing Infrastructure

| Component | Status | Location |
|-----------|--------|----------|
| Backend Chat API | Complete | `backend/app/routers/chat.py` |
| MCP Tools | Complete | `backend/app/mcp/tools.py` |
| Chat Schemas | Complete | `backend/app/schemas/chat.py` |
| Frontend Stack | Existing | Next.js 14, React, Tailwind CSS |
| Auth System | Complete | Better Auth with JWT |
| API Client | Existing | `frontend/src/lib/api.ts` |

### API Endpoints (Backend - Already Implemented)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat` | POST | Send message, get AI response |
| `/api/chat/conversations` | GET | List user's conversations |
| `/api/chat/conversations/{id}` | GET | Get conversation with messages |
| `/api/chat/conversations/{id}` | DELETE | Delete conversation |

### API Contracts

```typescript
// Request: POST /api/chat
interface ChatRequest {
  message: string;          // 1-2000 chars
  conversation_id?: string; // UUID, optional for new conversation
}

// Response: POST /api/chat
interface ChatResponse {
  message: string;
  conversation_id: string;
}

// Response: GET /api/chat/conversations
interface ConversationListResponse {
  conversations: Conversation[];
  total: number;
}

// Response: GET /api/chat/conversations/{id}
interface ConversationDetailResponse {
  id: string;
  title: string | null;
  messages: Message[];
  created_at: string;
  updated_at: string;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

interface Conversation {
  id: string;
  title: string | null;
  created_at: string;
  updated_at: string;
}
```

---

## Constitution Check

| Principle | Compliance | Notes |
|-----------|------------|-------|
| Spec First | PASS | Spec exists at `specs/005-chatbot-frontend-ui/spec.md` |
| Agent Discipline | PASS | Frontend-agent handles all implementation |
| Incremental Evolution | PASS | Part 1 backend complete, Part 2 is frontend |
| Test-Backed Progress | PLANNED | Will include component tests |
| Traceability | PLANNED | Code will reference FR-XXX requirements |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                        │
├─────────────────────────────────────────────────────────────────┤
│  /chat (page)                                                    │
│  ├── ChatLayout                                                  │
│  │   ├── ConversationSidebar (P3)                               │
│  │   │   ├── NewChatButton                                      │
│  │   │   └── ConversationList                                   │
│  │   └── ChatWindow                                             │
│  │       ├── MessageList                                        │
│  │       │   └── MessageBubble (user/assistant)                 │
│  │       ├── LoadingIndicator                                   │
│  │       └── ChatInput                                          │
│  │           ├── TextArea                                       │
│  │           └── SendButton                                     │
│  └── useChat (hook)                                             │
│       ├── messages state                                        │
│       ├── conversationId state                                  │
│       ├── sendMessage()                                         │
│       ├── loadConversation()                                    │
│       └── startNewChat()                                        │
├─────────────────────────────────────────────────────────────────┤
│  API Layer (existing)                                           │
│  ├── api.post('/chat', { message, conversation_id })           │
│  ├── api.get('/chat/conversations')                            │
│  └── api.get('/chat/conversations/{id}')                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Backend (FastAPI) - COMPLETE                 │
│  POST /api/chat → Agent Service → MCP Tools → Database          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Implementation Phases

### Phase 1: Core Chat Components (P1 Stories)

**Goal**: Users can send messages and receive AI responses

**Components to Create**:

1. **Chat Page** (`frontend/src/app/chat/page.tsx`)
   - Protected route (requires auth)
   - Contains ChatWindow component
   - Handles conversation state

2. **useChat Hook** (`frontend/src/hooks/useChat.ts`)
   - Manages messages state
   - Manages conversationId
   - sendMessage() function
   - Loading and error states

3. **ChatWindow Component** (`frontend/src/components/chat/ChatWindow.tsx`)
   - Container for messages and input
   - Handles scroll behavior
   - Displays loading state

4. **MessageList Component** (`frontend/src/components/chat/MessageList.tsx`)
   - Renders list of messages
   - Auto-scrolls to bottom
   - Handles empty state

5. **MessageBubble Component** (`frontend/src/components/chat/MessageBubble.tsx`)
   - Displays single message
   - Different styles for user/assistant
   - Shows timestamp

6. **ChatInput Component** (`frontend/src/components/chat/ChatInput.tsx`)
   - Text input with send button
   - Enter to send, Shift+Enter for newline
   - Character limit validation
   - Disabled while loading

**Spec References**: FR-001, FR-002, FR-003, FR-004, FR-007, FR-008, FR-013

---

### Phase 2: Conversation Management (P2 Stories)

**Goal**: Users can start new conversations and see visual feedback

**Components to Create**:

1. **NewChatButton Component** (`frontend/src/components/chat/NewChatButton.tsx`)
   - Clears current conversation
   - Starts fresh chat

2. **Error Display** (integrated into ChatWindow)
   - Shows API errors
   - Retry functionality

**Spec References**: FR-006, FR-009

---

### Phase 3: Conversation History (P3 Stories)

**Goal**: Users can access and continue previous conversations

**Components to Create**:

1. **ChatLayout Component** (`frontend/src/components/chat/ChatLayout.tsx`)
   - Sidebar + main chat area
   - Responsive layout

2. **ConversationSidebar Component** (`frontend/src/components/chat/ConversationSidebar.tsx`)
   - Lists previous conversations
   - Click to load conversation

3. **ConversationList Component** (`frontend/src/components/chat/ConversationList.tsx`)
   - Displays conversation titles
   - Shows timestamps
   - Highlights active conversation

4. **useConversations Hook** (`frontend/src/hooks/useConversations.ts`)
   - Fetches conversation list
   - Manages selection state

**Spec References**: FR-010, FR-011

---

## File Structure

```
frontend/src/
├── app/
│   └── chat/
│       └── page.tsx                 # Chat page (protected)
├── components/
│   └── chat/
│       ├── ChatLayout.tsx           # Layout with sidebar
│       ├── ChatWindow.tsx           # Main chat area
│       ├── ChatInput.tsx            # Message input
│       ├── MessageList.tsx          # Message display
│       ├── MessageBubble.tsx        # Single message
│       ├── ConversationSidebar.tsx  # Sidebar (P3)
│       ├── ConversationList.tsx     # Conv list (P3)
│       └── NewChatButton.tsx        # New chat button
├── hooks/
│   ├── useChat.ts                   # Chat state management
│   └── useConversations.ts          # Conversations list (P3)
└── lib/
    └── types.ts                     # Add chat types
```

---

## Data Flow

### Send Message Flow

```
1. User types message in ChatInput
2. User presses Enter or clicks Send
3. ChatInput validates (not empty, within limit)
4. useChat.sendMessage() called
5. Optimistically add user message to UI
6. Set loading state
7. POST /api/chat with { message, conversation_id }
8. Receive response { message, conversation_id }
9. Add assistant message to UI
10. Update conversationId if new conversation
11. Clear loading state
12. Auto-scroll to bottom
```

### Load Conversation Flow

```
1. User clicks conversation in sidebar
2. useChat.loadConversation(id) called
3. Set loading state
4. GET /api/chat/conversations/{id}
5. Receive conversation with messages
6. Replace messages state
7. Set conversationId
8. Clear loading state
```

---

## Error Handling

| Error | User Message | Recovery |
|-------|--------------|----------|
| Network error | "Connection lost. Check your internet and try again." | Retry button |
| 401 Unauthorized | Redirect to login | Auto-redirect |
| 503 Service Unavailable | "AI service is temporarily unavailable." | Retry after delay |
| 429 Rate Limited | "Too many requests. Please wait a moment." | Auto-retry after delay |
| 504 Timeout | "Request timed out. Try a shorter message." | Retry button |
| Validation error | "Message cannot be empty." | Inline validation |

---

## Success Metrics Mapping

| Success Criteria | Implementation |
|------------------|----------------|
| SC-001: Response within 5s | Loading indicator + timeout handling |
| SC-002: Page load < 2s | Code splitting, minimal bundle |
| SC-003: All operations work | E2E test coverage |
| SC-004: Workflow < 1 minute | Optimistic UI updates |
| SC-005: Errors < 1s | Immediate error display |
| SC-006: History load < 3s | Loading state + skeleton |
| SC-007: Responsive UI | Tailwind responsive classes |

---

## Dependencies

- Next.js 14 (existing)
- React 18 (existing)
- Tailwind CSS (existing)
- Better Auth (existing)
- API client (existing at `frontend/src/lib/api.ts`)

**No new dependencies required.**

---

## Testing Strategy

### Unit Tests
- useChat hook state management
- Message validation
- Error handling

### Component Tests
- ChatInput renders and validates
- MessageBubble displays correctly
- MessageList scrolls properly

### Integration Tests
- Full send/receive flow
- Conversation loading
- Authentication redirect

---

## Quickstart

### Prerequisites
- Backend running on `http://localhost:8000`
- Frontend running on `http://localhost:3000`
- User account created and logged in

### Test the Chat

1. Navigate to `http://localhost:3000/chat`
2. Type "Show my tasks" and press Enter
3. Verify AI response appears
4. Type "Add task: Test the chatbot" and press Enter
5. Verify task creation confirmation

### Verify Conversation Persistence

1. Send a few messages
2. Refresh the page
3. Click on the conversation in sidebar
4. Verify messages are restored
