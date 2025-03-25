import pytest

from preflight_check.core.models import RolePermissions


class TestRolePermission:
    """Test the RolePermission class"""

    test_cases = [
        {
            "permissions": RolePermissions(
                actions=[
                    "Microsoft.Compute/virtualMachines/read",
                    "Microsoft.Compute/virtualMachines/write",
                    "Microsoft.Compute/virtualMachines/delete",
                ],
            ),
            "cases": [
                ("Microsoft.Compute/virtualMachines/read", True),
                ("Microsoft.Compute/storageAccounts/delete", False),
            ],
        },
        {
            "permissions": RolePermissions(
                actions=[
                    "Microsoft.Compute/*/read",
                ],
            ),
            "cases": [
                ("Microsoft.Compute/virtualMachinesScaleSets/read", True),
                ("Microsoft.Compute/virtualMachinesScaleSets/write", False),
                (
                    "Microsoft.Compute/virtualMachinesScaleSets/virtualMachines/read",
                    True,
                ),
                (
                    "Microsoft.Compute/virtualMachinesScaleSets/virtualMachines/write",
                    False,
                ),
                ("Microsoft.Network/virtualNetworks/read", False),
            ],
        },
        {
            "permissions": RolePermissions(
                actions=[
                    "Microsoft.Compute/*",
                ],
                not_actions=[
                    "Microsoft.Compute/*/write",
                    "Microsoft.Compute/*/delete",
                ],
            ),
            "cases": [
                ("Microsoft.Compute/virtualMachinesScaleSets/read", True),
                ("Microsoft.Compute/virtualMachinesScaleSets/write", False),
                (
                    "Microsoft.Compute/virtualMachinesScaleSets/virtualMachines/read",
                    True,
                ),
                (
                    "Microsoft.Compute/virtualMachinesScaleSets/virtualMachines/write",
                    False,
                ),
                ("Microsoft.Network/virtualNetworks/read", False),
            ],
        },
        {
            "permissions": RolePermissions(
                actions=[
                    "Microsoft.Storage/storageAccounts/*",
                ],
                not_actions=[
                    "Microsoft.Storage/storageAccounts/listkeys/*",
                    "Microsoft.Storage/storageAccounts/blobServices/*",
                ],
            ),
            "cases": [
                ("Microsoft.Storage/storageAccounts/read", True),
                ("Microsoft.Storage/storageAccounts/listkeys/action", False),
            ],
        },
        {
            "permissions": RolePermissions(
                actions=[
                    "*/read",
                ],
            ),
            "cases": [
                ("Microsoft.Storage/storageAccounts/read", True),
                ("Microsoft.Compute/virtualMachines/read", True),
                ("Microsoft.Storage/storageAccounts/write", False),
                ("Microsoft.Compute/virtualMachines/delete", False),
            ],
        },
    ]

    @pytest.mark.parametrize(
        "role_permissions,action_string,expected",
        [
            (test_case["permissions"], action_string, expected)
            for test_case in test_cases
            for (action_string, expected) in test_case["cases"]
        ],
    )
    def test_grants_action(
        self,
        role_permissions: RolePermissions,
        action_string: str,
        expected: bool,
    ) -> None:
        """Test the grants_action method"""
        assert role_permissions.grants_action(action_string) == expected, (
            f"Expected {expected} for {action_string} in {role_permissions}"
        )
