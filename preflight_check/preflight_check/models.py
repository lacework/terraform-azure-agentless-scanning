from dataclasses import dataclass
from typing import Dict, List, Optional, Literal
from enum import Enum
from .helpers.quota import required_regional_vcpu_quota, required_regional_public_ip_quota


class IntegrationType(str, Enum):
    TENANT = "tenant"
    SUBSCRIPTION = "subscription"


@dataclass
class QuotaStatus:
    """Status of a quota check"""
    current: int
    required: int
    sufficient: bool
    remediation_url: Optional[str] = None


@dataclass
class Region:
    """Represents an Azure region with VM counts and quota requirements"""
    name: str
    vm_count: int

    def required_vcpu(self, batch_size: int) -> int:
        """Calculate required vCPUs based on VM count"""
        return required_regional_vcpu_quota(self.vm_count, batch_size)

    def required_public_ips(self, use_nat_gateway: bool, batch_size: int) -> int:
        """Calculate required public IPs based on NAT Gateway usage"""
        return required_regional_public_ip_quota(self.vm_count, use_nat_gateway, batch_size)


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
    use_nat_gateway: bool = True

    @property
    def all_regions(self) -> List[str]:
        """Get unique list of regions across all subscriptions"""
        regions = set()
        for sub in [self.scanning_subscription] + self.monitored_subscriptions:
            regions.update(sub.regions.keys())
        return sorted(regions)

    @property
    def total_vms(self) -> int:
        """Total VMs across all monitored subscriptions"""
        return sum(sub.total_vms for sub in self.monitored_subscriptions)
