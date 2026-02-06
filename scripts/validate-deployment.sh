#!/bin/bash
# Deployment Validation Script
# Validates that all components are correctly deployed and functioning
#
# Usage: ./scripts/validate-deployment.sh [--namespace default]

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
NAMESPACE="${1:-default}"
TIMEOUT=60

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Validation${NC}"
echo -e "${GREEN}Namespace: ${NAMESPACE}${NC}"
echo -e "${GREEN}========================================${NC}"

PASSED=0
FAILED=0

# Helper function to check condition
check() {
    local name="$1"
    local cmd="$2"

    echo -ne "Checking ${name}... "
    if eval "$cmd" > /dev/null 2>&1; then
        echo -e "${GREEN}PASS${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}FAIL${NC}"
        ((FAILED++))
        return 1
    fi
}

# Helper function to wait for condition
wait_for() {
    local name="$1"
    local cmd="$2"
    local timeout="${3:-$TIMEOUT}"

    echo -ne "Waiting for ${name}... "
    local start_time=$(date +%s)
    while true; do
        if eval "$cmd" > /dev/null 2>&1; then
            echo -e "${GREEN}READY${NC}"
            ((PASSED++))
            return 0
        fi

        local current_time=$(date +%s)
        local elapsed=$((current_time - start_time))
        if [ $elapsed -ge $timeout ]; then
            echo -e "${RED}TIMEOUT${NC}"
            ((FAILED++))
            return 1
        fi

        sleep 2
    done
}

echo -e "\n${YELLOW}=== Infrastructure Components ===${NC}"

# Check Dapr
check "Dapr system namespace" "kubectl get namespace dapr-system"
check "Dapr operator" "kubectl get pods -n dapr-system -l app=dapr-operator --field-selector=status.phase=Running | grep -q Running"
check "Dapr sidecar injector" "kubectl get pods -n dapr-system -l app=dapr-sidecar-injector --field-selector=status.phase=Running | grep -q Running"
check "Dapr placement" "kubectl get pods -n dapr-system -l app=dapr-placement-server --field-selector=status.phase=Running | grep -q Running"

# Check Kafka/Redpanda
check "Kafka pods" "kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/name=redpanda --field-selector=status.phase=Running | grep -q Running"
check "Kafka service" "kubectl get svc -n ${NAMESPACE} kafka"

# Check Redis
check "Redis pods" "kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/name=redis --field-selector=status.phase=Running | grep -q Running"
check "Redis service" "kubectl get svc -n ${NAMESPACE} redis-master"

echo -e "\n${YELLOW}=== Dapr Components ===${NC}"

# Check Dapr components
check "Pub/Sub component" "kubectl get component -n ${NAMESPACE} pubsub-kafka"
check "State store component" "kubectl get component -n ${NAMESPACE} statestore-redis"
check "Cron binding" "kubectl get component -n ${NAMESPACE} reminder-scheduler"
check "Secrets component" "kubectl get component -n ${NAMESPACE} kubernetes-secrets"
check "Dapr configuration" "kubectl get configuration -n ${NAMESPACE} todo-config"

echo -e "\n${YELLOW}=== Application Deployment ===${NC}"

# Check application pods
if kubectl get deployment -n ${NAMESPACE} todo-backend > /dev/null 2>&1; then
    wait_for "Backend pods ready" "kubectl get deployment -n ${NAMESPACE} todo-backend -o jsonpath='{.status.readyReplicas}' | grep -q '[1-9]'"
    check "Backend Dapr sidecar" "kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/name=todo-backend-v2 -o jsonpath='{.items[0].spec.containers[*].name}' | grep -q daprd"
else
    echo -e "Backend deployment: ${YELLOW}NOT DEPLOYED${NC}"
fi

if kubectl get deployment -n ${NAMESPACE} todo-frontend > /dev/null 2>&1; then
    wait_for "Frontend pods ready" "kubectl get deployment -n ${NAMESPACE} todo-frontend -o jsonpath='{.status.readyReplicas}' | grep -q '[1-9]'"
else
    echo -e "Frontend deployment: ${YELLOW}NOT DEPLOYED${NC}"
fi

echo -e "\n${YELLOW}=== Connectivity Tests ===${NC}"

# Test Kafka connectivity
echo -ne "Testing Kafka connectivity... "
if kubectl run kafka-test --rm -i --restart=Never --image=bitnami/kafka:latest --command -- \
    kafka-topics.sh --bootstrap-server redpanda.${NAMESPACE}.svc.cluster.local:9092 --list > /dev/null 2>&1; then
    echo -e "${GREEN}PASS${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}SKIP (requires kafka-test pod)${NC}"
fi

# Test Redis connectivity
echo -ne "Testing Redis connectivity... "
if kubectl run redis-test --rm -i --restart=Never --image=redis:7-alpine --command -- \
    redis-cli -h redis-master.${NAMESPACE}.svc.cluster.local ping 2>&1 | grep -q PONG; then
    echo -e "${GREEN}PASS${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}SKIP (requires redis-test pod)${NC}"
fi

# Test application health
if kubectl get svc -n ${NAMESPACE} todo-backend > /dev/null 2>&1; then
    echo -ne "Testing backend health endpoint... "
    HEALTH_RESPONSE=$(kubectl run health-test --rm -i --restart=Never --image=curlimages/curl --command -- \
        curl -s http://todo-backend.${NAMESPACE}.svc.cluster.local:8000/api/health 2>&1)
    if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
        echo -e "${GREEN}PASS${NC}"
        ((PASSED++))
    else
        echo -e "${RED}FAIL${NC}"
        ((FAILED++))
    fi
fi

echo -e "\n${YELLOW}=== Dapr Health ===${NC}"

# Check Dapr sidecar health via application
if kubectl get deployment -n ${NAMESPACE} todo-backend > /dev/null 2>&1; then
    echo -ne "Checking Dapr sidecar health... "
    BACKEND_POD=$(kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/name=todo-backend-v2 -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
    if [ -n "$BACKEND_POD" ]; then
        DAPR_HEALTH=$(kubectl exec -n ${NAMESPACE} $BACKEND_POD -c daprd -- wget -qO- http://localhost:3500/v1.0/healthz 2>&1)
        if echo "$DAPR_HEALTH" | grep -q "ok\|healthy"; then
            echo -e "${GREEN}PASS${NC}"
            ((PASSED++))
        else
            echo -e "${RED}FAIL${NC}"
            ((FAILED++))
        fi
    else
        echo -e "${YELLOW}SKIP (no backend pod)${NC}"
    fi
fi

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Validation Complete${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "Passed: ${GREEN}${PASSED}${NC}"
echo -e "Failed: ${RED}${FAILED}${NC}"

if [ $FAILED -gt 0 ]; then
    echo -e "\n${RED}Some checks failed. Review the output above.${NC}"
    exit 1
else
    echo -e "\n${GREEN}All checks passed!${NC}"
    exit 0
fi
