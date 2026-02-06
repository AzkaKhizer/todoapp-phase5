# =============================================================================
# Azure Cache for Redis
# =============================================================================
# Used by Dapr for:
# - State store (actor state, workflow state)
# - Distributed caching
# - Session management
# =============================================================================

# =============================================================================
# Azure Redis Cache
# =============================================================================

resource "azurerm_redis_cache" "main" {
  name                = local.redis_name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  capacity            = var.redis_capacity
  family              = var.redis_family
  sku_name            = var.redis_sku
  enable_non_ssl_port = false
  minimum_tls_version = "1.2"

  # Redis configuration
  redis_configuration {
    maxmemory_reserved              = var.redis_sku == "Premium" ? 50 : 10
    maxmemory_delta                 = var.redis_sku == "Premium" ? 50 : 10
    maxmemory_policy                = "volatile-lru"
    maxfragmentationmemory_reserved = var.redis_sku == "Premium" ? 50 : 10
  }

  # Enable data persistence for Premium tier
  dynamic "redis_configuration" {
    for_each = var.redis_sku == "Premium" ? [1] : []
    content {
      rdb_backup_enabled            = true
      rdb_backup_frequency          = 60
      rdb_backup_max_snapshot_count = 1
    }
  }

  # Patch schedule
  patch_schedule {
    day_of_week    = "Sunday"
    start_hour_utc = 2
  }

  tags = local.common_tags

  lifecycle {
    ignore_changes = [
      redis_configuration[0].rdb_storage_connection_string
    ]
  }
}

# =============================================================================
# Redis Firewall Rules (Optional - for production)
# =============================================================================

# Allow access from AKS
# Note: In production, use private endpoints instead
resource "azurerm_redis_firewall_rule" "allow_azure" {
  name                = "AllowAzure"
  redis_cache_name    = azurerm_redis_cache.main.name
  resource_group_name = azurerm_resource_group.main.name
  start_ip            = "0.0.0.0"
  end_ip              = "0.0.0.0"
}

# =============================================================================
# Private Endpoint (Optional - for production)
# =============================================================================

# Uncomment for production deployment with VNet integration
# resource "azurerm_private_endpoint" "redis" {
#   name                = "${local.redis_name}-pe"
#   location            = azurerm_resource_group.main.location
#   resource_group_name = azurerm_resource_group.main.name
#   subnet_id           = azurerm_subnet.private_endpoints.id
#
#   private_service_connection {
#     name                           = "${local.redis_name}-psc"
#     private_connection_resource_id = azurerm_redis_cache.main.id
#     is_manual_connection           = false
#     subresource_names              = ["redisCache"]
#   }
#
#   tags = local.common_tags
# }

# =============================================================================
# Diagnostic Settings
# =============================================================================

resource "azurerm_monitor_diagnostic_setting" "redis" {
  name                       = "${local.redis_name}-diag"
  target_resource_id         = azurerm_redis_cache.main.id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.aks.id

  enabled_log {
    category = "ConnectedClientList"
  }

  metric {
    category = "AllMetrics"
    enabled  = true
  }
}
