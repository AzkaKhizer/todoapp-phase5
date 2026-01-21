# Research: Todo AI Chatbot

**Feature**: 003-todo-ai-chatbot
**Date**: 2026-01-15
**Purpose**: Resolve technical unknowns and establish best practices before implementation

## Research Areas

### 1. OpenAI Agents SDK Integration

**Decision**: Use OpenAI Agents SDK with function calling for MCP tool execution

**Rationale**:
- OpenAI Agents SDK provides built-in support for tool/function calling
- Handles conversation context management automatically
- Supports streaming responses for better UX
- Well-documented with Python examples

**Alternatives Considered**:
- LangChain: More complex, overkill for this use case
- Direct OpenAI API: Would require manual tool orchestration
- Claude/Anthropic: Different API, would require separate implementation

**Implementation Pattern**:
```python
from openai import OpenAI

client = OpenAI()

tools = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Add a new task to the user's todo list",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Task title"},
                    "description": {"type": "string", "description": "Optional task description"}
                },
                "required": ["title"]
            }
        }
    }
]

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    tools=tools,
    tool_choice="auto"
)
```

---

### 2. MCP (Model Context Protocol) Architecture

**Decision**: Implement MCP tools as Python functions that wrap existing task service

**Rationale**:
- MCP provides standardized tool interface for AI agents
- Tools can be tested independently
- Clean separation between AI logic and business logic
- Reuses existing task CRUD operations

**Alternatives Considered**:
- Separate MCP server process: Too complex for this use case
- Direct database access from tools: Bypasses service layer validation
- REST API calls from tools: Adds unnecessary latency

**Implementation Pattern**:
```python
# backend/app/mcp/tools.py
from app.services import task as task_service

async def add_task(session, user_id: str, title: str, description: str = "") -> dict:
    """MCP tool: Create a new task"""
    task = await task_service.create_task(
        session, user_id, TaskCreate(title=title, description=description)
    )
    return {"id": str(task.id), "title": task.title, "message": f"Created task: {title}"}
```

---

### 3. OpenAI ChatKit Frontend Integration

**Decision**: Use `@ai-sdk/react` with custom chat components

**Rationale**:
- Vercel AI SDK provides React hooks for chat UX
- `useChat` hook handles streaming, loading states, error handling
- Works well with Next.js App Router
- Supports custom message rendering

**Alternatives Considered**:
- Raw fetch + state management: More boilerplate, no streaming
- Socket.io: Overkill, adds complexity
- Third-party chat widgets: Less customizable

**Implementation Pattern**:
```typescript
// frontend/src/hooks/useChat.ts
import { useChat as useAIChat } from 'ai/react';

export function useChat(conversationId?: string) {
  return useAIChat({
    api: '/api/chat',
    body: { conversation_id: conversationId },
    headers: async () => ({
      Authorization: `Bearer ${await getAuthToken()}`
    })
  });
}
```

---

### 4. Conversation Persistence Strategy

**Decision**: Store conversations and messages in PostgreSQL with simple integer IDs

**Rationale**:
- Consistent with existing Task model pattern
- Simple sequential IDs for user-friendly references
- Full message history enables context for AI
- Supports conversation continuity across sessions

**Alternatives Considered**:
- In-memory only: Data lost on restart
- Redis: Adds infrastructure complexity
- UUID for conversation IDs: Less user-friendly

**Schema Design**:
```
conversations
├── id: integer (PK, auto-increment)
├── user_id: string (FK to Better Auth users)
├── created_at: timestamp
└── updated_at: timestamp

messages
├── id: integer (PK, auto-increment)
├── conversation_id: integer (FK)
├── user_id: string
├── role: string (user/assistant)
├── content: text
├── tool_calls: jsonb (nullable)
└── created_at: timestamp
```

---

### 5. Task Reference Strategy

**Decision**: Use position-based numbering (1, 2, 3) within user context, not UUIDs

**Rationale**:
- Users say "complete task 3" not "complete task abc-123-def"
- Position based on creation order (most recent = highest number)
- Easier for AI to understand and validate
- Task lookup by position is simple SQL

**Alternatives Considered**:
- UUID references: Not human-friendly
- Title-based matching: Ambiguous with similar titles
- Fuzzy matching: Complex, error-prone

**Implementation**:
```python
# When listing tasks, assign position numbers
tasks = await get_tasks_for_user(session, user_id)
for i, task in enumerate(tasks, 1):
    task.position = i  # Transient, not stored

# When referencing by number
task = tasks[position - 1]  # Zero-indexed
```

---

### 6. Error Handling Strategy

**Decision**: Return user-friendly error messages with suggested actions

**Rationale**:
- AI should explain what went wrong in natural language
- Suggest corrective actions (e.g., "try listing your tasks first")
- Log technical errors for debugging
- Never expose internal errors to users

**Error Categories**:
| Category | User Message | Technical Action |
|----------|-------------|------------------|
| Task not found | "I couldn't find task {n}. Would you like to see your task list?" | Log warning, return 404 |
| Invalid input | "I need a task title to create a task. What should it be called?" | Validation error |
| AI service error | "I'm having trouble understanding. Could you rephrase that?" | Log error, retry once |
| Database error | "Something went wrong. Please try again in a moment." | Log error, alert |

---

### 7. Authentication Flow

**Decision**: Reuse existing Better Auth JWT verification for chat endpoint

**Rationale**:
- Consistent with existing `/api/tasks` authentication
- JWT contains user_id needed for task operations
- No additional auth complexity

**Flow**:
1. Frontend calls `getAuthToken()` from `auth-client.ts`
2. Token sent in `Authorization: Bearer <token>` header
3. Backend `get_current_user_id` dependency extracts user_id
4. All task operations scoped to authenticated user

---

## Dependencies Matrix

| Dependency | Version | Purpose | Risk Level |
|------------|---------|---------|------------|
| openai | ^1.0.0 | AI agent, function calling | Low - stable API |
| ai | ^3.0.0 | Vercel AI SDK for React | Low - well maintained |
| sqlmodel | existing | Conversation/Message models | None - already in use |

## Environment Setup

```bash
# Backend
pip install openai

# Frontend
npm install ai @ai-sdk/react

# Environment variables
OPENAI_API_KEY=sk-...
```

## Open Questions (Resolved)

1. ~~Which OpenAI model to use?~~ → `gpt-4o-mini` for cost efficiency, upgrade to `gpt-4o` if quality issues
2. ~~How to handle streaming?~~ → Use Vercel AI SDK streaming with FastAPI StreamingResponse
3. ~~How many messages to include in context?~~ → Last 20 messages, configurable
4. ~~How to handle tool execution errors?~~ → Return error message to AI, let it explain to user

## Next Steps

1. Create data-model.md with Conversation/Message schemas
2. Create contracts/chat-api.yaml with OpenAPI spec
3. Create quickstart.md with setup instructions
