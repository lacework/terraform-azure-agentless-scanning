from .auth_check import MonitoredSubscriptionAuthCheck, ScanningSubscriptionAuthCheck
from .models import DeploymentConfig, Region, Subscription, UsageQuotaLimit
from .quota_check import (
    DSFamilyVCPUQuotaCheck,
    PublicIPQuotaCheck,
    StandardPublicIPQuotaCheck,
    TotalVCPUsQuotaCheck,
    UsageQuotaCheck,
)


class QuotaChecks:
    subscription: Subscription
    """Map of region name to list of quota checks for that region"""
    quota_checks: dict[str, list[UsageQuotaCheck]]

    def __init__(
        self,
        usage_quota_limits: dict[str, dict[str, UsageQuotaLimit]],
        subscription: Subscription,
        regions: list[Region],
        use_nat_gateway: bool,
    ) -> None:
        self.subscription = subscription
        self.quota_checks = {}
        for region in regions:
            vcpu_quota_checks = [
                check(_quota_limits=usage_quota_limits[region.name], region=region)
                for check in [TotalVCPUsQuotaCheck, DSFamilyVCPUQuotaCheck]
            ]
            public_ip_quota_checks = [
                check(
                    _quota_limits=usage_quota_limits[region.name],
                    region=region,
                    use_nat_gateway=use_nat_gateway,
                )
                for check in [PublicIPQuotaCheck, StandardPublicIPQuotaCheck]
            ]
            self.quota_checks[region.name] = [
                *vcpu_quota_checks,
                *public_ip_quota_checks,
            ]

    def all_checks_pass(self) -> bool:
        """Return True if all quota checks pass, False otherwise"""
        return all(
            check.success for quota_checks in self.quota_checks.values() for check in quota_checks
        )


class AuthChecks:
    scanning_subscription: ScanningSubscriptionAuthCheck
    monitored_subscriptions: list[MonitoredSubscriptionAuthCheck]

    def __init__(
        self, deployment_config: DeploymentConfig, permissions: dict[str, list[str]]
    ) -> None:
        self.scanning_subscription = ScanningSubscriptionAuthCheck(
            deployment_config.scanning_subscription,
            permissions[deployment_config.scanning_subscription.id],
        )
        self.monitored_subscriptions = [
            MonitoredSubscriptionAuthCheck(subscription, permissions[subscription.id])
            for subscription in deployment_config.monitored_subscriptions
        ]

    def all_checks_pass(self) -> bool:
        """Return True if all auth checks pass, False otherwise"""
        return (
            all(check.success for check in self.monitored_subscriptions)
            and self.scanning_subscription.success
        )


class PreflightCheck:
    deployment_config: DeploymentConfig
    usage_quota_checks: QuotaChecks
    auth_checks: AuthChecks

    def __init__(
        self,
        deployment_config: DeploymentConfig,
        usage_quota_limits: dict[str, dict[str, UsageQuotaLimit]],
        permissions: dict[str, list[str]],
    ) -> None:
        self.deployment_config = deployment_config
        regions = [
            Region(
                name=region_name,
                vm_count=sum(
                    sub.regions[region_name].vm_count if region_name in sub.regions else 0
                    for sub in deployment_config.monitored_subscriptions
                ),
            )
            for region_name in deployment_config.regions
        ]
        self.usage_quota_checks = QuotaChecks(
            usage_quota_limits=usage_quota_limits,
            subscription=deployment_config.scanning_subscription,
            regions=regions,
            use_nat_gateway=deployment_config.use_nat_gateway,
        )
        self.auth_checks = AuthChecks(deployment_config=deployment_config, permissions=permissions)
