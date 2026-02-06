# =============================================================================
# Terraform Variables for Azure Infrastructure
# =============================================================================

# =============================================================================
# General Settings
# =============================================================================

variable "project_name" {
  description = "Name of the project (used in resource naming)"
  type        = string
  default     = "todoapp"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "eastus"
}

variable "app_namespace" {
  description = "Kubernetes namespace for the application"
  type        = string
  default     = "todo-app"
}

# =============================================================================
# AKS Settings
# =============================================================================

variable "kubernetes_version" {
  description = "Kubernetes version for AKS"
  type        = string
  default     = "1.28"
}

variable "aks_system_node_count" {
  description = "Initial number of system nodes"
  type        = number
  default     = 2
}

variable "aks_system_node_min" {
  description = "Minimum number of system nodes"
  type        = number
  default     = 2
}

variable "aks_system_node_max" {
  description = "Maximum number of system nodes"
  type        = number
  default     = 5
}

variable "aks_system_node_size" {
  description = "VM size for system nodes"
  type        = string
  default     = "Standard_DS2_v2"
}

variable "aks_user_node_count" {
  description = "Initial number of user nodes"
  type        = number
  default     = 2
}

variable "aks_user_node_min" {
  description = "Minimum number of user nodes"
  type        = number
  default     = 1
}

variable "aks_user_node_max" {
  description = "Maximum number of user nodes"
  type        = number
  default     = 10
}

variable "aks_user_node_size" {
  description = "VM size for user nodes"
  type        = string
  default     = "Standard_DS2_v2"
}

variable "aks_admin_group_ids" {
  description = "Azure AD group IDs for AKS cluster admins"
  type        = list(string)
  default     = []
}

# =============================================================================
# Dapr Settings
# =============================================================================

variable "dapr_version" {
  description = "Dapr Helm chart version"
  type        = string
  default     = "1.12.0"
}

# =============================================================================
# Event Hubs Settings
# =============================================================================

variable "eventhub_sku" {
  description = "Event Hubs namespace SKU (Basic, Standard, Premium)"
  type        = string
  default     = "Standard"

  validation {
    condition     = contains(["Basic", "Standard", "Premium"], var.eventhub_sku)
    error_message = "Event Hub SKU must be one of: Basic, Standard, Premium."
  }
}

variable "eventhub_capacity" {
  description = "Event Hubs throughput units"
  type        = number
  default     = 1
}

variable "eventhub_max_throughput" {
  description = "Maximum throughput units for auto-inflate"
  type        = number
  default     = 4
}

variable "eventhub_partition_count" {
  description = "Default partition count for Event Hubs"
  type        = number
  default     = 4
}

variable "eventhub_message_retention" {
  description = "Message retention in days"
  type        = number
  default     = 7
}

# =============================================================================
# Redis Settings
# =============================================================================

variable "redis_sku" {
  description = "Redis cache SKU (Basic, Standard, Premium)"
  type        = string
  default     = "Standard"

  validation {
    condition     = contains(["Basic", "Standard", "Premium"], var.redis_sku)
    error_message = "Redis SKU must be one of: Basic, Standard, Premium."
  }
}

variable "redis_family" {
  description = "Redis cache family (C for Basic/Standard, P for Premium)"
  type        = string
  default     = "C"

  validation {
    condition     = contains(["C", "P"], var.redis_family)
    error_message = "Redis family must be C or P."
  }
}

variable "redis_capacity" {
  description = "Redis cache capacity (0-6 for C family, 1-4 for P family)"
  type        = number
  default     = 1
}

# =============================================================================
# ACR Settings
# =============================================================================

variable "acr_sku" {
  description = "Container Registry SKU (Basic, Standard, Premium)"
  type        = string
  default     = "Standard"

  validation {
    condition     = contains(["Basic", "Standard", "Premium"], var.acr_sku)
    error_message = "ACR SKU must be one of: Basic, Standard, Premium."
  }
}

variable "acr_georeplication_locations" {
  description = "List of Azure regions for ACR geo-replication (Premium only)"
  type        = list(string)
  default     = null
}

variable "enable_acr_tasks" {
  description = "Enable ACR Tasks for automated builds"
  type        = bool
  default     = false
}

variable "github_repo" {
  description = "GitHub repository (owner/repo) for ACR Tasks"
  type        = string
  default     = ""
}

variable "github_token" {
  description = "GitHub PAT for ACR Tasks"
  type        = string
  default     = ""
  sensitive   = true
}

# =============================================================================
# PostgreSQL Settings
# =============================================================================

variable "postgres_version" {
  description = "PostgreSQL version"
  type        = string
  default     = "15"
}

variable "postgres_sku" {
  description = "PostgreSQL SKU name"
  type        = string
  default     = "B_Standard_B1ms"
}

variable "postgres_storage_mb" {
  description = "PostgreSQL storage in MB"
  type        = number
  default     = 32768
}

variable "postgres_admin_username" {
  description = "PostgreSQL administrator username"
  type        = string
  default     = "pgadmin"
}

variable "postgres_admin_password" {
  description = "PostgreSQL administrator password"
  type        = string
  sensitive   = true
}

variable "postgres_database_name" {
  description = "PostgreSQL database name"
  type        = string
  default     = "todoapp"
}

variable "postgres_backup_retention_days" {
  description = "PostgreSQL backup retention days"
  type        = number
  default     = 7
}

variable "postgres_ha_enabled" {
  description = "Enable high availability for PostgreSQL"
  type        = bool
  default     = false
}

# =============================================================================
# Application Secrets
# =============================================================================

variable "better_auth_secret" {
  description = "Better Auth JWT secret"
  type        = string
  sensitive   = true
}
