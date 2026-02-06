# =============================================================================
# Azure Infrastructure for Todo Application
# =============================================================================
# This Terraform configuration deploys:
# - Azure Kubernetes Service (AKS) cluster with Dapr
# - Azure Event Hubs (Kafka-compatible) for event streaming
# - Azure Cache for Redis for state management
# - Azure Container Registry for container images
# - Azure Key Vault for secrets management
# - Azure PostgreSQL Flexible Server for database
# =============================================================================

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.85"
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = "~> 2.47"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.12"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.25"
    }
  }

  # Backend configuration for state storage
  # Uncomment and configure for production use
  # backend "azurerm" {
  #   resource_group_name  = "tfstate-rg"
  #   storage_account_name = "tfstatetodoapp"
  #   container_name       = "tfstate"
  #   key                  = "todo-app.tfstate"
  # }
}

# =============================================================================
# Provider Configuration
# =============================================================================

provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy    = true
      recover_soft_deleted_key_vaults = true
    }
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }

  # Use environment variables for authentication:
  # ARM_CLIENT_ID, ARM_CLIENT_SECRET, ARM_SUBSCRIPTION_ID, ARM_TENANT_ID
}

provider "azuread" {
  # Uses same credentials as azurerm
}

provider "helm" {
  kubernetes {
    host                   = azurerm_kubernetes_cluster.aks.kube_config[0].host
    client_certificate     = base64decode(azurerm_kubernetes_cluster.aks.kube_config[0].client_certificate)
    client_key             = base64decode(azurerm_kubernetes_cluster.aks.kube_config[0].client_key)
    cluster_ca_certificate = base64decode(azurerm_kubernetes_cluster.aks.kube_config[0].cluster_ca_certificate)
  }
}

provider "kubernetes" {
  host                   = azurerm_kubernetes_cluster.aks.kube_config[0].host
  client_certificate     = base64decode(azurerm_kubernetes_cluster.aks.kube_config[0].client_certificate)
  client_key             = base64decode(azurerm_kubernetes_cluster.aks.kube_config[0].client_key)
  cluster_ca_certificate = base64decode(azurerm_kubernetes_cluster.aks.kube_config[0].cluster_ca_certificate)
}

# =============================================================================
# Data Sources
# =============================================================================

data "azurerm_client_config" "current" {}

data "azuread_client_config" "current" {}

# =============================================================================
# Random Suffix for Unique Names
# =============================================================================

resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}

# =============================================================================
# Resource Group
# =============================================================================

resource "azurerm_resource_group" "main" {
  name     = "${var.project_name}-${var.environment}-rg"
  location = var.location

  tags = local.common_tags
}

# =============================================================================
# Local Values
# =============================================================================

locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
    Repository  = "todoapp-phase3"
  }

  # Resource naming
  aks_name           = "${var.project_name}-${var.environment}-aks"
  acr_name           = "${var.project_name}${var.environment}acr${random_string.suffix.result}"
  eventhub_namespace = "${var.project_name}-${var.environment}-eh"
  redis_name         = "${var.project_name}-${var.environment}-redis"
  keyvault_name      = "${var.project_name}-${var.environment}-kv-${random_string.suffix.result}"
  postgres_name      = "${var.project_name}-${var.environment}-pg"
}

# =============================================================================
# Key Vault (for secrets management)
# =============================================================================

resource "azurerm_key_vault" "main" {
  name                        = local.keyvault_name
  location                    = azurerm_resource_group.main.location
  resource_group_name         = azurerm_resource_group.main.name
  tenant_id                   = data.azurerm_client_config.current.tenant_id
  sku_name                    = "standard"
  soft_delete_retention_days  = 7
  purge_protection_enabled    = false
  enabled_for_disk_encryption = true

  # Access policy for Terraform service principal
  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = data.azurerm_client_config.current.object_id

    secret_permissions = [
      "Get", "List", "Set", "Delete", "Purge", "Recover"
    ]
  }

  tags = local.common_tags
}

# =============================================================================
# Store secrets in Key Vault
# =============================================================================

resource "azurerm_key_vault_secret" "postgres_password" {
  name         = "postgres-password"
  value        = var.postgres_admin_password
  key_vault_id = azurerm_key_vault.main.id
}

resource "azurerm_key_vault_secret" "better_auth_secret" {
  name         = "better-auth-secret"
  value        = var.better_auth_secret
  key_vault_id = azurerm_key_vault.main.id
}

resource "azurerm_key_vault_secret" "redis_password" {
  name         = "redis-password"
  value        = azurerm_redis_cache.main.primary_access_key
  key_vault_id = azurerm_key_vault.main.id

  depends_on = [azurerm_redis_cache.main]
}

resource "azurerm_key_vault_secret" "eventhub_connection_string" {
  name         = "eventhub-connection-string"
  value        = azurerm_eventhub_namespace.main.default_primary_connection_string
  key_vault_id = azurerm_key_vault.main.id

  depends_on = [azurerm_eventhub_namespace.main]
}

# =============================================================================
# Dapr Installation on AKS
# =============================================================================

resource "helm_release" "dapr" {
  name             = "dapr"
  repository       = "https://dapr.github.io/helm-charts"
  chart            = "dapr"
  version          = var.dapr_version
  namespace        = "dapr-system"
  create_namespace = true

  set {
    name  = "global.ha.enabled"
    value = var.environment == "prod" ? "true" : "false"
  }

  set {
    name  = "global.logAsJson"
    value = "true"
  }

  depends_on = [azurerm_kubernetes_cluster.aks]
}

# =============================================================================
# Kubernetes Namespace for Application
# =============================================================================

resource "kubernetes_namespace" "app" {
  metadata {
    name = var.app_namespace

    labels = {
      "app.kubernetes.io/managed-by" = "terraform"
      "environment"                  = var.environment
    }
  }

  depends_on = [azurerm_kubernetes_cluster.aks]
}

# =============================================================================
# Kubernetes Secrets for Application
# =============================================================================

resource "kubernetes_secret" "app_secrets" {
  metadata {
    name      = "todo-app-secrets"
    namespace = kubernetes_namespace.app.metadata[0].name
  }

  data = {
    DATABASE_URL        = "postgresql://${var.postgres_admin_username}:${var.postgres_admin_password}@${azurerm_postgresql_flexible_server.main.fqdn}:5432/${var.postgres_database_name}?sslmode=require"
    BETTER_AUTH_SECRET  = var.better_auth_secret
    REDIS_URL           = "rediss://:${azurerm_redis_cache.main.primary_access_key}@${azurerm_redis_cache.main.hostname}:${azurerm_redis_cache.main.ssl_port}"
    EVENTHUB_CONNECTION = azurerm_eventhub_namespace.main.default_primary_connection_string
  }

  depends_on = [
    kubernetes_namespace.app,
    azurerm_postgresql_flexible_server.main,
    azurerm_redis_cache.main,
    azurerm_eventhub_namespace.main
  ]
}
