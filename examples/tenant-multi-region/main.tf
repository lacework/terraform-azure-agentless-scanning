// Create global resources, includes lacework cloud integration.
// This will also create regional resources too.
module "lacework_azure_agentless_scanning_tenant_us_west" {
  source = "../.."

  # Specify your Lacework account name - only specify this in the global module.
  # For example, 'my-org' is the account name in 'my-org.lacework.net'.
  lacework_account = "my-org"

  // specify the subscription in which AWLS will be deployed
  scanning_subscription_id       = "abcd-1234"

  integration_level              = "TENANT"
  global                         = true
  create_log_analytics_workspace = true
  region                         = "West US"
}

module "lacework_azure_agentless_scanning_single_tenant_us_east" {
  source = "../.."

  integration_level              = "TENANT"
  global                         = false
  create_log_analytics_workspace = true
  global_module_reference        = module.lacework_azure_agentless_scanning_tenant_us_west
  region                         = "East US"
}
