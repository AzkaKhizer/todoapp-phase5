# Quickstart: Advanced Cloud Deployment

**Feature**: 010-advanced-cloud-deployment
**Date**: 2026-02-03

## Prerequisites

| Tool | Version | Install Command |
|------|---------|-----------------|
| Docker Desktop | Latest | [docker.com/products/docker-desktop](https://docker.com/products/docker-desktop) |
| Minikube | 1.38+ | `winget install Kubernetes.minikube` |
| kubectl | 1.29+ | Included with Docker Desktop |
| Helm | 3.14+ | `winget install Helm.Helm` |
| Dapr CLI | 1.12+ | See below |

### Install Dapr CLI

**Windows (PowerShell)**:
```powershell
powershell -Command "iwr -useb https://raw.githubusercontent.com/dapr/cli/master/install/install.ps1 | iex"
```

**Linux/macOS**:
```bash
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash
```

**Verify**:
```bash
dapr --version
```

---

## Part 1: Local Development (Minikube)

### Step 1: Start Minikube with Resources

```bash
# Allocate sufficient resources for Kafka + Dapr
minikube start --driver=docker --memory=8192 --cpus=4
```

### Step 2: Initialize Dapr on Kubernetes

```bash
# Initialize Dapr in the cluster
dapr init -k --wait

# Verify Dapr is running
dapr status -k
```

Expected output:
```
NAME                   NAMESPACE    HEALTHY  STATUS   VERSION  AGE
dapr-dashboard         dapr-system  True     Running  0.12.0   1m
dapr-sidecar-injector  dapr-system  True     Running  1.12.0   1m
dapr-operator          dapr-system  True     Running  1.12.0   1m
dapr-placement-server  dapr-system  True     Running  1.12.0   1m
dapr-sentry            dapr-system  True     Running  1.12.0   1m
```

### Step 3: Deploy Kafka

```bash
# Add Bitnami repo
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Install Kafka with KRaft mode (no Zookeeper)
helm install kafka bitnami/kafka \
  --set replicaCount=1 \
  --set controller.replicaCount=1 \
  --set kraft.enabled=true \
  --set listeners.client.protocol=PLAINTEXT \
  --set resources.requests.memory=512Mi \
  --set resources.requests.cpu=250m

# Wait for Kafka to be ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=kafka --timeout=300s
```

### Step 4: Deploy Redis (Dapr State Store)

```bash
# Install Redis
helm install redis bitnami/redis \
  --set auth.enabled=false \
  --set master.persistence.enabled=false \
  --set replica.replicaCount=0

# Wait for Redis
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=redis --timeout=120s
```

### Step 5: Configure Dapr Components

Create the component configuration files:

**pubsub-kafka.yaml**:
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
      value: "kafka:9092"
    - name: consumerGroup
      value: "todo-backend-group"
    - name: authRequired
      value: "false"
```

**statestore-redis.yaml**:
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
      value: ""
```

**binding-cron.yaml**:
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
      value: "* * * * *"
    - name: direction
      value: "input"
```

Apply components:
```bash
kubectl apply -f infrastructure/dapr/components/
```

### Step 6: Build and Deploy Application

```bash
# Build Docker images
docker build -t todo-backend:v2 ./backend
docker build -t todo-frontend:v2 ./frontend

# Load into Minikube
minikube image load todo-backend:v2
minikube image load todo-frontend:v2

# Deploy with Helm
helm upgrade --install todo-backend ./helm/todo-backend-v2 \
  --set secrets.DATABASE_URL="your-database-url" \
  --set secrets.BETTER_AUTH_SECRET="your-auth-secret"

helm upgrade --install todo-frontend ./helm/todo-frontend-v2 \
  --set secrets.DATABASE_URL="your-database-url" \
  --set secrets.BETTER_AUTH_SECRET="your-auth-secret"
```

### Step 7: Verify Deployment

```bash
# Check pods (should show Dapr sidecars)
kubectl get pods

# Expected: Each pod has 2/2 containers (app + dapr sidecar)
# NAME                            READY   STATUS
# todo-backend-xxx                2/2     Running
# todo-frontend-xxx               2/2     Running
```

### Step 8: Access the Application

```bash
# Port forward services
kubectl port-forward svc/todo-backend 8000:8000 &
kubectl port-forward svc/todo-frontend 3000:3000 &

# Access Dapr dashboard
dapr dashboard -k
```

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/docs
- **Dapr Dashboard**: http://localhost:8080

---

## Part 2: Validation Checklist

### Dapr Building Blocks

| Component | Test | Expected Result |
|-----------|------|-----------------|
| Pub/Sub | Create a task | Event appears in Kafka topic |
| State Store | Save/retrieve state | Data persists in Redis |
| Bindings | Wait 1 minute | Cron trigger fires |
| Secrets | App starts | DB credentials loaded |
| Service Invocation | Backend calls service | mTLS communication works |

### Kafka Topics

```bash
# List topics
kubectl exec -it kafka-0 -- kafka-topics.sh --list --bootstrap-server localhost:9092

# Expected topics:
# - task.events
# - reminder.due
# - notification.send
# - sync.events
# - activity.log
```

### End-to-End Flow

1. **Create task with reminder**:
   ```bash
   curl -X POST http://localhost:8000/api/tasks \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Test task",
       "due_date": "2026-02-03T15:00:00Z",
       "reminder_offset_minutes": 5
     }'
   ```

2. **Verify Kafka event**:
   ```bash
   kubectl exec -it kafka-0 -- kafka-console-consumer.sh \
     --bootstrap-server localhost:9092 \
     --topic task.events \
     --from-beginning \
     --max-messages 1
   ```

3. **Check reminder scheduled**:
   ```bash
   curl http://localhost:8000/api/tasks/<id>/reminder \
     -H "Authorization: Bearer <token>"
   ```

---

## Part 3: Cloud Deployment (Azure AKS)

### Step 1: Provision Infrastructure

```bash
# Login to Azure
az login

# Create resource group
az group create --name todo-rg --location eastus

# Create AKS cluster
az aks create \
  --resource-group todo-rg \
  --name todo-aks \
  --node-count 3 \
  --node-vm-size Standard_DS2_v2 \
  --enable-managed-identity \
  --generate-ssh-keys

# Get credentials
az aks get-credentials --resource-group todo-rg --name todo-aks
```

### Step 2: Deploy Dapr on AKS

```bash
dapr init -k --wait
```

### Step 3: Configure Azure Event Hubs (Kafka)

```bash
# Create Event Hubs namespace
az eventhubs namespace create \
  --resource-group todo-rg \
  --name todo-eventhubs \
  --sku Standard \
  --enable-kafka true

# Get connection string
az eventhubs namespace authorization-rule keys list \
  --resource-group todo-rg \
  --namespace-name todo-eventhubs \
  --name RootManageSharedAccessKey \
  --query primaryConnectionString -o tsv
```

Update Dapr component for Event Hubs:
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
      value: "todo-eventhubs.servicebus.windows.net:9093"
    - name: authType
      value: "password"
    - name: saslUsername
      value: "$ConnectionString"
    - name: saslPassword
      secretKeyRef:
        name: eventhubs-secret
        key: connection-string
    - name: saslMechanism
      value: "PLAIN"
    - name: tls
      value: "true"
```

### Step 4: Deploy Application

```bash
# Push images to ACR
az acr create --resource-group todo-rg --name todoacr --sku Basic
az acr login --name todoacr

docker tag todo-backend:v2 todoacr.azurecr.io/todo-backend:v2
docker tag todo-frontend:v2 todoacr.azurecr.io/todo-frontend:v2
docker push todoacr.azurecr.io/todo-backend:v2
docker push todoacr.azurecr.io/todo-frontend:v2

# Deploy with Helm
helm upgrade --install todo-backend ./helm/todo-backend-v2 \
  --set image.repository=todoacr.azurecr.io/todo-backend \
  --set image.tag=v2 \
  --set secrets.DATABASE_URL="your-neon-url"
```

### Step 5: Configure Monitoring

```bash
# Install Prometheus stack
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack

# Access Grafana
kubectl port-forward svc/prometheus-grafana 3001:80
```

---

## Troubleshooting

### Dapr Sidecar Not Injecting

```bash
# Check namespace has Dapr annotation
kubectl get namespace default -o yaml | grep dapr

# If missing, enable injection
kubectl label namespace default dapr.io/enabled=true
```

### Kafka Connection Issues

```bash
# Check Kafka pods
kubectl logs kafka-0

# Test connectivity
kubectl run kafka-test --rm -it --image=bitnami/kafka -- \
  kafka-topics.sh --list --bootstrap-server kafka:9092
```

### Reminder Not Firing

```bash
# Check cron binding logs
kubectl logs -l app=todo-backend -c daprd | grep "reminder-scheduler"

# Verify binding is registered
dapr components -k | grep reminder
```

### WebSocket Connection Failed

```bash
# Check backend logs
kubectl logs -l app=todo-backend -c todo-backend | grep websocket

# Verify CORS settings
curl -I http://localhost:8000/api/ws/tasks
```

---

## Quick Reference

| Command | Description |
|---------|-------------|
| `dapr status -k` | Check Dapr status |
| `dapr components -k` | List Dapr components |
| `dapr logs -a todo-backend -k` | View Dapr sidecar logs |
| `dapr dashboard -k` | Open Dapr dashboard |
| `kubectl get pods` | List all pods |
| `kubectl logs <pod> -c daprd` | View Dapr sidecar logs |
| `minikube tunnel` | Enable LoadBalancer access |
