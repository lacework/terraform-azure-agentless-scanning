import asyncio
import json
import subprocess

from azure.mgmt.authorization.v2022_04_01.models import RoleAssignment, RoleDefinition
from msgraph import GraphServiceClient

from preflight_check.core import models

from .azure import AuthorizationManagementClient, AzureClientFactory


class AuthService:
    """Handles all interactions with Azure Auth"""

    _azure_client_factory: AzureClientFactory
    _principal_id: str
    _tenant_id: str

    """Map from role definition ID to role definition"""
    _role_definitions: dict[str, RoleDefinition] = {}
    """Map from role definition ID to role permissions"""
    _role_permissions: dict[str, models.RolePermissions] = {}

    def __init__(self, azure_client_factory: AzureClientFactory) -> None:
        self._azure_client_factory = azure_client_factory
        self._principal_id, self._tenant_id = asyncio.run(
            self._get_principal_and_tenant_id())

    def get_all_assigned_roles(
        self,
        subscriptions: list[models.Subscription],
        include_root_management_group: bool = True,
    ) -> dict[str, list[models.AssignedRole]]:
        """
        Lists all roles that the authenticated principal has for a list of subscriptions.
        """
        assigned_roles = {}
        for subscription in subscriptions:
            assigned_roles[subscription.id] = self._get_assigned_roles_for_subscription(
                subscription.id
            )
        if include_root_management_group:
            root_roles = self._get_assigned_roles_for_root_management_group(subscriptions[0].id)
            assigned_roles[self.get_root_management_group_id()] = root_roles
        return assigned_roles

    # def get_assigned_roles_for_subscription(
    #     self,
    #     subscription_id: str,
    # ) -> list[models.AssignedRole]:
    #     """
    #     Lists the roles that the authenticated principal has for a subscription.
    #     """
    #     auth_client = self._auth_client(subscription_id)
    #     role_assignments = auth_client.role_assignments.list_for_subscription(
    #         filter=f"assignedTo('{self._principal_id}')"
    #     )
    #     assigned_roles = []
    #     for role_assignment in role_assignments:
    #         role_definition = self._get_role_definition(
    #             subscription_id, role_assignment.role_definition_id)
    #         assigned_roles.append(self._create_role(role_assignment, role_definition))
    #     return assigned_roles

    def _get_assigned_roles_for_subscription(
        self,
        subscription_id: str,
    ) -> list[models.AssignedRole]:
        """
        Lists the roles that the authenticated principal has for a subscription.
        """
        return self._get_assigned_roles_for_scope(
            subscription_id, f"/subscriptions/{subscription_id}"
        )

    def _get_assigned_roles_for_root_management_group(
        self, subscription_id: str
    ) -> list[models.AssignedRole]:
        """
        Lists the roles that the authenticated principal has for the root management group.
        """
        return self._get_assigned_roles_for_scope(
            subscription_id, self.get_root_management_group_id()
        )

    def _get_assigned_roles_for_scope(
        self,
        subscription_id: str,
        scope: str,
    ) -> list[models.AssignedRole]:
        """
        Lists the roles that the authenticated principal has for a scope.
        """
        auth_client = self._auth_client(subscription_id)
        role_assignments = auth_client.role_assignments.list_for_scope(
            scope, filter=f"assignedTo('{self._principal_id}')"
        )
        assigned_roles = []
        for role_assignment in role_assignments:
            role_definition = self._get_role_definition(
                subscription_id, role_assignment.role_definition_id
            )
            assigned_roles.append(self._create_role(role_assignment, role_definition))
        return assigned_roles

    def _create_role(
        self,
        role_assignment: RoleAssignment,
        role_definition: RoleDefinition,
    ) -> models.AssignedRole:
        """
        Create a Role object from an Azure RoleAssignment and RoleDefinition.
        """
        return models.AssignedRole(
            id=role_assignment.role_definition_id or "",
            name=role_definition.role_name or "",
            scope=role_assignment.scope or "",
            principal=models.Principal(
                id=role_assignment.principal_id or "",
                type=role_assignment.principal_type or "",
            ),
            permissions=self._get_permissions_from_role_definition(role_definition),
            condition=role_assignment.condition or None,
        )

    def _get_permissions_from_role_definition(
        self, role_definition: RoleDefinition
    ) -> models.RolePermissions:
        """
        Get permissions from a role definition.

        Returns:
            List of permissions
        """
        if role_definition.id not in self._role_permissions:
            if not role_definition.permissions:
                raise ValueError("Role definition has no permissions")
            permissions = models.RolePermissions()
            for permission in role_definition.permissions:
                permissions.actions.extend(permission.actions or [])
                permissions.not_actions.extend(permission.not_actions or [])
                permissions.data_actions.extend(permission.data_actions or [])
                permissions.not_data_actions.extend(permission.not_data_actions or [])
            self._role_permissions[role_definition.id] = permissions
        return self._role_permissions[role_definition.id]

    def _get_role_definition(self, subscription_id: str, role_definition_id: str) -> RoleDefinition:
        """
        Get a role definition by ID.
        """
        if role_definition_id not in self._role_definitions:
            self._role_definitions[role_definition_id] = self._auth_client(
                subscription_id
            ).role_definitions.get_by_id(role_definition_id)
        return self._role_definitions[role_definition_id]

    def get_root_management_group_id(self) -> str:
        """
        Get the ID of the root management group.
        """
        return f"/providers/Microsoft.Management/managementGroups/{self._tenant_id}"

    async def _get_principal_and_tenant_id(self) -> tuple[str, str]:
        """
        Get the principal ID of the authenticated principal.
        """
        account_show_response = subprocess.run(
            ["az", "account", "show"], capture_output=True, text=True, check=True
        )
        account = json.loads(account_show_response.stdout)
        # get the tenant ID from the account show response
        tenant_id = account.get("tenantId")
        if not tenant_id:
            raise RuntimeError("No tenant ID found for user")
        # get the principal ID
        principal = account.get("user", {})
        # determine if the authenticated principal is a user or service principal
        principal_id: str = ""
        is_service_principal = principal.get("type") == "servicePrincipal"
        # for service principals, the principal ID is in the account show response
        if is_service_principal:
            principal_id = principal.get("name")
            if not principal_id:
                raise RuntimeError(
                    "No principal ID found for service principal; response:",
                    f"\n{account_show_response.stdout}",
                )
        # for users, get the principal ID from the graph client
        else:
            principal = await self._graph_client().me.get()
            principal_id = principal.id
            if not principal_id:
                raise RuntimeError("No principal ID found for user")
        return principal_id, tenant_id

    def _auth_client(self, subscription_id: str) -> AuthorizationManagementClient:
        return self._azure_client_factory.get_auth_client(subscription_id)

    def _graph_client(self) -> GraphServiceClient:
        return self._azure_client_factory.get_graph_client()
