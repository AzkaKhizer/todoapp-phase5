---
id: 002
title: Create Implementation Plan
stage: plan
date: 2026-01-20
surface: agent
model: claude-opus-4-5
feature: 004-todo-chatbot-tasks
branch: 004-todo-chatbot-tasks
user: TOSHIBA
command: /sp.plan
labels: ["plan", "architecture", "mcp", "openai", "chatbot"]
links:
  spec: specs/004-todo-chatbot-tasks/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/004-todo-chatbot-tasks/plan.md
  - specs/004-todo-chatbot-tasks/research.md
tests:
  - N/A (planning phase)
---

## Prompt

User provided implementation approach for AI-Powered Todo Chatbot - Part 1:

```
name: "AI-Powered Todo Chatbot - Part 1"
description: "Plan for implementing task management functionality through the AI-powered Todo chatbot interface."

approach:
  - Frontend: OpenAI ChatKit for chatbot interface (deferred to Part 2)
  - Backend: FastAPI with MCP server for task operations
  - Better Auth for user authentication
  - Neon PostgreSQL for storage
  - SQLModel ORM for models

tasks:
  - Implement user authentication with Better Auth
  - Implement task CRUD via MCP tools
  - Set up FastAPI endpoints
  - Define SQLModel ORM models
  - Integrate frontend (Part 2)
  - Implement stateless interaction flow

milestones:
  - Better Auth setup
  - Task CRUD via MCP tools
  - FastAPI endpoints
  - Statelessness with Neon PostgreSQL
```

## Response snapshot

Generated comprehensive implementation plan with:

**Technical Context**:
- Python 3.11+ backend only for Part 1
- OpenAI SDK for function calling
- Reuses existing Task model and service
- New Conversation/Message models for chat persistence

**Architecture**:
- POST /api/chat endpoint with JWT auth
- ChatService for conversation management
- OpenAI Agent with MCP tool execution
- Task Service integration (existing)

**5 MCP Tools Defined**:
| Tool | Purpose | Parameters |
|------|---------|------------|
| add_task | Create task | title, description? |
| list_tasks | View tasks | filter? |
| complete_task | Mark done | position |
| delete_task | Remove task | position |
| update_task | Modify task | position, title?, description? |

**Key Decisions**:
1. OpenAI native function calling (not LangChain)
2. Position-based task references (1, 2, 3)
3. Tools return string messages for AI relay
4. UUID primary keys for conversations
5. User-friendly error strings (not exceptions)

**5 Implementation Phases**:
1. Setup (install openai, env vars)
2. Foundation (models, schemas, router skeleton)
3. P1 User Stories (add, list, complete tools)
4. P2 User Stories (delete, update tools)
5. Integration (wire up, error handling, validation)

## Outcome

- ✅ Impact: Created focused Part 1 plan for backend MCP tools implementation
- 🧪 Tests: N/A (planning phase - manual curl testing planned)
- 📁 Files: 2 files created (plan.md, research.md)
- 🔁 Next prompts: `/sp.tasks` to generate implementation task list
- 🧠 Reflection: Scoped to backend only, frontend deferred to Part 2. References 003 research for consistency.

## Evaluation notes (flywheel)

- Failure modes observed: None - plan builds on existing 003 research
- Graders run and results (PASS/FAIL): Constitution check - PASS (all gates satisfied)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
