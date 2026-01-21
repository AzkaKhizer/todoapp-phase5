# Tasks: AI-Powered Todo Chatbot - Part 1

**Input**: Design documents from `/specs/004-todo-chatbot-tasks/`
**Prerequisites**: plan.md, spec.md, research.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US5)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/app/` for source, `backend/tests/` for tests

---

## Phase 1: Setup

**Purpose**: Install dependencies and configure environment

- [x] T001 Add `openai>=1.0.0` to backend/requirements.txt
- [x] T002 [P] Add OPENAI_API_KEY to backend/.env.example
- [ ] T003 [P] Add OPENAI_API_KEY to backend/.env (local development)

**Checkpoint**: Dependencies installed, environment configured

---

## Phase 2: Foundation (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Models (Required for all stories)

- [x] T004 [P] Create Conversation model in backend/app/models/conversation.py
- [x] T005 [P] Create Message model in backend/app/models/message.py
- [x] T006 Register models in backend/app/models/__init__.py
- [x] T007 Import models in backend/app/main.py for table creation

### Chat Schemas (Required for API)

- [x] T008 [P] Create ChatRequest schema in backend/app/schemas/chat.py
- [x] T009 [P] Create ChatResponse schema in backend/app/schemas/chat.py
- [x] T010 [P] Create ConversationResponse schema in backend/app/schemas/chat.py
- [x] T011 [P] Create MessageResponse schema in backend/app/schemas/chat.py

### MCP Tools Infrastructure (Required for all task operations)

- [x] T012 Create backend/app/mcp/__init__.py package
- [x] T013 [P] Create MCP tool definitions structure in backend/app/mcp/tools.py
- [x] T014 [P] Create OpenAI agent configuration in backend/app/services/agent.py

### Chat Service (Required for API)

- [x] T015 Create chat service with conversation CRUD in backend/app/services/chat.py
- [x] T016 [P] Add message storage functions to backend/app/services/chat.py

### API Router (Required for all stories)

- [x] T017 Create chat router with POST /api/chat endpoint in backend/app/routers/chat.py
- [x] T018 [P] Add GET /api/chat/conversations endpoint in backend/app/routers/chat.py
- [x] T019 [P] Add GET /api/chat/conversations/{id} endpoint in backend/app/routers/chat.py
- [x] T020 [P] Add DELETE /api/chat/conversations/{id} endpoint in backend/app/routers/chat.py
- [x] T021 Register chat router in backend/app/main.py

**Checkpoint**: Foundation ready - backend can receive chat messages and execute MCP tools

---

## Phase 3: User Story 1 - Create Task via Natural Language (Priority: P1) 🎯 MVP

**Goal**: Users can create tasks by sending natural language messages like "Add a task to buy groceries"

**Independent Test**: Send "Add a task to buy groceries" via POST /api/chat and verify task is created

**Spec Reference**: FR-001, FR-002, FR-011, FR-013, SC-001

### Implementation for User Story 1

- [x] T022 [US1] Implement add_task MCP tool definition in backend/app/mcp/tools.py
- [x] T023 [US1] Implement add_task tool executor in backend/app/mcp/tools.py
- [x] T024 [US1] Add task creation intent handling in agent system prompt in backend/app/services/agent.py
- [ ] T025 [US1] Test add_task via curl: POST /api/chat with {"message": "Add a task to buy groceries"}
- [ ] T026 [US1] Verify task appears in database with correct user_id

**Checkpoint**: User Story 1 complete - users can create tasks via natural language

---

## Phase 4: User Story 2 - View Tasks via Natural Language (Priority: P1)

**Goal**: Users can view their tasks by asking "Show me all my tasks"

**Independent Test**: Send "Show me all my tasks" and verify bot returns formatted task list with positions

**Spec Reference**: FR-003, FR-004, FR-005, FR-011, SC-002

### Implementation for User Story 2

- [x] T027 [US2] Implement list_tasks MCP tool definition in backend/app/mcp/tools.py
- [x] T028 [US2] Implement list_tasks tool executor in backend/app/mcp/tools.py
- [x] T029 [US2] Add position numbering (1, 2, 3) to list_tasks output for user-friendly display
- [x] T030 [US2] Add filter parameter support (all, pending, completed) to list_tasks
- [x] T031 [US2] Add task listing intent handling in agent system prompt in backend/app/services/agent.py
- [ ] T032 [US2] Test list_tasks via POST /api/chat with {"message": "Show me all my tasks"}
- [ ] T033 [US2] Verify empty list response: "You have no tasks yet. Would you like to add one?"

**Checkpoint**: User Story 2 complete - users can view tasks via natural language

---

## Phase 5: User Story 3 - Mark Task Complete via Natural Language (Priority: P1)

**Goal**: Users can mark tasks complete by saying "Mark task 1 as complete"

**Independent Test**: Create task, view tasks to get position, then mark complete and verify status change

**Spec Reference**: FR-006, FR-011, FR-012, SC-004

### Implementation for User Story 3

- [x] T034 [US3] Implement complete_task MCP tool definition in backend/app/mcp/tools.py
- [x] T035 [US3] Implement complete_task tool executor in backend/app/mcp/tools.py
- [x] T036 [US3] Handle task lookup by position number (not UUID)
- [x] T037 [US3] Add error handling for non-existent task: "Task #N not found. You have X tasks."
- [x] T038 [US3] Add error handling for already completed task: "'title' is already marked as complete."
- [x] T039 [US3] Add task completion intent handling in agent system prompt in backend/app/services/agent.py
- [ ] T040 [US3] Test complete_task via POST /api/chat with {"message": "Mark task 1 as complete"}

**Checkpoint**: User Story 3 complete - users can complete tasks via natural language

---

## Phase 6: User Story 4 - Delete Task via Natural Language (Priority: P2)

**Goal**: Users can delete tasks by saying "Delete task 2"

**Independent Test**: Create task, then delete via "Delete task 1" and verify removal

**Spec Reference**: FR-007, FR-011, FR-012, SC-004

### Implementation for User Story 4

- [x] T041 [US4] Implement delete_task MCP tool definition in backend/app/mcp/tools.py
- [x] T042 [US4] Implement delete_task tool executor in backend/app/mcp/tools.py
- [x] T043 [US4] Handle task lookup by position number
- [x] T044 [US4] Add error handling for non-existent task
- [x] T045 [US4] Add task deletion intent handling in agent system prompt in backend/app/services/agent.py
- [ ] T046 [US4] Test delete_task via POST /api/chat with {"message": "Delete task 1"}

**Checkpoint**: User Story 4 complete - users can delete tasks via natural language

---

## Phase 7: User Story 5 - Update Task via Natural Language (Priority: P2)

**Goal**: Users can update task details by saying "Change task 1 title to..."

**Independent Test**: Create task, update title, verify change persisted

**Spec Reference**: FR-008, FR-011, FR-012, SC-004

### Implementation for User Story 5

- [x] T047 [US5] Implement update_task MCP tool definition in backend/app/mcp/tools.py
- [x] T048 [US5] Implement update_task tool executor in backend/app/mcp/tools.py
- [x] T049 [US5] Handle title and description updates by position
- [x] T050 [US5] Add error handling for non-existent task
- [x] T051 [US5] Add error handling for no updates specified: "What would you like to change?"
- [x] T052 [US5] Add task update intent handling in agent system prompt in backend/app/services/agent.py
- [ ] T053 [US5] Test update_task via POST /api/chat with {"message": "Change task 1 title to Buy organic groceries"}

**Checkpoint**: User Story 5 complete - users can update tasks via natural language

---

## Phase 8: Integration & Polish

**Purpose**: Wire up all components and add cross-cutting concerns

### Integration

- [x] T054 Wire up chat router with agent service for full message flow
- [x] T055 Implement conversation persistence (save user and assistant messages)
- [x] T056 Implement conversation history loading for context (last 20 messages)

### Validation & Error Handling (FR-012, FR-014)

- [x] T057 [P] Create input validation module in backend/app/mcp/validation.py
- [x] T058 [P] Add title validation: not empty, max 200 chars
- [x] T059 [P] Add position validation: positive integer, within task count
- [x] T060 Add OpenAI API error handling with user-friendly messages
- [x] T061 Add timeout handling (30s max) for AI responses

### Final Testing

- [ ] T062 Test full workflow: create → view → complete → delete via curl
- [ ] T063 Test user isolation: verify user A cannot see user B's tasks
- [ ] T064 Test conversation persistence: send message, get conversation_id, send follow-up
- [ ] T065 Run quickstart.md validation end-to-end

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - can start immediately
- **Phase 2 (Foundation)**: Depends on Phase 1 - BLOCKS all user stories
- **Phases 3-7 (User Stories)**: All depend on Phase 2 completion
  - US1, US2, US3 are P1 priority - implement first
  - US4, US5 are P2 priority - implement after P1 stories
- **Phase 8 (Integration)**: Depends on at least US1-US3 being complete

### User Story Dependencies

- **US1 (Create)**: No dependencies on other stories - MVP entry point
- **US2 (View)**: No dependencies - can test with tasks from US1
- **US3 (Complete)**: Requires tasks to exist (US1) but can be implemented independently
- **US4 (Delete)**: Requires tasks to exist (US1) but independent implementation
- **US5 (Update)**: Requires tasks to exist (US1) but independent implementation

### Parallel Opportunities

Within Phase 2 (Foundation):
```
T004 [P] Conversation model  ||  T005 [P] Message model
T008-T011 Schemas can run in parallel
T013 [P] MCP tools  ||  T014 [P] Agent config
T017-T020 Router endpoints can run in parallel
```

Within Phase 8 (Integration):
```
T057 [P] validation.py  ||  T058 [P] title validation  ||  T059 [P] position validation
```

---

## Implementation Strategy

### MVP First (User Stories 1-3 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundation (T004-T021)
3. Complete Phase 3: US1 Create Task (T022-T026)
4. **VALIDATE**: Test "Add a task to buy groceries" works
5. Complete Phase 4: US2 View Tasks (T027-T033)
6. Complete Phase 5: US3 Complete Task (T034-T040)
7. **DEPLOY MVP**: Core CRUD via chat working

### Full Feature (Add P2 Stories)

8. Complete Phase 6: US4 Delete (T041-T046)
9. Complete Phase 7: US5 Update (T047-T053)
10. Complete Phase 8: Integration (T054-T065)

---

## Summary

| Phase | Task Count | Focus |
|-------|-----------|-------|
| Setup | 3 | Dependencies & environment |
| Foundation | 18 | Models, schemas, MCP, router |
| US1 Create | 5 | add_task MCP tool |
| US2 View | 7 | list_tasks MCP tool |
| US3 Complete | 7 | complete_task MCP tool |
| US4 Delete | 6 | delete_task MCP tool |
| US5 Update | 7 | update_task MCP tool |
| Integration | 12 | Wiring, validation, testing |
| **Total** | **65** | |

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [US#] label maps task to specific user story for traceability
- Task model already exists - reuse backend/app/models/task.py
- Task service already exists - reuse backend/app/services/task.py
- Auth already exists - reuse backend/app/dependencies/auth.py
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Frontend chat UI is OUT OF SCOPE for Part 1 (deferred to Part 2)
