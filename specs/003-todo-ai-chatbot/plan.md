# Implementation Plan: Todo AI Chatbot

**Branch**: `003-todo-ai-chatbot` | **Date**: 2026-01-15 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-todo-ai-chatbot/spec.md`

## Summary

Implement an AI-powered chatbot that enables users to manage their todo tasks through natural language conversation. The chatbot will use the OpenAI Agents SDK with Model Context Protocol (MCP) tools to interpret user intent and execute task operations (create, view, update, delete, complete). The system integrates with the existing FastAPI backend and Next.js frontend, adding new conversation/message models and a chat endpoint.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5.x (frontend)
**Primary Dependencies**:
- Backend: FastAPI, OpenAI Agents SDK, MCP SDK, SQLModel, python-jose
- Frontend: Next.js 14, OpenAI ChatKit, React 18
**Storage**: Neon Serverless PostgreSQL (existing) + new Conversation/Message tables
**Testing**: pytest (backend), Jest/React Testing Library (frontend)
**Target Platform**: Web application (desktop/mobile browsers)
**Project Type**: Web (monorepo with backend/ and frontend/)
**Performance Goals**: <5s response time for AI interactions, <3s for task operations
**Constraints**: Better Auth JWT verification required, single OpenAI API key
**Scale/Scope**: Single-user conversations, 100+ messages per conversation supported

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Spec First | ✅ PASS | Spec created at `specs/003-todo-ai-chatbot/spec.md` with 14 FRs, 8 SCs |
| II. Agent Discipline | ✅ PASS | chatbot-agent designated for this feature per constitution |
| III. Incremental Evolution | ✅ PASS | Phase II (Full-Stack) complete, Phase III (AI Chatbot) now authorized |
| IV. Test-Backed Progress | ⏳ PENDING | Tests will be written alongside implementation |
| V. Traceability | ✅ PASS | All tasks will reference FR-xxx and SC-xxx from spec |

**Phase III Entry Criteria** (from Constitution):
- ✅ Full CRUD via web UI working
- ✅ Auth working (Better Auth with JWT)
- ✅ Database persisted (Neon PostgreSQL)
- ✅ Tests pass (existing task CRUD tests)

## Project Structure

### Documentation (this feature)

```text
specs/003-todo-ai-chatbot/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (OpenAPI specs)
│   └── chat-api.yaml
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── models/
│   │   ├── task.py           # Existing - reuse
│   │   ├── conversation.py   # NEW - chat sessions
│   │   └── message.py        # NEW - chat messages
│   ├── routers/
│   │   ├── tasks.py          # Existing - reuse
│   │   └── chat.py           # NEW - chat endpoint
│   ├── services/
│   │   ├── task.py           # Existing - reuse
│   │   ├── chat.py           # NEW - conversation logic
│   │   └── agent.py          # NEW - OpenAI agent setup
│   ├── schemas/
│   │   └── chat.py           # NEW - request/response schemas
│   └── mcp/
│       ├── __init__.py       # NEW - MCP tools package
│       ├── tools.py          # NEW - MCP tool definitions
│       └── server.py         # NEW - MCP server setup
└── tests/
    ├── test_chat.py          # NEW - chat endpoint tests
    └── test_mcp_tools.py     # NEW - MCP tool tests

frontend/
├── src/
│   ├── app/
│   │   └── chat/
│   │       └── page.tsx      # NEW - chat page
│   ├── components/
│   │   └── chat/
│   │       ├── ChatWindow.tsx    # NEW - main chat component
│   │       ├── MessageBubble.tsx # NEW - message display
│   │       └── ChatInput.tsx     # NEW - message input
│   ├── hooks/
│   │   └── useChat.ts        # NEW - chat state management
│   └── lib/
│       └── chat-api.ts       # NEW - chat API client
└── tests/
    └── chat.test.tsx         # NEW - chat component tests
```

**Structure Decision**: Extending existing web application structure. Backend adds new models, routers, and MCP package. Frontend adds new chat page and components.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js)                       │
│  ┌─────────────┐    ┌──────────────┐    ┌──────────────────┐   │
│  │  ChatKit UI │ -> │  useChat()   │ -> │  /api/chat POST  │   │
│  └─────────────┘    └──────────────┘    └──────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Backend (FastAPI)                          │
│  ┌──────────────┐    ┌──────────────┐    ┌─────────────────┐   │
│  │ POST /chat   │ -> │ ChatService  │ -> │ OpenAI Agent    │   │
│  │ (JWT auth)   │    │              │    │ + MCP Tools     │   │
│  └──────────────┘    └──────────────┘    └─────────────────┘   │
│                              │                    │              │
│                              ▼                    ▼              │
│                    ┌──────────────┐    ┌─────────────────┐      │
│                    │ Conversation │    │ Task Service    │      │
│                    │ + Message    │    │ (existing CRUD) │      │
│                    └──────────────┘    └─────────────────┘      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Database (Neon PostgreSQL)                     │
│  ┌───────────┐  ┌───────────────┐  ┌────────────────┐          │
│  │   tasks   │  │ conversations │  │    messages    │          │
│  └───────────┘  └───────────────┘  └────────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

## MCP Tools Design

| Tool | Operation | Parameters | Returns |
|------|-----------|------------|---------|
| `add_task` | Create task | `title: str`, `description?: str` | Task object |
| `list_tasks` | Get all tasks | `status?: "all" \| "pending" \| "completed"` | List of tasks |
| `complete_task` | Mark complete | `task_id: int` or `title: str` | Updated task |
| `delete_task` | Remove task | `task_id: int` or `title: str` | Success message |
| `update_task` | Modify task | `task_id: int`, `title?: str`, `description?: str` | Updated task |

## Conversational Flow

1. **Receive** user message via `POST /api/chat`
2. **Authenticate** user via JWT (existing middleware)
3. **Load/Create** conversation from database
4. **Store** user message in database
5. **Build** message history array for agent context
6. **Execute** OpenAI agent with MCP tools
7. **Store** assistant response in database
8. **Return** response with tool_calls list

## Dependencies & Integration Points

### Existing Components (Reuse)
- `backend/app/models/task.py` - Task model
- `backend/app/services/task.py` - Task CRUD operations
- `backend/app/dependencies/auth.py` - JWT authentication
- `frontend/src/lib/auth-client.ts` - Auth token handling
- `frontend/src/lib/api.ts` - API client base

### New Dependencies Required
- `openai` - OpenAI Python SDK for Agents
- `mcp` - Model Context Protocol SDK
- OpenAI ChatKit (frontend) - Chat UI components

### Environment Variables Required
```
OPENAI_API_KEY=sk-...           # OpenAI API key for agent
```

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| OpenAI API latency | Medium | High | Implement streaming responses, timeout handling |
| Intent misclassification | Medium | Medium | Provide clear error messages, fallback prompts |
| Token cost escalation | Low | Medium | Limit conversation history length, use efficient prompts |
| MCP tool failures | Low | High | Wrap tools in try/catch, return user-friendly errors |

## Complexity Tracking

> No constitution violations requiring justification.

The implementation follows existing patterns:
- Models extend SQLModel (same as Task)
- Router follows existing patterns (same as tasks.py)
- Services follow existing patterns (same as task.py)
- Frontend follows existing patterns (same as dashboard)
