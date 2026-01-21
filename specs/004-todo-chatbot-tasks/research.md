# Research: AI-Powered Todo Chatbot - Part 1

**Feature**: 004-todo-chatbot-tasks
**Date**: 2026-01-20
**Purpose**: Technical decisions for task management via MCP tools

> **Note**: This feature is Part 1 of the AI chatbot implementation. Full research is documented in `specs/003-todo-ai-chatbot/research.md`. This document focuses on decisions specific to Part 1 (backend MCP tools).

## Scope Clarification

**Part 1 (This Feature)**: Backend MCP tools + chat endpoint
- MCP tool definitions (add_task, list_tasks, complete_task, delete_task, update_task)
- OpenAI Agent integration
- Conversation/Message models
- POST /api/chat endpoint

**Out of Scope for Part 1**: Frontend chat UI (deferred to Part 2)

## Key Technical Decisions

### 1. OpenAI Function Calling Approach

**Decision**: Use OpenAI's native function calling (not LangChain/agents framework)

**Rationale**:
- Simpler implementation with fewer dependencies
- Direct control over tool execution
- Well-documented API with Python SDK
- No agent orchestration overhead needed for this use case

**Implementation**:
```python
from openai import AsyncOpenAI

client = AsyncOpenAI()

response = await client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    tools=TOOL_DEFINITIONS,  # List of function schemas
    tool_choice="auto"
)

# Handle tool calls
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        result = await execute_tool(tool_call, user_id, session)
```

---

### 2. Position-Based Task References

**Decision**: Use position numbers (1, 2, 3) instead of UUIDs for task references

**Rationale**:
- Natural language: "complete task 3" vs "complete task abc-123"
- Easier for AI to parse and validate
- Consistent with common todo app UX
- Position calculated from ordered task list

**Implementation**:
```python
async def get_task_by_position(session, user_id: str, position: int) -> Task:
    """Get task by 1-indexed position number."""
    tasks, _ = await task_service.get_tasks(session, user_id)
    if position < 1 or position > len(tasks):
        raise ValueError(f"Task #{position} not found. You have {len(tasks)} tasks.")
    return tasks[position - 1]  # Convert to 0-indexed
```

---

### 3. MCP Tool Design Pattern

**Decision**: Tools return string messages for AI to relay to user

**Rationale**:
- AI can incorporate result into natural response
- Consistent format for all tool outputs
- Easy to test and debug
- User-friendly error messages

**Tool Return Pattern**:
```python
async def add_task(...) -> str:
    task = await create_task(...)
    return f"Created task: '{task.title}'"

async def list_tasks(...) -> str:
    tasks = await get_tasks(...)
    if not tasks:
        return "You have no tasks yet. Would you like to add one?"
    lines = [f"{i}. {t.title} ({'completed' if t.is_complete else 'pending'})"
             for i, t in enumerate(tasks, 1)]
    return "Your tasks:\n" + "\n".join(lines)
```

---

### 4. Conversation Persistence Model

**Decision**: Store conversations and messages with UUID primary keys

**Rationale**:
- Consistent with existing Task model
- UUID avoids collision issues
- Messages linked to conversation via foreign key
- Supports multi-turn conversations

**Schema**:
```python
class Conversation(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(index=True)
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class Message(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id")
    role: str  # user, assistant, tool
    content: str
    created_at: datetime
```

---

### 5. System Prompt Design

**Decision**: Concise system prompt with clear tool descriptions

**Rationale**:
- Reduces token usage
- Tool descriptions guide intent classification
- Clear instructions for position-based references

**System Prompt**:
```
You are a helpful task management assistant. Help users manage their todo list.

When users want to:
- Add a task: Use add_task with the title
- View tasks: Use list_tasks (optionally filter by status)
- Complete a task: Use complete_task with the position number
- Delete a task: Use delete_task with the position number
- Update a task: Use update_task with the position number

Always confirm actions with the task title. Be concise and friendly.
```

---

### 6. Error Handling Strategy

**Decision**: Return user-friendly error strings from tools, not exceptions

**Rationale**:
- AI can incorporate errors into natural response
- Consistent with successful return pattern
- No need for complex error propagation
- Errors include suggested actions

**Error Patterns**:
```python
# Position validation
if position > len(tasks):
    return f"Task #{position} not found. You have {len(tasks)} tasks."

# Empty list
if not tasks:
    return "You have no tasks yet. Would you like to add one?"

# Already completed
if task.is_complete:
    return f"'{task.title}' is already marked as complete."
```

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| openai | >=1.0.0 | Function calling API |
| sqlmodel | (existing) | Conversation/Message models |
| python-jose | (existing) | JWT verification |

## Environment Setup

```bash
# Install OpenAI SDK
pip install openai>=1.0.0

# Environment variable
OPENAI_API_KEY=sk-proj-...
```

## References

- Full chatbot research: `specs/003-todo-ai-chatbot/research.md`
- OpenAI Function Calling: https://platform.openai.com/docs/guides/function-calling
- Existing Task Service: `backend/app/services/task.py`
