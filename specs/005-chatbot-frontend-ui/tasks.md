# Tasks: AI-Powered Todo Chatbot - Part 2 (Frontend Chat UI)

**Input**: Design documents from `/specs/005-chatbot-frontend-ui/`
**Prerequisites**: plan.md, spec.md, contracts/chat-api.ts

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US5)
- Include exact file paths in descriptions

## Path Conventions

- **Frontend**: `frontend/src/` for source code

---

## Phase 1: Setup

**Purpose**: Add TypeScript types and create component directory structure

- [ ] T001 Add chat TypeScript types to frontend/src/lib/types.ts
- [ ] T002 [P] Create chat components directory at frontend/src/components/chat/
- [ ] T003 [P] Add chat link to Header navigation in frontend/src/components/layout/Header.tsx

**Checkpoint**: Types defined, directory ready, navigation updated

---

## Phase 2: Foundation (Blocking Prerequisites)

**Purpose**: Core hook and page that MUST be complete before any user story components

**CRITICAL**: No user story component work can begin until this phase is complete

### Core Hook (Required for all stories)

- [ ] T004 Create useChat hook with state management in frontend/src/hooks/useChat.ts
- [ ] T005 Implement sendMessage() function in useChat hook
- [ ] T006 Implement loading and error state handling in useChat hook

### Chat Page (Required for all stories)

- [ ] T007 Create protected chat page at frontend/src/app/chat/page.tsx
- [ ] T008 Add authentication redirect for unauthenticated users in chat page

**Checkpoint**: Foundation ready - useChat hook works, chat page renders

---

## Phase 3: User Story 1 - Send and Receive Messages (Priority: P1)

**Goal**: Users can send messages and receive AI responses

**Independent Test**: User types "Show my tasks", presses Enter, sees AI response with task list

**Spec Reference**: FR-001, FR-002, FR-003, FR-004, FR-007, FR-008, FR-013

### Implementation for User Story 1

- [ ] T009 [US1] Create ChatWindow component container in frontend/src/components/chat/ChatWindow.tsx
- [ ] T010 [US1] Create MessageBubble component with user/assistant styles in frontend/src/components/chat/MessageBubble.tsx
- [ ] T011 [US1] Create MessageList component with auto-scroll in frontend/src/components/chat/MessageList.tsx
- [ ] T012 [US1] Create ChatInput component with text area in frontend/src/components/chat/ChatInput.tsx
- [ ] T013 [US1] Implement Enter to send, Shift+Enter for newline in ChatInput
- [ ] T014 [US1] Add character limit validation (2000 chars) to ChatInput
- [ ] T015 [US1] Add empty message validation to ChatInput
- [ ] T016 [US1] Implement loading indicator in ChatWindow
- [ ] T017 [US1] Wire up ChatWindow with useChat hook in chat page
- [ ] T018 [US1] Test send message flow: type message, press Enter, see response

**Checkpoint**: User Story 1 complete - users can send messages and receive AI responses

---

## Phase 4: User Story 2 - View Chat History Within Conversation (Priority: P1)

**Goal**: Users can see all messages in current conversation with proper styling

**Independent Test**: After sending 3 messages, all messages visible in chronological order

**Spec Reference**: FR-003, FR-008

### Implementation for User Story 2

- [ ] T019 [US2] Add timestamp display to MessageBubble component
- [ ] T020 [US2] Implement smart auto-scroll (only when at bottom) in MessageList
- [ ] T021 [US2] Add "new message" indicator when scrolled up in MessageList
- [ ] T022 [US2] Style user messages (right-aligned, primary color) in MessageBubble
- [ ] T023 [US2] Style assistant messages (left-aligned, secondary color) in MessageBubble
- [ ] T024 [US2] Test chat history: send multiple messages, verify all visible in order

**Checkpoint**: User Story 2 complete - users see full conversation history

---

## Phase 5: User Story 3 - Visual Feedback for Task Operations (Priority: P2)

**Goal**: Users see clear confirmation when tasks are added, completed, or deleted

**Independent Test**: Send "Add task: Test", see clear success message from AI

**Spec Reference**: FR-003, FR-006

### Implementation for User Story 3

- [ ] T025 [US3] Add success styling for confirmation messages in MessageBubble
- [ ] T026 [US3] Add error styling for failed operations in MessageBubble
- [ ] T027 [US3] Implement error display with retry button in ChatWindow
- [ ] T028 [US3] Add error message mapping for API errors in useChat hook
- [ ] T029 [US3] Test error handling: disconnect network, verify error displays with retry

**Checkpoint**: User Story 3 complete - users see visual feedback for all operations

---

## Phase 6: User Story 4 - Start New Conversation (Priority: P2)

**Goal**: Users can start a fresh conversation

**Independent Test**: Click "New Chat", verify chat clears, new conversation begins

**Spec Reference**: FR-009

### Implementation for User Story 4

- [ ] T030 [US4] Create NewChatButton component in frontend/src/components/chat/NewChatButton.tsx
- [ ] T031 [US4] Implement startNewChat() function in useChat hook
- [ ] T032 [US4] Add NewChatButton to ChatWindow header area
- [ ] T033 [US4] Test new conversation: send messages, click New Chat, verify chat clears

**Checkpoint**: User Story 4 complete - users can start new conversations

---

## Phase 7: User Story 5 - Access Previous Conversations (Priority: P3)

**Goal**: Users can view and continue previous conversations

**Independent Test**: See list of past conversations, click one, see full message history

**Spec Reference**: FR-010, FR-011

### Implementation for User Story 5

- [ ] T034 [US5] Create useConversations hook in frontend/src/hooks/useConversations.ts
- [ ] T035 [US5] Implement fetchConversations() in useConversations hook
- [ ] T036 [US5] Create ConversationList component in frontend/src/components/chat/ConversationList.tsx
- [ ] T037 [US5] Create ConversationSidebar component in frontend/src/components/chat/ConversationSidebar.tsx
- [ ] T038 [US5] Create ChatLayout component with sidebar in frontend/src/components/chat/ChatLayout.tsx
- [ ] T039 [US5] Implement loadConversation() function in useChat hook
- [ ] T040 [US5] Add active conversation highlighting in ConversationList
- [ ] T041 [US5] Implement responsive sidebar (collapsible on mobile) in ChatLayout
- [ ] T042 [US5] Update chat page to use ChatLayout in frontend/src/app/chat/page.tsx
- [ ] T043 [US5] Test conversation history: create conversations, click to load, verify messages

**Checkpoint**: User Story 5 complete - users can access previous conversations

---

## Phase 8: Polish & Integration

**Purpose**: Final touches and cross-cutting concerns

### Responsive Design

- [ ] T044 [P] Add mobile-responsive styles to ChatWindow
- [ ] T045 [P] Add mobile-responsive styles to ChatInput
- [ ] T046 [P] Add hamburger menu for sidebar toggle on mobile

### Edge Cases

- [ ] T047 Handle network disconnection gracefully in useChat hook
- [ ] T048 Handle 401 unauthorized with redirect to login
- [ ] T049 Handle empty conversation state (first time user)

### Final Validation

- [ ] T050 Test full workflow: create task, list tasks, complete task via chat
- [ ] T051 Test user isolation: verify user only sees their conversations
- [ ] T052 Test responsive design on mobile viewport

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - can start immediately
- **Phase 2 (Foundation)**: Depends on Phase 1 - BLOCKS all user stories
- **Phases 3-7 (User Stories)**: All depend on Phase 2 completion
  - US1, US2 are P1 priority - implement first
  - US3, US4 are P2 priority - implement after P1 stories
  - US5 is P3 priority - implement last
- **Phase 8 (Polish)**: Depends on at least US1-US4 being complete

### User Story Dependencies

- **US1 (Send/Receive)**: No dependencies - MVP entry point
- **US2 (View History)**: Builds on US1 components but independent implementation
- **US3 (Visual Feedback)**: Extends US1 but independent implementation
- **US4 (New Chat)**: Independent - adds button to existing UI
- **US5 (Conversation History)**: Most complex - requires sidebar components

### Parallel Opportunities

Within Phase 1 (Setup):
```
T002 [P] Create directory  ||  T003 [P] Update Header
```

Within Phase 8 (Polish):
```
T044 [P] ChatWindow responsive  ||  T045 [P] ChatInput responsive  ||  T046 [P] Sidebar toggle
```

---

## Implementation Strategy

### MVP First (User Stories 1-2 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundation (T004-T008)
3. Complete Phase 3: US1 Send/Receive (T009-T018)
4. **VALIDATE**: Test "Show my tasks" works end-to-end
5. Complete Phase 4: US2 View History (T019-T024)
6. **DEPLOY MVP**: Core chat functionality working

### Full Feature (Add P2-P3 Stories)

7. Complete Phase 5: US3 Visual Feedback (T025-T029)
8. Complete Phase 6: US4 New Chat (T030-T033)
9. Complete Phase 7: US5 Conversation History (T034-T043)
10. Complete Phase 8: Polish (T044-T052)

---

## Summary

| Phase | Task Count | Focus |
|-------|-----------|-------|
| Setup | 3 | Types, directory, navigation |
| Foundation | 5 | useChat hook, chat page |
| US1 Send/Receive | 10 | Core chat components |
| US2 View History | 6 | Message display, scrolling |
| US3 Visual Feedback | 5 | Error handling, confirmations |
| US4 New Chat | 4 | New conversation button |
| US5 Conversation History | 10 | Sidebar, conversation list |
| Polish | 9 | Responsive, edge cases, testing |
| **Total** | **52** | |

---

## Notes

- Backend is COMPLETE - no backend tasks needed
- All components use existing Tailwind CSS
- No new npm dependencies required
- [P] tasks = different files, no dependencies on incomplete tasks
- [US#] label maps task to specific user story for traceability
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
