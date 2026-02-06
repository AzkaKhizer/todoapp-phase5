#!/bin/bash
# Local Development Setup Script
# Sets up Minikube with Dapr, Kafka (Redpanda), and Redis
#
# Prerequisites:
# - Docker Desktop running
# - minikube installed
# - helm installed
# - dapr CLI installed
#
# Usage: ./scripts/local-setup.sh [--skip-minikube] [--skip-dapr] [--skip-kafka] [--skip-redis]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Parse arguments
SKIP_MINIKUBE=false
SKIP_DAPR=false
SKIP_KAFKA=false
SKIP_REDIS=false

for arg in "$@"; do
  case $arg in
    --skip-minikube) SKIP_MINIKUBE=true ;;
    --skip-dapr) SKIP_DAPR=true ;;
    --skip-kafka) SKIP_KAFKA=true ;;
    --skip-redis) SKIP_REDIS=true ;;
  esac
done

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Todo App Local Development Setup${NC}"
echo -e "${GREEN}========================================${NC}"

# Step 1: Start Minikube
if [ "$SKIP_MINIKUBE" = false ]; then
  echo -e "\n${YELLOW}Step 1: Starting Minikube...${NC}"
  if minikube status | grep -q "Running"; then
    echo "Minikube is already running"
  else
    minikube start --driver=docker --cpus=4 --memory=8192 --disk-size=30g
  fi

  # Enable required addons
  minikube addons enable ingress
  minikube addons enable metrics-server
else
  echo -e "\n${YELLOW}Skipping Minikube setup${NC}"
fi

# Step 2: Install Dapr
if [ "$SKIP_DAPR" = false ]; then
  echo -e "\n${YELLOW}Step 2: Installing Dapr...${NC}"

  # Check if Dapr is already installed
  if kubectl get namespace dapr-system &> /dev/null; then
    echo "Dapr is already installed"
  else
    # Initialize Dapr on Kubernetes
    dapr init -k --wait

    # Verify Dapr installation
    dapr status -k
  fi

  # Apply Dapr configuration
  echo "Applying Dapr configuration..."
  kubectl apply -f infrastructure/dapr/config.yaml
else
  echo -e "\n${YELLOW}Skipping Dapr setup${NC}"
fi

# Step 3: Install Kafka (using Redpanda - lightweight Kafka-compatible)
if [ "$SKIP_KAFKA" = false ]; then
  echo -e "\n${YELLOW}Step 3: Installing Kafka (Redpanda)...${NC}"

  # Add Redpanda Helm repo
  helm repo add redpanda https://charts.redpanda.com
  helm repo update

  # Install Redpanda (Kafka-compatible)
  if helm status redpanda &> /dev/null; then
    echo "Redpanda is already installed"
  else
    helm install redpanda redpanda/redpanda \
      --namespace default \
      --set statefulset.replicas=1 \
      --set resources.cpu.cores=1 \
      --set resources.memory.container.max=2Gi \
      --set storage.persistentVolume.size=10Gi \
      --set external.enabled=false \
      --set auth.sasl.enabled=false \
      --set tls.enabled=false \
      --wait
  fi

  # Wait for Redpanda to be ready
  echo "Waiting for Kafka to be ready..."
  kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=redpanda --timeout=300s

  # Create Kafka service alias for Dapr component compatibility
  kubectl apply -f - <<EOF
apiVersion: v1
kind: Service
metadata:
  name: kafka
  namespace: default
spec:
  type: ExternalName
  externalName: redpanda.default.svc.cluster.local
  ports:
    - port: 9092
      targetPort: 9092
EOF

else
  echo -e "\n${YELLOW}Skipping Kafka setup${NC}"
fi

# Step 4: Install Redis
if [ "$SKIP_REDIS" = false ]; then
  echo -e "\n${YELLOW}Step 4: Installing Redis...${NC}"

  # Add Bitnami Helm repo
  helm repo add bitnami https://charts.bitnami.com/bitnami
  helm repo update

  # Install Redis
  if helm status redis &> /dev/null; then
    echo "Redis is already installed"
  else
    helm install redis bitnami/redis \
      --namespace default \
      --set architecture=standalone \
      --set auth.enabled=false \
      --set master.persistence.size=1Gi \
      --wait
  fi

  # Wait for Redis to be ready
  echo "Waiting for Redis to be ready..."
  kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=redis --timeout=120s
else
  echo -e "\n${YELLOW}Skipping Redis setup${NC}"
fi

# Step 5: Apply Dapr components
echo -e "\n${YELLOW}Step 5: Applying Dapr components...${NC}"
kubectl apply -f infrastructure/dapr/components/

# Step 6: Verify installation
echo -e "\n${YELLOW}Step 6: Verifying installation...${NC}"

echo -e "\n${GREEN}Dapr Status:${NC}"
dapr status -k

echo -e "\n${GREEN}Kafka/Redpanda Status:${NC}"
kubectl get pods -l app.kubernetes.io/name=redpanda

echo -e "\n${GREEN}Redis Status:${NC}"
kubectl get pods -l app.kubernetes.io/name=redis

echo -e "\n${GREEN}Dapr Components:${NC}"
kubectl get components

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "\nNext steps:"
echo -e "1. Deploy the application: helm install todo-backend infrastructure/helm/todo-backend-v2/"
echo -e "2. Port-forward to access services:"
echo -e "   kubectl port-forward svc/todo-backend 8000:8000"
echo -e "   kubectl port-forward svc/todo-frontend 3000:3000"
echo -e "3. Run validation: ./scripts/validate-deployment.sh"
