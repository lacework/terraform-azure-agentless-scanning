from .. import models
from . import azure


class SubscriptionService:
    """Handles all interactions with Azure models.Subscriptions"""

    _azure: azure.AzureClientFactory
    _subscriptions: dict[str, models.Subscription] = {}

    def __init__(self, azure_client_factory: azure.AzureClientFactory) -> None:
        self.azure_client_factory = azure_client_factory
        self.get_subscriptions()

    def get_subscriptions(self) -> list[models.Subscription]:
        """
        Get all subscriptions available to the authenticated principal.

        Returns:
            List of models.Subscription objects
        """
        if not self._subscriptions:
            try:
                subs = self._subscription_client().subscriptions.list()
                self._subscriptions = {
                    sub.subscription_id: models.Subscription(
                        id=sub.subscription_id or "",
                        name=sub.display_name or "",
                        regions={},  # Empty initially, populated when needed
                    )
                    for sub in subs
                }
            except Exception as e:
                raise RuntimeError(f"Failed to list subscriptions: {str(e)}") from e
        return list(self._subscriptions.values())

    def get_subscription(self, subscription_id: str) -> models.Subscription:
        """
        Get a subscription by ID.
        """
        if subscription_id not in self._subscriptions:
            raise ValueError(f"models.Subscription {subscription_id} not found")
        return self._subscriptions[subscription_id]

    def get_subscription_vms(self, subscription: models.Subscription) -> models.Subscription:
        """
        Count VMs in each region for a subscription.
        Updates the subscription's regions with VM counts.

        Args:
            subscription: The subscription to enumerate

        Returns:
            Updated models.Subscription object with region VM counts
        """
        try:
            # Track instances by region
            vm_counts: dict[str, int] = {}

            # List all VMs in the subscription
            for vm in self._compute_client(subscription.id).virtual_machines.list_all():
                region = vm.location.lower()
                vm_counts[region] = vm_counts.get(region, 0) + 1

            # List all VMSS VMs in the subscription
            for vmss in self._compute_client(subscription.id).virtual_machine_scale_sets.list_all():
                region = vmss.location.lower()
                vmss_resource_group_name = _get_resource_group_name_from_vmss_id(vmss.id)
                for _ in self._compute_client(subscription.id).virtual_machine_scale_set_vms.list(
                    vmss_resource_group_name, vmss.name
                ):
                    vm_counts[region] = vm_counts.get(region, 0) + 1

            # Convert to Region objects
            subscription.regions = {
                region_name: models.Region(name=region_name, vm_count=vm_count)
                for region_name, vm_count in vm_counts.items()
            }

            return subscription

        except Exception as e:
            # TODO: Better error handling
            raise RuntimeError(
                f"Failed to count VMs in subscription {subscription.id}: {str(e)}"
            ) from e

    def _compute_client(self, subscription_id: str) -> azure.ComputeManagementClient:
        return self.azure_client_factory.get_compute_client(subscription_id)

    def _subscription_client(self) -> azure.SubscriptionClient:
        return self.azure_client_factory.get_subscription_client()

def _get_resource_group_name_from_vmss_id(vmss_id: str) -> str:
    """
    Extract the resource group name from a VMSS ID.

    VMSS ID format: /subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Compute/virtualMachineScaleSets/{vmScaleSetName}
    """
    id_parts = vmss_id.split("/")
    if len(id_parts) != 9:
        raise RuntimeError(f"Invalid VMSS ID: {vmss_id}")

    return id_parts[4]
