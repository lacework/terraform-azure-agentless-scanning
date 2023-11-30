// Create resources including lacework cloud integration in one region
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