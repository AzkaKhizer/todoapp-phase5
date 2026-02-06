# Tasks: Advanced Cloud Deployment with Dapr, Kafka & Event-Driven Architecture

**Input**: Design documents from `/specs/010-advanced-cloud-deployment/`
**Prerequisites**: plan.md (required), spec.md (required), data-model.md, contracts/, research.md

**Tests**: Integration tests included for Kafka events and Dapr components.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/app/`
- **Frontend**: `frontend/src/`
- **Infrastructure**: `infrastructure/`
- **Tests**: `backend/tests/`, `frontend/__tests__/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, new dependencies, and directory structure.

- [x] T001 Create infrastructure directory structure: `infrastructure/dapr/components/`, `infrastructure/kafka/`, `infrastructure/helm/`, `infrastructure/terraform/`
- [x] T002 [P] Add Python dependencies to backend/pyproject.toml: `dapr>=1.12.0`, `dapr-ext-fastapi>=1.12.0`, `aiokafka>=0.9.0`, `redis>=5.0.0`, `structlog>=24.1.0`
- [x] T003 [P] Add Node dependencies to frontend/package.json: `reconnecting-websocket`, `@dapr/dapr`
- [x] T004 [P] Create backend event schemas module: `backend/app/events/__init__.py`, `backend/app/events/schemas.py`, `backend/app/events/topics.py`
- [x] T005 [P] Create backend Dapr module: `backend/app/dapr/__init__.py`

---

## Phase 2: Foundational (Database Migrations)

**Purpose**: Database schema changes that MUST be complete before ANY user story implementation.

**⚠️ CRITICAL**: All migrations must complete before user story work begins.

- [x] T006 Create database migration 001: Add Task extended fields (due_date, priority, reminder_offset, recurrence_id, parent_task_id) in `backend/app/models/task.py`
- [x] T007 Create Tag model in `backend/app/models/tag.py` with fields: id, name, color, user_id, created_at
- [x] T008 Create TaskTag junction table model in `backend/app/models/task_tag.py`
- [x] T009 Create RecurrencePattern model in `backend/app/models/recurrence.py` with fields: id, type, interval, days_of_week, day_of_month, end_date, user_id
- [x] T010 Create Reminder model in `backend/app/models/reminder.py` with fields: id, task_id, user_id, scheduled_time, status, delivery_channel, retry_count
- [x] T011 Create ActivityLogEntry model in `backend/app/models/activity_log.py` with fields: id, user_id, event_type, entity_type, entity_id, timestamp, details
- [x] T012 Update `backend/app/models/__init__.py` to export all new models
- [x] T013 Run database migrations to apply schema changes

**Checkpoint**: Database schema ready - user story implementation can now begin.

---

## Phase 3: User Story 1 - Enhanced Task Management (Priority: P1) 🎯 MVP

**Goal**: Extend Task model and API with due dates, priorities, tags, and search/filter/sort capabilities.

**Independent Test**: Create tasks with due dates/priorities/tags and verify search/filter/sort operations.

**References**: FR-001 to FR-007, SC-001, SC-002

### Backend Implementation for US1

- [x] T014 [P] [US1] Create TaskPriority enum in `backend/app/models/task.py`
- [x] T015 [P] [US1] Update Task model with due_date, priority fields in `backend/app/models/task.py`
- [x] T016 [US1] Create TagService in `backend/app/services/tag_service.py` with CRUD operations
- [x] T017 [US1] Update TaskService in `backend/app/services/task_service.py` with search/filter/sort logic
- [x] T018 [US1] Create TaskFilterParams schema in `backend/app/schemas/task.py` for query parameters
- [x] T019 [US1] Update TaskCreate/TaskUpdate schemas in `backend/app/schemas/task.py` with new fields
- [x] T020 [US1] Extend GET /api/tasks endpoint in `backend/app/routers/tasks.py` with filter/sort params
- [x] T021 [US1] Create tag router in `backend/app/routers/tags.py` with GET, POST, DELETE endpoints
- [x] T022 [US1] Register tag router in `backend/app/main.py`

### Frontend Implementation for US1

- [x] T023 [P] [US1] Create DatePicker component in `frontend/src/components/ui/DatePicker.tsx`
- [x] T024 [P] [US1] Create PrioritySelect component in `frontend/src/components/ui/PrioritySelect.tsx`
- [x] T025 [P] [US1] Create TagInput component in `frontend/src/components/ui/TagInput.tsx`
- [x] T026 [US1] Create TaskFilters component in `frontend/src/components/tasks/TaskFilters.tsx`
- [x] T027 [US1] Create useTaskFilters hook in `frontend/src/hooks/useTaskFilters.ts`
- [x] T028 [US1] Update TaskForm component in `frontend/src/components/forms/TaskForm.tsx` with new fields
- [x] T029 [US1] Update TaskCard/TaskItem to display priority badges and tags in `frontend/src/components/tasks/`
- [x] T030 [US1] Add overdue task visual highlighting (red border/background) in TaskCard
- [x] T031 [US1] Update API client for new task fields and filter params in `frontend/src/lib/api.ts`

### Tests for US1

- [x] T032 [P] [US1] Write unit tests for TaskService filter/sort in `backend/tests/unit/test_task_service.py`
- [x] T033 [P] [US1] Write API tests for tag endpoints in `backend/tests/api/test_tags.py`

**Checkpoint**: US1 complete. Tasks have due dates, priorities, tags with search/filter/sort. FR-001 to FR-007 satisfied.

---

## Phase 4: User Story 4 - Local Minikube with Dapr (Priority: P2)

**Goal**: Deploy Dapr and Kafka on Minikube as infrastructure foundation for event-driven features.

**Independent Test**: Deploy to Minikube, verify all Dapr building blocks function correctly.

**References**: FR-016 to FR-020, FR-026 to FR-028, SC-009, SC-011

### Infrastructure Setup for US4

- [x] T034 [US4] Create Dapr Kafka pub/sub component in `infrastructure/dapr/components/pubsub-kafka.yaml`
- [x] T035 [P] [US4] Create Dapr Redis state store component in `infrastructure/dapr/components/statestore-redis.yaml`
- [x] T036 [P] [US4] Create Dapr cron binding component in `infrastructure/dapr/components/binding-cron.yaml`
- [x] T037 [P] [US4] Create Dapr secrets component in `infrastructure/dapr/components/secrets-k8s.yaml`
- [x] T038 [US4] Create Dapr configuration in `infrastructure/dapr/config.yaml`
- [x] T039 [US4] Create Kafka topic definitions in `infrastructure/kafka/topics.yaml`
- [x] T040 [US4] Create local setup script in `scripts/local-setup.sh` (Minikube + Dapr + Kafka + Redis)

### Helm Chart Updates for US4

- [x] T041 [US4] Create todo-backend-v2 Helm chart in `infrastructure/helm/todo-backend-v2/` with Dapr annotations
- [x] T042 [P] [US4] Create todo-frontend-v2 Helm chart in `infrastructure/helm/todo-frontend-v2/`
- [x] T043 [US4] Create Kafka Helm values in `infrastructure/helm/kafka/values.yaml`
- [x] T044 [P] [US4] Create Redis Helm values in `infrastructure/helm/redis/values.yaml`

### Dapr SDK Integration for US4

- [x] T045 [US4] Implement Dapr pub/sub helper in `backend/app/dapr/pubsub.py`
- [x] T046 [P] [US4] Implement Dapr state store helper in `backend/app/dapr/state.py`
- [x] T047 [P] [US4] Implement Dapr secrets helper in `backend/app/dapr/secrets.py`
- [x] T048 [US4] Implement Dapr bindings helper in `backend/app/dapr/bindings.py`
- [x] T049 [US4] Update backend Dockerfile for Dapr sidecar compatibility in `backend/Dockerfile`

### Validation for US4

- [x] T050 [US4] Write integration test for Dapr pub/sub in `backend/tests/integration/test_dapr_pubsub.py`
- [x] T051 [US4] Create deployment validation script in `scripts/validate-deployment.sh`

**Checkpoint**: US4 complete. Dapr + Kafka running on Minikube. SC-009, SC-011 satisfied.

---

## Phase 5: User Story 2 - Task Reminders (Priority: P1)

**Goal**: Implement reminder system using Kafka events triggered by Dapr cron binding.

**Independent Test**: Create task with reminder, verify notification delivered within 60 seconds of scheduled time.

**References**: FR-008 to FR-011, SC-003

**Dependencies**: Requires US1 (due dates) and US4 (Dapr/Kafka) to be complete.

### Backend Implementation for US2

- [x] T052 [US2] Create ReminderService in `backend/app/services/reminder_service.py` with schedule/cancel logic
- [x] T053 [US2] Create reminder event schemas in `backend/app/events/schemas.py` (ReminderDueEvent)
- [x] T054 [US2] Create reminder scheduler handler in `backend/app/events/handlers.py` (cron binding endpoint)
- [x] T055 [US2] Create reminder consumer handler in `backend/app/events/handlers.py` (Kafka subscriber)
- [x] T056 [US2] Create reminder router in `backend/app/routers/reminders.py` with GET, PUT, DELETE endpoints
- [x] T057 [US2] Register reminder router in `backend/app/main.py`
- [x] T058 [US2] Implement reminder cancellation on task completion in TaskService
- [x] T059 [US2] Implement retry logic with dead-letter queue for failed reminders

### Frontend Implementation for US2

- [x] T060 [P] [US2] Create NotificationToast component in `frontend/src/components/NotificationToast.tsx`
- [x] T061 [US2] Create useNotifications hook in `frontend/src/hooks/useNotifications.ts`
- [x] T062 [US2] Add reminder offset input to TaskForm in `frontend/src/components/TaskForm.tsx`
- [x] T063 [US2] Display scheduled reminder on task details

### Tests for US2

- [x] T064 [US2] Write integration test for reminder flow in `backend/tests/integration/test_reminders.py`
- [x] T065 [P] [US2] Write contract test for ReminderDueEvent schema in `backend/tests/contract/test_kafka_events.py`

**Checkpoint**: US2 complete. Reminders delivered via Kafka events. FR-008 to FR-011, SC-003 satisfied.

---

## Phase 6: User Story 3 - Recurring Tasks (Priority: P2)

**Goal**: Implement automatic task generation when recurring tasks are completed.

**Independent Test**: Complete a recurring task, verify next occurrence created within 5 seconds.

**References**: FR-012 to FR-014, SC-004

**Dependencies**: Requires US1 (task model) and US4 (Kafka) to be complete.

### Backend Implementation for US3

- [x] T066 [US3] Create RecurrenceService in `backend/app/services/recurrence_service.py` with next-date calculation
- [x] T067 [US3] Implement recurrence patterns (daily, weekly, monthly, yearly, custom) in RecurrenceService
- [x] T068 [US3] Create recurrence consumer handler in `backend/app/events/handlers.py` (subscribes to task.completed)
- [x] T069 [US3] Create RecurrenceCreate schema in `backend/app/schemas/recurrence.py`
- [x] T070 [US3] Add recurrence endpoints to task router in `backend/app/routers/tasks.py` (via task service)
- [x] T071 [US3] Handle edge cases (Feb 30th, last day of month) in RecurrenceService

### Frontend Implementation for US3

- [x] T072 [US3] Create RecurrenceEditor component in `frontend/src/components/RecurrenceEditor.tsx`
- [x] T073 [US3] Add recurrence pattern selector to TaskForm (RecurrenceEditor created, integration via TaskForm)
- [x] T074 [US3] Display recurrence indicator on task cards (already in TaskCard.tsx)

### Tests for US3

- [x] T075 [US3] Write unit tests for recurrence calculation in `backend/tests/unit/test_recurrence_service.py`
- [x] T076 [US3] Write integration test for recurring task flow in `backend/tests/integration/test_recurrence.py`

**Checkpoint**: US3 complete. Recurring tasks auto-generate on completion. FR-012 to FR-014, SC-004 satisfied.

---

## Phase 7: User Story 5 - Real-Time Sync (Priority: P2)

**Goal**: Implement WebSocket-based real-time sync via Kafka events.

**Independent Test**: Open app in two tabs, create task in one, verify appears in other within 2 seconds.

**References**: FR-021 to FR-023, SC-005

**Dependencies**: Requires US4 (Kafka infrastructure) to be complete.

### Backend Implementation for US5

- [x] T077 [US5] Create task event schemas in `backend/app/events/schemas.py` (TaskCreated, TaskUpdated, etc.)
- [x] T078 [US5] Create sync event producer in `backend/app/services/kafka_producer.py`
- [x] T079 [US5] Publish task events on create/update/delete in TaskService (via KafkaProducer)
- [x] T080 [US5] Create WebSocket router in `backend/app/routers/websocket.py` with JWT authentication
- [x] T081 [US5] Implement connection manager for WebSocket broadcast in `backend/app/services/websocket_manager.py`
- [x] T082 [US5] Create sync consumer to forward Kafka events to WebSocket in `backend/app/events/handlers.py`
- [x] T083 [US5] Register WebSocket router in `backend/app/main.py`

### Frontend Implementation for US5

- [x] T084 [US5] Create WebSocket client in `frontend/src/lib/websocket.ts`
- [x] T085 [US5] Create useWebSocket hook in `frontend/src/hooks/useWebSocket.ts`
- [x] T086 [US5] Integrate WebSocket events into task state management (useTasks with real-time sync)
- [x] T087 [US5] Implement reconnection logic with missed event sync (WebSocketClient with exponential backoff)

### Tests for US5

- [x] T088 [US5] Write integration test for WebSocket sync in `backend/tests/integration/test_websocket.py`
- [x] T089 [P] [US5] Write contract tests for task event schemas in `backend/tests/contract/test_kafka_events.py` (already done in Phase 5)

**Checkpoint**: US5 complete. Real-time sync working via WebSocket + Kafka. FR-021 to FR-023, SC-005 satisfied.

---

## Phase 8: User Story 6 - Activity Log (Priority: P3)

**Goal**: Persist all task events to activity log for audit and productivity tracking.

**Independent Test**: Perform task operations, verify activity log shows accurate entries.

**References**: FR-024, FR-025

**Dependencies**: Requires US4 (Kafka) and US5 (task events) to be complete.

### Backend Implementation for US6

- [x] T090 [US6] Create ActivityService in `backend/app/services/activity_service.py`
- [x] T091 [US6] Create activity consumer handler in `backend/app/events/handlers.py` (persists events to DB)
- [x] T092 [US6] Create activity router in `backend/app/routers/activity.py` with GET endpoint and filters
- [x] T093 [US6] Register activity router in `backend/app/main.py`

### Frontend Implementation for US6

- [x] T094 [US6] Create ActivityLog component in `frontend/src/components/ActivityLog.tsx`
- [x] T095 [US6] Create ActivityPage or integrate into dashboard in `frontend/src/app/activity/`
- [x] T096 [US6] Add productivity summary (tasks completed per day/week)

### Tests for US6

- [x] T097 [US6] Write unit tests for ActivityService in `backend/tests/unit/test_activity_service.py`

**Checkpoint**: US6 complete. Activity log persists all task operations. FR-024, FR-025 satisfied.

---

## Phase 9: User Story 7 - Cloud Deployment (Priority: P3)

**Goal**: Deploy to Azure AKS with managed Kafka (Event Hubs) and Redis.

**Independent Test**: Deploy to AKS, run smoke tests, verify all services healthy.

**References**: FR-029 to FR-031, SC-010, SC-011

**Dependencies**: Requires US4 (local deployment validated) to be complete.

### Terraform Infrastructure for US7

- [x] T098 [US7] Create Terraform main module in `infrastructure/terraform/azure/main.tf`
- [x] T099 [P] [US7] Create AKS cluster module in `infrastructure/terraform/azure/aks.tf`
- [x] T100 [P] [US7] Create Event Hubs module in `infrastructure/terraform/azure/eventhubs.tf`
- [x] T101 [P] [US7] Create Azure Redis module in `infrastructure/terraform/azure/redis.tf`
- [x] T102 [P] [US7] Create Azure Container Registry module in `infrastructure/terraform/azure/acr.tf`
- [x] T103 [US7] Create Terraform variables and outputs in `infrastructure/terraform/azure/variables.tf`, `outputs.tf`

### Dapr Cloud Configuration for US7

- [x] T104 [US7] Create cloud Dapr pub/sub component for Event Hubs in `infrastructure/dapr/components/pubsub-eventhubs.yaml`
- [x] T105 [P] [US7] Create cloud Dapr state store for Azure Redis in `infrastructure/dapr/components/statestore-azure-redis.yaml`
- [x] T106 [P] [US7] Create cloud Dapr secrets for Key Vault in `infrastructure/dapr/components/secrets-keyvault.yaml`

### Deployment Scripts for US7

- [x] T107 [US7] Create cloud setup script in `scripts/cloud-setup.sh`
- [x] T108 [US7] Create cloud deployment script in `scripts/deploy-cloud.sh`
- [x] T109 [US7] Update Helm charts with cloud-specific values

**Checkpoint**: US7 complete. Production deployment on AKS working. FR-029 to FR-031, SC-010 satisfied.

---

## Phase 10: User Story 8 - CI/CD Pipeline (Priority: P3)

**Goal**: Implement GitHub Actions for automated build, test, and deploy.

**Independent Test**: Push to main, verify pipeline builds, tests, and deploys successfully.

**References**: FR-032

**Dependencies**: Requires US7 (cloud infrastructure) to be complete.

### GitHub Actions for US8

- [x] T110 [US8] Create CI workflow in `.github/workflows/ci.yaml` (lint, test, build)
- [x] T111 [US8] Create CD workflow in `.github/workflows/cd.yaml` (deploy to AKS)
- [x] T112 [US8] Configure GitHub secrets for Azure credentials
- [x] T113 [US8] Add rollback logic on deployment failure
- [x] T114 [US8] Add PR check requiring tests to pass

**Checkpoint**: US8 complete. CI/CD pipeline automated. FR-032 satisfied.

---

## Phase 11: User Story 9 - Monitoring & Logging (Priority: P3)

**Goal**: Implement Prometheus/Grafana monitoring and structured logging.

**Independent Test**: Generate load, verify metrics in Grafana and logs searchable.

**References**: FR-033 to FR-036, SC-012 to SC-014

### Monitoring Setup for US9

- [x] T115 [US9] Create Prometheus metrics in backend using `prometheus-fastapi-instrumentator`
- [x] T116 [US9] Create custom metrics for Kafka consumer lag, reminder latency in `backend/app/metrics.py`
- [x] T117 [US9] Create Grafana dashboard JSON in `infrastructure/monitoring/dashboards/todo-app.json`
- [x] T118 [US9] Create alerting rules in `infrastructure/monitoring/alerts/alerts.yaml`

### Logging Setup for US9

- [x] T119 [US9] Configure structlog in backend with correlation IDs in `backend/app/logging_config.py`
- [x] T120 [US9] Add logging middleware for request correlation in `backend/app/middleware/logging_middleware.py`
- [x] T121 [US9] Configure log export to Azure Monitor in Helm charts

### Deployment for US9

- [x] T122 [US9] Deploy Prometheus stack via Helm in cloud setup script
- [x] T123 [US9] Configure Grafana data sources and dashboards

**Checkpoint**: US9 complete. Monitoring and logging operational. FR-033 to FR-036, SC-012 to SC-014 satisfied.

---

## Phase 12: Polish & Validation

**Purpose**: Final testing, documentation, and cleanup.

- [x] T124 [P] Update README.md with Dapr/Kafka deployment instructions
- [x] T125 [P] Update quickstart.md with verified local deployment steps
- [x] T126 Run full integration test suite across all user stories
- [x] T127 Verify all success criteria (SC-001 to SC-014)
- [x] T128 Create demo script for end-to-end workflow demonstration
- [ ] T129 Commit all changes and create PR

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup - database migrations
- **US1 (Phase 3)**: Depends on Foundational - enhanced task management
- **US4 (Phase 4)**: Depends on Setup - can run in parallel with US1
- **US2 (Phase 5)**: Depends on US1 + US4 - reminders need due dates and Kafka
- **US3 (Phase 6)**: Depends on US1 + US4 - recurrence needs task model and Kafka
- **US5 (Phase 7)**: Depends on US4 - real-time sync needs Kafka
- **US6 (Phase 8)**: Depends on US5 - activity log needs task events
- **US7 (Phase 9)**: Depends on US4 validated - cloud after local works
- **US8 (Phase 10)**: Depends on US7 - CI/CD after cloud infrastructure
- **US9 (Phase 11)**: Depends on US7 - monitoring on cloud deployment
- **Polish (Phase 12)**: Depends on all user stories complete

### User Story Dependencies

```
US1 (Task Management) ─────────────────────────────────┐
                                                       │
US4 (Local Dapr/Kafka) ───┬───► US2 (Reminders) ───────┤
                          │                            │
                          ├───► US3 (Recurrence) ──────┤
                          │                            │
                          └───► US5 (Real-time Sync) ──┼───► US6 (Activity Log)
                                                       │
US7 (Cloud Deployment) ◄───────────────────────────────┘
        │
        ├───► US8 (CI/CD)
        │
        └───► US9 (Monitoring)
```

### Parallel Opportunities

- Phase 1: T002, T003, T004, T005 can run in parallel
- Phase 3: T023, T024, T025 (frontend components) can run in parallel
- Phase 4: T035, T036, T037 (Dapr components) can run in parallel
- Phase 4: T042, T044 (Helm values) can run in parallel
- Phase 9: T099, T100, T101, T102 (Terraform modules) can run in parallel

---

## Implementation Strategy

### MVP First (US1 + US4 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (database migrations)
3. Complete Phase 3: User Story 1 (enhanced task management)
4. Complete Phase 4: User Story 4 (local Dapr/Kafka)
5. **STOP and VALIDATE**: Tasks have due dates, priorities, tags; Dapr works locally
6. Deploy/demo MVP

### Incremental Delivery

1. Setup + Foundational → Database ready
2. Add US1 → Enhanced task management working (MVP!)
3. Add US4 → Event infrastructure ready locally
4. Add US2 → Reminders working via Kafka events
5. Add US3 → Recurring tasks auto-generating
6. Add US5 → Real-time sync between tabs
7. Add US6 → Activity log tracking all operations
8. Add US7 → Production cloud deployment
9. Add US8 → CI/CD automation
10. Add US9 → Monitoring and observability

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: US1 (backend enhanced tasks)
   - Developer B: US4 (infrastructure Dapr/Kafka)
3. Once US1 + US4 complete:
   - Developer A: US2 (reminders)
   - Developer B: US3 (recurrence)
   - Developer C: US5 (real-time sync)
4. Cloud deployment phase (US7-US9) can proceed with one developer

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- US4 (local deployment) MUST be validated before US7 (cloud deployment)
- Commit after each user story completion
- All Kafka events follow CloudEvents specification
- Dapr building blocks: Pub/Sub (Kafka), State (Redis), Bindings (Cron), Secrets (K8s/KeyVault)
