# Implementation Plan: Advanced Cloud Deployment with Dapr, Kafka & Event-Driven Architecture

**Branch**: `010-advanced-cloud-deployment` | **Date**: 2026-02-03 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/010-advanced-cloud-deployment/spec.md`

## Summary

This feature transforms the Todo application into a cloud-native, event-driven system using Dapr and Kafka. The implementation follows a progressive approach: first enhancing task management (due dates, priorities, tags, reminders, recurring tasks), then adding event-driven infrastructure (Dapr + Kafka on Minikube), and finally deploying to production cloud (AKS/GKE/OKE with managed Kafka).

## Technical Context

**Language/Version**: Python 3.11 (backend), TypeScript/Node 20 (frontend)
**Primary Dependencies**: FastAPI, Dapr SDK, kafka-python/aiokafka, SQLModel, Next.js 15, React 19
**Storage**: PostgreSQL (Neon) for primary data, Redis (Dapr state store), Kafka (event streaming)
**Testing**: pytest (backend), Jest/Vitest (frontend), integration tests with testcontainers
**Target Platform**: Minikube (local), Azure AKS / Google GKE / Oracle OKE (production)
**Project Type**: Web application (backend + frontend + event services)
**Performance Goals**: <500ms API response, <2s real-time sync, 1000 concurrent users
**Constraints**: At-least-once Kafka semantics, <60s reminder delivery, event ordering per user
**Scale/Scope**: 10k tasks per user, 1000 concurrent users, 100 events/second peak

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Spec First | PASS | Spec exists at `specs/010-advanced-cloud-deployment/spec.md` with 36 FRs, 14 SCs |
| II. Agent Discipline | PASS | event-agent scope: Kafka & Dapr event flows; devops-agent scope: Docker, K8s, Helm |
| III. Incremental Evolution | PASS | Builds on completed Phase IV (007-009 features); local before cloud |
| IV. Test-Backed Progress | PASS | Contract tests for Kafka messages, integration tests for Dapr components |
| V. Traceability | PASS | All tasks will reference FR/SC IDs from spec |

**Gate Status**: PASS (5/5 principles satisfied)

## Project Structure

### Documentation (this feature)

```text
specs/010-advanced-cloud-deployment/
├── plan.md              # This file
├── research.md          # Phase 0 output - Dapr/Kafka research
├── data-model.md        # Phase 1 output - Extended task entities
├── quickstart.md        # Phase 1 output - Local + cloud deployment guide
├── contracts/           # Phase 1 output - Kafka message schemas, API extensions
│   ├── kafka-events.md  # Event message formats
│   ├── task-api-v2.md   # Extended task endpoints
│   └── dapr-components.md # Dapr component configurations
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── models/
│   │   ├── task.py           # Extended with due_date, priority, tags, recurrence
│   │   ├── reminder.py       # NEW: Reminder entity
│   │   ├── activity_log.py   # NEW: Activity log entry
│   │   └── tag.py            # NEW: Tag entity (many-to-many with tasks)
│   ├── services/
│   │   ├── task_service.py   # Extended for search/filter/sort
│   │   ├── reminder_service.py    # NEW: Reminder scheduling
│   │   ├── recurrence_service.py  # NEW: Recurring task generation
│   │   ├── activity_service.py    # NEW: Activity log persistence
│   │   └── kafka_producer.py      # NEW: Kafka event publishing
│   ├── events/
│   │   ├── __init__.py
│   │   ├── handlers.py       # NEW: Kafka event handlers (consumers)
│   │   ├── schemas.py        # NEW: Event message schemas (Pydantic)
│   │   └── topics.py         # NEW: Kafka topic definitions
│   ├── routers/
│   │   ├── tasks.py          # Extended for new fields
│   │   ├── reminders.py      # NEW: Reminder endpoints
│   │   ├── activity.py       # NEW: Activity log endpoints
│   │   └── websocket.py      # NEW: Real-time sync endpoint
│   └── dapr/
│       ├── __init__.py
│       ├── pubsub.py         # NEW: Dapr Pub/Sub integration
│       ├── state.py          # NEW: Dapr State store operations
│       ├── bindings.py       # NEW: Dapr Bindings (cron, email)
│       └── secrets.py        # NEW: Dapr Secrets component
├── tests/
│   ├── contract/
│   │   └── test_kafka_events.py  # NEW: Event schema validation
│   └── integration/
│       ├── test_dapr_pubsub.py   # NEW: Dapr pub/sub tests
│       └── test_reminders.py     # NEW: Reminder flow tests

frontend/
├── src/
│   ├── components/
│   │   ├── TaskForm.tsx      # Extended for due date, priority, tags
│   │   ├── TaskFilters.tsx   # NEW: Filter/sort controls
│   │   ├── TagInput.tsx      # NEW: Tag management
│   │   ├── DatePicker.tsx    # NEW: Due date selection
│   │   ├── PrioritySelect.tsx # NEW: Priority selector
│   │   ├── RecurrenceEditor.tsx # NEW: Recurrence pattern editor
│   │   ├── ActivityLog.tsx   # NEW: Activity log view
│   │   └── NotificationToast.tsx # NEW: In-app notifications
│   ├── hooks/
│   │   ├── useWebSocket.ts   # NEW: Real-time sync hook
│   │   ├── useNotifications.ts # NEW: Notification handling
│   │   └── useTaskFilters.ts # NEW: Filter state management
│   └── lib/
│       └── websocket.ts      # NEW: WebSocket client

# Infrastructure (NEW directory)
infrastructure/
├── dapr/
│   ├── components/
│   │   ├── pubsub-kafka.yaml    # Kafka pub/sub component
│   │   ├── statestore-redis.yaml # Redis state store
│   │   ├── binding-cron.yaml    # Cron binding for reminders
│   │   ├── binding-email.yaml   # Email output binding
│   │   └── secrets-k8s.yaml     # Kubernetes secrets component
│   └── config.yaml              # Dapr configuration
├── kafka/
│   ├── topics.yaml              # Topic definitions
│   └── consumer-groups.yaml     # Consumer group configs
├── helm/
│   ├── todo-backend-v2/         # Extended backend chart with Dapr
│   ├── todo-frontend-v2/        # Extended frontend chart
│   ├── kafka/                   # Kafka Helm chart values
│   ├── redis/                   # Redis Helm chart values
│   └── dapr/                    # Dapr Helm chart values
├── terraform/
│   ├── azure/                   # AKS infrastructure
│   ├── gcp/                     # GKE infrastructure
│   └── oci/                     # OKE infrastructure
└── github-actions/
    ├── ci.yaml                  # Build and test workflow
    └── cd.yaml                  # Deploy workflow

# Scripts
scripts/
├── local-setup.sh               # Minikube + Dapr + Kafka setup
├── cloud-setup.sh               # Cloud infrastructure provisioning
└── dev-env.sh                   # Local development environment
```

**Structure Decision**: Extended web application structure with new `infrastructure/` directory for Dapr components, Kafka configuration, Terraform modules, and CI/CD workflows. Event-driven services are part of the backend, not separate microservices, to minimize complexity.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Additional infrastructure directory | Event-driven architecture requires Dapr components, Kafka configs, and IaC | Embedding in existing helm/ would make it cluttered and hard to maintain |
| Multiple Dapr building blocks | Spec requires Pub/Sub, State, Bindings, Secrets, Service Invocation | Single building block insufficient for reminders + sync + secrets |
| Kafka + Redis | Kafka for events, Redis for state store | Single store cannot handle both event streaming and fast state access |

## Implementation Phases

### Phase A: Enhanced Task Management (US1 - P1)

**Goal**: Extend Task model and API with due dates, priorities, tags, and search/filter/sort capabilities.

**Duration Estimate**: Foundation for all event-driven features

#### A.1 Data Model Extensions

1. Extend Task model with new fields:
   - `due_date: Optional[datetime]`
   - `priority: Enum[low, medium, high, urgent]`
   - `reminder_offset: Optional[timedelta]` (e.g., 1 hour before)
   - `recurrence_id: Optional[UUID]` (FK to RecurrencePattern)

2. Create Tag model (many-to-many with Task):
   - `id: UUID`
   - `name: str`
   - `user_id: str`
   - `color: Optional[str]`

3. Create TaskTag junction table:
   - `task_id: UUID`
   - `tag_id: UUID`

4. Create RecurrencePattern model:
   - `id: UUID`
   - `type: Enum[daily, weekly, monthly, yearly, custom]`
   - `interval: int` (every N days/weeks/etc.)
   - `days_of_week: List[int]` (for weekly: 0=Mon, 6=Sun)
   - `day_of_month: Optional[int]`
   - `end_date: Optional[datetime]`
   - `user_id: str`

#### A.2 API Extensions

1. Extend `POST /api/tasks` and `PUT /api/tasks/{id}`:
   - Accept `due_date`, `priority`, `tags[]`, `reminder_offset`, `recurrence`

2. Add query parameters to `GET /api/tasks`:
   - `priority`: Filter by priority level
   - `due_before`, `due_after`: Date range filter
   - `tags`: Filter by tag names (comma-separated)
   - `sort_by`: `due_date`, `priority`, `created_at`, `title`
   - `sort_order`: `asc`, `desc`
   - `search`: Full-text search on title/description

3. New endpoints:
   - `GET /api/tags` - List user's tags
   - `POST /api/tags` - Create tag
   - `DELETE /api/tags/{id}` - Delete tag

#### A.3 Frontend Updates

1. TaskForm component:
   - DatePicker for due date
   - PrioritySelect dropdown
   - TagInput with autocomplete
   - RecurrenceEditor (optional toggle)

2. TaskFilters component:
   - Priority filter chips
   - Date range picker
   - Tag filter multi-select
   - Sort dropdown

3. TaskList enhancements:
   - Visual indicators for overdue tasks (red highlight)
   - Priority badges
   - Tag chips
   - Due date display with relative time ("Due in 2 hours")

---

### Phase B: Event Infrastructure - Local Dapr & Kafka (US2 + US4 - P1/P2)

**Goal**: Deploy Dapr and Kafka on Minikube, implement reminder system as first event-driven feature.

**Duration Estimate**: Critical infrastructure foundation

#### B.1 Minikube Infrastructure Setup

1. Dapr installation on Minikube:
   ```bash
   dapr init -k
   ```

2. Kafka deployment (Bitnami Helm chart):
   ```bash
   helm install kafka bitnami/kafka --set replicaCount=1
   ```

3. Redis deployment for Dapr state store:
   ```bash
   helm install redis bitnami/redis --set auth.enabled=false
   ```

4. Configure Dapr components:
   - `pubsub-kafka.yaml`: Kafka pub/sub component
   - `statestore-redis.yaml`: Redis state store
   - `binding-cron.yaml`: Cron binding for reminder scheduler
   - `secrets-k8s.yaml`: Kubernetes secrets component

#### B.2 Dapr Integration in Backend

1. Install Dapr SDK:
   ```
   dapr-ext-fastapi
   ```

2. Implement Dapr service wrappers:
   - `dapr/pubsub.py`: Publish/subscribe helpers
   - `dapr/state.py`: State store CRUD operations
   - `dapr/secrets.py`: Secret retrieval

3. Update Helm chart for Dapr sidecar injection:
   ```yaml
   annotations:
     dapr.io/enabled: "true"
     dapr.io/app-id: "todo-backend"
     dapr.io/app-port: "8000"
   ```

#### B.3 Reminder System (Event-Driven)

1. Create Reminder model:
   - `id: UUID`
   - `task_id: UUID`
   - `user_id: str`
   - `scheduled_time: datetime`
   - `status: Enum[pending, sent, cancelled]`
   - `delivery_channel: str` (default: "in-app")

2. Reminder Scheduler Service:
   - Dapr cron binding triggers every minute
   - Query due reminders: `scheduled_time <= now() AND status = 'pending'`
   - Publish `reminder.due` event to Kafka

3. Reminder Consumer:
   - Subscribe to `reminder.due` topic
   - Deliver notification (initially: publish to `notification.send` topic)
   - Update reminder status to `sent`
   - Handle retries (max 3, exponential backoff)

4. Kafka Topics:
   - `task.events`: All task lifecycle events
   - `reminder.due`: Reminders ready to send
   - `notification.send`: Notifications to deliver
   - `notification.dlq`: Dead letter queue for failed notifications

5. Event Schemas (Pydantic):
   ```python
   class TaskEvent(BaseModel):
       event_type: Literal["created", "updated", "completed", "deleted"]
       task_id: UUID
       user_id: str
       timestamp: datetime
       payload: dict

   class ReminderDueEvent(BaseModel):
       reminder_id: UUID
       task_id: UUID
       user_id: str
       task_title: str
       due_date: datetime
   ```

---

### Phase C: Full Event-Driven Features (US3 + US5 + US6 - P2/P3)

**Goal**: Implement recurring tasks, real-time sync, and activity logging using the event infrastructure.

#### C.1 Recurring Tasks (US3)

1. Recurrence Service:
   - Subscribe to `task.completed` events
   - Check if task has `recurrence_id`
   - Calculate next occurrence date based on pattern
   - Create new task with updated `due_date`
   - Publish `task.created` event for new instance

2. Recurrence calculation logic:
   - Daily: Add `interval` days
   - Weekly: Find next matching day of week
   - Monthly: Same day next month (handle edge cases like 31st)
   - Yearly: Same date next year
   - Custom: Apply interval to base unit

3. Edge case handling:
   - "Last day of month" → Use actual last day
   - February 30th → Use February 28/29
   - End date reached → Stop creating new instances

#### C.2 Real-Time Sync (US5)

1. WebSocket endpoint:
   - `WS /api/ws/tasks` - Real-time task updates
   - Authentication via JWT in query param or first message

2. Sync Service:
   - Subscribe to `task.events` Kafka topic
   - Maintain WebSocket connections per user
   - Broadcast relevant events to connected clients

3. Frontend WebSocket hook:
   ```typescript
   const { events, connected } = useWebSocket('/api/ws/tasks');
   useEffect(() => {
     events.forEach(event => {
       if (event.type === 'task.created') addTask(event.payload);
       if (event.type === 'task.updated') updateTask(event.payload);
       // ...
     });
   }, [events]);
   ```

4. Reconnection handling:
   - On disconnect: Queue local changes
   - On reconnect: Request sync from last known event ID
   - Apply missed events in order

#### C.3 Activity Log (US6)

1. ActivityLogEntry model:
   - `id: UUID`
   - `user_id: str`
   - `event_type: str`
   - `entity_type: Literal["task", "reminder", "tag"]`
   - `entity_id: UUID`
   - `timestamp: datetime`
   - `details: JSON`

2. Activity Consumer:
   - Subscribe to `task.events`, `reminder.events`
   - Persist each event to activity log table
   - Index by user_id and timestamp for queries

3. Activity API:
   - `GET /api/activity` - Paginated activity log
   - Query params: `from`, `to`, `event_type`, `limit`, `offset`

4. Frontend ActivityLog component:
   - Timeline view of recent actions
   - Filterable by date range
   - Productivity summary (tasks completed per day/week)

---

### Phase D: Cloud Deployment (US7 + US8 + US9 - P3)

**Goal**: Deploy to production cloud infrastructure with managed services, CI/CD, and observability.

#### D.1 Cloud Infrastructure (US7)

1. Choose primary cloud (recommendation: Azure AKS for simplicity):
   - Azure: AKS + Azure Event Hubs (Kafka-compatible) + Azure Redis
   - GCP: GKE + Confluent Cloud + Memorystore Redis
   - OCI: OKE + Redpanda Cloud + OCI Cache

2. Terraform modules:
   ```
   infrastructure/terraform/azure/
   ├── main.tf           # Resource group, AKS cluster
   ├── networking.tf     # VNet, subnets, NSGs
   ├── aks.tf            # AKS configuration
   ├── eventhubs.tf      # Event Hubs namespace + topics
   ├── redis.tf          # Azure Cache for Redis
   ├── acr.tf            # Container registry
   └── outputs.tf        # Connection strings, endpoints
   ```

3. Dapr on AKS:
   ```bash
   dapr init -k --runtime-version 1.12.0
   ```

4. Update Dapr components for cloud:
   - Swap Kafka broker URLs to Event Hubs/Confluent
   - Swap Redis to managed Redis endpoint
   - Use Azure Key Vault for secrets

#### D.2 CI/CD Pipeline (US8)

1. GitHub Actions - CI (`.github/workflows/ci.yaml`):
   ```yaml
   on: [push, pull_request]
   jobs:
     test:
       - Lint (ruff, eslint)
       - Unit tests (pytest, jest)
       - Build Docker images
       - Push to ACR (on main only)
   ```

2. GitHub Actions - CD (`.github/workflows/cd.yaml`):
   ```yaml
   on:
     push:
       branches: [main]
   jobs:
     deploy:
       - Pull latest images
       - Helm upgrade to AKS
       - Run smoke tests
       - Rollback on failure
   ```

3. Environment management:
   - `dev`: Auto-deploy on PR merge to `develop`
   - `staging`: Auto-deploy on merge to `main`
   - `production`: Manual approval required

#### D.3 Monitoring & Observability (US9)

1. Prometheus + Grafana stack:
   ```bash
   helm install prometheus prometheus-community/kube-prometheus-stack
   ```

2. Custom metrics:
   - `todo_api_requests_total`: API request count by endpoint
   - `todo_kafka_consumer_lag`: Consumer lag per topic
   - `todo_reminder_delivery_time_seconds`: Reminder delivery latency
   - `todo_websocket_connections_active`: Active WebSocket connections

3. Grafana dashboards:
   - API Performance: Latency p50/p95/p99, error rate, throughput
   - Kafka Health: Consumer lag, message rate, partition status
   - Dapr Components: Pub/sub success rate, state store latency
   - Application Health: Pod status, CPU/memory usage

4. Alerting rules:
   - API error rate > 1% for 5 minutes
   - Kafka consumer lag > 1000 messages
   - Reminder delivery latency > 60 seconds
   - Pod restart count > 3 in 10 minutes

5. Structured logging:
   - Use `structlog` in Python backend
   - Correlation ID in all logs
   - Export to Azure Monitor / Cloud Logging

---

## Risk Analysis

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Dapr learning curve | Medium | Medium | Start with Pub/Sub only, add components incrementally |
| Kafka message ordering | Medium | High | Use user_id as partition key for per-user ordering |
| WebSocket scaling | Medium | Medium | Use Redis pub/sub for cross-pod WebSocket broadcast |
| Cloud cost overrun | Low | Medium | Use dev/staging with minimal resources; auto-shutdown |
| Reminder timing drift | Medium | Medium | Use Dapr cron with 1-minute granularity; accept ±30s variance |
| Schema evolution | Medium | High | Use Avro/JSON Schema with compatibility checks |

## Dependencies

### External Services

- **Managed Kafka**: Confluent Cloud, Redpanda Cloud, or Azure Event Hubs
- **Managed Redis**: Azure Cache, Memorystore, or OCI Cache
- **Container Registry**: Azure ACR, GCP Artifact Registry, or OCI Registry
- **Managed Kubernetes**: AKS, GKE, or OKE

### Local Development

- **Minikube**: v1.38+ with Docker driver
- **Dapr CLI**: v1.12+
- **Helm**: v3.14+
- **kubectl**: v1.29+

### Python Dependencies (new)

```
dapr>=1.12.0
dapr-ext-fastapi>=1.12.0
aiokafka>=0.9.0
redis>=5.0.0
structlog>=24.1.0
```

### Node Dependencies (new)

```
@dapr/dapr
reconnecting-websocket
```

## Decision Log

| Decision | Options Considered | Chosen | Rationale |
|----------|-------------------|--------|-----------|
| Event broker | Kafka, RabbitMQ, NATS | Kafka | Spec requires Kafka; best for event sourcing |
| State store | Redis, PostgreSQL | Redis via Dapr | Fast access, Dapr native support |
| Reminder scheduler | Celery, APScheduler, Dapr Cron | Dapr Cron | Kubernetes-native, no separate worker needed |
| Real-time sync | Polling, SSE, WebSocket | WebSocket | Bidirectional, lower latency |
| Cloud provider | Azure, GCP, OCI | Azure (primary) | Best Dapr integration, Event Hubs Kafka-compatible |
| IaC tool | Terraform, Pulumi, ARM | Terraform | Industry standard, multi-cloud |
