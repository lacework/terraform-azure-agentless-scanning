from typing import List, Dict

from .models import DeploymentConfig, Subscription, Region, UsageQuotaLimit
from .quota_check import UsageQuotaCheck, TotalVCPUsQuotaCheck, DSFamilyVCPUQuotaCheck, PublicIPQuotaCheck, StandardPublicIPQuotaCheck


class QuotaChecks:
    subscription: Subscription
    """Map of region name to list of quota checks for that region"""
    quota_checks: Dict[str, List[UsageQuotaCheck]]

    def __init__(self,
                 usage_quota_limits: Dict[str, Dict[str, UsageQuotaLimit]],
                 subscription: Subscription,
                 regions: List[Region],
                 use_nat_gateway: bool):
        self.subscription = subscription
        self.quota_checks = {}
        for region in regions:
            vcpu_quota_checks = [
                check(
                    _quota_limits=usage_quota_limits[region.name],
                    region=region
                )
                for check in [TotalVCPUsQuotaCheck, DSFamilyVCPUQuotaCheck]
            ]
            public_ip_quota_checks = [
                check(
                    _quota_limits=usage_quota_limits[region.name],
                    region=region,
                    use_nat_gateway=use_nat_gateway
                )
                for check in [PublicIPQuotaCheck, StandardPublicIPQuotaCheck]
            ]
            self.quota_checks[region.name] = [
                *vcpu_quota_checks, *public_ip_quota_checks]

    def all_checks_pass(self) -> bool:
        """Return True if all quota checks pass, False otherwise"""
        return all(check.success for quota_checks in self.quota_checks.values() for check in quota_checks)


class PreflightCheck:
    deployment_config: DeploymentConfig
    usage_quota_checks: QuotaChecks

    def __init__(self,
                 deployment_config: DeploymentConfig,
                 usage_quota_limits: Dict[str, Dict[str, UsageQuotaLimit]]):
        self.deployment_config = deployment_config
        regions = [
            Region(
                name=region_name,
                vm_count=sum(
                    sub.regions[region_name].vm_count if region_name in sub.regions.keys(
                    ) else 0
                    for sub in deployment_config.monitored_subscriptions
                )
            )
            for region_name in deployment_config.regions
        ]
        self.usage_quota_checks = QuotaChecks(
            usage_quota_limits=usage_quota_limits,
            subscription=deployment_config.scanning_subscription,
            regions=regions,
            use_nat_gateway=deployment_config.use_nat_gateway
        )
