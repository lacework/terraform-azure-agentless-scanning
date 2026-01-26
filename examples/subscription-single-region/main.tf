// Create resources including lacework cloud integration in one region
module "lacework_azure_agentless_scanning_subscription_us_west" {
  source = "../.."

  # Specify your Lacework account name - only specify this in the global module.
  # For example, 'my-org' is the account name in 'my-org.lacework.net'.
  lacework_account = "my-org"
  
  // specify the subscription in which AWLS will be deployed
  scanning_subscription_id       = "abcd-1234"

  integration_level              = "SUBSCRIPTION"
  global                         = true
  create_log_analytics_workspace = true
  region                         = "West US"

  // specify which subscriptions to monitor - only do this in the global module
  included_subscriptions         = ["/subscriptions/subscription-1", "/subscriptions/subscription-2"]
}