import re
from dataclasses import dataclass, field


@dataclass
class RolePermissions:
    """Represents the permissions of an Azure role"""

    actions: list[str] = field(default_factory=list)
    not_actions: list[str] = field(default_factory=list)
    data_actions: list[str] = field(default_factory=list)
    not_data_actions: list[str] = field(default_factory=list)

    def grants_action(self, action_string: str) -> bool:
        """Checks if the role definition grants a specific action"""
        return (
            self._action_matches(action_string) and not self._not_action_matches(action_string)
        ) or (
            self._data_action_matches(action_string)
            and not self._not_data_action_matches(action_string)
        )

    def _action_matches(self, action_string: str) -> bool:
        """Checks if the role definition matches a specific action"""
        return any(self._pattern_matches(pattern, action_string) for pattern in self.actions)

    def _data_action_matches(self, action_string: str) -> bool:
        """Checks if the role definition matches a specific data action"""
        return any(self._pattern_matches(pattern, action_string) for pattern in self.data_actions)

    def _not_action_matches(self, action_string: str) -> bool:
        """Checks if the role definition matches a specific not action"""
        return any(self._pattern_matches(pattern, action_string) for pattern in self.not_actions)

    def _not_data_action_matches(self, action_string: str) -> bool:
        """Checks if the role definition matches a specific not data action"""
        return any(
            self._pattern_matches(pattern, action_string) for pattern in self.not_data_actions
        )

    def _pattern_matches(self, pattern: str, action_string: str) -> bool:
        """
        Convert Azure wildcard pattern to regex and check for match

        Azure uses * as wildcard for permissions, which needs to be converted
        to proper regex patterns
        """
        # Convert Azure permission pattern to regex pattern
        regex_pattern = "^" + pattern.replace("*", ".*") + "$"
        return bool(re.match(regex_pattern, action_string))


@dataclass
class Principal:
    """Represents a principal in an Azure role assignment"""

    id: str
    type: str

    def __str__(self) -> str:
        return f"{self.id} ({self.type})"


@dataclass
class AssignedRole:
    """Represents an Azure role assignment"""

    id: str
    name: str
    scope: str
    principal: Principal
    permissions: RolePermissions
    condition: str | None = None

    def grants_action(self, action_string: str) -> bool:
        """Checks if the role grants a specific action"""
        return self.permissions.grants_action(action_string)
