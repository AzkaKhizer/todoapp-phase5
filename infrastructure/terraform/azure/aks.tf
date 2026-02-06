# =============================================================================
# Azure Kubernetes Service (AKS) Cluster
# =============================================================================
# Features:
# - Managed Kubernetes with auto-scaling
# - Azure CNI networking for Dapr compatibility
# - Workload Identity for secure pod authentication
# - Container Insights for monitoring
# =============================================================================

# =============================================================================
# User Assigned Identity for AKS
# =============================================================================

resource "azurerm_user_assigned_identity" "aks" {
  name                = "${local.aks_name}-identity"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location

  tags = local.common_tags
}

# =============================================================================
# Log Analytics Workspace (for Container Insights)
# =============================================================================

resource "azurerm_log_analytics_workspace" "aks" {
  name                = "${local.aks_name}-logs"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "PerGB2018"
  retention_in_days   = 30

  tags = local.common_tags
}

# =============================================================================
# AKS Cluster
# =============================================================================

resource "azurerm_kubernetes_cluster" "aks" {
  name                = local.aks_name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  dns_prefix          = "${var.project_name}-${var.environment}"
  kubernetes_version  = var.kubernetes_version

  # Use User Assigned Identity
  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.aks.id]
  }

  # Default node pool (system)
  default_node_pool {
    name                = "system"
    node_count          = var.aks_system_node_count
    vm_size             = var.aks_system_node_size
    os_disk_size_gb     = 50
    os_disk_type        = "Managed"
    type                = "VirtualMachineScaleSets"
    enable_auto_scaling = true
    min_count           = var.aks_system_node_min
    max_count           = var.aks_system_node_max

    node_labels = {
      "nodepool-type" = "system"
      "environment"   = var.environment
    }

    tags = local.common_tags
  }

  # Network configuration
  network_profile {
    network_plugin    = "azure"
    network_policy    = "calico"
    load_balancer_sku = "standard"
    service_cidr      = "10.0.0.0/16"
    dns_service_ip    = "10.0.0.10"
  }

  # Container Insights
  oms_agent {
    log_analytics_workspace_id = azurerm_log_analytics_workspace.aks.id
  }

  # Azure AD integration
  azure_active_directory_role_based_access_control {
    managed                = true
    azure_rbac_enabled     = true
    admin_group_object_ids = var.aks_admin_group_ids
  }

  # Workload Identity (for Dapr secrets)
  oidc_issuer_enabled       = true
  workload_identity_enabled = true

  # Auto-upgrade
  automatic_channel_upgrade = "patch"

  # Maintenance window
  maintenance_window {
    allowed {
      day   = "Sunday"
      hours = [2, 3, 4, 5]
    }
  }

  tags = local.common_tags

  lifecycle {
    ignore_changes = [
      default_node_pool[0].node_count,
      kubernetes_version
    ]
  }
}

# =============================================================================
# User Node Pool (for application workloads)
# =============================================================================

resource "azurerm_kubernetes_cluster_node_pool" "user" {
  name                  = "user"
  kubernetes_cluster_id = azurerm_kubernetes_cluster.aks.id
  vm_size               = var.aks_user_node_size
  node_count            = var.aks_user_node_count
  os_disk_size_gb       = 100
  os_disk_type          = "Managed"
  enable_auto_scaling   = true
  min_count             = var.aks_user_node_min
  max_count             = var.aks_user_node_max

  node_labels = {
    "nodepool-type" = "user"
    "environment"   = var.environment
    "workload"      = "todo-app"
  }

  node_taints = []

  tags = local.common_tags

  lifecycle {
    ignore_changes = [node_count]
  }
}

# =============================================================================
# Role Assignments
# =============================================================================

# Allow AKS to pull images from ACR
resource "azurerm_role_assignment" "aks_acr" {
  scope                = azurerm_container_registry.main.id
  role_definition_name = "AcrPull"
  principal_id         = azurerm_kubernetes_cluster.aks.kubelet_identity[0].object_id
}

# Allow AKS to access Key Vault secrets
resource "azurerm_role_assignment" "aks_keyvault" {
  scope                = azurerm_key_vault.main.id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = azurerm_user_assigned_identity.aks.principal_id
}

# =============================================================================
# Key Vault Access Policy for AKS
# =============================================================================

resource "azurerm_key_vault_access_policy" "aks" {
  key_vault_id = azurerm_key_vault.main.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = azurerm_user_assigned_identity.aks.principal_id

  secret_permissions = [
    "Get", "List"
  ]
}
