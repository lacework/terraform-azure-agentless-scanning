from typing import Dict, Tuple
from .azure import AzureClientFactory, ComputeManagementClient, NetworkManagementClient

from ..models import UsageQuotaLimit


class QuotaService:
    """Handles all interactions with Azure Usage Quotas"""

    _azure_client_factory: AzureClientFactory

    # Cache of quotas for each subscription and region
    # Dict from (subscription_id, region) to a map of quota names to quota checks
    _quotas: Dict[Tuple[str, str], Dict[str, UsageQuotaLimit]] = {}

    def __init__(self, azure_client_factory: AzureClientFactory):
        self._azure_client_factory = azure_client_factory

    def get_quota_limit(self, subscription_id: str, region: str, quota_name: str) -> UsageQuotaLimit:
        """
        Get a usage quota limit for a subscription and region.

        Args:
            subscription_id: Subscription to get quota for
            region: Region to get quota for
            quota_name: Name of the quota to get

        Returns:
            Usage quota
        """
        regional_quotas_for_sub = self.get_quota_limits(
            subscription_id, region)
        if quota_name not in regional_quotas_for_sub:
            raise RuntimeError(
                f"Quota not found for subscription {subscription_id} in region {region} and quota {quota_name}")
        return regional_quotas_for_sub[quota_name]

    def get_quota_limits(self, subscription_id: str, region: str) -> Dict[str, UsageQuotaLimit]:
        """
        Get and cache compute and network usage quota limits for a subscription and region.

        Args:
            subscription_id: Subscription to get quotas for
            region: Region to get quotas for

        Returns:
            Dict of quota name to quota check
        """
        if (subscription_id, region) in self._quotas:
            return self._quotas[subscription_id, region]
        try:
            # Get compute quotas (cores)
            compute_usage = self._compute_client(
                subscription_id).usage.list(region)
            # Get network quotas (public IPs)
            network_usage = self._network_client(
                subscription_id).usages.list(region)
            # Cache quotas for this subscription and region
            self._quotas[subscription_id, region] = {
                usage.name.value: UsageQuotaLimit(
                    name=usage.name.value,
                    display_name=usage.name.localized_value,
                    limit=usage.limit
                )
                for usage in [*compute_usage, *network_usage]
            }
            return self._quotas[subscription_id, region]
        except Exception as e:
            raise RuntimeError(
                f"Failed to get quotas for subscription {subscription_id} in region {region}: {str(e)}")

    def _compute_client(self, subscription_id: str) -> ComputeManagementClient:
        return self._azure_client_factory.get_compute_client(subscription_id)

    def _network_client(self, subscription_id: str) -> NetworkManagementClient:
        return self._azure_client_factory.get_network_client(subscription_id)
