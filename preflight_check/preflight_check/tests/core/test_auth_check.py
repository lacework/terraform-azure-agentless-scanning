import pytest

from preflight_check.core.auth_check import Permission, RequiredPermissionCheck

# Test case structure:
# (required_permission, granted_permissions, expected_result)
test_cases = [
    # Direct matches
    ("Microsoft.Storage/storageAccounts/read",
     ["Microsoft.Storage/storageAccounts/read"], True),
    ("Microsoft.KeyVault/vaults/read",
     ["Microsoft.KeyVault/vaults/read", "Microsoft.Storage/storageAccounts/write"], True),

    # Non-matches
    ("Microsoft.Storage/storageAccounts/read",
     ["Microsoft.Storage/storageAccounts/write"], False),
    ("Microsoft.Storage/storageAccounts/read",
     ["Microsoft.KeyVault/vaults/read"], False),
    ("Microsoft.Storage/storageAccounts/read", [], False),

    # Global wildcards (*/action)
    ("Microsoft.Storage/storageAccounts/read", ["*/read"], True),
    ("Microsoft.KeyVault/vaults/secrets/read", ["*/read"], True),
    ("Microsoft.Storage/storageAccounts/write", ["*/read"], False),

    # Namespace wildcards (Microsoft.Storage/*)
    ("Microsoft.Storage/storageAccounts/read", ["Microsoft.Storage/*"], True),
    ("Microsoft.Storage/storageAccounts/write", ["Microsoft.Storage/*"], True),
    ("Microsoft.Storage/storageAccounts/blobServices/containers/read",
     ["Microsoft.Storage/*"], False),
    ("Microsoft.KeyVault/vaults/read", ["Microsoft.Storage/*"], False),

    # Namespace level checking for wildcards
    ("Microsoft.StorageSync/storageSyncServices/read",
     ["Microsoft.Storage/*"], False),

    # Middle wildcards (Microsoft.Storage/*/action)
    ("Microsoft.Storage/storageAccounts/read",
     ["Microsoft.Storage/*/read"], True),
    ("Microsoft.Storage/blobServices/read",
     ["Microsoft.Storage/*/read"], True),
    ("Microsoft.Storage/storageAccounts/blobServices/read",
     ["Microsoft.Storage/*/read"], False),

    # Complex cases - multiple levels
    ("Microsoft.Storage/storageAccounts/blobServices/containers/read",
     ["Microsoft.Storage/storageAccounts/blobServices/*"], True),
    ("Microsoft.Storage/storageAccounts/fileServices/shares/read",
     ["Microsoft.Storage/storageAccounts/*/shares/read"], True),
    ("Microsoft.Storage/storageAccounts/fileServices/shares/write",
     ["Microsoft.Storage/storageAccounts/*/shares/read"], False),

    # Multiple permissions granted, only one needs to match
    ("Microsoft.Storage/storageAccounts/read",
     ["Microsoft.KeyVault/*", "Microsoft.Network/*", "Microsoft.Storage/*"], True),

    # Edge cases
    ("*/read", ["*/read"], True),  # Wildcard matching wildcard
]


class TestRequiredPermissionCheck:
    """Test the RequiredPermissionCheck class"""

    @pytest.mark.parametrize("required_permission_string,granted_permissions_strings,expected", test_cases)
    def test_permission_matching(self, required_permission_string, granted_permissions_strings, expected):
        """Test permission matching with various patterns"""
        # Arrange & Act
        required_permission = Permission(required_permission_string)
        granted_permissions = [Permission(permission_string)
                               for permission_string in granted_permissions_strings]
        check = RequiredPermissionCheck(
            required_permission, granted_permissions)

        # Assert
        assert check.is_granted == expected, \
            f"Required: {required_permission_string}, Granted: {granted_permissions_strings}, Expected: {expected}, Got: {check.is_granted}"
