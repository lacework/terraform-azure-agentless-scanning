# Creating a Service Principal to Deploy AWLS
We suggest creating a new Azure service principal to use specifically for deploying AWLS. You can do so by executing the terraform module in this directory, or by following the steps below. 

Please note that in order to create the service principal with sufficient permissions (via the terraform module or manually by following the steps below), the az cli must be authenticated as a principal with at least the following permissions:

* `Microsoft.Authorization/roleAssignments/*`
* `Microsoft.Authorization/roleDefinitions/*`
* `Microsoft.Graph/Application.ReadWrite.All`
* `Microsoft.Graph/Directory.ReadWrite.All`

If you do not wish to create a new service principal, you can authenticate as an Azure user, as long as the user has the necessary permissions listed in the steps below.

## Create a New Service Principal
Create a new service principal named `awls-deployment-sp`.
```bash
az ad sp create-for-rbac --name "awls-deployment-sp"
```
In the following steps, we will assign the necessary permissions to this service principal.

## Assign Permissions to the Service Principal
1. Create a custom role that grants permissions required in the scanning subscription (i.e., the subscription where AWLS resources will be deployed).
   1. Create a json file with the following role definition and replace `<scanning-subscription-id>` with the ID of your scanning subscription.
      ```json
      // ./awls-deployment-role.json
      {
         "Name": "AWLS Deployment",
         "Description": "Permissions required on scanning subscription to deploy AWLS",
         "Actions": [
            "Microsoft.App/jobs/*",
            "Microsoft.App/managedEnvironments/*",
            "Microsoft.Authorization/roleAssignments/*",
            "Microsoft.Authorization/roleDefinitions/*",
            "Microsoft.Compute/virtualMachines/read",
            "Microsoft.Compute/virtualMachines/delete",
            "Microsoft.Compute/virtualMachineScaleSets/read",
            "Microsoft.Compute/virtualMachineScaleSets/virtualMachines/read",
            "Microsoft.KeyVault/vaults/*",
            "Microsoft.KeyVault/locations/deletedVaults/purge/*",
            "Microsoft.KeyVault/locations/operationResults/*",
            "Microsoft.ManagedIdentity/userAssignedIdentities/*",
            "Microsoft.Network/natGateways/*",
            "Microsoft.Network/networkSecurityGroups/*",
            "Microsoft.Network/publicIPAddresses/*",
            "Microsoft.Network/virtualNetworks/*",
            "Microsoft.OperationalInsights/workspaces/*",
            "Microsoft.OperationalInsights/workspaces/sharedKeys/*",
            "Microsoft.Resources/subscriptions/resourcegroups/*",
            "Microsoft.Storage/storageAccounts/*",
            "Microsoft.Storage/storageAccounts/blobServices/*",
            "Microsoft.Storage/storageAccounts/fileServices/*",
            "Microsoft.Storage/storageAccounts/listKeys/*"
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
2. Create another custom role that grants permissions required in the monitored subscriptions (i.e., any subscriptions in the tenant which you wish to scan with AWLS). 
   1. Create a json file with the following role definition and replace `<tenant-id>` with the ID of your Azure tenant.
   ```json
      // ./awls-deployment-monitored-subscriptions-role.json
      {
         "Name": "AWLS Deployment - Monitored Subscriptions",
         "Description": "Permissions required on all monitored subscriptions to deploy AWLS",
         "Actions": [
            "Microsoft.Authorization/roleAssignments/*",
            "Microsoft.Authorization/roleDefinitions/*"
         ],
         "AssignableScopes": [
            "/providers/Microsoft.Management/managementGroups/<tenant-id>"
         ]
      }  
      ```
      > [!TIP]
      > `<tenant-id>` is the ID of your Azure Active Directory tenant - you can retrieve it by running `az account show --query 'tenantId' -o tsv`.
   2. Create the custom role, passing the json file created in the previous step as the role definition.
      ```bash
      az role definition create --role-definition ./awls-deployment-monitored-subscriptions-role.json
      ```
3. Assign the custom roles to the previously created service principal (`awls-deployment-sp`).
   1. Get the service principal object ID
      ```bash
      SP_OBJECT_ID=$(az ad sp list --display-name "awls-deployment-sp" --query '[0].id' -o tsv)
      ```
   2. Assign the `AWLS Deployment` role to the service principal, scoped to the scanning subscription.
      ```bash
      az role assignment create --assignee $SP_OBJECT_ID --role "AWLS Deployment" --scope "/subscriptions/<scanning-subscription-id>"
      ```
   2. Assign the `AWLS Deployment - Monitored Subscriptions` role to the service principal, scoped to the root management group.
      ```bash
      az role assignment create --assignee $SP_OBJECT_ID --role "AWLS Deployment - Monitored Subscriptions" --scope "/providers/Microsoft.Management/managementGroups/<tenant-id>"
      ```
      > [!NOTE]
      > Alternatively, if you want AWLS to only monitor a fixed subset of subscriptions rather than all subscriptions in the tenant (i.e., subscription-level integration instead of tenant-level integration), you can scope the role assignment to that specific set of subscriptions as follows:
      > ```bash
      > az role assignment create --assignee $SP_OBJECT_ID --role "AWLS Deployment - Monitored Subscriptions" --scope "/subscriptions/<monitored-subscription-id-1>"
      >
      > az role assignment create --assignee $SP_OBJECT_ID --role "AWLS Deployment - Monitored Subscriptions" --scope "/subscriptions/<monitored-subscription-id-2>"
      >
      > ...
      > ```
4. Finally, grant the required `Microsoft.Graph/Application.ReadWrite.OwnedBy` permission to the service principal. For context, this permission enables the service principal to create applications as well as update and delete applications it creates.
   > [!NOTE]
   > Granting this permission requires admin consent, so the user running these commands needs to have _Global Administrator_ or _Privileged Role Administrator_ rights in the Azure AD tenant.
   1. Get the service principal application ID
      ```bash
      SP_APP_ID=$(az ad app list --display-name "awls-deployment-sp" --query '[0].id' -o tsv)
      ```
   2. Add the API permission. For reference, `00000003-0000-0000-c000-000000000000` is Microsoft Graph's application ID and `18a4783c-866b-4cc7-a460-3d5e5662c884` is the `Application.ReadWrite.OwnedBy` permission ID
      ```bash
      az ad app permission add --id $SP_APP_ID \
         --api 00000003-0000-0000-c000-000000000000 \
         --api-permissions 18a4783c-866b-4cc7-a460-3d5e5662c884=Role
      ```
   3. Grant admin consent for the permission
      ```bash
      az ad app permission admin-consent --id $SP_APP_ID
      ```

Confirm that the custom roles have been successfully assigned to the service principal by running the following command:
```bash
az role assignment list --all --assignee $SP_OBJECT_ID --query "[].{roleDefinitionName:roleDefinitionName,scope:scope}" -o table
```
Expected output:
```bash
RoleDefinitionName                         Scope
-----------------------------------------  -------------------------------------------------------------------------------------
AWLS Deployment                            /subscriptions/0252a545-04d4-4262-a82c-ceef83344237
AWLS Deployment - Monitored Subscriptions  /providers/Microsoft.Management/managementGroups/a329d4bf-4557-4ccf-b132-84e7025ea22d
```

## Authenticating with the Service Principal

Once the service principal has been created and assigned the necessary permissions, you can authenticate Azure CLI using the service principal as instructed here: https://learn.microsoft.com/en-us/cli/azure/authenticate-azure-cli-service-principal.