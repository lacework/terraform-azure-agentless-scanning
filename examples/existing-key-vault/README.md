This example shows you how to use a Key Vault that you create yourself, here one with RBAC authorization
and purge protection. Note it requires several steps:
1. `terraform init`
2. `terraform apply -target "azurerm_role_assignment.example"`
3. `terraform apply`

The module needs `key_vault_id` and the Key Vault's settings at plan time: they decide whether it creates its own
Key Vault, and whether it grants the scanner a role or an access policy. In this example the Key Vault is created
in the same configuration, so Terraform only knows them after it exists, and planning everything in one go fails
with "Invalid count argument". Step 2 creates the Key Vault first, together with the role that lets you write the
secret, so that the role is in effect when step 3 writes it.

## Sample Code

### versions.tf
```hcl
terraform {
  required_version = ">= 0.13"

  required_providers {
    lacework = {
      source = "lacework/lacework"
    }
  }
}
```

### main.tf
```hcl
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
```
