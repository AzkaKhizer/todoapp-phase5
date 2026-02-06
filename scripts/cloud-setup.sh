#!/bin/bash
# =============================================================================
# Azure Cloud Infrastructure Setup Script
# =============================================================================
# This script sets up the Azure infrastructure for the Todo application.
#
# Prerequisites:
# - Azure CLI installed and authenticated
# - Terraform installed
# - kubectl installed
# - Helm installed
#
# Usage:
#   ./scripts/cloud-setup.sh [environment]
#
# Example:
#   ./scripts/cloud-setup.sh dev
#   ./scripts/cloud-setup.sh prod
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT="${1:-dev}"
PROJECT_NAME="todoapp"
LOCATION="eastus"
TERRAFORM_DIR="infrastructure/terraform/azure"

echo -e "${GREEN}=============================================${NC}"
echo -e "${GREEN}  Todo App - Azure Cloud Setup${NC}"
echo -e "${GREEN}  Environment: ${ENVIRONMENT}${NC}"
echo -e "${GREEN}=============================================${NC}"

# =============================================================================
# Step 1: Verify Prerequisites
# =============================================================================

echo -e "\n${YELLOW}Step 1: Verifying prerequisites...${NC}"

command -v az >/dev/null 2>&1 || { echo -e "${RED}Azure CLI is required but not installed.${NC}" >&2; exit 1; }
command -v terraform >/dev/null 2>&1 || { echo -e "${RED}Terraform is required but not installed.${NC}" >&2; exit 1; }
command -v kubectl >/dev/null 2>&1 || { echo -e "${RED}kubectl is required but not installed.${NC}" >&2; exit 1; }
command -v helm >/dev/null 2>&1 || { echo -e "${RED}Helm is required but not installed.${NC}" >&2; exit 1; }

# Check Azure CLI login
az account show >/dev/null 2>&1 || { echo -e "${RED}Not logged in to Azure. Run 'az login' first.${NC}" >&2; exit 1; }

SUBSCRIPTION_ID=$(az account show --query id -o tsv)
TENANT_ID=$(az account show --query tenantId -o tsv)

echo -e "${GREEN}Prerequisites verified.${NC}"
echo "  Subscription: $SUBSCRIPTION_ID"
echo "  Tenant: $TENANT_ID"

# =============================================================================
# Step 2: Check for Required Environment Variables
# =============================================================================

echo -e "\n${YELLOW}Step 2: Checking environment variables...${NC}"

if [ -z "$TF_VAR_postgres_admin_password" ]; then
    echo -e "${RED}TF_VAR_postgres_admin_password is not set.${NC}"
    echo "Please set it: export TF_VAR_postgres_admin_password='your-secure-password'"
    exit 1
fi

if [ -z "$TF_VAR_better_auth_secret" ]; then
    echo -e "${RED}TF_VAR_better_auth_secret is not set.${NC}"
    echo "Please set it: export TF_VAR_better_auth_secret='your-jwt-secret'"
    exit 1
fi

echo -e "${GREEN}Environment variables verified.${NC}"

# =============================================================================
# Step 3: Initialize Terraform
# =============================================================================

echo -e "\n${YELLOW}Step 3: Initializing Terraform...${NC}"

cd "$TERRAFORM_DIR"

terraform init -upgrade

echo -e "${GREEN}Terraform initialized.${NC}"

# =============================================================================
# Step 4: Validate Terraform Configuration
# =============================================================================

echo -e "\n${YELLOW}Step 4: Validating Terraform configuration...${NC}"

terraform validate

echo -e "${GREEN}Terraform configuration is valid.${NC}"

# =============================================================================
# Step 5: Plan Infrastructure Changes
# =============================================================================

echo -e "\n${YELLOW}Step 5: Planning infrastructure changes...${NC}"

terraform plan \
    -var="environment=${ENVIRONMENT}" \
    -var="project_name=${PROJECT_NAME}" \
    -var="location=${LOCATION}" \
    -out=tfplan

echo -e "${GREEN}Terraform plan created.${NC}"

# =============================================================================
# Step 6: Apply Infrastructure Changes
# =============================================================================

echo -e "\n${YELLOW}Step 6: Applying infrastructure changes...${NC}"
echo "This will create/modify Azure resources. Press Ctrl+C to cancel."
read -p "Press Enter to continue..."

terraform apply tfplan

echo -e "${GREEN}Infrastructure deployed successfully.${NC}"

# =============================================================================
# Step 7: Configure kubectl
# =============================================================================

echo -e "\n${YELLOW}Step 7: Configuring kubectl...${NC}"

RESOURCE_GROUP=$(terraform output -raw resource_group_name)
AKS_NAME=$(terraform output -raw aks_cluster_name)

az aks get-credentials \
    --resource-group "$RESOURCE_GROUP" \
    --name "$AKS_NAME" \
    --overwrite-existing

kubectl get nodes

echo -e "${GREEN}kubectl configured for AKS cluster.${NC}"

# =============================================================================
# Step 8: Configure ACR Authentication
# =============================================================================

echo -e "\n${YELLOW}Step 8: Configuring ACR authentication...${NC}"

ACR_NAME=$(terraform output -raw acr_name)

az acr login --name "$ACR_NAME"

echo -e "${GREEN}ACR authentication configured.${NC}"

# =============================================================================
# Step 9: Verify Dapr Installation
# =============================================================================

echo -e "\n${YELLOW}Step 9: Verifying Dapr installation...${NC}"

kubectl get pods -n dapr-system

echo -e "${GREEN}Dapr is running.${NC}"

# =============================================================================
# Step 10: Deploy Dapr Components
# =============================================================================

echo -e "\n${YELLOW}Step 10: Deploying Dapr components...${NC}"

# Get values from Terraform outputs
KEYVAULT_NAME=$(terraform output -raw keyvault_name)
REDIS_HOST=$(terraform output -raw redis_hostname)
AZURE_TENANT_ID="$TENANT_ID"

# Return to project root
cd ../../..

# Apply Dapr components with substitutions
cat infrastructure/dapr/components/pubsub-eventhubs.yaml | kubectl apply -f -

cat infrastructure/dapr/components/statestore-azure-redis.yaml | \
    sed "s/\${REDIS_HOST}/${REDIS_HOST}/" | \
    kubectl apply -f -

echo -e "${GREEN}Dapr components deployed.${NC}"

# =============================================================================
# Summary
# =============================================================================

echo -e "\n${GREEN}=============================================${NC}"
echo -e "${GREEN}  Cloud Setup Complete!${NC}"
echo -e "${GREEN}=============================================${NC}"
echo ""
echo "Resources created:"
echo "  - Resource Group: $RESOURCE_GROUP"
echo "  - AKS Cluster: $AKS_NAME"
echo "  - Container Registry: $ACR_NAME"
echo "  - Key Vault: $KEYVAULT_NAME"
echo ""
echo "Next steps:"
echo "  1. Build and push Docker images:"
echo "     ./scripts/deploy-cloud.sh build"
echo ""
echo "  2. Deploy the application:"
echo "     ./scripts/deploy-cloud.sh deploy"
echo ""
echo "  3. Access the application:"
echo "     kubectl get ingress -n todo-app"
echo ""
