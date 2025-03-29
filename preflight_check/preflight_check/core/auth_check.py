from abc import ABC, abstractmethod

from preflight_check.core.models import AssignedRole, Subscription


class RequiredPermissionCheck:
    """Represents a permission that must be granted on a subscription"""

    required_permission: str
    is_granted: bool
    satisfying_role: AssignedRole | None = None

    def __init__(self, required_permission: str, assigned_roles: list[AssignedRole]) -> None:
        self.required_permission = required_permission
        for role in assigned_roles:
            if role.grants_action(required_permission):
                self.satisfying_role = role
                break
        self.is_granted = self.satisfying_role is not None


class AuthCheck(ABC):
    """
    Base class for MonitoredSubscriptionAuthCheck and ScanningSubscriptionAuthCheck
    """

    subscription: Subscription
    checked_permissions: list[RequiredPermissionCheck]

    def __init__(self, subscription: Subscription, assigned_roles: list[AssignedRole]) -> None:
        """
        Checks whether the set of assigned roles covers the required permissions

        Args:
            subscription: The subscription to check
            assigned_roles: The set of roles that have been assigned to the authenticated principal
            for the subscription
        """
        self.subscription = subscription
        self.checked_permissions = [
            RequiredPermissionCheck(required_permission, assigned_roles)
            for required_permission in self.required_permissions
        ]

    @property
    @abstractmethod
    def required_permissions(self) -> list[str]:
        pass

    @property
    def success(self) -> bool:
        return all(check.is_granted for check in self.checked_permissions)

    @property
    def missing_permissions(self) -> list[RequiredPermissionCheck]:
        return [check for check in self.checked_permissions if not check.is_granted]


class MonitoredSubscriptionAuthCheck(AuthCheck):
    """Defines the permissions required on a monitored subscription"""

    @property
    def required_permissions(self) -> list[str]:
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
    def required_permissions(self) -> list[str]:
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
            "Microsoft.Storage/storageAccounts/fileServices/read",
            "Microsoft.Storage/storageAccounts/fileServices/write",
            "Microsoft.Storage/storageAccounts/fileServices/delete",
            "Microsoft.Storage/storageAccounts/fileServices/shares/read",
            "Microsoft.Storage/storageAccounts/fileServices/shares/write",
            "Microsoft.Storage/storageAccounts/fileServices/shares/delete",
            "Microsoft.Storage/storageAccounts/listKeys/action",
        ]