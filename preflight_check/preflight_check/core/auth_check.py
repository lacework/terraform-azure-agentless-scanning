from abc import ABC, abstractmethod
from typing import List

from .models import Subscription


class Permission:
    """Represents an Azure permission"""
    resource_provider: str
    resource_type: str
    action: str

    def __init__(self, permission: str):
        # permission format: "{resourceProvider}/{resourceType}/{action}"
        if permission == "*":
            self.resource_provider = "*"
            self.resource_type = "*"
            self.action = "*"
            return
        parts = permission.split("/")
        if len(parts) == 1:
            raise ValueError(f"Invalid permission: {permission}")
        if len(parts) == 2:
            # a permission with 2 parts must include a wildcard
            if "*" not in parts:
                raise ValueError(f"Invalid permission: {permission}")
            # "*/{action}" -> {action} on all resource providers and types
            if parts[0] == "*":
                self.resource_provider = "*"
                self.resource_type = "*"
                self.action = parts[1]
                return
            # "{resourceProvider}/*" -> all actions on all resource types for the resource provider
            else:
                self.resource_provider = parts[0]
                self.resource_type = "*"
                self.action = "*"
                return
        self.resource_provider = parts[0]
        self.resource_type = "/".join(parts[1:-1])
        self.action = parts[-1]

    def __str__(self):
        return f"{self.resource_provider}/{self.resource_type}/{self.action}"

    def __repr__(self):
        return f"Permission(resource_provider={self.resource_provider}, resource_type={self.resource_type}, action={self.action})"

    def __eq__(self, other):
        resource_provider_match = self.resource_provider == other.resource_provider \
            or self.resource_provider == "*" \
            or other.resource_provider == "*"
        resource_type_match = self.resource_type == other.resource_type \
            or self.resource_type == "*" \
            or other.resource_type == "*"
        action_match = self.action == other.action \
            or self.action == "*" \
            or other.action == "*"
        return resource_provider_match and resource_type_match and action_match


class RequiredPermissionCheck():
    """Represents a permission that must be granted on a subscription"""
    required_permission: Permission
    is_granted: bool = False

    def __init__(self, required_permission: Permission, granted_permissions: List[Permission]):
        self.required_permission = required_permission
        self.is_granted = self.required_permission in granted_permissions

class AuthCheck(ABC):
    """
    Base class for MonitoredSubscriptionAuthCheck and ScanningSubscriptionAuthCheck
    """
    subscription: Subscription
    checked_permissions: List[RequiredPermissionCheck]

    def __init__(self, subscription: Subscription, granted_permission_strings: List[str]):
        """
        Checks whether the set of permissions granted for a subscription covers the required permissions
        :param subscription: The subscription to check
        :type subscription: Subscription
        :param granted_permissions: The set of permissions that have been granted to the authenticated principal for the subscription
        :type granted_permissions: List[str]
        """
        self.subscription = subscription
        granted_permissions = [Permission(
            permission_string) for permission_string in granted_permission_strings]
        self.checked_permissions = [
            RequiredPermissionCheck(required_permission, granted_permissions)
            for required_permission in self.required_permissions
        ]

    @property
    @abstractmethod
    def required_permissions_strings(self) -> List[str]:
        pass

    @property
    def required_permissions(self) -> List[Permission]:
        return [Permission(permission_string) for permission_string in self.required_permissions_strings]

    @property
    def success(self):
        return all(check.is_granted for check in self.checked_permissions)


class MonitoredSubscriptionAuthCheck(AuthCheck):
    """Defines the permissions required on a monitored subscription"""
    @property
    def required_permissions_strings(self) -> List[str]:
        return [
            "Microsoft.Authorization/roleAssignments/write",
            "Microsoft.Authorization/roleAssignments/delete",
            "Microsoft.Authorization/roleAssignments/read",
            "Microsoft.Authorization/roleDefinitions/write",
            "Microsoft.Authorization/roleDefinitions/delete",
            "Microsoft.Authorization/roleDefinitions/read",
        ]


class ScanningSubscriptionAuthCheck(AuthCheck):
    """Defines the permissions required on the scanning subscription"""
    @property
    def required_permissions_strings(self) -> List[str]:
        return [
            "Microsoft.App/jobs/read",
            "Microsoft.App/jobs/write",
            "Microsoft.App/jobs/delete",
            "Microsoft.App/jobs/start/action",
            "Microsoft.App/jobs/stop/action",
            "Microsoft.App/jobs/restart/action",
            "Microsoft.App/jobs/listSecrets/action",
            "Microsoft.App/managedEnvironments/read",
            "Microsoft.App/managedEnvironments/write",
            "Microsoft.App/managedEnvironments/delete",
            "Microsoft.App/managedEnvironments/certificates/read",
            "Microsoft.App/managedEnvironments/certificates/write",
            "Microsoft.App/managedEnvironments/certificates/delete",
            "Microsoft.App/managedEnvironments/storages/read",
            "Microsoft.App/managedEnvironments/storages/write",
            "Microsoft.App/managedEnvironments/storages/delete",
            "Microsoft.App/managedEnvironments/certificates/listSecrets/action",
            "Microsoft.Authorization/roleAssignments/read",
            "Microsoft.Authorization/roleAssignments/write",
            "Microsoft.Authorization/roleAssignments/delete",
            "Microsoft.Authorization/roleDefinitions/write",
            "Microsoft.Authorization/roleDefinitions/delete",
            "Microsoft.Authorization/roleDefinitions/read",
            "Microsoft.Compute/virtualMachines/read",
            "Microsoft.Compute/virtualMachineScaleSets/read",
            "Microsoft.Compute/virtualMachineScaleSets/virtualMachines/read",
            "Microsoft.KeyVault/vaults/read",
            "Microsoft.KeyVault/vaults/write",
            "Microsoft.KeyVault/vaults/delete",
            "Microsoft.KeyVault/vaults/accessPolicies/read",
            "Microsoft.KeyVault/vaults/accessPolicies/write",
            "Microsoft.KeyVault/vaults/secrets/read",
            "Microsoft.KeyVault/vaults/secrets/write",
            "Microsoft.KeyVault/vaults/secrets/delete",
            "Microsoft.KeyVault/vaults/secrets/recover/action",
            "Microsoft.KeyVault/vaults/certificates/read",
            "Microsoft.KeyVault/vaults/certificates/write",
            "Microsoft.KeyVault/vaults/certificates/delete",
            "Microsoft.KeyVault/vaults/certificates/recover/action",
            "Microsoft.KeyVault/vaults/keys/read",
            "Microsoft.KeyVault/vaults/keys/write",
            "Microsoft.KeyVault/vaults/keys/delete",
            "Microsoft.KeyVault/vaults/keys/recover/action",
            "Microsoft.KeyVault/vaults/backup/action",
            "Microsoft.KeyVault/vaults/restore/action",
            "Microsoft.KeyVault/locations/deletedVaults/purge/action",
            "Microsoft.KeyVault/locations/operationResults/read",
            "Microsoft.ManagedIdentity/userAssignedIdentities/read",
            "Microsoft.ManagedIdentity/userAssignedIdentities/write",
            "Microsoft.ManagedIdentity/userAssignedIdentities/delete",
            "Microsoft.ManagedIdentity/userAssignedIdentities/assign/action",
            "Microsoft.Network/natGateways/read",
            "Microsoft.Network/natGateways/write",
            "Microsoft.Network/natGateways/delete",
            "Microsoft.Network/natGateways/join/action",
            "Microsoft.Network/networkSecurityGroups/read",
            "Microsoft.Network/networkSecurityGroups/write",
            "Microsoft.Network/networkSecurityGroups/delete",
            "Microsoft.Network/networkSecurityGroups/join/action",
            "Microsoft.Network/networkSecurityGroups/securityRules/read",
            "Microsoft.Network/networkSecurityGroups/securityRules/write",
            "Microsoft.Network/networkSecurityGroups/securityRules/delete",
            "Microsoft.Network/publicIPAddresses/read",
            "Microsoft.Network/publicIPAddresses/write",
            "Microsoft.Network/publicIPAddresses/delete",
            "Microsoft.Network/publicIPAddresses/join/action",
            "Microsoft.Network/virtualNetworks/read",
            "Microsoft.Network/virtualNetworks/write",
            "Microsoft.Network/virtualNetworks/delete",
            "Microsoft.Network/virtualNetworks/join/action",
            "Microsoft.Network/virtualNetworks/subnets/read",
            "Microsoft.Network/virtualNetworks/subnets/write",
            "Microsoft.Network/virtualNetworks/subnets/delete",
            "Microsoft.Network/virtualNetworks/subnets/join/action",
            "Microsoft.Network/virtualNetworks/peers/read",
            "Microsoft.Network/virtualNetworks/peers/write",
            "Microsoft.Network/virtualNetworks/peers/delete",
            "Microsoft.OperationalInsights/workspaces/read",
            "Microsoft.OperationalInsights/workspaces/write",
            "Microsoft.OperationalInsights/workspaces/delete",
            "Microsoft.OperationalInsights/workspaces/query/action",
            "Microsoft.OperationalInsights/workspaces/search/action",
            "Microsoft.OperationalInsights/workspaces/data/read",
            "Microsoft.OperationalInsights/workspaces/schema/read",
            "Microsoft.OperationalInsights/workspaces/savedSearches/read",
            "Microsoft.OperationalInsights/workspaces/savedSearches/write",
            "Microsoft.OperationalInsights/workspaces/savedSearches/delete",
            "Microsoft.OperationalInsights/workspaces/intelligencePacks/read",
            "Microsoft.OperationalInsights/workspaces/intelligencePacks/write",
            "Microsoft.OperationalInsights/workspaces/intelligencePacks/delete",
            "Microsoft.OperationalInsights/workspaces/sharedKeys/read",
            "Microsoft.OperationalInsights/workspaces/sharedKeys/action",
            "Microsoft.Resources/subscriptions/resourcegroups/read",
            "Microsoft.Resources/subscriptions/resourcegroups/write",
            "Microsoft.Resources/subscriptions/resourcegroups/delete",
            "Microsoft.Resources/subscriptions/resourcegroups/deployments/read",
            "Microsoft.Resources/subscriptions/resourcegroups/deployments/write",
            "Microsoft.Resources/subscriptions/resourcegroups/deployments/delete",
            "Microsoft.Resources/subscriptions/resourcegroups/deployments/operations/read",
            "Microsoft.Resources/subscriptions/resourcegroups/resources/read",
            "Microsoft.Resources/subscriptions/resourcegroups/moveResources/action",
            "Microsoft.Resources/subscriptions/resourcegroups/validateMoveResources/action",
            "Microsoft.Storage/storageAccounts/read",
            "Microsoft.Storage/storageAccounts/write",
            "Microsoft.Storage/storageAccounts/delete",
            "Microsoft.Storage/storageAccounts/listkeys/action",
            "Microsoft.Storage/storageAccounts/regeneratekey/action",
            "Microsoft.Storage/storageAccounts/blobServices/read",
            "Microsoft.Storage/storageAccounts/queueServices/read",
            "Microsoft.Storage/storageAccounts/tableServices/read",
            "Microsoft.Storage/storageAccounts/fileServices/read",
            "Microsoft.Storage/storageAccounts/blobServices/read",
            "Microsoft.Storage/storageAccounts/blobServices/write",
            "Microsoft.Storage/storageAccounts/blobServices/delete",
            "Microsoft.Storage/storageAccounts/blobServices/containers/read",
            "Microsoft.Storage/storageAccounts/blobServices/containers/write",
            "Microsoft.Storage/storageAccounts/blobServices/containers/delete",
            "Microsoft.Storage/storageAccounts/blobServices/containers/blobs/read",
            "Microsoft.Storage/storageAccounts/blobServices/containers/blobs/write",
            "Microsoft.Storage/storageAccounts/blobServices/containers/blobs/delete",
            "Microsoft.Storage/storageAccounts/blobServices/containers/blobs/move/action",
            "Microsoft.Storage/storageAccounts/blobServices/containers/blobs/lease/action",
            "Microsoft.Storage/storageAccounts/fileServices/read",
            "Microsoft.Storage/storageAccounts/fileServices/write",
            "Microsoft.Storage/storageAccounts/fileServices/delete",
            "Microsoft.Storage/storageAccounts/fileServices/shares/read",
            "Microsoft.Storage/storageAccounts/fileServices/shares/write",
            "Microsoft.Storage/storageAccounts/fileServices/shares/delete",
            "Microsoft.Storage/storageAccounts/listKeys/action",
        ]
