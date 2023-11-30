// Create global resources, includes lacework cloud integration.
// This will also create regional resources too.
module "lacework_azure_agentless_scanning_subscription_us_west" {
  source = "../.."

  integration_level              = "SUBSCRIPTION"
  is_global_resource             = true
  create_log_analytics_workspace = true
  region                         = "West US"
  scanning_subscription_id       = "xxxxxxxx-1234-5678-abcd-xxxxxxxxxxxx"
  subscriptions_list = [
    "/subscriptions/xxxxxxxx-4321-8765-dcba-xxxxxxxxxxxx",
  ]
}

module "lacework_azure_agentless_scanning_subscription_us_east" {
  source = "../.."

  integration_level              = "SUBSCRIPTION"
  is_global_resource             = false
  create_log_analytics_workspace = true
  global_module_reference        = module.lacework_azure_agentless_scanning_subscription_us_west
  region                         = "East US"
  scanning_subscription_id       = "xxxxxxxx-1234-5678-abcd-xxxxxxxxxxxx"
  subscriptions_list = [
    "/subscriptions/xxxxxxxx-4321-8765-dcba-xxxxxxxxxxxx",
  ]
}
