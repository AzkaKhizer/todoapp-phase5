# The Evolution of Todo: Spec-Driven, Agentic AI Development

A hackathon project demonstrating the evolution from a simple console application to a cloud-native, event-driven web application using Spec-Driven Development (SDD).

## Phases

### Phase I: Todo Console Application
A Python console-based todo application with in-memory storage.

### Phase II: Todo Full-Stack Web Application
A modern, full-stack todo application with FastAPI backend and Next.js frontend.

### Phase III: Cloud-Native Event-Driven Architecture
An advanced cloud-native implementation with Dapr, Kafka, real-time sync, and Azure deployment.

## Phase III Features

- **Enhanced Task Management**: Due dates, priorities, tags, search/filter/sort
- **Task Reminders**: Scheduled notifications with retry logic and dead-letter queue
- **Recurring Tasks**: Daily, weekly, monthly, yearly patterns with automatic generation
- **Real-Time Sync**: WebSocket-based updates via Kafka events
- **Activity Log**: Audit trail and productivity tracking
- **Cloud Deployment**: Azure AKS with Terraform infrastructure
- **CI/CD Pipeline**: GitHub Actions with automated testing and deployment
- **Monitoring**: Prometheus metrics and Grafana dashboards

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLModel** - SQL database ORM with Pydantic integration
- **PostgreSQL** (Neon/Azure) - Cloud database
- **Dapr** - Distributed application runtime
- **Kafka/Event Hubs** - Event streaming platform
- **Redis** - State store and caching
- **Better Auth** - JWT authentication

### Frontend
- **Next.js 15** - React framework with App Router
- **React 19** - UI library
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **WebSocket** - Real-time updates

### Infrastructure
- **Azure AKS** - Managed Kubernetes
- **Azure Event Hubs** - Kafka-compatible event streaming
- **Azure Cache for Redis** - Managed Redis
- **Terraform** - Infrastructure as Code
- **Helm** - Kubernetes package manager
- **GitHub Actions** - CI/CD pipelines

## Quick Start

### Prerequisites

- Python 3.13+
- Node.js 20+
- Docker & Docker Compose
- kubectl (for Kubernetes deployment)
- Terraform (for cloud deployment)

### Local Development

#### 1. Backend Setup

```bash
cd backend

# Copy environment variables
cp .env.example .env

# Edit .env with your configuration:
# DATABASE_URL=postgresql+asyncpg://user:pass@host/db
# BETTER_AUTH_SECRET=your-secret-key

# Install dependencies
uv sync

# Run the backend
uv run uvicorn app.main:app --reload --port 8000
```

#### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment variables
cp .env.example .env

# Run the development server
npm run dev
```

### Local Kubernetes (Minikube)

```bash
# Start Minikube with Dapr
./scripts/local-setup.sh

# Deploy the application
kubectl apply -f infrastructure/dapr/components/
helm upgrade --install todo-backend infrastructure/helm/todo-backend-v2 -n todo-app
helm upgrade --install todo-frontend infrastructure/helm/todo-frontend-v2 -n todo-app
```

### Cloud Deployment (Azure)

```bash
# Set required environment variables
export TF_VAR_postgres_admin_password="your-secure-password"
export TF_VAR_better_auth_secret="your-jwt-secret"

# Deploy infrastructure
./scripts/cloud-setup.sh dev

# Build and deploy application
./scripts/deploy-cloud.sh all
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/logout` - Logout user
- `GET /api/auth/me` - Get current user info

### Tasks
- `GET /api/tasks` - List tasks (with filter/sort/pagination)
- `POST /api/tasks` - Create task (with reminders, recurrence)
- `GET /api/tasks/{id}` - Get single task
- `PUT /api/tasks/{id}` - Full update task
- `PATCH /api/tasks/{id}` - Partial update task
- `DELETE /api/tasks/{id}` - Delete task
- `PATCH /api/tasks/{id}/toggle` - Toggle completion

### Tags
- `GET /api/tags` - List user's tags
- `POST /api/tags` - Create tag
- `DELETE /api/tags/{id}` - Delete tag

### Reminders
- `GET /api/reminders/{task_id}` - Get task reminder
- `PUT /api/reminders/{task_id}` - Update reminder
- `DELETE /api/reminders/{task_id}` - Cancel reminder

### Activity Log
- `GET /api/activities` - List activities (with filters)
- `GET /api/activities/productivity` - Get productivity summary
- `GET /api/activities/entity/{type}/{id}` - Get entity history

### WebSocket
- `WS /ws/sync?token={jwt}` - Real-time sync connection

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── dapr/              # Dapr building block helpers
│   │   ├── events/            # Kafka event schemas & handlers
│   │   ├── middleware/        # Request logging middleware
│   │   ├── models/            # SQLModel models
│   │   ├── routers/           # API routes
│   │   ├── services/          # Business logic
│   │   ├── metrics.py         # Prometheus metrics
│   │   └── logging_config.py  # Structured logging
│   └── tests/
│       ├── unit/              # Unit tests
│       ├── integration/       # Integration tests
│       └── contract/          # Kafka event contract tests
├── frontend/
│   ├── src/
│   │   ├── app/               # Next.js pages
│   │   ├── components/        # React components
│   │   ├── hooks/             # Custom hooks (useTasks, useWebSocket)
│   │   └── lib/               # API client, WebSocket client
├── infrastructure/
│   ├── dapr/
│   │   └── components/        # Dapr component configs
│   ├── helm/
│   │   ├── todo-backend-v2/   # Backend Helm chart
│   │   └── todo-frontend-v2/  # Frontend Helm chart
│   ├── terraform/
│   │   └── azure/             # Azure infrastructure
│   └── monitoring/
│       ├── dashboards/        # Grafana dashboards
│       └── alerts/            # Prometheus alerting rules
├── scripts/
│   ├── local-setup.sh         # Local Minikube setup
│   ├── cloud-setup.sh         # Azure infrastructure setup
│   └── deploy-cloud.sh        # Application deployment
├── specs/                     # Design specifications
└── .github/
    └── workflows/             # CI/CD pipelines
```

## Event-Driven Architecture

### Kafka Topics

| Topic | Purpose | Retention |
|-------|---------|-----------|
| `task.events` | Task lifecycle events | 7 days |
| `reminder.due` | Due reminder notifications | 1 day |
| `notification.send` | Notification delivery | 1 day |
| `notification.dlq` | Failed notifications | 30 days |
| `activity.log` | Audit trail events | 30 days |
| `sync.events` | Real-time sync | 1 hour |

### Dapr Building Blocks

- **Pub/Sub**: Kafka (local) / Event Hubs (Azure)
- **State Store**: Redis
- **Secrets**: Kubernetes / Azure Key Vault
- **Bindings**: Cron (reminder scheduler)

## Monitoring

### Prometheus Metrics

- HTTP request latency (p50, p90, p95, p99)
- Error rates by endpoint
- Task operations (created, completed, deleted)
- Kafka consumer lag
- Reminder delivery latency
- WebSocket connection count

### Grafana Dashboards

Import `infrastructure/monitoring/dashboards/todo-app.json` to visualize:
- API performance overview
- Business metrics
- Kafka health
- Resource utilization

### Alerting

Prometheus alerting rules in `infrastructure/monitoring/alerts/alerts.yaml`:
- Service availability
- High latency (P95 > 500ms)
- Error rate (> 1%)
- Kafka consumer lag (> 1000)
- Pod resource issues

## Running Tests

```bash
# Backend unit tests
cd backend
uv run pytest tests/unit -v

# Backend integration tests (requires services)
uv run pytest tests/integration -v

# Frontend build verification
cd frontend
npm run build
```

## Environment Variables

### Backend

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `BETTER_AUTH_SECRET` | JWT signing secret | Yes |
| `BETTER_AUTH_URL` | Frontend URL for auth | Yes |
| `REDIS_URL` | Redis connection string | No |
| `DAPR_HTTP_PORT` | Dapr sidecar port | No |

### Frontend

| Variable | Description | Required |
|----------|-------------|----------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | Yes |
| `NEXT_PUBLIC_WS_URL` | WebSocket URL | No |

## License

MIT License
