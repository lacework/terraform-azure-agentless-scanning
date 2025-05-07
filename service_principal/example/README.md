This example demonstrates how to create a service principal for the Azure Agentless Workload Scanning (AWLS) deployment using this terraform module.

1. Create the service principal module as shown in the [`main.tf`](./main.tf) file.
1. Run the module to create the service principal.
```
terraform init
terraform apply
```
1. Retrieve the client ID and client secret of the service principal.
```
terraform output example_service_principal_client_id
terraform output example_service_principal_client_secret
```
1. Use the client ID and client secret to authenticate az cli.
```
az login --service-principal --username=<CLIENT_ID> --password=<CLIENT_SECRET> --tenant=<TENANT_ID>
```
