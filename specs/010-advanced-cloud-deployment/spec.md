# Feature Specification: Advanced Cloud Deployment with Dapr, Kafka & Event-Driven Architecture

**Feature Branch**: `010-advanced-cloud-deployment`
**Created**: 2026-02-03
**Status**: Draft
**Input**: User description: "Deploy an event-driven cloud-native AI-powered Todo app using Dapr, Kafka, and Kubernetes on cloud platforms (Azure AKS, Google GKE, or Oracle OKE). First complete local deployment with Minikube and Dapr before scaling to production."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Enhanced Task Management with Due Dates and Priorities (Priority: P1)

As a user, I want to set due dates, priorities, and tags on my tasks so I can organize my work effectively and never miss deadlines. I also want to search, filter, and sort tasks by these attributes.

**Why this priority**: Core user value - enhanced task management is the foundation that all event-driven features build upon. Without these attributes, reminders and recurring tasks have nothing to operate on.

**Independent Test**: Can be fully tested by creating tasks with due dates/priorities/tags and verifying search/filter/sort operations return correct results. Delivers immediate productivity improvement.

**Acceptance Scenarios**:

1. **Given** I am on the task creation form, **When** I set a due date, priority (low/medium/high/urgent), and tags, **Then** the task is saved with all attributes visible in the task list
2. **Given** I have tasks with different priorities, **When** I filter by "high priority", **Then** only high-priority tasks are displayed
3. **Given** I have tasks with various due dates, **When** I sort by due date ascending, **Then** tasks are ordered from soonest to latest deadline
4. **Given** I have tasks with tags, **When** I search for a tag name, **Then** all tasks with that tag are returned
5. **Given** I have a task with a due date, **When** I view my task list, **Then** overdue tasks are visually highlighted

---

### User Story 2 - Task Reminders via Event-Driven Notifications (Priority: P1)

As a user, I want to receive reminders before task due dates so I can take action before deadlines pass. Reminders should be delivered via the notification system and triggered by Kafka events.

**Why this priority**: Critical for user engagement and the primary use case for event-driven architecture. Demonstrates Kafka integration value.

**Independent Test**: Can be tested by creating a task with a reminder, advancing time or using a test event, and verifying the notification is delivered via Kafka consumer.

**Acceptance Scenarios**:

1. **Given** I create a task with a due date and reminder (e.g., 1 hour before), **When** the reminder time arrives, **Then** I receive a notification via the configured channel
2. **Given** I have multiple tasks with reminders, **When** reminder events are published to Kafka, **Then** each reminder is processed and delivered independently
3. **Given** a reminder event fails to deliver, **When** the system retries, **Then** the event is retried up to 3 times before being sent to dead-letter queue
4. **Given** I mark a task as complete, **When** a pending reminder exists, **Then** the reminder is cancelled

---

### User Story 3 - Recurring Tasks with Automatic Generation (Priority: P2)

As a user, I want to create recurring tasks (daily, weekly, monthly, custom) that automatically generate new instances when completed, so I don't have to manually recreate routine tasks.

**Why this priority**: High user value but depends on basic task management (US1) and event system (US2) being in place.

**Independent Test**: Can be tested by creating a recurring task, completing it, and verifying a new instance is automatically created with the correct next due date.

**Acceptance Scenarios**:

1. **Given** I create a task with recurrence "weekly on Monday", **When** I complete the task, **Then** a new task is created for the next Monday automatically
2. **Given** a recurring task is completed, **When** the completion event is published to Kafka, **Then** the recurrence service consumes it and creates the next occurrence
3. **Given** I have a daily recurring task, **When** I view my task list on any day, **Then** I see only the current occurrence (not future instances)
4. **Given** I edit the recurrence pattern of a task, **When** the next occurrence is generated, **Then** it follows the new pattern

---

### User Story 4 - Local Minikube Deployment with Dapr (Priority: P2)

As a DevOps engineer, I want to deploy the complete event-driven system locally on Minikube with Dapr and Kafka, so I can validate the architecture before cloud deployment.

**Why this priority**: Foundation for cloud deployment. All Dapr components must work locally first.

**Independent Test**: Can be tested by running `minikube start`, deploying Dapr and Kafka, deploying the application, and verifying all Dapr building blocks (Pub/Sub, State, Bindings, Secrets, Service Invocation) function correctly.

**Acceptance Scenarios**:

1. **Given** Minikube is running with Dapr initialized, **When** I deploy the backend and frontend, **Then** both services register with Dapr sidecar and are accessible
2. **Given** Kafka is deployed via Helm, **When** I publish a task reminder event, **Then** the subscriber receives and processes it
3. **Given** Dapr state store is configured, **When** I save/retrieve task state, **Then** data persists correctly across pod restarts
4. **Given** Dapr secrets component is configured, **When** the application requests secrets, **Then** database credentials and API keys are retrieved securely
5. **Given** services are deployed with Dapr, **When** backend calls frontend or vice versa, **Then** service invocation works via Dapr's mTLS

---

### User Story 5 - Real-Time Task Sync via Kafka Events (Priority: P2)

As a user with multiple devices, I want my task changes to sync in real-time across all open sessions, so I always see the latest state without manual refresh.

**Why this priority**: Demonstrates the full power of event-driven architecture for user experience.

**Independent Test**: Can be tested by opening the app in two browser tabs, making a change in one, and verifying the other updates within 2 seconds without refresh.

**Acceptance Scenarios**:

1. **Given** I have the app open in two browser tabs, **When** I create a task in tab A, **Then** tab B shows the new task within 2 seconds
2. **Given** I complete a task in one session, **When** the completion event is published to Kafka, **Then** all subscribed sessions update their UI
3. **Given** a user goes offline briefly, **When** they reconnect, **Then** they receive any missed events and sync to current state
4. **Given** high event volume (100+ events/second), **When** events are published, **Then** consumers process them without message loss

---

### User Story 6 - Activity Log and Audit Trail (Priority: P3)

As a user, I want to view an activity log showing all changes to my tasks (created, updated, completed, deleted), so I can track my productivity and audit changes.

**Why this priority**: Nice-to-have feature that leverages event stream for analytics without blocking core functionality.

**Independent Test**: Can be tested by performing various task operations and verifying the activity log shows accurate timestamps and change details.

**Acceptance Scenarios**:

1. **Given** I create a task, **When** I view the activity log, **Then** I see an entry "Task created: [title]" with timestamp
2. **Given** multiple task events occur, **When** Kafka consumers process them, **Then** each event is persisted to the activity log store
3. **Given** I want to see my weekly productivity, **When** I filter the activity log by date range, **Then** I see a summary of completed tasks

---

### User Story 7 - Cloud Deployment on AKS/GKE/OKE (Priority: P3)

As a DevOps engineer, I want to deploy the production system to a managed Kubernetes service (Azure AKS, Google GKE, or Oracle OKE) with Confluent Cloud or Redpanda Cloud for Kafka, so the system is production-ready with enterprise reliability.

**Why this priority**: Production deployment after local validation is complete.

**Independent Test**: Can be tested by deploying to cloud, running smoke tests, and verifying all services are healthy with proper monitoring.

**Acceptance Scenarios**:

1. **Given** AKS/GKE/OKE cluster is provisioned, **When** I deploy via Helm charts, **Then** all pods reach Running state within 5 minutes
2. **Given** Confluent Cloud or Redpanda Cloud is configured, **When** the application publishes events, **Then** messages flow through the cloud Kafka cluster
3. **Given** Dapr is deployed on the cloud cluster, **When** services use Dapr building blocks, **Then** Pub/Sub, State, Bindings, Secrets, and Service Invocation all function correctly
4. **Given** the system is deployed, **When** I access the monitoring dashboard, **Then** I see metrics for all services, Kafka topics, and Dapr components

---

### User Story 8 - CI/CD Pipeline with GitHub Actions (Priority: P3)

As a DevOps engineer, I want automated CI/CD using GitHub Actions that builds, tests, and deploys to the cloud cluster on every merge to main, so deployments are consistent and reliable.

**Why this priority**: Automation after manual deployment is validated.

**Independent Test**: Can be tested by pushing a commit to main and verifying the pipeline builds, tests, and deploys successfully.

**Acceptance Scenarios**:

1. **Given** code is merged to main, **When** GitHub Actions triggers, **Then** Docker images are built and pushed to container registry
2. **Given** images are built, **When** deployment step runs, **Then** Helm upgrade is applied to the cloud cluster
3. **Given** deployment fails, **When** the pipeline detects failure, **Then** it rolls back to previous version and notifies team
4. **Given** a pull request is opened, **When** CI runs, **Then** tests must pass before merge is allowed

---

### User Story 9 - Cloud Monitoring and Logging (Priority: P3)

As a DevOps engineer, I want centralized monitoring (Prometheus/Grafana) and logging (ELK or cloud-native) for the production system, so I can observe system health and troubleshoot issues.

**Why this priority**: Observability for production operations.

**Independent Test**: Can be tested by generating load and verifying metrics appear in dashboards and logs are searchable.

**Acceptance Scenarios**:

1. **Given** the system is deployed, **When** I open Grafana, **Then** I see dashboards for API latency, Kafka consumer lag, and error rates
2. **Given** an error occurs, **When** I search logs, **Then** I find the relevant log entries with correlation IDs
3. **Given** Kafka consumer lag increases, **When** threshold is exceeded, **Then** an alert is triggered

---

### Edge Cases

- What happens when Kafka is temporarily unavailable? (System should queue events locally and retry)
- What happens when a recurring task has no valid next occurrence (e.g., "last day of February" in non-leap year)? (Use nearest valid date)
- What happens when a user deletes a task with pending reminders? (Cancel all associated reminders)
- What happens when cloud deployment exceeds resource limits? (Auto-scaling should kick in; alerts should fire)
- What happens when multiple reminder events fire simultaneously for the same task? (Deduplicate at consumer level)
- What happens when Dapr sidecar is unavailable? (Application should fail gracefully with clear error messages)

## Requirements *(mandatory)*

### Functional Requirements

**Task Management (Enhanced)**
- **FR-001**: System MUST allow users to set due dates on tasks with date and optional time
- **FR-002**: System MUST support task priorities: low, medium, high, urgent
- **FR-003**: System MUST allow users to add multiple tags to tasks
- **FR-004**: System MUST support searching tasks by title, description, and tags
- **FR-005**: System MUST support filtering tasks by priority, due date range, tags, and completion status
- **FR-006**: System MUST support sorting tasks by due date, priority, created date, and title
- **FR-007**: System MUST visually distinguish overdue tasks from upcoming tasks

**Reminders**
- **FR-008**: System MUST allow users to set reminders relative to due date (e.g., 1 hour before, 1 day before)
- **FR-009**: System MUST publish reminder events to Kafka at the scheduled time
- **FR-010**: System MUST deliver reminders via configured notification channel (initially in-app, extensible to email/push)
- **FR-011**: System MUST cancel pending reminders when a task is completed or deleted

**Recurring Tasks**
- **FR-012**: System MUST support recurrence patterns: daily, weekly, monthly, yearly, and custom (e.g., every 2 weeks)
- **FR-013**: System MUST automatically create next occurrence when current occurrence is completed
- **FR-014**: System MUST process recurrence via Kafka events for scalability

**Event-Driven Architecture**
- **FR-015**: System MUST use Kafka for all inter-service communication (reminders, recurrence, sync, activity log)
- **FR-016**: System MUST use Dapr Pub/Sub component for Kafka integration
- **FR-017**: System MUST use Dapr State component for distributed state management
- **FR-018**: System MUST use Dapr Bindings for external integrations (e.g., email notifications)
- **FR-019**: System MUST use Dapr Secrets component for secure credential management
- **FR-020**: System MUST use Dapr Service Invocation for internal service-to-service calls

**Real-Time Sync**
- **FR-021**: System MUST publish task change events (create, update, delete, complete) to Kafka
- **FR-022**: System MUST support WebSocket or Server-Sent Events for real-time UI updates
- **FR-023**: System MUST sync changes across all user sessions within 2 seconds

**Activity Log**
- **FR-024**: System MUST record all task operations as events
- **FR-025**: System MUST persist activity log for user audit and productivity tracking

**Deployment - Local**
- **FR-026**: System MUST deploy on Minikube with Dapr and Kafka
- **FR-027**: System MUST provide Helm charts for all components
- **FR-028**: System MUST include deployment scripts for local environment setup

**Deployment - Cloud**
- **FR-029**: System MUST deploy to at least one managed Kubernetes service (AKS, GKE, or OKE)
- **FR-030**: System MUST integrate with Confluent Cloud or Redpanda Cloud for production Kafka
- **FR-031**: System MUST include Terraform or Pulumi scripts for cloud infrastructure provisioning
- **FR-032**: System MUST implement GitHub Actions CI/CD pipeline

**Monitoring & Observability**
- **FR-033**: System MUST expose Prometheus metrics for all services
- **FR-034**: System MUST include Grafana dashboards for key metrics
- **FR-035**: System MUST implement structured logging with correlation IDs
- **FR-036**: System MUST integrate with cloud-native logging (Azure Monitor, Cloud Logging, or OCI Logging)

### Key Entities

- **Task**: Extended with dueDate, priority, tags[], reminderOffset, recurrencePattern, parentTaskId (for recurring instances)
- **Reminder**: taskId, scheduledTime, status (pending/sent/cancelled), deliveryChannel
- **RecurrencePattern**: type (daily/weekly/monthly/yearly/custom), interval, daysOfWeek[], dayOfMonth, endDate (optional)
- **TaskEvent**: eventType (created/updated/completed/deleted), taskId, userId, timestamp, payload
- **ActivityLogEntry**: userId, eventType, entityType, entityId, timestamp, details

### Assumptions

- Minikube deployment from Phase IV (007/008 features) is complete and working
- Users have access to at least one cloud platform (Azure, GCP, or Oracle Cloud)
- Confluent Cloud or Redpanda Cloud account available for managed Kafka
- GitHub repository with Actions enabled for CI/CD
- Basic Kubernetes and Helm knowledge for deployment operations

## Success Criteria *(mandatory)*

### Measurable Outcomes

**Functional**
- **SC-001**: Users can create tasks with due dates, priorities, and tags in under 30 seconds
- **SC-002**: Search/filter/sort operations return results within 500ms for datasets up to 10,000 tasks
- **SC-003**: Reminders are delivered within 60 seconds of scheduled time
- **SC-004**: Recurring task next occurrence is created within 5 seconds of completion
- **SC-005**: Real-time sync delivers changes to all sessions within 2 seconds

**Reliability**
- **SC-006**: Kafka message delivery achieves 99.9% success rate with at-least-once semantics
- **SC-007**: System handles 1000 concurrent users without degradation
- **SC-008**: Zero data loss during Kafka broker failover (replication factor ≥ 3 in production)

**Deployment**
- **SC-009**: Local Minikube deployment completes in under 10 minutes from fresh start
- **SC-010**: Cloud deployment completes in under 15 minutes via CI/CD pipeline
- **SC-011**: All Dapr building blocks (Pub/Sub, State, Bindings, Secrets, Service Invocation) validated in both environments

**Observability**
- **SC-012**: Grafana dashboards show real-time metrics for API latency p95, Kafka consumer lag, and error rates
- **SC-013**: Logs are searchable within 30 seconds of generation
- **SC-014**: Alerts fire within 2 minutes of threshold breach
