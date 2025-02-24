from typing import Dict, List
from azure.identity import DefaultAzureCredential
from azure.mgmt.subscription import SubscriptionClient
from azure.mgmt.compute import ComputeManagementClient

from ..models import Subscription, Region


class AzureService:
    """Handles all interactions with Azure APIs"""

    def __init__(self, credential: DefaultAzureCredential):
        self.credential = credential
        self._subscription_client = SubscriptionClient(credential)

    def list_subscriptions(self) -> List[Subscription]:
        """
        List all accessible subscriptions.
        
        Returns:
            List of Subscription objects
        """
        try:
            subs = self._subscription_client.subscriptions.list()
            return [
                Subscription(
                    id=sub.subscription_id,
                    name=sub.display_name,
                    regions={}  # Empty initially, populated when needed
                )
                for sub in subs
            ]
        except Exception as e:
            # TODO: Better error handling
            raise RuntimeError(f"Failed to list subscriptions: {str(e)}")

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
            compute_client = ComputeManagementClient(
                self.credential,
                subscription.id
            )

            # Track instances by region
            vm_counts: Dict[str, int] = {}

            # List all VMs in the subscription
            for vm in compute_client.virtual_machines.list_all():
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

    def check_permissions(self) -> List[str]:
        """
        Check if the authenticated principal has required permissions.
        
        Returns:
            List of missing permissions
        """
        # TODO: Implement permission checking
        return []

    def check_quotas(self, region: Region) -> Dict[str, int]:
        """
        Check quota limits for a region.
        
        Returns:
            Dictionary of quota limits
        """
        # TODO: Implement quota checking
        return {}
