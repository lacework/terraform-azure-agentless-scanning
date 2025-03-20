import asyncio
from typing import List, Dict, Tuple
from .azure import AzureClientFactory, AuthorizationManagementClient
from msgraph import GraphServiceClient
from azure.mgmt.authorization.v2022_04_01.models import RoleAssignment, RoleDefinition


class AuthService:
    """Handles all interactions with Azure Auth"""

    _azure_client_factory: AzureClientFactory
    _principal_id: str
    _tenant_id: str

    """Map from role definition ID to role definition"""
    _role_definitions: Dict[str, RoleDefinition] = {}

    def __init__(self, azure_client_factory: AzureClientFactory):
        self._azure_client_factory = azure_client_factory
        self._principal_id, self._tenant_id = asyncio.run(
            self._get_principal_and_tenant_id())

    def get_permissions_for_subscription(self, subscription_id: str) -> List[str]:
        """
        Lists the permissions that the authenticated principal has for a subscription.

        Returns:
            List of permissions
        """
        # List role assignments
        auth_client = self._auth_client(subscription_id)
        role_assignments = auth_client.role_assignments.list_for_subscription(
            filter=f"assignedTo('{self._principal_id}')"
        )
        # Get permissions from role assignments
        permissions = [
            permission
            for role_assignment in role_assignments
            for permission in self._get_permissions_from_role_assignment(subscription_id, role_assignment)
        ]
        return permissions

    def get_permissions_for_root_management_group(self, subscription_id: str):
        """
        Lists the permissions that the authenticated principal has for the root management group.

        Returns:
            List of permissions
        """
        auth_client = self._auth_client(subscription_id)
        print('\n\nGetting permissions for root management group - WITH FILTER...\n\n')
        role_assignments = auth_client.role_assignments.list_for_scope(
            self.get_root_management_group_id(),
            filter=f"assignedTo('{self._principal_id}')"
        )
        permissions = self._get_permissions_from_role_assignment_list(
            self.get_root_management_group_id(), role_assignments)
        return permissions

    def _get_permissions_from_role_assignment_list(self, subscription_id: str, role_assignments: List[RoleAssignment]) -> List[str]:
        """
        Get permissions from a list of role assignments.
        """
        return [
            permission
            for role_assignment in role_assignments
            for permission in self._get_permissions_from_role_assignment(subscription_id, role_assignment)
        ]

    def _get_permissions_from_role_assignment(self, subscription_id: str, assignment: RoleAssignment) -> List[str]:
        """
        Get permissions from a role assignment.

        Returns:
            List of permissions
        """
        role_definition_id = assignment.role_definition_id
        print(
            f'Getting permissions for assignment {assignment.id}\n\tscope: {assignment.scope}\n\tprincipal: {assignment.principal_id} ({assignment.principal_type})\n\trole definition: {role_definition_id}')
        # get role definition
        role_definition = self._get_role_definition(
            subscription_id, role_definition_id)
        # get permissions from role definition
        permissions = []
        if role_definition.permissions:
            permissions = [
                action
                for permission in role_definition.permissions
                for action in permission.actions
            ]
        return permissions

    def _get_role_definition(self, subscription_id: str, role_definition_id: str) -> RoleDefinition:
        """
        Get a role definition by ID.
        """
        if role_definition_id not in self._role_definitions:
            self._role_definitions[role_definition_id] = self._auth_client(
                subscription_id).role_definitions.get_by_id(role_definition_id)
            permissions = []
            if self._role_definitions[role_definition_id].permissions:
                permissions = [
                    action
                    for permission in self._role_definitions[role_definition_id].permissions
                    for action in permission.actions
                ]
            print(
                f'=== Got role definition {role_definition_id} for subscription {subscription_id}\n\trole name: {self._role_definitions[role_definition_id].role_name} ({self._role_definitions[role_definition_id].role_type})\n\trole description: {self._role_definitions[role_definition_id].description}\n\tpermissions: {permissions}\n\tassignable scopes: {self._role_definitions[role_definition_id].assignable_scopes}')
        return self._role_definitions[role_definition_id]

    def get_root_management_group_id(self) -> str:
        """
        Get the ID of the root management group.
        """
        return f"/providers/Microsoft.Management/managementGroups/{self._tenant_id}"

    async def _get_principal_and_tenant_id(self) -> Tuple[str, str]:
        """
        Get the principal ID of the authenticated principal.
        """
        graph_client = self._graph_client()
        principal, org_response = await asyncio.gather(
            graph_client.me.get(),
            graph_client.organization.get()
        )
        tenant = org_response.value[0]
        return principal.id, tenant.id

    def _auth_client(self, subscription_id: str) -> AuthorizationManagementClient:
        return self._azure_client_factory.get_auth_client(subscription_id)

    def _graph_client(self) -> GraphServiceClient:
        return self._azure_client_factory.get_graph_client()
