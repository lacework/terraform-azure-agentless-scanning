provider "lacework" {}

// Create global resources, includes lacework cloud integration.
// This will also create regional resources too.
module "lacework_azure_agentless_scanning_single_tenant" {
  source = "../.."

  is_global_resource = true
  create_log_analytics_workspace = true
  integration_level          = "tenant"
  tags                       = { "lw-example-tf" : "true" }
  scanning_subscription_id       = "xxxxxxxx-1234-5678-abcd-xxxxxxxxxxxx"
  subscriptions_list = [
    "/subscriptions/xxxxxxxx-4321-8765-dcba-xxxxxxxxxxxx",
  ]

}
