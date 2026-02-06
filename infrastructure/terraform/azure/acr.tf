# =============================================================================
# Azure Container Registry (ACR)
# =============================================================================
# Stores Docker images for:
# - Todo Backend API
# - Todo Frontend
# =============================================================================

# =============================================================================
# Container Registry
# =============================================================================

resource "azurerm_container_registry" "main" {
  name                = local.acr_name
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = var.acr_sku
  admin_enabled       = false

  # Geo-replication for Premium tier
  dynamic "georeplications" {
    for_each = var.acr_sku == "Premium" && var.acr_georeplication_locations != null ? var.acr_georeplication_locations : []
    content {
      location                = georeplications.value
      zone_redundancy_enabled = true
      tags                    = local.common_tags
    }
  }

  # Network rules (Premium tier only)
  dynamic "network_rule_set" {
    for_each = var.acr_sku == "Premium" ? [1] : []
    content {
      default_action = "Allow"
    }
  }

  # Content trust (Premium tier)
  trust_policy {
    enabled = var.acr_sku == "Premium"
  }

  # Retention policy (Premium tier)
  retention_policy {
    enabled = var.acr_sku == "Premium"
    days    = 30
  }

  tags = local.common_tags
}

# =============================================================================
# ACR Tasks for Automated Builds (Optional)
# =============================================================================

# Backend image build task
resource "azurerm_container_registry_task" "backend" {
  count                 = var.enable_acr_tasks ? 1 : 0
  name                  = "build-backend"
  container_registry_id = azurerm_container_registry.main.id

  platform {
    os           = "Linux"
    architecture = "amd64"
  }

  docker_step {
    dockerfile_path      = "backend/Dockerfile"
    context_path         = "https://github.com/${var.github_repo}#main:backend"
    context_access_token = var.github_token
    image_names          = ["todo-backend:{{.Run.ID}}", "todo-backend:latest"]
  }

  source_trigger {
    name           = "github-push"
    events         = ["commit"]
    repository_url = "https://github.com/${var.github_repo}"
    source_type    = "Github"
    branch         = "main"

    authentication {
      token      = var.github_token
      token_type = "PAT"
    }
  }

  tags = local.common_tags
}

# Frontend image build task
resource "azurerm_container_registry_task" "frontend" {
  count                 = var.enable_acr_tasks ? 1 : 0
  name                  = "build-frontend"
  container_registry_id = azurerm_container_registry.main.id

  platform {
    os           = "Linux"
    architecture = "amd64"
  }

  docker_step {
    dockerfile_path      = "frontend/Dockerfile"
    context_path         = "https://github.com/${var.github_repo}#main:frontend"
    context_access_token = var.github_token
    image_names          = ["todo-frontend:{{.Run.ID}}", "todo-frontend:latest"]
  }

  source_trigger {
    name           = "github-push"
    events         = ["commit"]
    repository_url = "https://github.com/${var.github_repo}"
    source_type    = "Github"
    branch         = "main"

    authentication {
      token      = var.github_token
      token_type = "PAT"
    }
  }

  tags = local.common_tags
}

# =============================================================================
# Diagnostic Settings
# =============================================================================

resource "azurerm_monitor_diagnostic_setting" "acr" {
  name                       = "${local.acr_name}-diag"
  target_resource_id         = azurerm_container_registry.main.id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.aks.id

  enabled_log {
    category = "ContainerRegistryRepositoryEvents"
  }

  enabled_log {
    category = "ContainerRegistryLoginEvents"
  }

  metric {
    category = "AllMetrics"
    enabled  = true
  }
}
