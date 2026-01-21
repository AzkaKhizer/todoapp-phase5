# Implementation Plan: AI-Powered Todo Chatbot - Part 3

**Branch**: `006-chat-flow-errors` | **Date**: 2026-01-21 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-chat-flow-errors/spec.md`

## Summary

Finalize the conversation flow, error handling, and database persistence for the AI-powered Todo Chatbot. The implementation focuses on ensuring smooth integration between the ChatKit UI (frontend) and FastAPI backend, with proper authentication, user-scoped operations, and comprehensive error handling.

**Key Focus Areas**:
1. Fix authentication flow for chat API endpoints (401 errors)
2. Enhance error handling in MCP tools with user-friendly messages
3. Ensure conversation persistence works correctly
4. Add missing error states to frontend components

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript/Next.js 15 (frontend)
**Primary Dependencies**: FastAPI, SQLModel, OpenAI SDK, Better Auth, React
**Storage**: Neon PostgreSQL (via SQLModel async)
**Testing**: Manual testing (hackathon scope)
**Target Platform**: Web application (desktop/mobile browsers)
**Project Type**: Web application (monorepo with backend + frontend)
**Performance Goals**: <2s response time for chat operations
**Constraints**: Stateless operations, JWT-based auth, user data isolation
**Scale/Scope**: Single-user to small team usage

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] Single backend project (FastAPI)
- [x] Single frontend project (Next.js)
- [x] No additional services introduced
- [x] Uses existing database schema
- [x] Follows existing authentication pattern

## Project Structure

### Documentation (this feature)

```text
specs/006-chat-flow-errors/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Technical analysis
├── quickstart.md        # Testing guide
└── checklists/
    └── requirements.md  # Validation checklist
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── dependencies/
│   │   └── auth.py          # JWT authentication dependency
│   ├── mcp/
│   │   ├── tools.py         # MCP tool definitions and executors
│   │   └── validation.py    # Input validation helpers
│   ├── routers/
│   │   └── chat.py          # Chat API endpoints
│   ├── services/
│   │   ├── agent.py         # OpenAI agent service
│   │   └── chat.py          # Conversation CRUD service
│   └── schemas/
│       └── chat.py          # Chat request/response schemas

frontend/
├── src/
│   ├── app/
│   │   ├── api/auth/token/  # JWT token endpoint
│   │   └── chat/            # Chat page
│   ├── components/chat/     # Chat UI components
│   ├── hooks/
│   │   ├── useChat.ts       # Chat state management
│   │   └── useConversations.ts  # Conversation list
│   └── lib/
│       ├── api.ts           # API client with auth
│       └── auth-client.ts   # Better Auth client
```

**Structure Decision**: Existing monorepo structure with backend/ and frontend/ directories is maintained. No new projects needed.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js)                       │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐ │
│  │  ChatPage   │───▶│  useChat    │───▶│  api.ts (JWT auth)  │ │
│  │  (ChatKit)  │    │  Hook       │    │  getAuthToken()     │ │
│  └─────────────┘    └─────────────┘    └──────────┬──────────┘ │
│         │                                          │            │
│         ▼                                          ▼            │
│  ┌─────────────────┐                    ┌──────────────────┐   │
│  │ ConversationList│                    │ /api/auth/token  │   │
│  │ (Sidebar)       │                    │ (HS256 JWT)      │   │
│  └─────────────────┘                    └──────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP + JWT Bearer Token
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Backend (FastAPI)                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐                                            │
│  │  /api/chat/*    │──▶ get_current_user_id() ──▶ JWT Verify   │
│  │  Endpoints      │                                            │
│  └────────┬────────┘                                            │
│           │                                                      │
│           ▼                                                      │
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │  agent.py       │───▶│  MCP Tools      │                    │
│  │  (OpenAI SDK)   │    │  (tools.py)     │                    │
│  └────────┬────────┘    └────────┬────────┘                    │
│           │                       │                              │
│           ▼                       ▼                              │
│  ┌─────────────────────────────────────────┐                   │
│  │           chat.py / task.py Services     │                   │
│  │           (User-scoped CRUD)             │                   │
│  └─────────────────────┬───────────────────┘                   │
│                        │                                         │
│                        ▼                                         │
│  ┌─────────────────────────────────────────┐                   │
│  │         Neon PostgreSQL                  │                   │
│  │  ┌────────────┐ ┌────────┐ ┌─────────┐  │                   │
│  │  │Conversation│ │Message │ │  Task   │  │                   │
│  │  └────────────┘ └────────┘ └─────────┘  │                   │
│  └─────────────────────────────────────────┘                   │
└─────────────────────────────────────────────────────────────────┘
```

## Implementation Phases

### Phase 1: Fix Authentication Flow (Priority: Critical)

**Goal**: Resolve 401 Unauthorized errors on chat endpoints

**Analysis**: The 401 error on `/api/chat/conversations` suggests the JWT token isn't being passed or verified correctly. Need to verify:
1. Frontend token retrieval from `/api/auth/token`
2. Token being included in Authorization header
3. Backend JWT verification

**Tasks**:
1. Debug token flow - add logging to identify where auth fails
2. Verify BETTER_AUTH_SECRET matches between frontend and backend
3. Ensure credentials are passed with fetch requests

### Phase 2: Enhance Error Handling (Priority: High)

**Goal**: Implement user-friendly error messages for all edge cases

**Current State**: MCP tools already have good error messages. Need to:
1. Add validation helper functions for cleaner code
2. Ensure consistent error format across all tools
3. Add helpful suggestions to error messages

**Tasks**:
1. Create `mcp/validation.py` with helper functions
2. Update error messages to include suggestions
3. Handle unrecognized commands gracefully in agent

### Phase 3: Frontend Error Display (Priority: High)

**Goal**: Display errors properly in ChatKit UI

**Tasks**:
1. Handle 401 errors with redirect to login
2. Display retry button for transient errors
3. Show helpful error messages in chat bubbles

### Phase 4: Conversation Flow Verification (Priority: Medium)

**Goal**: Ensure end-to-end conversation flow works correctly

**Tasks**:
1. Test conversation creation and persistence
2. Verify conversation history loads correctly
3. Test conversation selection from sidebar

## Key Technical Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Auth Token Flow | Custom HS256 JWT endpoint | Allows frontend session to generate backend-compatible tokens |
| Error Format | User-friendly strings | MCP tools return natural language for AI to relay |
| Position-based Tasks | 1-indexed positions | More natural for chat ("Complete task 1") than UUIDs |
| Conversation Scoping | user_id filter on all queries | Ensures data isolation without complex ACL |

## Risk Analysis

| Risk | Impact | Mitigation |
|------|--------|------------|
| Token verification mismatch | High - Blocks all auth | Verify shared secret, add debug logging |
| OpenAI rate limits | Medium - Degraded UX | Already handled with 429 response |
| Session expiry | Medium - Broken auth | Frontend checks session before requests |

## Success Metrics

From spec SC-001 to SC-007:
- [ ] Task workflow completes in <30s
- [ ] Error responses in <500ms with suggestions
- [ ] 100% user-scoped operations
- [ ] Conversation persistence across sessions
- [ ] Conversation list loads in <1s
- [ ] Graceful service unavailability handling
- [ ] 401 for unauthenticated requests
