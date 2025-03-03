from typing import Dict, List
from .azure import AzureClientFactory, SubscriptionClient, ComputeManagementClient

from ..models import Subscription, Region


class SubscriptionService:
    """Handles all interactions with Azure Subscriptions"""

    _azure: AzureClientFactory
    _subscriptions: Dict[str, Subscription] = None

    def __init__(self, azure_client_factory: AzureClientFactory):
        self.azure_client_factory = azure_client_factory

    def get_subscriptions(self) -> List[Subscription]:
        """
        Get all subscriptions available to the authenticated principal.

        Returns:
            List of Subscription objects
        """
        if not self._subscriptions:
            try:
                subs = self._subscription_client().subscriptions.list()
                self._subscriptions = {
                    sub.subscription_id: Subscription(
                        id=sub.subscription_id,
                        name=sub.display_name,
                        regions={}  # Empty initially, populated when needed
                    )
                    for sub in subs
                }
            except Exception as e:
                raise RuntimeError(f"Failed to list subscriptions: {str(e)}")
        return list(self._subscriptions.values())

    def get_subscription(self, subscription_id: str) -> Subscription:
        """
        Get a subscription by ID.
        """
        if subscription_id not in self._subscriptions:
            raise ValueError(f"Subscription {subscription_id} not found")
        return self._subscriptions[subscription_id]

    def get_subscription_vms(self, subscription: Subscription) -> Subscription:
        """
        Count VMs in each region for a subscription.
        Updates the subscription's regions with VM counts.

        Args:
            subscription: The subscription to enumerate

        Returns:
            Updated Subscription object with region VM counts
        """
        try:
            # Track instances by region
            vm_counts: Dict[str, int] = {}

            # List all VMs in the subscription
            for vm in self._compute_client(subscription.id).virtual_machines.list_all():
                region = vm.location.lower()
                vm_counts[region] = vm_counts.get(region, 0) + 1

            # Convert to Region objects
            subscription.regions = {
                name: Region(name=name, vm_count=count)
                for name, count in vm_counts.items()
            }

            # TODO: Add VMSS enumeration

            return subscription

        except Exception as e:
            # TODO: Better error handling
            raise RuntimeError(
                f"Failed to count VMs in subscription {subscription.id}: {str(e)}")

    def _compute_client(self, subscription_id: str) -> ComputeManagementClient:
        return self.azure_client_factory.get_compute_client(subscription_id)

    def _subscription_client(self) -> SubscriptionClient:
        return self.azure_client_factory.get_subscription_client()
