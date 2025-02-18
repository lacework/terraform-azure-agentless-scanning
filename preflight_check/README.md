# Azure Agentless Scanner Preflight Check

A validation tool to ensure your Azure environment is properly configured for deploying the Lacework Agentless Scanner.

## Overview

This tool
1. counts the VMs in your Azure environment, and 
2. validates the following resource quotas (computed based on the number of VMs to be scanned by AWLS):
   - vCPU quotas
   - Public IP address quotas (if deploying without a NAT Gateway)

## Prerequisites
1. [Authenticate Azure CLI](#authentication--authorization)
1. [Install `uv` package manager](https://docs.astral.sh/uv/getting-started/installation/)

## Usage

### Interactive Mode

```bash
uv run preflight_check.py
```

The script will prompt for:
- Integration type (tenant-level or subscription-level)
- Scanning subscription ID
- Deployment regions
- Number of VMs to be scanned
- NAT Gateway preference

### Non-Interactive Mode

```bash
uv run preflight_check.py \
  --integration-type tenant \
  --subscription <SCANNING_SUB_ID> \
  --regions eastus,westus \
  --vm-count 100 \
  --nat-gateway true
```

## Output

The script provides:
- Real-time CLI feedback with validation results
- Detailed error messages and remediation steps
- JSON report file (`preflight_report.json`)

### Sample Output

```
🔍 Azure Preflight Check for Deployment
--------------------------------------
Integration Type: Tenant-Level
Scanning Subscription: ********-****-****-****-************
Deployment Regions: eastus, westus
VMs to be Scanned: 100
Using NAT Gateway: Yes

Checking Resource Quotas...
✅ vCPU quota sufficient in eastus (50 required, 100 available)
✅ vCPU quota sufficient in westus (50 required, 100 available)
✅ NAT Gateway deployment selected - no public IP quota check required

📊 Summary: All checks passed! Ready for deployment.
💾 Detailed report saved to preflight_report.json
```

## Authentication & Authorization

We suggest creating a new Azure Service Principal as instructed below to use for deploying AWLS. Alternatively, you can authenticate as an Azure user, as long as the user has the necessary permissions listed below.

### Create a Service Principal
In the following steps, `<scanning-subscription-id>` is the ID of the Azure subscription where AWLS resources will be deployed.

1. Create a json file defining a custom role with the permissions required to deploy AWLS. You can copy the following example and replace `<scanning-subscription-id>` with your subscription ID.
   ```json
   // ./awls-deployment-role.json
   {
      "Name": "AWLS Deployment",
      "Description": "Role for deploying AWLS",
      "Actions": [
         "Microsoft.App/jobs/*",
         "Microsoft.App/managedEnvironments/*",
         "Microsoft.Authorization/roleAssignments/*",
         "Microsoft.Authorization/roleDefinitions/*",
         "Microsoft.Compute/virtualMachines/read",
         "Microsoft.Compute/virtualMachineScaleSets/read",
         "Microsoft.Compute/virtualMachineScaleSets/virtualMachines/read",
         "Microsoft.KeyVault/vaults/*",
         "Microsoft.KeyVault/locations/deletedVaults/purge/*",
         "Microsoft.KeyVault/locations/operationResults/*",
         "Microsoft.ManagedIdentity/userAssignedIdentities/*",
         "Microsoft.Network/natGateways/*"
         "Microsoft.Network/networkSecurityGroups/*",
         "Microsoft.Network/publicIPAddresses/*",
         "Microsoft.Network/virtualNetworks/*",
         "Microsoft.OperationalInsights/workspaces/*",
         "Microsoft.OperationalInsights/workspaces/sharedKeys/*",
         "Microsoft.Resources/subscriptions/resourcegroups/*",
         "Microsoft.Storage/storageAccounts/*",
         "Microsoft.Storage/storageAccounts/blobServices/*",
         "Microsoft.Storage/storageAccounts/fileServices/*",
         "Microsoft.Storage/storageAccounts/listKeys/*",
      ],
      "NotActions": [],
      "AssignableScopes": [
         "/subscriptions/<scanning-subscription-id>"
      ]
   }
   ```

2. Create the custom role, passing the json file created in the previous step as the role definition.
   ```bash
   az role definition create --role-definition ./awls-deployment-role.json
   ```

3. Create a new Service Principal with the custom role assigned to it (scoped to the scanning subscription).
   ```bash
   az ad sp create-for-rbac --name "awls-deployment-sp" --role "AWLS Deployment" --scopes /subscriptions/<scanning-subscription-id>
   ```

4. Grant the required `Microsoft.Graph/Application.ReadWrite.OwnedBy` permission to the service principal - please note that this requires admin consent (so the user running these commands needs to have _Global Administrator_ or _Privileged Role Administrator_ rights in the Azure AD tenant). For context, this permission enables the service principal to create, update, and delete applications it creates.
   ```bash
   # Get the service principal object ID
   SP_OBJECT_ID=$(az ad sp list --display-name "awls-deployment-sp" --query '[0].id' -o tsv)

   # Add the API permission
   # 00000003-0000-0000-c000-000000000000 is Microsoft Graph's application ID
   # 06b708a9-e830-4db3-a914-8e69da51d44f is the Application.ReadWrite.OwnedBy permission ID
   az ad app permission add --id $SP_OBJECT_ID \
      --api 00000003-0000-0000-c000-000000000000 \
      --api-permissions 06b708a9-e830-4db3-a914-8e69da51d44f=Role

   # Grant admin consent for the permission
   az ad app permission admin-consent --id $SP_OBJECT_ID
   ```

At this point, the service principal should have the necessary permissions to deploy AWLS at the subscription level. Please additionally follow the steps below if you're deploying AWLS at the tenant level.

#### Additional Permissions for Tenant-Level Deployment
If you're deploying AWLS at the tenant level, you must also grant the `Microsoft.Authorization/roleAssignments/*` and `Microsoft.Authorization/roleDefinitions/*` permissions to the service principal, scoped to all monitored subscriptions (i.e., any other subscriptions in the tenant which you wish to scan with AWLS).
1. Create a json file defining a custom role with the permissions required to deploy AWLS. You can copy the following example and include the IDs of your monitored subscriptions in the `AssignableScopes` array.
   ```json
   // ./awls-deployment-monitored-subscriptions-role.json
   {
      "Name": "AWLS Deployment (monitored subscriptions)",
      "Description": "Role for deploying AWLS at the tenant level",
      "Actions": [
         "Microsoft.Authorization/roleAssignments/*",
         "Microsoft.Authorization/roleDefinitions/*"
      ],
      "AssignableScopes": [
         "/subscriptions/<monitored-subscription-id-1>",
         "/subscriptions/<monitored-subscription-id-2>",
         ...
      ]
   }
   ```
   Alternatively, you can make the role assignable to all subscriptions in the tenant by setting the scope to `/` (root scope).
   ```json
   // ./awls-deployment-monitored-subscriptions-role.json
   {
      "Name": "AWLS Deployment (monitored subscriptions)",
      "Description": "Role for deploying AWLS at the tenant level",
      "Actions": [
         "Microsoft.Authorization/roleAssignments/*",
         "Microsoft.Authorization/roleDefinitions/*"
      ],
      "AssignableScopes": [
         "/"
      ]
   }  
   ```

2. Create the custom role, passing the json file created in the previous step as the role definition.
   ```bash
   az role definition create --role-definition ./awls-deployment-monitored-subscriptions-role.json
   ```

3. Assign the custom role to the previously created service principal (scoped to all monitored subscriptions).
   ```bash
   az role assignment create --assignee $SP_OBJECT_ID --role "AWLS Deployment (monitored subscriptions)" --scope /subscriptions/<monitored-subscription-id-1> /subscriptions/<monitored-subscription-id-2> ...
   ```
   Alternatively, you can assign the role to all subscriptions in the tenant by setting the scope to `/` (root scope).
   ```bash
   az role assignment create --assignee $SP_OBJECT_ID --role "AWLS Deployment (monitored subscriptions)" --scope /
   ```

### Authenticating with the Service Principal

Once the service principal has been created with the necessary permissions, you can authenticate Azure CLI using the service principal as instructed here: https://learn.microsoft.com/en-us/cli/azure/authenticate-azure-cli-service-principal.
