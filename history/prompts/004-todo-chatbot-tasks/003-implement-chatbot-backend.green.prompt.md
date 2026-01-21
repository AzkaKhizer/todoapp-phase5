---
id: 003
title: Implement Chatbot Backend
stage: green
date: 2026-01-20
surface: agent
model: claude-opus-4-5
feature: 004-todo-chatbot-tasks
branch: 004-todo-chatbot-tasks
user: TOSHIBA
command: /sp.implement (continuation)
labels: ["implementation", "mcp", "openai", "chatbot", "fastapi"]
links:
  spec: specs/004-todo-chatbot-tasks/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/app/models/conversation.py
  - backend/app/models/message.py
  - backend/app/models/__init__.py
  - backend/app/schemas/chat.py
  - backend/app/mcp/__init__.py
  - backend/app/mcp/tools.py
  - backend/app/mcp/validation.py
  - backend/app/services/agent.py
  - backend/app/services/chat.py
  - backend/app/routers/chat.py
  - backend/app/main.py
  - backend/.env.example
tests:
  - Manual import verification (PASS)
---

## Prompt

Continue implementation of AI-Powered Todo Chatbot - Part 1 from tasks.md. Execute all phases from setup through integration.

## Response snapshot

Implemented complete backend for AI chatbot task management:

**Phase 1: Setup**
- Verified openai>=1.0.0 in requirements.txt
- Added OPENAI_API_KEY to .env.example

**Phase 2: Foundation (18 tasks)**
- Created Conversation model with UUID primary key, user_id, title, timestamps
- Created Message model with role (user/assistant/tool), content, tool_calls
- Registered models in __init__.py and main.py
- Created chat schemas: ChatRequest, ChatResponse, ConversationResponse, MessageResponse
- Created MCP package with tool definitions
- Created OpenAI agent service with system prompt
- Created chat service with conversation/message CRUD
- Created chat router with POST /api/chat and conversation management endpoints

**Phase 3-7: User Stories (all 5 MCP tools)**
- `add_task`: Create tasks with title validation
- `list_tasks`: View tasks with position numbers and filter (all/pending/completed)
- `complete_task`: Mark complete by position with error handling
- `delete_task`: Delete by position
- `update_task`: Update title/description by position

**Phase 8: Integration**
- Full message flow: router -> agent -> MCP tools -> task service
- Conversation persistence with message storage
- History loading for context (last 20 messages)
- Input validation module
- OpenAI API error handling (timeout, rate limit, API errors)
- 30s request timeout

## Outcome

- Impact: Complete backend implementation for AI chatbot with 5 MCP tools
- Tests: Import verification passed; manual curl testing required
- Files: 11 files created/modified
- Next prompts: Manual testing with curl, then frontend chat UI (Part 2)
- Reflection: Efficient implementation reusing existing Task model and services

## Evaluation notes (flywheel)

- Failure modes observed: OpenAI client initialization at module level caused import errors when API key not set; fixed with lazy initialization
- Graders run and results (PASS/FAIL): Import verification - PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
