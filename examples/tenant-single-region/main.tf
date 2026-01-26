provider "lacework" {}

// Create global resources, includes lacework cloud integration.
// This will also create regional resources too.
module "lacework_azure_agentless_scanning_single_tenant" {
  source = "../.."

  # Specify your Lacework account name - only specify this in the global module.
  # For example, 'my-org' is the account name in 'my-org.lacework.net'.
  lacework_account = "my-org"

  // specify the subscription in which AWLS will be deployed
  scanning_subscription_id       = "abcd-1234"

  global                         = true
  create_log_analytics_workspace = true
  integration_level              = "tenant"
  region                         = "West US"
  tags                           = { "lw-example-tf" : "true" }
}
