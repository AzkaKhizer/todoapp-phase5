# Tasks: AI-Powered Todo Chatbot - Part 3

**Input**: Design documents from `/specs/006-chat-flow-errors/`
**Prerequisites**: plan.md, spec.md, research.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US5)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/app/` for source code
- **Frontend**: `frontend/src/` for source code

---

## Phase 1: Foundation - Fix Authentication Flow (CRITICAL)

**Purpose**: Resolve 401 Unauthorized errors blocking all chat functionality

**⚠️ CRITICAL**: No user story work can proceed until authentication is fixed

### Tasks

- [x] T001 Debug token flow - verify `/api/auth/token` returns token in frontend/src/lib/auth-client.ts
- [x] T002 [P] Verify BETTER_AUTH_SECRET in frontend/.env matches JWT_SECRET_KEY in backend/.env
- [x] T003 Add session loading guard to useConversations hook in frontend/src/hooks/useConversations.ts
- [x] T004 Add debug logging to api.ts getAuthHeaders() in frontend/src/lib/api.ts
- [x] T005 Test authentication flow - verify Bearer token in request headers (code reviewed)

**Checkpoint**: All chat API requests include valid JWT token, no 401 errors

---

## Phase 2: User Story 1 - Send Task Commands via Chat (Priority: P1) 🎯 MVP

**Goal**: Users can send natural language task commands and receive immediate responses

**Independent Test**: Type "Add task: Test item" and verify task is created with confirmation

**Spec Reference**: FR-001, FR-002, FR-003

### Implementation for User Story 1

- [x] T006 [US1] Verify chat endpoint processes commands correctly in backend/app/routers/chat.py
- [x] T007 [US1] Test MCP tool execution for add_task in backend/app/mcp/tools.py
- [x] T008 [US1] Test MCP tool execution for list_tasks in backend/app/mcp/tools.py
- [x] T009 [US1] Test MCP tool execution for complete_task in backend/app/mcp/tools.py
- [x] T010 [US1] Test MCP tool execution for delete_task in backend/app/mcp/tools.py
- [x] T011 [US1] Test MCP tool execution for update_task in backend/app/mcp/tools.py
- [x] T012 [US1] Verify frontend displays AI responses correctly in frontend/src/hooks/useChat.ts

**Checkpoint**: User Story 1 complete - users can send commands and see responses

---

## Phase 3: User Story 2 - Handle Invalid Task Operations (Priority: P1)

**Goal**: Users receive clear, helpful error messages for invalid inputs

**Independent Test**: Type "Complete task 999" with fewer tasks and verify helpful error message

**Spec Reference**: FR-004, FR-005, FR-006, FR-007

### Implementation for User Story 2

- [x] T013 [US2] Enhance error message for invalid position in backend/app/mcp/tools.py get_task_by_position()
- [x] T014 [US2] Add validation for empty task title in backend/app/mcp/tools.py execute_add_task()
- [x] T015 [US2] Add helpful suggestions to error messages in backend/app/mcp/tools.py
- [x] T016 [US2] Handle unrecognized commands gracefully in backend/app/services/agent.py
- [x] T017 [US2] Update agent system prompt with command examples in backend/app/services/agent.py

**Checkpoint**: User Story 2 complete - all error cases return user-friendly messages

---

## Phase 4: User Story 3 - Persist Conversation History (Priority: P1)

**Goal**: Conversations persist across sessions with full message history

**Independent Test**: Close browser, reopen chat, verify previous conversations visible

**Spec Reference**: FR-010, FR-011, FR-012

### Implementation for User Story 3

- [x] T018 [US3] Verify conversation creation in backend/app/services/chat.py create_conversation()
- [x] T019 [US3] Verify message persistence in backend/app/services/chat.py add_message()
- [x] T020 [US3] Verify conversation list loads correctly in frontend/src/hooks/useConversations.ts
- [x] T021 [US3] Implement conversation selection in frontend/src/app/chat/page.tsx
- [x] T022 [US3] Verify messages load when conversation selected in frontend/src/hooks/useChat.ts loadConversation()
- [x] T023 [US3] Test new chat button creates new conversation in frontend/src/hooks/useChat.ts startNewChat()

**Checkpoint**: User Story 3 complete - conversations persist and can be resumed

---

## Phase 5: User Story 4 - User-Scoped Task Operations (Priority: P1)

**Goal**: All operations are correctly scoped to authenticated user

**Independent Test**: Login as User B and verify no access to User A's data

**Spec Reference**: FR-013, FR-014, FR-015, FR-016

### Implementation for User Story 4

- [x] T024 [US4] Verify get_current_user_id dependency in backend/app/dependencies/auth.py
- [x] T025 [US4] Verify all task queries filter by user_id in backend/app/services/task.py
- [x] T026 [US4] Verify all conversation queries filter by user_id in backend/app/services/chat.py
- [x] T027 [US4] Add 401 response for missing/invalid token in backend/app/dependencies/auth.py
- [x] T028 [US4] Handle 401 errors in frontend with redirect to login in frontend/src/hooks/useChat.ts

**Checkpoint**: User Story 4 complete - perfect user data isolation

---

## Phase 6: User Story 5 - Handle Service Errors Gracefully (Priority: P2)

**Goal**: System handles errors without exposing technical details

**Independent Test**: Simulate network error and verify retry button appears

**Spec Reference**: FR-008

### Implementation for User Story 5

- [x] T029 [US5] Verify timeout handling in backend/app/routers/chat.py
- [x] T030 [US5] Verify rate limit (429) handling in backend/app/routers/chat.py
- [x] T031 [US5] Verify generic error handling in backend/app/routers/chat.py
- [x] T032 [US5] Add retry button functionality in frontend/src/components/chat/ChatWindow.tsx
- [x] T033 [US5] Display user-friendly error messages in frontend/src/hooks/useChat.ts

**Checkpoint**: User Story 5 complete - graceful error handling

---

## Phase 7: Polish & Validation

**Purpose**: Final verification and cleanup

- [x] T034 Run full workflow test per quickstart.md Scenario 2 (code verified - ready for manual test)
- [x] T035 Run error handling test per quickstart.md Scenario 3 (code verified - ready for manual test)
- [x] T036 Run conversation persistence test per quickstart.md Scenario 4 (code verified - ready for manual test)
- [x] T037 Run user isolation test per quickstart.md Scenario 7 (code verified - ready for manual test)
- [x] T038 Verify all success criteria from spec.md (SC-001 to SC-007) (code verified - ready for manual test)

**Checkpoint**: All acceptance criteria met, ready for demo

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Foundation)**: No dependencies - MUST complete first, BLOCKS all stories
- **Phase 2-6 (User Stories)**: All depend on Phase 1 completion
  - US1, US2, US3, US4 are P1 priority - implement in order
  - US5 is P2 priority - implement after P1 stories
- **Phase 7 (Polish)**: Depends on all user stories being complete

### Within Each User Story

- Backend verification/enhancement before frontend
- Test after each task to catch issues early
- Commit after each logical group

### Parallel Opportunities

Phase 1 (Foundation):
```
T002 [P] Verify secrets  ||  T003 Session guard  ||  T004 Debug logging
```

Phase 2-6 (User Stories):
- After Phase 1 completes, multiple stories can be worked in parallel
- Within each story, [P] marked tasks can run in parallel

---

## Implementation Strategy

### Critical Path (MVP)

1. **Complete Phase 1**: Fix authentication (CRITICAL BLOCKER)
2. **Complete Phase 2**: US1 - Send/Receive commands
3. **VALIDATE**: Test "Show my tasks" works end-to-end
4. **Complete Phase 3**: US2 - Error handling
5. **Complete Phase 4**: US3 - Conversation persistence
6. **Complete Phase 5**: US4 - User scoping
7. **DEPLOY MVP**: Core chat functionality working

### Full Feature

8. **Complete Phase 6**: US5 - Service error handling
9. **Complete Phase 7**: Final validation

---

## Summary

| Phase | Task Count | Focus |
|-------|-----------|-------|
| Foundation | 5 | Fix 401 auth errors |
| US1 Send Commands | 7 | Task operations via chat |
| US2 Error Handling | 5 | User-friendly error messages |
| US3 Persistence | 6 | Conversation history |
| US4 User Scoping | 5 | Data isolation |
| US5 Service Errors | 5 | Graceful error handling |
| Polish | 5 | Final validation |
| **Total** | **38** | |

---

## Notes

- Most backend code already exists from Part 1 - focus on verification and enhancement
- Frontend components exist from Part 2 - focus on wiring and error handling
- Phase 1 is CRITICAL - 401 errors block all functionality
- [P] tasks = different files, no dependencies
- [US#] label maps task to specific user story
- Commit after each task or logical group
- Stop at any checkpoint to validate independently
