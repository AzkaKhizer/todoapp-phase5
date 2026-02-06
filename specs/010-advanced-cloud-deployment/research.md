# Research: Dapr, Kafka, and Event-Driven Architecture

**Feature**: 010-advanced-cloud-deployment
**Date**: 2026-02-03
**Status**: Complete

## 1. Dapr (Distributed Application Runtime)

### Overview

Dapr is a portable, event-driven runtime that makes it easy to build resilient, stateless and stateful microservices. It provides building blocks for common distributed system patterns.

### Building Blocks Required (FR-016 to FR-020)

| Building Block | Use Case | Configuration |
|---------------|----------|---------------|
| **Pub/Sub** | Kafka integration for events | `pubsub.kafka` component |
| **State Management** | Distributed state (Redis) | `state.redis` component |
| **Bindings** | Cron triggers, email output | `bindings.cron`, `bindings.smtp` |
| **Secrets** | Secure credential storage | `secretstores.kubernetes` |
| **Service Invocation** | Inter-service mTLS calls | Built-in with app-id |

### Dapr on Kubernetes

```yaml
# Deployment annotation for Dapr sidecar injection
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-backend
spec:
  template:
    metadata:
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "todo-backend"
        dapr.io/app-port: "8000"
        dapr.io/config: "dapr-config"
        dapr.io/log-level: "info"
```

### Dapr Python SDK

```python
from dapr.clients import DaprClient

# Publish event
with DaprClient() as client:
    client.publish_event(
        pubsub_name="kafka-pubsub",
        topic_name="task.events",
        data=json.dumps(event_data),
        data_content_type="application/json"
    )

# Subscribe to events (FastAPI)
from dapr.ext.fastapi import DaprApp

dapr_app = DaprApp(app)

@dapr_app.subscribe(pubsub="kafka-pubsub", topic="task.events")
async def handle_task_event(event: dict):
    # Process event
    pass
```

### Dapr Components Configuration

**Kafka Pub/Sub** (`infrastructure/dapr/components/pubsub-kafka.yaml`):
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "kafka:9092"  # Local: kafka.default.svc.cluster.local:9092
    - name: consumerGroup
      value: "todo-backend-group"
    - name: authRequired
      value: "false"  # Set to true for cloud with SASL
```

**Redis State Store** (`infrastructure/dapr/components/statestore-redis.yaml`):
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.redis
  version: v1
  metadata:
    - name: redisHost
      value: "redis-master:6379"
    - name: redisPassword
      secretKeyRef:
        name: redis-secret
        key: redis-password
```

**Cron Binding** (`infrastructure/dapr/components/binding-cron.yaml`):
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: reminder-scheduler
spec:
  type: bindings.cron
  version: v1
  metadata:
    - name: schedule
      value: "* * * * *"  # Every minute
    - name: direction
      value: "input"
```

---

## 2. Apache Kafka

### Overview

Kafka is a distributed event streaming platform for high-throughput, fault-tolerant messaging. It provides durable message storage with replay capability.

### Topic Design

| Topic | Purpose | Partitions | Retention |
|-------|---------|------------|-----------|
| `task.events` | All task lifecycle events | 12 | 7 days |
| `reminder.due` | Reminders ready to send | 6 | 1 day |
| `notification.send` | Notifications to deliver | 6 | 1 day |
| `notification.dlq` | Failed notifications | 3 | 30 days |
| `activity.log` | Activity stream | 12 | 30 days |
| `sync.events` | Real-time sync events | 12 | 1 hour |

### Partition Strategy

- **Key**: `user_id` for all topics
- **Rationale**: Ensures per-user event ordering
- **Consumer Groups**: One per service (backend, reminder-worker, sync-worker)

### Message Format (CloudEvents)

```json
{
  "specversion": "1.0",
  "type": "com.todo.task.created",
  "source": "/api/tasks",
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "time": "2026-02-03T10:30:00Z",
  "datacontenttype": "application/json",
  "data": {
    "task_id": "123e4567-e89b-12d3-a456-426614174000",
    "user_id": "user_abc123",
    "title": "Buy groceries",
    "due_date": "2026-02-04T18:00:00Z",
    "priority": "high"
  }
}
```

### Kafka on Minikube (Bitnami Helm)

```bash
# Add Bitnami repo
helm repo add bitnami https://charts.bitnami.com/bitnami

# Install Kafka with minimal resources
helm install kafka bitnami/kafka \
  --set replicaCount=1 \
  --set controller.replicaCount=1 \
  --set kraft.enabled=true \
  --set listeners.client.protocol=PLAINTEXT \
  --set resources.requests.memory=512Mi \
  --set resources.requests.cpu=250m
```

### Python Kafka Client (aiokafka)

```python
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer

# Producer
producer = AIOKafkaProducer(
    bootstrap_servers='kafka:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)
await producer.start()
await producer.send_and_wait("task.events", value=event_data, key=user_id.encode())

# Consumer
consumer = AIOKafkaConsumer(
    "task.events",
    bootstrap_servers='kafka:9092',
    group_id="todo-backend-group",
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)
await consumer.start()
async for msg in consumer:
    await handle_event(msg.value)
```

---

## 3. Cloud Kafka Options

### Confluent Cloud

- **Pros**: Full Kafka API, Schema Registry, ksqlDB, excellent tooling
- **Cons**: Higher cost, overkill for small workloads
- **Pricing**: Pay per throughput + storage (~$0.11/GB transferred)

### Redpanda Cloud

- **Pros**: Kafka-compatible, simpler ops, lower latency
- **Cons**: Smaller ecosystem, fewer integrations
- **Pricing**: More predictable pricing, free tier available

### Azure Event Hubs (Kafka-compatible)

- **Pros**: Native Azure integration, managed scaling
- **Cons**: Not 100% Kafka compatible, some limitations
- **Pricing**: Included in Azure subscription tiers

**Recommendation**: Azure Event Hubs for Azure deployments (simplicity), Confluent Cloud for GCP/OCI (full Kafka compatibility).

---

## 4. Event-Driven Use Cases

### 4.1 Reminder System

```
[User creates task with reminder]
       ↓
[Task saved to DB] → [Reminder scheduled in DB]
       ↓
[Cron binding fires every minute]
       ↓
[Reminder service queries due reminders]
       ↓
[Publish to reminder.due topic]
       ↓
[Notification consumer processes]
       ↓
[Push to WebSocket / In-app notification]
       ↓
[Update reminder status to 'sent']
```

### 4.2 Recurring Task Generation

```
[User completes recurring task]
       ↓
[Task marked complete in DB]
       ↓
[Publish task.completed event to Kafka]
       ↓
[Recurrence consumer receives event]
       ↓
[Check if task has recurrence pattern]
       ↓
[Calculate next due date]
       ↓
[Create new task via API/direct DB]
       ↓
[Publish task.created event]
       ↓
[Real-time sync broadcasts to clients]
```

### 4.3 Real-Time Sync

```
[Client A modifies task]
       ↓
[API updates DB + publishes sync.events]
       ↓
[Sync service consumes event]
       ↓
[Lookup all WebSocket connections for user]
       ↓
[Broadcast event to all connected clients]
       ↓
[Client B, C, D update UI instantly]
```

### 4.4 Activity Log

```
[Any task operation occurs]
       ↓
[Event published to task.events]
       ↓
[Activity consumer persists to activity_log table]
       ↓
[User queries /api/activity]
       ↓
[Return paginated activity entries]
```

---

## 5. Local Development Setup

### Prerequisites

```bash
# Install Dapr CLI
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash

# Install Minikube (if not already)
winget install Kubernetes.minikube

# Install Helm (if not already)
winget install Helm.Helm
```

### Setup Script (`scripts/local-setup.sh`)

```bash
#!/bin/bash
set -e

echo "Starting Minikube..."
minikube start --driver=docker --memory=8192 --cpus=4

echo "Installing Dapr..."
dapr init -k --wait

echo "Installing Kafka..."
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install kafka bitnami/kafka \
  --set replicaCount=1 \
  --set kraft.enabled=true

echo "Installing Redis..."
helm install redis bitnami/redis \
  --set auth.enabled=false \
  --set master.persistence.enabled=false

echo "Waiting for Kafka to be ready..."
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=kafka --timeout=300s

echo "Applying Dapr components..."
kubectl apply -f infrastructure/dapr/components/

echo "Building and deploying application..."
minikube image load todo-backend:latest
minikube image load todo-frontend:latest
helm upgrade --install todo-backend ./helm/todo-backend-v2
helm upgrade --install todo-frontend ./helm/todo-frontend-v2

echo "Setup complete! Access at:"
echo "  Backend: kubectl port-forward svc/todo-backend 8000:8000"
echo "  Frontend: kubectl port-forward svc/todo-frontend 3000:3000"
```

---

## 6. Testing Strategy

### Contract Tests (Kafka Events)

```python
# tests/contract/test_kafka_events.py
from pydantic import ValidationError
from app.events.schemas import TaskEvent, ReminderDueEvent

def test_task_event_schema():
    event = TaskEvent(
        event_type="created",
        task_id=uuid4(),
        user_id="user_123",
        timestamp=datetime.utcnow(),
        payload={"title": "Test"}
    )
    assert event.event_type == "created"

def test_invalid_event_type_rejected():
    with pytest.raises(ValidationError):
        TaskEvent(event_type="invalid", ...)
```

### Integration Tests (Dapr)

```python
# tests/integration/test_dapr_pubsub.py
import pytest
from testcontainers.kafka import KafkaContainer

@pytest.fixture
def kafka():
    with KafkaContainer() as kafka:
        yield kafka

async def test_publish_subscribe_roundtrip(kafka):
    # Publish event
    await publish_task_event(...)

    # Consume and verify
    event = await consume_next_event("task.events")
    assert event["type"] == "task.created"
```

---

## 7. Security Considerations

### Kafka Authentication (Production)

```yaml
# SASL/SCRAM authentication
metadata:
  - name: authType
    value: "password"
  - name: saslUsername
    secretKeyRef:
      name: kafka-credentials
      key: username
  - name: saslPassword
    secretKeyRef:
      name: kafka-credentials
      key: password
  - name: saslMechanism
    value: "SCRAM-SHA-256"
```

### Dapr mTLS

```yaml
# dapr-config.yaml
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: dapr-config
spec:
  mtls:
    enabled: true
    workloadCertTTL: "24h"
    allowedClockSkew: "15m"
```

### Secret Management

- **Local**: Kubernetes secrets mounted as environment variables
- **Cloud**: Azure Key Vault / GCP Secret Manager / OCI Vault via Dapr secretstores

---

## 8. Performance Benchmarks

### Target Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| API Latency (p95) | <500ms | Prometheus histogram |
| Kafka Producer Latency | <50ms | Client metrics |
| Kafka Consumer Lag | <1000 msgs | Consumer group metrics |
| Reminder Delivery | <60s from scheduled | End-to-end test |
| WebSocket Broadcast | <2s | Client-side measurement |

### Load Testing

```bash
# Using k6 for API load testing
k6 run --vus 100 --duration 5m scripts/load-test.js

# Kafka load testing
kafka-producer-perf-test.sh \
  --topic task.events \
  --num-records 100000 \
  --record-size 1000 \
  --throughput 1000 \
  --producer-props bootstrap.servers=localhost:9092
```

---

## 9. References

- [Dapr Documentation](https://docs.dapr.io/)
- [Dapr Python SDK](https://github.com/dapr/python-sdk)
- [Bitnami Kafka Helm Chart](https://github.com/bitnami/charts/tree/main/bitnami/kafka)
- [aiokafka Documentation](https://aiokafka.readthedocs.io/)
- [CloudEvents Specification](https://cloudevents.io/)
- [Azure Event Hubs for Kafka](https://docs.microsoft.com/en-us/azure/event-hubs/event-hubs-for-kafka-ecosystem-overview)
