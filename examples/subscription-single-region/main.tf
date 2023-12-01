// Create resources including lacework cloud integration in one region
module "lacework_azure_agentless_scanning_subscription_us_west" {
  source = "../.."

  integration_level              = "SUBSCRIPTION"
  is_global_resource             = true
  create_log_analytics_workspace = true
  region                         = "West US"
}