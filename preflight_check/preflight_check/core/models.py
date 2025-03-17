from dataclasses import dataclass
from typing import Dict, List, Optional, Literal
from enum import Enum
from ..helpers.quota import required_regional_vcpu_quota, required_regional_public_ip_quota


class IntegrationType(str, Enum):
    TENANT = "tenant"
    SUBSCRIPTION = "subscription"


@dataclass
class UsageQuotaLimit:
    """Represents an Azure usage quota limit"""
    name: str
    display_name: str
    limit: int


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
    regions: Dict[str, Region]

    @property
    def total_vms(self) -> int:
        """Total VMs across all regions"""
        return sum(region.vm_count for region in self.regions.values())


@dataclass
class DeploymentConfig:
    """Configuration for AWLS deployment"""
    integration_type: IntegrationType
    scanning_subscription: Subscription
    monitored_subscriptions: List[Subscription]
    regions: List[str]
    use_nat_gateway: bool = True
