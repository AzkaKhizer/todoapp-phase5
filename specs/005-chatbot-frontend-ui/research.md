# Research: AI-Powered Todo Chatbot - Part 2 (Frontend Chat UI)

**Feature**: Frontend Chat UI
**Date**: 2026-01-20

---

## Research Summary

This feature has minimal unknowns since it builds on existing infrastructure. All technical decisions leverage the established stack.

---

## Decision 1: Chat State Management

**Decision**: Use custom React hook (`useChat`) with `useState`

**Rationale**:
- Simple state needs (messages array, conversationId, loading, error)
- No complex state sharing across distant components
- Existing `useTasks` hook follows this pattern
- Avoids adding state management library overhead

**Alternatives Considered**:
- Redux/Zustand: Overkill for single-page chat state
- React Context: Adds unnecessary complexity
- TanStack Query: Good for caching but chat is session-based

---

## Decision 2: Message Display Pattern

**Decision**: Chronological list with distinct bubble styles for user/assistant

**Rationale**:
- Industry standard for chat interfaces
- Clear visual distinction improves readability
- User messages right-aligned, assistant left-aligned
- Follows existing UI patterns (Tailwind classes)

**Alternatives Considered**:
- Unified bubble style: Less clear who sent what
- Thread-based display: Unnecessary complexity for linear chat

---

## Decision 3: Auto-scroll Behavior

**Decision**: Auto-scroll only when user is at bottom; show "new message" indicator otherwise

**Rationale**:
- Respects user's scroll position when reading history
- Industry standard UX pattern
- Prevents jarring scroll interruption

**Alternatives Considered**:
- Always auto-scroll: Disrupts reading history
- Never auto-scroll: User misses new messages

---

## Decision 4: Conversation Sidebar (P3)

**Decision**: Left sidebar with conversation list, collapsible on mobile

**Rationale**:
- Standard chat app layout (WhatsApp, Slack, ChatGPT)
- Responsive design with hamburger menu on mobile
- Existing Header component can integrate toggle

**Alternatives Considered**:
- Dropdown menu: Less discoverable
- Separate page: Disrupts conversation flow

---

## Decision 5: Keyboard Shortcuts

**Decision**: Enter to send, Shift+Enter for newline

**Rationale**:
- Most common chat convention
- Matches user expectations from other apps
- Easy to implement with onKeyDown handler

**Alternatives Considered**:
- Ctrl+Enter to send: Less intuitive for chat
- Only button click: Slower user interaction

---

## Decision 6: Optimistic UI Updates

**Decision**: Show user message immediately, then wait for AI response

**Rationale**:
- Instant feedback improves perceived performance
- User sees their message while waiting for AI
- On error, message can be marked as failed with retry

**Alternatives Considered**:
- Wait for response before showing message: Feels slow
- Show both optimistically: Can't predict AI response

---

## Technical Constraints

1. **Backend API is fixed**: Must conform to existing `/api/chat` contract
2. **Auth is session-based**: JWT token obtained via `/api/auth/token`
3. **Message limit**: 2000 characters (enforced by backend)
4. **Response format**: AI always returns text (no structured data)

---

## No Unknowns Remaining

All technical decisions are resolved. Implementation can proceed with the plan.
