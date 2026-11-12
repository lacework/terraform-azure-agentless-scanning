// The module uses this provider for every region. subscription_id must match
// scanning_subscription_id below.
provider "azurerm" {
  subscription_id = "abcd-1234"
  features {
    resource_group {
      // the scanner creates disks in its resource group; let `terraform destroy` remove them
      prevent_deletion_if_contains_resources = false
    }
  }
}

data "azurerm_client_config" "current" {}

resource "azurerm_resource_group" "example" {
  name     = "example-key-vault-rg"
  location = "West US"
}

/* A Key Vault with RBAC authorization and purge protection, in the scanning subscription */
resource "azurerm_key_vault" "example" {
  name                       = "example-lacework-kv"
  location                   = azurerm_resource_group.example.location
  resource_group_name        = azurerm_resource_group.example.name
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  sku_name                   = "standard"
  enable_rbac_authorization  = true
  purge_protection_enabled   = true
  soft_delete_retention_days = 7
}

/* Lets the identity running Terraform write the Lacework secret to the Key Vault */
resource "azurerm_role_assignment" "example" {
  scope                = azurerm_key_vault.example.id
  role_definition_name = "Key Vault Secrets Officer"
  principal_id         = data.azurerm_client_config.current.object_id
}

module "lacework_azure_agentless_scanning_subscription" {
  source = "../.."

  # Specify your Lacework account name - only specify this in the global module.
  # For example, 'my-org' is the account name in 'my-org.lacework.net'.
  lacework_account = "my-org"

  // specify the subscription in which AWLS will be deployed
  scanning_subscription_id = "abcd-1234"

  integration_level              = "SUBSCRIPTION"
  global                         = true
  create_log_analytics_workspace = true
  region                         = "West US"
  included_subscriptions         = ["/subscriptions/subscription-1", "/subscriptions/subscription-2"]

  // use the Key Vault above instead of creating one
  key_vault_id = azurerm_key_vault.example.id
}
