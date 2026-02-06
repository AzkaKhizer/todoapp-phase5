# =============================================================================
# Azure Event Hubs (Kafka-Compatible)
# =============================================================================
# Azure Event Hubs provides Kafka-compatible event streaming.
# Topics are called "Event Hubs" and partitions work the same way.
# =============================================================================

# =============================================================================
# Event Hubs Namespace
# =============================================================================

resource "azurerm_eventhub_namespace" "main" {
  name                = local.eventhub_namespace
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = var.eventhub_sku
  capacity            = var.eventhub_capacity

  # Enable Kafka protocol
  kafka_enabled = true

  # Auto-inflate for scaling (Standard tier only)
  auto_inflate_enabled     = var.eventhub_sku == "Standard" ? true : false
  maximum_throughput_units = var.eventhub_sku == "Standard" ? var.eventhub_max_throughput : null

  # Network rules (optional - for production)
  # network_rulesets {
  #   default_action = "Deny"
  #   trusted_service_access_enabled = true
  # }

  tags = local.common_tags
}

# =============================================================================
# Event Hubs (Kafka Topics)
# =============================================================================

# Task Events Topic
resource "azurerm_eventhub" "task_events" {
  name                = "task.events"
  namespace_name      = azurerm_eventhub_namespace.main.name
  resource_group_name = azurerm_resource_group.main.name
  partition_count     = var.eventhub_partition_count
  message_retention   = var.eventhub_message_retention
}

# Reminder Due Topic
resource "azurerm_eventhub" "reminder_due" {
  name                = "reminder.due"
  namespace_name      = azurerm_eventhub_namespace.main.name
  resource_group_name = azurerm_resource_group.main.name
  partition_count     = 4
  message_retention   = 1
}

# Notification Send Topic
resource "azurerm_eventhub" "notification_send" {
  name                = "notification.send"
  namespace_name      = azurerm_eventhub_namespace.main.name
  resource_group_name = azurerm_resource_group.main.name
  partition_count     = 4
  message_retention   = 1
}

# Notification DLQ Topic
resource "azurerm_eventhub" "notification_dlq" {
  name                = "notification.dlq"
  namespace_name      = azurerm_eventhub_namespace.main.name
  resource_group_name = azurerm_resource_group.main.name
  partition_count     = 2
  message_retention   = 7
}

# Activity Log Topic
resource "azurerm_eventhub" "activity_log" {
  name                = "activity.log"
  namespace_name      = azurerm_eventhub_namespace.main.name
  resource_group_name = azurerm_resource_group.main.name
  partition_count     = var.eventhub_partition_count
  message_retention   = var.eventhub_message_retention
}

# Sync Events Topic
resource "azurerm_eventhub" "sync_events" {
  name                = "sync.events"
  namespace_name      = azurerm_eventhub_namespace.main.name
  resource_group_name = azurerm_resource_group.main.name
  partition_count     = var.eventhub_partition_count
  message_retention   = 1
}

# =============================================================================
# Consumer Groups
# =============================================================================

# Task Events Consumer Groups
resource "azurerm_eventhub_consumer_group" "task_events_backend" {
  name                = "todo-backend"
  namespace_name      = azurerm_eventhub_namespace.main.name
  eventhub_name       = azurerm_eventhub.task_events.name
  resource_group_name = azurerm_resource_group.main.name
}

resource "azurerm_eventhub_consumer_group" "task_events_activity" {
  name                = "activity-service"
  namespace_name      = azurerm_eventhub_namespace.main.name
  eventhub_name       = azurerm_eventhub.task_events.name
  resource_group_name = azurerm_resource_group.main.name
}

# Sync Events Consumer Group
resource "azurerm_eventhub_consumer_group" "sync_events" {
  name                = "sync-service"
  namespace_name      = azurerm_eventhub_namespace.main.name
  eventhub_name       = azurerm_eventhub.sync_events.name
  resource_group_name = azurerm_resource_group.main.name
}

# Notification Consumer Group
resource "azurerm_eventhub_consumer_group" "notification_delivery" {
  name                = "notification-delivery"
  namespace_name      = azurerm_eventhub_namespace.main.name
  eventhub_name       = azurerm_eventhub.notification_send.name
  resource_group_name = azurerm_resource_group.main.name
}

# Activity Log Consumer Group
resource "azurerm_eventhub_consumer_group" "activity_log" {
  name                = "activity-logger"
  namespace_name      = azurerm_eventhub_namespace.main.name
  eventhub_name       = azurerm_eventhub.activity_log.name
  resource_group_name = azurerm_resource_group.main.name
}

# =============================================================================
# Authorization Rules
# =============================================================================

# Shared Access Policy for Backend Application
resource "azurerm_eventhub_namespace_authorization_rule" "backend" {
  name                = "backend-policy"
  namespace_name      = azurerm_eventhub_namespace.main.name
  resource_group_name = azurerm_resource_group.main.name

  listen = true
  send   = true
  manage = false
}

# Shared Access Policy for Admin Operations
resource "azurerm_eventhub_namespace_authorization_rule" "admin" {
  name                = "admin-policy"
  namespace_name      = azurerm_eventhub_namespace.main.name
  resource_group_name = azurerm_resource_group.main.name

  listen = true
  send   = true
  manage = true
}
