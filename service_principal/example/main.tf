module "azure_agentless_deployment_service_principal" {
  source = "./.."

  service_principal_name = "example-awls-deployment-sp"
  scanning_subscription_id = "my-subscription-id"
}

# Outputs
# These outputs must be defined to retrieve the client ID and secret of the created service principal.
output "example_service_principal_client_id" {
  description = "Client ID of the AWLS deployment service principal created by the module."
  value       = module.azure_agentless_deployment_service_principal.service_principal_client_id
}

output "example_service_principal_client_secret" {
  description = "Client Secret of the AWLS deployment service principal created by the module. This is a sensitive value."
  value       = module.azure_agentless_deployment_service_principal.service_principal_client_secret
  sensitive   = true
} 