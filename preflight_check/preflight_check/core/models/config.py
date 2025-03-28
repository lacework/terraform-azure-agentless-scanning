from dataclasses import dataclass
from enum import Enum


class IntegrationType(str, Enum):
    TENANT = "tenant"
    SUBSCRIPTION = "subscription"


@dataclass
class Region:
    """Represents an Azure region with VM counts and quota requirements"""

    name: str
    vm_count: int


@dataclass
class Subscription:
    """Represents an Azure subscription"""

    id: str
    name: str
    regions: dict[str, Region]

    @property
    def total_vms(self) -> int:
        """Total VMs across all regions"""
        return sum(region.vm_count for region in self.regions.values())

    def __str__(self) -> str:
        return f"{self.name} ({self.id})"


@dataclass
class DeploymentConfig:
    """Configuration for AWLS deployment"""

    integration_type: IntegrationType
    scanning_subscription: Subscription
    monitored_subscriptions: list[Subscription]
    regions: list[str]
    use_nat_gateway: bool = True
