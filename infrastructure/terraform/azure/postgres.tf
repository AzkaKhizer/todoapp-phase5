# =============================================================================
# Azure Database for PostgreSQL Flexible Server
# =============================================================================
# Production-ready PostgreSQL database for the Todo application.
# Features:
# - High availability (optional)
# - Automated backups
# - SSL enforcement
# =============================================================================

# =============================================================================
# PostgreSQL Flexible Server
# =============================================================================

resource "azurerm_postgresql_flexible_server" "main" {
  name                   = local.postgres_name
  resource_group_name    = azurerm_resource_group.main.name
  location               = azurerm_resource_group.main.location
  version                = var.postgres_version
  administrator_login    = var.postgres_admin_username
  administrator_password = var.postgres_admin_password
  storage_mb             = var.postgres_storage_mb
  sku_name               = var.postgres_sku

  # Backup configuration
  backup_retention_days        = var.postgres_backup_retention_days
  geo_redundant_backup_enabled = var.environment == "prod"

  # High availability (optional, for production)
  dynamic "high_availability" {
    for_each = var.postgres_ha_enabled ? [1] : []
    content {
      mode                      = "ZoneRedundant"
      standby_availability_zone = "2"
    }
  }

  # Maintenance window
  maintenance_window {
    day_of_week  = 0  # Sunday
    start_hour   = 2
    start_minute = 0
  }

  tags = local.common_tags

  lifecycle {
    ignore_changes = [
      zone,
      high_availability[0].standby_availability_zone
    ]
  }
}

# =============================================================================
# PostgreSQL Database
# =============================================================================

resource "azurerm_postgresql_flexible_server_database" "main" {
  name      = var.postgres_database_name
  server_id = azurerm_postgresql_flexible_server.main.id
  collation = "en_US.utf8"
  charset   = "UTF8"
}

# =============================================================================
# PostgreSQL Firewall Rules
# =============================================================================

# Allow Azure services (for AKS access)
resource "azurerm_postgresql_flexible_server_firewall_rule" "allow_azure" {
  name             = "AllowAzureServices"
  server_id        = azurerm_postgresql_flexible_server.main.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"
}

# Allow all IPs for development (disable in production)
resource "azurerm_postgresql_flexible_server_firewall_rule" "allow_all" {
  count            = var.environment != "prod" ? 1 : 0
  name             = "AllowAll"
  server_id        = azurerm_postgresql_flexible_server.main.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "255.255.255.255"
}

# =============================================================================
# PostgreSQL Server Configuration
# =============================================================================

resource "azurerm_postgresql_flexible_server_configuration" "timezone" {
  name      = "timezone"
  server_id = azurerm_postgresql_flexible_server.main.id
  value     = "UTC"
}

resource "azurerm_postgresql_flexible_server_configuration" "log_connections" {
  name      = "log_connections"
  server_id = azurerm_postgresql_flexible_server.main.id
  value     = "on"
}

resource "azurerm_postgresql_flexible_server_configuration" "log_disconnections" {
  name      = "log_disconnections"
  server_id = azurerm_postgresql_flexible_server.main.id
  value     = "on"
}

resource "azurerm_postgresql_flexible_server_configuration" "connection_throttling" {
  name      = "connection_throttle.enable"
  server_id = azurerm_postgresql_flexible_server.main.id
  value     = "on"
}

# =============================================================================
# Diagnostic Settings
# =============================================================================

resource "azurerm_monitor_diagnostic_setting" "postgres" {
  name                       = "${local.postgres_name}-diag"
  target_resource_id         = azurerm_postgresql_flexible_server.main.id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.aks.id

  enabled_log {
    category = "PostgreSQLLogs"
  }

  metric {
    category = "AllMetrics"
    enabled  = true
  }
}
