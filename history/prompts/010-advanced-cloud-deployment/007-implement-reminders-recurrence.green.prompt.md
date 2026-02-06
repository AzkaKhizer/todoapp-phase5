---
id: "007"
title: "Implement Task Reminders and Recurring Tasks"
stage: green
date: "2026-02-05"
surface: agent
model: claude-opus-4-5-20251101
feature: 010-advanced-cloud-deployment
branch: 010-advanced-cloud-deployment
user: HP
command: continue
labels: ["reminders", "recurrence", "kafka", "dapr", "event-driven"]
links:
  spec: specs/010-advanced-cloud-deployment/spec.md
  plan: specs/010-advanced-cloud-deployment/plan.md
  tasks: specs/010-advanced-cloud-deployment/tasks.md
files:
  - backend/app/services/reminder_service.py
  - backend/app/services/recurrence_service.py
  - backend/app/events/handlers.py
  - backend/app/routers/reminders.py
  - backend/app/schemas/recurrence.py
  - frontend/src/components/NotificationToast.tsx
  - frontend/src/components/RecurrenceEditor.tsx
  - frontend/src/hooks/useNotifications.ts
  - frontend/src/lib/types.ts
  - backend/tests/integration/test_reminders.py
  - backend/tests/integration/test_recurrence.py
  - backend/tests/unit/test_recurrence_service.py
  - backend/tests/contract/test_kafka_events.py
tests:
  - backend/tests/integration/test_reminders.py
  - backend/tests/integration/test_recurrence.py
  - backend/tests/unit/test_recurrence_service.py
  - backend/tests/contract/test_kafka_events.py
---

## Prompt

continue

## Response

Continued implementation of feature 010-advanced-cloud-deployment, completing Phase 5 (US2 - Task Reminders) and Phase 6 (US3 - Recurring Tasks).

### Phase 5: Task Reminders (T052-T065)

**Backend Implementation:**
- Created `ReminderService` in `backend/app/services/reminder_service.py`:
  - `schedule_reminder()` - Schedule reminders based on task due date and offset
  - `cancel_reminder()` - Cancel pending reminders when tasks are completed/deleted
  - `get_due_reminders()` - Query reminders ready for delivery
  - `process_due_reminders()` - Batch process due reminders
  - `mark_reminder_sent/failed()` - Update reminder status
  - Retry logic with exponential backoff (max 3 attempts)
  - Dead-letter queue for failed reminders

- Created event handlers in `backend/app/events/handlers.py`:
  - `/dapr/bindings/reminder-scheduler` - Cron binding endpoint (every minute)
  - `/dapr/subscribe/reminder-due` - Kafka consumer for reminder delivery
  - `/dapr/subscribe/task-events` - Task lifecycle event handler
  - Dapr subscription configuration endpoint

- Created reminder API router in `backend/app/routers/reminders.py`:
  - GET `/api/reminders` - List user's reminders with status filter
  - GET `/api/reminders/task/{id}` - Get reminders for a task
  - GET `/api/reminders/{id}` - Get specific reminder
  - PUT `/api/reminders/{id}` - Update reminder settings
  - DELETE `/api/reminders/{id}` - Cancel a reminder
  - POST `/api/reminders/task/{id}/cancel` - Cancel all task reminders

**Frontend Implementation:**
- Created `NotificationToast` component for displaying notifications
- Created `NotificationContainer` for managing multiple toasts
- Created `useNotifications` hook with:
  - `addNotification()`, `dismissNotification()`, `clearAll()`
  - Convenience methods: `showReminder()`, `showSuccess()`, `showError()`, `showInfo()`
- Created `useWebSocketNotifications` for real-time notification delivery
- Added `Notification` and `NotificationType` types to types.ts

**Tests:**
- Integration tests for reminder scheduling, cancellation, status updates
- Contract tests for ReminderDueEvent, TaskEvents, NotificationEvent schemas

### Phase 6: Recurring Tasks (T066-T076)

**Backend Implementation:**
- Created `RecurrenceService` in `backend/app/services/recurrence_service.py`:
  - `calculate_next_occurrence()` - Calculate next date based on pattern
  - `generate_next_task()` - Create new task instance on completion
  - Pattern calculations for daily, weekly, monthly, yearly, custom
  - Edge case handling:
    - Feb 30 -> Feb 28/29
    - Jan 31 -> Feb 28/29 (last day of month)
    - Feb 29 in non-leap years
  - `describe_pattern()` - Human-readable description

- Updated event handlers to generate next occurrence on task.completed

- Created `RecurrenceCreate` schema in `backend/app/schemas/recurrence.py`

**Frontend Implementation:**
- Created `RecurrenceEditor` component with:
  - Enable/disable toggle
  - Type selector (daily, weekly, monthly, yearly)
  - Interval input
  - Day-of-week selector for weekly
  - Day-of-month selector for monthly
  - End date picker
  - Live preview of pattern description
- Created `RecurrenceIndicator` component for task cards

**Tests:**
- Unit tests for all recurrence pattern calculations
- Unit tests for edge cases (Feb 30, leap years)
- Integration tests for task generation on completion
- Integration tests for end date handling

### Outcome

All 25 tasks completed (T052-T076). Both frontend and backend build successfully.

- Reminders are scheduled via Dapr cron binding and delivered via Kafka
- Recurring tasks automatically generate next occurrence on completion
- Comprehensive test coverage for all scenarios
