# Single tenant Example

In this example we'll create resources to support scanning for a single location.


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
provider "lacework" {}

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

// Create global resources, includes lacework cloud integration.
// This will also create regional resources too.
module "lacework_azure_agentless_scanning_single_tenant" {
  source = "lacework/agentless-scanning/azure"

  # Specify your Lacework account name - only specify this in the global module.
  # For example, 'my-org' is the account name in 'my-org.lacework.net'.
  lacework_account = "my-org"

  global                         = true
  create_log_analytics_workspace = true
  integration_level              = "tenant"
  region                         = "West US"
  tags                           = { "lw-example-tf" : "true" }
  scanning_subscription_id       = "abcd-1234"
  tenant_id                      = "efgh-5678"
}
```
