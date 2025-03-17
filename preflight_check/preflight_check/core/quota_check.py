from dataclasses import dataclass, field
# ABC = Abstract Base Class, used to make classes that can't be instantiated directly
from abc import ABC, abstractmethod
from math import ceil
from typing import Dict

from .models import Subscription, Region, UsageQuotaLimit


@dataclass
class UsageQuotaCheck(ABC):
    """Base class for Azure usage quota checks"""
    _quota_limits: Dict[str, UsageQuotaLimit]
    region: Region
    batch_size: int = 4

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for the quota"""
        pass

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable name"""
        pass

    @property
    @abstractmethod
    def fix_url(self) -> str:
        """URL for requesting quota increase"""
        pass

    @property
    @abstractmethod
    def required_quota(self) -> int:
        """Required quota for the region"""
        pass

    @property
    def configured_limit(self) -> int:
        return self._get_quota_limit(self.name)

    @property
    def success(self) -> bool:
        """Check if quota is sufficient"""
        if self.configured_limit is None:
            return False
        return self.configured_limit >= self.required_quota

    def _get_quota_limit(self, quota_name: str) -> int:
        return self._quota_limits[quota_name].limit


@dataclass
class VCPUQuotaCheck(UsageQuotaCheck):
    """Implements the logic for computing the required vCPU quota"""

    @property
    def required_quota(self) -> int:
        vcpu_per_vm = 2 / self.batch_size
        return ceil(self.region.vm_count * vcpu_per_vm)


@dataclass
class PublicIPQuotaCheck(UsageQuotaCheck):
    """Implements the logic for computing the required public IP quota"""
    use_nat_gateway: bool = False

    @property
    def required_quota(self) -> int:
        if self.use_nat_gateway:
            return 1
        return ceil(self.region.vm_count / self.batch_size)


@dataclass
class TotalVCPUsQuotaCheck(VCPUQuotaCheck):
    """Usage quota check for total regional vCPUs"""

    @property
    def name(self) -> str:
        return "cores"

    @property
    def display_name(self) -> str:
        return "Total Regional vCPUs"

    @property
    def fix_url(self) -> str:
        return "https://portal.azure.com/#blade/Microsoft_Azure_Capacity/QuotaRequestsBlade"


@dataclass
class DSFamilyVCPUQuotaCheck(VCPUQuotaCheck):
    """Usage quota check for combined DS family vCPUs"""

    @property
    def name(self) -> str:
        return "SUM_standardDSv3Family_standardDSv4Family_standardDSv5Family"

    @property
    def display_name(self) -> str:
        return "Sum of vCPU families (DSv3, DSv4, and DSv5)"

    @property
    def fix_url(self) -> str:
        return "https://portal.azure.com/#blade/Microsoft_Azure_Capacity/QuotaRequestsBlade"

    @property
    def configured_limit(self) -> int:
        """Sum the limits for the DS vCPU families"""
        dsv3 = self._get_quota_limit("standardDSv3Family")
        dsv4 = self._get_quota_limit("standardDSv4Family")
        dsv5 = self._get_quota_limit("standardDSv5Family")
        return dsv3 + dsv4 + dsv5


@dataclass
class PublicIPQuotaCheck(PublicIPQuotaCheck):
    """Usage quota check for public IP addresses"""

    @property
    def name(self) -> str:
        return "PublicIPAddresses"

    @property
    def display_name(self) -> str:
        return "Total Regional Public IPs"

    @property
    def fix_url(self) -> str:
        return "https://portal.azure.com/#blade/Microsoft_Azure_Capacity/QuotaRequestsBlade"


@dataclass
class StandardPublicIPQuotaCheck(PublicIPQuotaCheck):
    """Usage quota check for standard public IPv4 addresses"""

    @property
    def name(self) -> str:
        return "IPv4StandardSkuPublicIpAddresses"

    @property
    def display_name(self) -> str:
        return "Public IPv4 Addresses - Standard"

    @property
    def fix_url(self) -> str:
        return "https://portal.azure.com/#blade/Microsoft_Azure_Capacity/QuotaRequestsBlade"
