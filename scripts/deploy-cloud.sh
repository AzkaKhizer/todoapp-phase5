#!/bin/bash
# =============================================================================
# Azure Cloud Deployment Script
# =============================================================================
# This script builds and deploys the Todo application to Azure AKS.
#
# Prerequisites:
# - Azure infrastructure created (run cloud-setup.sh first)
# - kubectl configured for AKS cluster
# - Docker installed and running
#
# Usage:
#   ./scripts/deploy-cloud.sh [command]
#
# Commands:
#   build    - Build and push Docker images to ACR
#   deploy   - Deploy application to AKS
#   all      - Build and deploy (default)
#   rollback - Rollback to previous deployment
#   status   - Show deployment status
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMMAND="${1:-all}"
ENVIRONMENT="${ENVIRONMENT:-dev}"
PROJECT_NAME="todoapp"
NAMESPACE="todo-app"
TERRAFORM_DIR="infrastructure/terraform/azure"

# Get Terraform outputs
get_terraform_output() {
    cd "$TERRAFORM_DIR" && terraform output -raw "$1" 2>/dev/null
    cd - >/dev/null
}

echo -e "${GREEN}=============================================${NC}"
echo -e "${GREEN}  Todo App - Cloud Deployment${NC}"
echo -e "${GREEN}  Command: ${COMMAND}${NC}"
echo -e "${GREEN}=============================================${NC}"

# =============================================================================
# Get Configuration from Terraform
# =============================================================================

echo -e "\n${YELLOW}Loading configuration from Terraform...${NC}"

ACR_NAME=$(get_terraform_output acr_name)
ACR_LOGIN_SERVER=$(get_terraform_output acr_login_server)
AKS_NAME=$(get_terraform_output aks_cluster_name)
RESOURCE_GROUP=$(get_terraform_output resource_group_name)

if [ -z "$ACR_NAME" ]; then
    echo -e "${RED}Could not get ACR name from Terraform. Run cloud-setup.sh first.${NC}"
    exit 1
fi

echo "  ACR: $ACR_LOGIN_SERVER"
echo "  AKS: $AKS_NAME"

# =============================================================================
# Build Function
# =============================================================================

build_images() {
    echo -e "\n${YELLOW}Building Docker images...${NC}"

    # Login to ACR
    echo "Logging in to ACR..."
    az acr login --name "$ACR_NAME"

    # Get the commit SHA for tagging
    GIT_SHA=$(git rev-parse --short HEAD 2>/dev/null || echo "latest")
    TIMESTAMP=$(date +%Y%m%d%H%M%S)
    IMAGE_TAG="${GIT_SHA}-${TIMESTAMP}"

    echo "Image tag: $IMAGE_TAG"

    # Build and push backend
    echo -e "\n${BLUE}Building backend image...${NC}"
    docker build -t "${ACR_LOGIN_SERVER}/todo-backend:${IMAGE_TAG}" \
                 -t "${ACR_LOGIN_SERVER}/todo-backend:latest" \
                 ./backend

    echo "Pushing backend image..."
    docker push "${ACR_LOGIN_SERVER}/todo-backend:${IMAGE_TAG}"
    docker push "${ACR_LOGIN_SERVER}/todo-backend:latest"

    # Build and push frontend
    echo -e "\n${BLUE}Building frontend image...${NC}"
    docker build -t "${ACR_LOGIN_SERVER}/todo-frontend:${IMAGE_TAG}" \
                 -t "${ACR_LOGIN_SERVER}/todo-frontend:latest" \
                 --build-arg NEXT_PUBLIC_API_URL="https://api.todoapp.example.com" \
                 ./frontend

    echo "Pushing frontend image..."
    docker push "${ACR_LOGIN_SERVER}/todo-frontend:${IMAGE_TAG}"
    docker push "${ACR_LOGIN_SERVER}/todo-frontend:latest"

    echo -e "${GREEN}Images built and pushed successfully.${NC}"
    echo "  Backend: ${ACR_LOGIN_SERVER}/todo-backend:${IMAGE_TAG}"
    echo "  Frontend: ${ACR_LOGIN_SERVER}/todo-frontend:${IMAGE_TAG}"

    # Save the image tag for deployment
    echo "$IMAGE_TAG" > .image-tag
}

# =============================================================================
# Deploy Function
# =============================================================================

deploy_app() {
    echo -e "\n${YELLOW}Deploying application to AKS...${NC}"

    # Get the image tag
    if [ -f .image-tag ]; then
        IMAGE_TAG=$(cat .image-tag)
    else
        IMAGE_TAG="latest"
    fi

    echo "Using image tag: $IMAGE_TAG"

    # Ensure namespace exists
    kubectl get namespace "$NAMESPACE" >/dev/null 2>&1 || \
        kubectl create namespace "$NAMESPACE"

    # Deploy backend
    echo -e "\n${BLUE}Deploying backend...${NC}"
    helm upgrade --install todo-backend \
        infrastructure/helm/todo-backend-v2 \
        --namespace "$NAMESPACE" \
        --set image.repository="${ACR_LOGIN_SERVER}/todo-backend" \
        --set image.tag="${IMAGE_TAG}" \
        --set dapr.enabled=true \
        --set dapr.appId="todo-backend" \
        --set dapr.appPort=8000 \
        --set env.DATABASE_URL="$(get_terraform_output postgres_connection_string 2>/dev/null || echo 'from-secret')" \
        --wait \
        --timeout 5m

    # Deploy frontend
    echo -e "\n${BLUE}Deploying frontend...${NC}"
    helm upgrade --install todo-frontend \
        infrastructure/helm/todo-frontend-v2 \
        --namespace "$NAMESPACE" \
        --set image.repository="${ACR_LOGIN_SERVER}/todo-frontend" \
        --set image.tag="${IMAGE_TAG}" \
        --wait \
        --timeout 5m

    echo -e "${GREEN}Deployment complete.${NC}"
}

# =============================================================================
# Rollback Function
# =============================================================================

rollback_app() {
    echo -e "\n${YELLOW}Rolling back deployment...${NC}"

    # Rollback backend
    echo "Rolling back backend..."
    helm rollback todo-backend -n "$NAMESPACE"

    # Rollback frontend
    echo "Rolling back frontend..."
    helm rollback todo-frontend -n "$NAMESPACE"

    echo -e "${GREEN}Rollback complete.${NC}"
}

# =============================================================================
# Status Function
# =============================================================================

show_status() {
    echo -e "\n${YELLOW}Deployment Status${NC}"
    echo "============================================="

    echo -e "\n${BLUE}Helm Releases:${NC}"
    helm list -n "$NAMESPACE"

    echo -e "\n${BLUE}Pods:${NC}"
    kubectl get pods -n "$NAMESPACE"

    echo -e "\n${BLUE}Services:${NC}"
    kubectl get svc -n "$NAMESPACE"

    echo -e "\n${BLUE}Ingress:${NC}"
    kubectl get ingress -n "$NAMESPACE"

    echo -e "\n${BLUE}Dapr Components:${NC}"
    kubectl get components.dapr.io -n "$NAMESPACE"

    echo -e "\n${BLUE}Recent Events:${NC}"
    kubectl get events -n "$NAMESPACE" --sort-by='.lastTimestamp' | tail -10
}

# =============================================================================
# Main
# =============================================================================

case "$COMMAND" in
    build)
        build_images
        ;;
    deploy)
        deploy_app
        ;;
    all)
        build_images
        deploy_app
        ;;
    rollback)
        rollback_app
        ;;
    status)
        show_status
        ;;
    *)
        echo "Usage: $0 {build|deploy|all|rollback|status}"
        exit 1
        ;;
esac

echo -e "\n${GREEN}=============================================${NC}"
echo -e "${GREEN}  Done!${NC}"
echo -e "${GREEN}=============================================${NC}"
