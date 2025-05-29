# Provider Configurations
provider "azurerm" {
  features {}
  subscription_id = var.scanning_subscription_id
}

# Data Sources
data "azurerm_subscription" "scanning" {
  subscription_id = var.scanning_subscription_id
}

data "azuread_client_config" "current" {} # Provides information about the authenticated principal, including tenant_id

data "azuread_service_principal" "msgraph" {
  client_id = "00000003-0000-0000-c000-000000000000" # Microsoft Graph Application (Client) ID
}

# Azure AD Application
resource "azuread_application" "awls_deployment_app" {
  display_name = var.service_principal_name

  required_resource_access {
    resource_app_id = data.azuread_service_principal.msgraph.client_id # Microsoft Graph
    resource_access {
      id   = "18a4783c-866b-4cc7-a460-3d5e5662c884" # Permission ID for Application.ReadWrite.OwnedBy
      type = "Role"                                 # Type "Role" indicates an Application Permission
    }
  }
}

# Azure AD Service Principal for the Application
resource "azuread_service_principal" "awls_deployment_sp" {
  client_id = azuread_application.awls_deployment_app.client_id
  # By default, the service principal is created in the same tenant as the application.
}

# Client Secret for the Service Principal
resource "azuread_service_principal_password" "awls_deployment_sp_password" {
  service_principal_id = "servicePrincipals/${azuread_service_principal.awls_deployment_sp.object_id}"
  end_date             = timeadd(timestamp(), var.client_secret_expiry_duration_hours)
}

# Custom Role Definition: AWLS Deployment (for Scanning Subscription)
resource "azurerm_role_definition" "awls_deployment_role" {
  name        = "AWLS Deployment (${var.service_principal_name})"
  scope       = data.azurerm_subscription.scanning.id
  description = "Permissions required on scanning subscription to deploy AWLS"

  permissions {
    actions = [
      "Microsoft.App/jobs/*",
      "Microsoft.App/managedEnvironments/*",
      "Microsoft.Authorization/roleAssignments/*",
      "Microsoft.Authorization/roleDefinitions/*",
      "Microsoft.Compute/virtualMachines/read",
      "Microsoft.Compute/virtualMachines/delete",
      "Microsoft.Compute/virtualMachineScaleSets/read",
      "Microsoft.Compute/virtualMachineScaleSets/virtualMachines/read",
      "Microsoft.KeyVault/vaults/*",
      "Microsoft.KeyVault/locations/deletedVaults/purge/*",
      "Microsoft.KeyVault/locations/operationResults/*",
      "Microsoft.ManagedIdentity/userAssignedIdentities/*",
      "Microsoft.Network/natGateways/*",
      "Microsoft.Network/networkSecurityGroups/*",
      "Microsoft.Network/publicIPAddresses/*",
      "Microsoft.Network/virtualNetworks/*",
      "Microsoft.OperationalInsights/workspaces/*",
      "Microsoft.OperationalInsights/workspaces/sharedKeys/*",
      "Microsoft.Resources/subscriptions/resourcegroups/*",
      "Microsoft.Storage/storageAccounts/*",
      "Microsoft.Storage/storageAccounts/blobServices/*",
      "Microsoft.Storage/storageAccounts/fileServices/*",
      "Microsoft.Storage/storageAccounts/listKeys/*"
    ]
    not_actions = []
  }

  assignable_scopes = [
    data.azurerm_subscription.scanning.id,
  ]
}

# Custom Role Definition: AWLS Deployment - Monitored Subscriptions (for Tenant/Monitored Subscriptions)
resource "azurerm_role_definition" "awls_monitored_subs_role" {
  name        = "AWLS Deployment (${var.service_principal_name}) - Monitored Subscriptions"
  scope       = "/providers/Microsoft.Management/managementGroups/${data.azuread_client_config.current.tenant_id}" # Defined at root management group
  description = "Permissions required on all monitored subscriptions to deploy AWLS"

  permissions {
    actions = [
      "Microsoft.Authorization/roleAssignments/*",
      "Microsoft.Authorization/roleDefinitions/*"
    ]
    not_actions = []
  }

  assignable_scopes = [
    "/providers/Microsoft.Management/managementGroups/${data.azuread_client_config.current.tenant_id}",
    # This role, defined at the MG, can also be assigned to subscriptions within this MG.
  ]
}

# Role Assignment: Assign "AWLS Deployment" role to SP on Scanning Subscription
resource "azurerm_role_assignment" "awls_deployment_role_assignment" {
  scope                = data.azurerm_subscription.scanning.id
  role_definition_id   = azurerm_role_definition.awls_deployment_role.role_definition_resource_id
  principal_id         = azuread_service_principal.awls_deployment_sp.object_id
  principal_type       = "ServicePrincipal"
}

# Role Assignment: Assign "AWLS Deployment - Monitored Subscriptions" role to SP
# Option 1: Assign to Tenant Root Management Group
resource "azurerm_role_assignment" "awls_monitored_subs_role_assignment_mg" {
  count = length(var.included_subscription_ids) == 0 ? 1 : 0

  scope                = "/providers/Microsoft.Management/managementGroups/${data.azuread_client_config.current.tenant_id}"
  role_definition_id   = azurerm_role_definition.awls_monitored_subs_role.role_definition_resource_id
  principal_id         = azuread_service_principal.awls_deployment_sp.object_id
  principal_type       = "ServicePrincipal"
}

# Option 2: Assign to specific Monitored Subscriptions
resource "azurerm_role_assignment" "awls_monitored_subs_role_assignment_subs" {
  count = length(var.included_subscription_ids) > 0 ? length(var.included_subscription_ids) : 0

  scope                = "/subscriptions/${var.included_subscription_ids[count.index]}"
  role_definition_id   = azurerm_role_definition.awls_monitored_subs_role.role_definition_resource_id # Assumes subscriptions are under the MG where role is defined/assignable
  principal_id         = azuread_service_principal.awls_deployment_sp.object_id
  principal_type       = "ServicePrincipal"
}

# Grant Microsoft Graph API Permission (Application.ReadWrite.OwnedBy) to the Service Principal
resource "azuread_app_role_assignment" "awls_deployment_sp_graph_permission" {
  app_role_id         = "18a4783c-866b-4cc7-a460-3d5e5662c884" # ID of Application.ReadWrite.OwnedBy app role in Microsoft Graph
  principal_object_id = azuread_service_principal.awls_deployment_sp.object_id
  resource_object_id  = data.azuread_service_principal.msgraph.object_id # Object ID of Microsoft Graph Service Principal
}

