# Tasks: Todo AI Chatbot

**Input**: Design documents from `/specs/003-todo-ai-chatbot/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/chat-api.yaml, research.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US6)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/app/` for source, `backend/tests/` for tests
- **Frontend**: `frontend/src/` for source, `frontend/tests/` for tests

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Install dependencies and configure environment

- [ ] T001 Install openai Python SDK in backend/requirements.txt
- [ ] T002 [P] Install ai and @ai-sdk/react packages in frontend/package.json
- [ ] T003 [P] Add OPENAI_API_KEY to backend/.env.example
- [ ] T004 [P] Add OPENAI_API_KEY to backend/.env (local development)

**Checkpoint**: Dependencies installed, environment configured

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Models (Required for all stories)

- [ ] T005 [P] Create Conversation model in backend/app/models/conversation.py
- [ ] T006 [P] Create Message model in backend/app/models/message.py
- [ ] T007 Register models in backend/app/models/__init__.py
- [ ] T008 Import models in backend/app/main.py for table creation

### Chat Schemas (Required for API)

- [ ] T009 Create ChatRequest schema in backend/app/schemas/chat.py
- [ ] T010 [P] Create ChatResponse schema in backend/app/schemas/chat.py
- [ ] T011 [P] Create ConversationResponse schemas in backend/app/schemas/chat.py
- [ ] T012 [P] Create MessageResponse schema in backend/app/schemas/chat.py

### MCP Tools Infrastructure (Required for all task operations)

- [ ] T013 Create backend/app/mcp/__init__.py package
- [ ] T014 [P] Create MCP tool definitions in backend/app/mcp/tools.py with add_task, list_tasks, complete_task, delete_task, update_task
- [ ] T015 [P] Create OpenAI agent configuration in backend/app/services/agent.py

### Chat Service (Required for API)

- [ ] T016 Create chat service with conversation CRUD in backend/app/services/chat.py
- [ ] T017 [P] Add message storage functions to backend/app/services/chat.py

### API Router (Required for all stories)

- [ ] T018 Create chat router with POST /api/chat endpoint in backend/app/routers/chat.py
- [ ] T019 [P] Add GET /api/chat/conversations endpoint in backend/app/routers/chat.py
- [ ] T020 [P] Add GET /api/chat/conversations/{id} endpoint in backend/app/routers/chat.py
- [ ] T021 [P] Add DELETE /api/chat/conversations/{id} endpoint in backend/app/routers/chat.py
- [ ] T022 Register chat router in backend/app/main.py

**Checkpoint**: Foundation ready - backend can receive chat messages and execute MCP tools

---

## Phase 3: User Story 1 - Create Task via Natural Language (Priority: P1) 🎯 MVP

**Goal**: Users can create tasks by sending natural language messages like "Add a task to buy groceries"

**Independent Test**: Send "Add a task to buy groceries" via POST /api/chat and verify task is created

**Spec Reference**: FR-001, FR-002, FR-013, SC-001

### Implementation for User Story 1

- [ ] T023 [US1] Implement add_task MCP tool logic in backend/app/mcp/tools.py
- [ ] T024 [US1] Add task creation intent handling in agent system prompt in backend/app/services/agent.py
- [ ] T025 [US1] Test add_task via curl/Postman: POST /api/chat with {"message": "Add a task to buy groceries"}
- [ ] T026 [US1] Verify task appears in database with correct user_id

**Checkpoint**: User Story 1 complete - users can create tasks via natural language

---

## Phase 4: User Story 2 - View Tasks via Natural Language (Priority: P1)

**Goal**: Users can view their tasks by asking "Show me all my tasks"

**Independent Test**: Send "Show me all my tasks" and verify bot returns formatted task list

**Spec Reference**: FR-001, FR-003, SC-003

### Implementation for User Story 2

- [ ] T027 [US2] Implement list_tasks MCP tool logic in backend/app/mcp/tools.py
- [ ] T028 [US2] Add task listing intent handling in agent system prompt in backend/app/services/agent.py
- [ ] T029 [US2] Add position numbering (1, 2, 3) to list_tasks output for user-friendly display
- [ ] T030 [US2] Test list_tasks via POST /api/chat with {"message": "Show me all my tasks"}
- [ ] T031 [US2] Verify empty list response: "You have no tasks. Would you like to add one?"

**Checkpoint**: User Story 2 complete - users can view tasks via natural language

---

## Phase 5: User Story 3 - Mark Task Complete via Natural Language (Priority: P1)

**Goal**: Users can mark tasks complete by saying "Mark task 1 as complete"

**Independent Test**: Create task, view tasks to get position, then mark complete and verify status change

**Spec Reference**: FR-001, FR-004, FR-013, FR-014, SC-004

### Implementation for User Story 3

- [ ] T032 [US3] Implement complete_task MCP tool logic in backend/app/mcp/tools.py
- [ ] T033 [US3] Add task completion intent handling in agent system prompt in backend/app/services/agent.py
- [ ] T034 [US3] Handle task lookup by position number (not UUID)
- [ ] T035 [US3] Add error handling for non-existent task: "I couldn't find that task"
- [ ] T036 [US3] Test complete_task via POST /api/chat with {"message": "Mark task 1 as complete"}

**Checkpoint**: User Story 3 complete - users can complete tasks via natural language

---

## Phase 6: User Story 4 - Delete Task via Natural Language (Priority: P2)

**Goal**: Users can delete tasks by saying "Delete task 2"

**Independent Test**: Create task, then delete via "Delete task 1" and verify removal

**Spec Reference**: FR-001, FR-005, FR-013, FR-014, SC-004

### Implementation for User Story 4

- [ ] T037 [US4] Implement delete_task MCP tool logic in backend/app/mcp/tools.py
- [ ] T038 [US4] Add task deletion intent handling in agent system prompt in backend/app/services/agent.py
- [ ] T039 [US4] Handle task lookup by position or title
- [ ] T040 [US4] Test delete_task via POST /api/chat with {"message": "Delete task 1"}

**Checkpoint**: User Story 4 complete - users can delete tasks via natural language

---

## Phase 7: User Story 5 - Update Task via Natural Language (Priority: P2)

**Goal**: Users can update task details by saying "Update task 1 title to..."

**Independent Test**: Create task, update title, verify change persisted

**Spec Reference**: FR-001, FR-006, FR-013, SC-004

### Implementation for User Story 5

- [ ] T041 [US5] Implement update_task MCP tool logic in backend/app/mcp/tools.py
- [ ] T042 [US5] Add task update intent handling in agent system prompt in backend/app/services/agent.py
- [ ] T043 [US5] Handle title and description updates
- [ ] T044 [US5] Test update_task via POST /api/chat with {"message": "Change task 1 title to Buy organic groceries"}

**Checkpoint**: User Story 5 complete - users can update tasks via natural language

---

## Phase 8: User Story 6 - Conversation Persistence (Priority: P2)

**Goal**: Chat history is saved and can be resumed across sessions

**Independent Test**: Have conversation, close chat, reopen with conversation_id, verify history loads

**Spec Reference**: FR-007, FR-010, FR-011, FR-012, SC-005, SC-008

### Implementation for User Story 6

- [ ] T045 [US6] Implement get_or_create_conversation in backend/app/services/chat.py
- [ ] T046 [US6] Implement save_message for both user and assistant messages in backend/app/services/chat.py
- [ ] T047 [US6] Implement get_conversation_history (last 20 messages) in backend/app/services/chat.py
- [ ] T048 [US6] Build message array for OpenAI agent context from conversation history
- [ ] T049 [US6] Test conversation persistence: send message, note conversation_id, send another with same ID
- [ ] T050 [US6] Test new conversation creation when no conversation_id provided

**Checkpoint**: User Story 6 complete - conversation history persists across sessions

---

## Phase 9: Frontend Chat UI (Priority: P1)

**Goal**: Web interface for chatting with the AI bot

**Independent Test**: Open /chat page, send message, see response

**Spec Reference**: FR-001, FR-009, SC-006

### Implementation for Frontend

- [ ] T051 [P] Create useChat hook in frontend/src/hooks/useChat.ts
- [ ] T052 [P] Create chat API client in frontend/src/lib/chat-api.ts
- [ ] T053 [P] Create MessageBubble component in frontend/src/components/chat/MessageBubble.tsx
- [ ] T054 [P] Create ChatInput component in frontend/src/components/chat/ChatInput.tsx
- [ ] T055 Create ChatWindow component in frontend/src/components/chat/ChatWindow.tsx
- [ ] T056 Create chat page in frontend/src/app/chat/page.tsx
- [ ] T057 Add chat link to navigation in frontend/src/components/layout/Header.tsx
- [ ] T058 Test frontend: login, navigate to /chat, send "Add a task to test", verify response

**Checkpoint**: Frontend complete - full chat UI working

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T059 [P] Add error handling for OpenAI API failures in backend/app/services/agent.py
- [ ] T060 [P] Add timeout handling (30s max) for AI responses
- [ ] T061 [P] Add rate limiting to chat endpoint (10 req/min per user)
- [ ] T062 Add logging for all MCP tool invocations
- [ ] T063 [P] Handle ambiguous user messages with clarification prompt
- [ ] T064 [P] Handle long task titles (>200 chars) with truncation warning
- [ ] T065 Run quickstart.md validation end-to-end

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - can start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 - BLOCKS all user stories
- **Phases 3-8 (User Stories)**: All depend on Phase 2 completion
  - US1, US2, US3 are P1 priority - implement first
  - US4, US5, US6 are P2 priority - implement after P1 stories
- **Phase 9 (Frontend)**: Can start after Phase 2, but best after US1-US3
- **Phase 10 (Polish)**: Depends on all desired user stories being complete

### User Story Dependencies

- **US1 (Create)**: No dependencies on other stories - MVP entry point
- **US2 (View)**: No dependencies - can test with tasks from US1
- **US3 (Complete)**: Requires tasks to exist (US1) but can be implemented independently
- **US4 (Delete)**: Requires tasks to exist (US1) but independent implementation
- **US5 (Update)**: Requires tasks to exist (US1) but independent implementation
- **US6 (Persistence)**: Infrastructure task, affects all stories but can be added incrementally

### Parallel Opportunities

Within Phase 2 (Foundational):
```
T005 [P] Conversation model  ||  T006 [P] Message model
T009-T012 Schemas can run in parallel
T014 [P] MCP tools  ||  T015 [P] Agent config
T018-T021 Router endpoints can run in parallel
```

Within Phase 9 (Frontend):
```
T051 [P] useChat hook  ||  T052 [P] chat-api  ||  T053 [P] MessageBubble  ||  T054 [P] ChatInput
```

---

## Implementation Strategy

### MVP First (User Stories 1-3 Only)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational (T005-T022)
3. Complete Phase 3: US1 Create Task (T023-T026)
4. **VALIDATE**: Test "Add a task to buy groceries" works
5. Complete Phase 4: US2 View Tasks (T027-T031)
6. Complete Phase 5: US3 Complete Task (T032-T036)
7. **DEPLOY MVP**: Core CRUD via chat working

### Full Feature (Add P2 Stories)

8. Complete Phase 6: US4 Delete (T037-T040)
9. Complete Phase 7: US5 Update (T041-T044)
10. Complete Phase 8: US6 Persistence (T045-T050)
11. Complete Phase 9: Frontend (T051-T058)
12. Complete Phase 10: Polish (T059-T065)

---

## Summary

| Phase | Task Count | Focus |
|-------|-----------|-------|
| Setup | 4 | Dependencies & environment |
| Foundational | 18 | Models, schemas, MCP, router |
| US1 Create | 4 | add_task MCP tool |
| US2 View | 5 | list_tasks MCP tool |
| US3 Complete | 5 | complete_task MCP tool |
| US4 Delete | 4 | delete_task MCP tool |
| US5 Update | 4 | update_task MCP tool |
| US6 Persistence | 6 | Conversation history |
| Frontend | 8 | Chat UI components |
| Polish | 7 | Error handling, edge cases |
| **Total** | **65** | |

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [US#] label maps task to specific user story for traceability
- Task model already exists - reuse backend/app/models/task.py
- Auth already exists - reuse backend/app/dependencies/auth.py
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
