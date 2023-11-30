// Create global resources, includes lacework cloud integration.
// This will also create regional resources too.
module "lacework_azure_agentless_scanning_tenant_us_west" {
  source = "../.."

  integration_level              = "TENANT"
  is_global_resource             = true
  create_log_analytics_workspace = true
  region                         = "West US"
 scanning_subscription_id = "0252a545-04d4-4262-a82c-ceef83344237"
 subscriptions_list = [
   "/subscriptions/e64af596-838e-43c9-9112-d7d53d546e65"
  ]
 image_url = "public.ecr.aws/z0d9u1f3/kilby-test:latest"
}

module "lacework_azure_agentless_scanning_single_tenant_us_east" {
  source = "../.."

  integration_level              = "TENANT"
  is_global_resource             = false
  create_log_analytics_workspace = true
  global_module_reference        = module.lacework_azure_agentless_scanning_tenant_us_west
  region                         = "East US"
 scanning_subscription_id = "0252a545-04d4-4262-a82c-ceef83344237"
 subscriptions_list = [
   "/subscriptions/e64af596-838e-43c9-9112-d7d53d546e65"
  ]
 image_url = "public.ecr.aws/z0d9u1f3/kilby-test:latest"
}
