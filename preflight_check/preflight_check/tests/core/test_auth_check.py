import pytest

from preflight_check.core.auth_check import RequiredPermissionCheck
from preflight_check.core.models.auth import AssignedRole, Principal, RolePermissions


class TestRequiredPermissionCheck:
    """Test the RequiredPermissionCheck class"""

    principal = Principal(
        id="compute_write_only",
        type="User",
    )

    assigned_roles: list[AssignedRole] = [
        AssignedRole(
            id="compute_write_only",
            name="Compute Write Only",
            scope="*",
            principal=principal,
            permissions=RolePermissions(
                actions=[
                    "Microsoft.Compute/*/write",
                ],
            ),
        ),
        AssignedRole(
            id="storage_all_actions_no_child_types",
            name="Storage All Actions (No Child Types)",
            scope="*",
            principal=principal,
            permissions=RolePermissions(
                actions=[
                    "Microsoft.Storage/*",
                ],
                not_actions=[
                    "Microsoft.Storage/storageAccounts/listkeys/*",
                    "Microsoft.Storage/storageAccounts/blobServices/*",
                ],
            ),
        ),
        AssignedRole(
            id="allow_all_reads",
            name="Allow All Reads",
            scope="*",
            principal=principal,
            permissions=RolePermissions(
                actions=[
                    "*/read",
                ],
            ),
        ),
    ]

    @pytest.mark.parametrize(
        ("required_permission", "expected", "satisfying_role_id"),
        [
            ("Microsoft.Compute/virtualMachines/read", True, "allow_all_reads"),
            ("Microsoft.Compute/virtualMachines/write", True, "compute_write_only"),
            (
                "Microsoft.Storage/storageAccounts/read",
                True,
                ["storage_all_actions_no_child_types", "allow_all_reads"],
            ),
            ("Microsoft.Storage/storageAccounts/write", True, "storage_all_actions_no_child_types"),
            ("Microsoft.Storage/storageAccounts/listkeys/action", False, None),
            ("Microsoft.Compute/virtualMachines/delete", False, None),
        ],
    )
    def test_permission_matching(
        self,
        required_permission: str,
        expected: bool,
        satisfying_role_id: str | list[str] | None,
    ) -> None:
        """Test permission matching with various patterns"""
        check = RequiredPermissionCheck(
            required_permission,
            self.assigned_roles,
        )

        assert check.is_granted == expected
        if expected:
            assert check.satisfying_role is not None
            if isinstance(satisfying_role_id, list):
                assert check.satisfying_role.id in satisfying_role_id
            else:
                assert check.satisfying_role.id == satisfying_role_id
        else:
            assert check.satisfying_role is None
