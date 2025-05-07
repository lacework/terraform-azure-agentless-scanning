# Variables
variable "service_principal_name" {
  description = "The display name for the Azure AD application and service principal."
  type        = string
  default     = "awls-deployment-sp"
}

variable "scanning_subscription_id" {
  description = "The subscription ID where AWLS scanning resources will be deployed and where the 'AWLS Deployment' role will be scoped."
  type        = string
}

variable "included_subscription_ids" {
  description = "A fixed list of subscription IDs to be monitored by AWLS. The 'AWLS Deployment - Monitored Subscriptions' role will be assigned to these subscriptions. Leave this empty if you want AWLS to monitor all subscriptions in the tenant."
  type        = list(string)
  default     = []
}

variable "client_secret_expiry_duration_hours" {
  description = "Duration in hours for the client secret's validity. For example, '2160h' for 90 days. Default is 6 months if not set."
  type        = string
  default     = "4380h" # Default to 6 months (approx 6 * 30 * 24)
}