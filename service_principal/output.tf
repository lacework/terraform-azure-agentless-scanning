output "service_principal_client_id" {
  description = "The Client ID (Application ID) of the created service principal."
  value       = azuread_application.awls_deployment_app.client_id
}

output "service_principal_object_id" {
  description = "The Object ID of the created service principal."
  value       = azuread_service_principal.awls_deployment_sp.object_id
}

output "service_principal_tenant_id" {
  description = "The Tenant ID where the service principal was created."
  value       = data.azuread_client_config.current.tenant_id
}

output "service_principal_client_secret" {
  description = "The Client Secret for the service principal. Store this securely and use it immediately."
  value       = azuread_service_principal_password.awls_deployment_sp_password.value
  sensitive   = true
}

output "awls_deployment_role_id" {
  description = "The resource ID of the 'AWLS Deployment' custom role definition."
  value       = azurerm_role_definition.awls_deployment_role.id
}

output "awls_monitored_subscriptions_role_id" {
  description = "The resource ID of the 'AWLS Deployment - Monitored Subscriptions' custom role definition."
  value       = azurerm_role_definition.awls_monitored_subs_role.id
}
