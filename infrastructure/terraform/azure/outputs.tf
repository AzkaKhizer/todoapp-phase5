# =============================================================================
# Terraform Outputs for Azure Infrastructure
# =============================================================================

# =============================================================================
# Resource Group
# =============================================================================

output "resource_group_name" {
  description = "Name of the resource group"
  value       = azurerm_resource_group.main.name
}

output "resource_group_location" {
  description = "Location of the resource group"
  value       = azurerm_resource_group.main.location
}

# =============================================================================
# AKS Cluster
# =============================================================================

output "aks_cluster_name" {
  description = "Name of the AKS cluster"
  value       = azurerm_kubernetes_cluster.aks.name
}

output "aks_cluster_id" {
  description = "ID of the AKS cluster"
  value       = azurerm_kubernetes_cluster.aks.id
}

output "aks_kube_config" {
  description = "Kube config for the AKS cluster"
  value       = azurerm_kubernetes_cluster.aks.kube_config_raw
  sensitive   = true
}

output "aks_host" {
  description = "AKS cluster API server host"
  value       = azurerm_kubernetes_cluster.aks.kube_config[0].host
  sensitive   = true
}

output "aks_oidc_issuer_url" {
  description = "OIDC issuer URL for workload identity"
  value       = azurerm_kubernetes_cluster.aks.oidc_issuer_url
}

output "aks_kubelet_identity_object_id" {
  description = "Object ID of the AKS kubelet identity"
  value       = azurerm_kubernetes_cluster.aks.kubelet_identity[0].object_id
}

# =============================================================================
# Container Registry
# =============================================================================

output "acr_name" {
  description = "Name of the Azure Container Registry"
  value       = azurerm_container_registry.main.name
}

output "acr_login_server" {
  description = "Login server URL for ACR"
  value       = azurerm_container_registry.main.login_server
}

output "acr_id" {
  description = "ID of the Azure Container Registry"
  value       = azurerm_container_registry.main.id
}

# =============================================================================
# Event Hubs
# =============================================================================

output "eventhub_namespace" {
  description = "Event Hubs namespace name"
  value       = azurerm_eventhub_namespace.main.name
}

output "eventhub_namespace_id" {
  description = "Event Hubs namespace ID"
  value       = azurerm_eventhub_namespace.main.id
}

output "eventhub_connection_string" {
  description = "Event Hubs namespace connection string"
  value       = azurerm_eventhub_namespace.main.default_primary_connection_string
  sensitive   = true
}

output "eventhub_kafka_endpoint" {
  description = "Kafka-compatible endpoint for Event Hubs"
  value       = "${azurerm_eventhub_namespace.main.name}.servicebus.windows.net:9093"
}

# =============================================================================
# Redis
# =============================================================================

output "redis_hostname" {
  description = "Redis cache hostname"
  value       = azurerm_redis_cache.main.hostname
}

output "redis_ssl_port" {
  description = "Redis SSL port"
  value       = azurerm_redis_cache.main.ssl_port
}

output "redis_connection_string" {
  description = "Redis connection string"
  value       = "rediss://:${azurerm_redis_cache.main.primary_access_key}@${azurerm_redis_cache.main.hostname}:${azurerm_redis_cache.main.ssl_port}"
  sensitive   = true
}

output "redis_primary_key" {
  description = "Redis primary access key"
  value       = azurerm_redis_cache.main.primary_access_key
  sensitive   = true
}

# =============================================================================
# PostgreSQL
# =============================================================================

output "postgres_fqdn" {
  description = "PostgreSQL server FQDN"
  value       = azurerm_postgresql_flexible_server.main.fqdn
}

output "postgres_server_name" {
  description = "PostgreSQL server name"
  value       = azurerm_postgresql_flexible_server.main.name
}

output "postgres_database_name" {
  description = "PostgreSQL database name"
  value       = azurerm_postgresql_flexible_server_database.main.name
}

output "postgres_connection_string" {
  description = "PostgreSQL connection string"
  value       = "postgresql://${var.postgres_admin_username}:${var.postgres_admin_password}@${azurerm_postgresql_flexible_server.main.fqdn}:5432/${var.postgres_database_name}?sslmode=require"
  sensitive   = true
}

# =============================================================================
# Key Vault
# =============================================================================

output "keyvault_name" {
  description = "Key Vault name"
  value       = azurerm_key_vault.main.name
}

output "keyvault_uri" {
  description = "Key Vault URI"
  value       = azurerm_key_vault.main.vault_uri
}

output "keyvault_id" {
  description = "Key Vault ID"
  value       = azurerm_key_vault.main.id
}

# =============================================================================
# Kubernetes Namespace
# =============================================================================

output "app_namespace" {
  description = "Kubernetes namespace for the application"
  value       = kubernetes_namespace.app.metadata[0].name
}

# =============================================================================
# Useful Commands
# =============================================================================

output "connect_to_aks" {
  description = "Command to connect to AKS cluster"
  value       = "az aks get-credentials --resource-group ${azurerm_resource_group.main.name} --name ${azurerm_kubernetes_cluster.aks.name}"
}

output "login_to_acr" {
  description = "Command to login to ACR"
  value       = "az acr login --name ${azurerm_container_registry.main.name}"
}
