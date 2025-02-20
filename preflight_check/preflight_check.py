import math
import typer
from rich.console import Console
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.box import HEAVY_EDGE
from typing import Optional, List, Dict
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.subscription import SubscriptionClient
from rich.table import Table

DEFAULT_BATCH_SIZE = 4

# Initialize rich console for pretty output
console = Console()
app = typer.Typer()


class PreflightConfig:
    def __init__(
        self,
        integration_type: str,
        scanning_subscription: str,
        monitored_subscriptions: List[str],
        regions: List[str],
        use_nat_gateway: bool
    ):
        self.integration_type = integration_type
        self.scanning_subscription = scanning_subscription
        self.monitored_subscriptions = monitored_subscriptions
        self.regions = regions
        self.use_nat_gateway = use_nat_gateway


def prompt_for_config(credential: DefaultAzureCredential) -> PreflightConfig:
    """Interactive prompt for configuration values with user-friendly messages"""
    console.print("\n🔍 [bold]Preflight Check for Azure AWLS Deployment[/bold]")
    console.print("-" * 40)

    # Integration Type
    console.print("\n[bold]Integration Type[/bold]")
    console.print(
        "[dim]Choose whether to deploy the scanner at the tenant level or subscription level.[/dim]")
    integration_type = Prompt.ask(
        "Integration type",
        choices=["tenant", "subscription"]
    )

    console.print(
        "\n[dim]Enumerating subscriptions in the tenant...[/dim]")
    available_subscriptions = enumerate_subscriptions(credential)
    print_subscriptions(available_subscriptions)

    if integration_type == "subscription":
        console.print("\n[bold]Subscription[/bold]")
        console.print(
            "[dim]This is the subscription that you'd like AWLS to scan (and where the scanner resources will be deployed).[/dim]")
        scanning_subscription = Prompt.ask(
            "Subscription ID", choices=available_subscriptions.values(), show_choices=False)
        monitored_subscriptions = [scanning_subscription]
    else:
        monitored_subscriptions = prompt_for_monitored_subscriptions(
            available_subscriptions)
        console.print("\n[bold]Scanning Subscription[/bold]")
        console.print(
            "[dim]This is where the AWLS scanning resources will be deployed.[/dim]")
        scanning_sub = Prompt.ask("Subscription ID").strip()

    # Enumerate VMs for each subscription
    all_detected_regions = set()
    detected_vm_counts_by_sub: Dict[str, Dict[str, int]] = {}
    for subscription_id in monitored_subscriptions:
        subscription_name = available_subscriptions[subscription_id]
        console.print(
            f"\n[dim]Enumerating VMs in subscription {subscription_name}...[/dim]")
        try:
            vm_count_by_region = enumerate_instances_in_subscription(
                credential,
                subscription_id)
            detected_vm_counts_by_sub[subscription_id] = vm_count_by_region
            all_detected_regions.update(vm_count_by_region.keys())
        except Exception as e:
            console.print(
                f"[red]Failed to enumerate VMs in subscription {subscription_id}.[/red]")
            console.print(f"[dim]Error: {str(e)}[/dim]")

    # Show breakdown by region using table
    print_vm_counts(
        detected_vm_counts_by_sub, available_subscriptions)

    # Regions
    console.print("\n[bold]Deployment Regions[/bold]")
    console.print(
        "[dim]Enter the Azure regions that you'd like to monitor.[/dim]")
    console.print("[dim]The scanner will be deployed in these regions.[/dim]")

    # Use detected regions as default if available
    regions_default = ",".join(
        sorted(all_detected_regions)) if all_detected_regions else None
    regions_input = Prompt.ask(
        "Azure regions (comma-separated)",
        default=regions_default
    )
    regions = sorted([r.strip() for r in regions_input.split(",")])

    # filter VM count based on user-selected regions and print updated VM count
    detected_vm_counts_by_sub = {
        sub_id: {
            region: vm_count for region, vm_count in vm_counts.items() if region in regions
        }
        for sub_id, vm_counts in detected_vm_counts_by_sub.items()
    }
    console.print("\n[bold]Filtered VM Counts[/bold]")
    console.print(
        f"[dim]The following is the updated VM count based on the user-selected regions:[/dim]\n{', '.join(regions)}")
    print_vm_counts(detected_vm_counts_by_sub, available_subscriptions)

    # NAT Gateway
    console.print("\n[bold]Network Configuration[/bold]")
    console.print(
        "[dim]We recommend deploying AWLS with a NAT Gateway, but you can opt out if you prefer.[/dim]")
    use_nat_gateway = Confirm.ask(
        "Use NAT Gateway?",
        default=True
    )

    console.print("\n[bold]Quota Requirements[/bold]")
    console.print(
        f"Please ensure that the usage quotas configured in the subscription {scanning_sub} meet the required quotas:")
    print_quota_requirements(compute_quota_requirements(
        detected_vm_counts_by_sub, DEFAULT_BATCH_SIZE, use_nat_gateway))

    return PreflightConfig(
        integration_type=integration_type,
        scanning_subscription=scanning_sub,
        monitored_subscriptions=monitored_subscriptions,
        regions=regions,
        use_nat_gateway=use_nat_gateway
    )


def enumerate_instances_in_subscription(credential: DefaultAzureCredential, subscription_id: str) -> Dict[str, int]:
    """
    List all instances in a subscription, grouped by region.

    Args:
        subscription_id: The subscription to enumerate

    Returns:
        Dictionary mapping regions to instance counts
    """
    try:
        # Initialize the compute client
        compute_client = ComputeManagementClient(
            credential, subscription_id)

        # Track instances by region
        instances_by_region: Dict[str, int] = {}

        # List all VMs in the subscription
        for vm in compute_client.virtual_machines.list_all():
            # Extract region from VM location
            region = vm.location.lower()
            instances_by_region[region] = instances_by_region.get(
                region, 0) + 1

        # TODO: Add support for VMSS

        return instances_by_region

    except Exception as e:
        console.print(
            f"[red]Error enumerating VMs in subscription {subscription_id}: {str(e)}[/red]")
        raise


def prompt_for_monitored_subscriptions(available_subscriptions: Dict[str, str]) -> List[str]:
    """
    Prompt the user to select a subscription from a list of available subscriptions.
    """
    console.print("\n[bold]Monitored Subscriptions[/bold]")
    scan_scope = Prompt.ask(
        "Do you want to scan all subscriptions, exclude specific subscriptions, or specify a set of subscriptions to scan?",
        choices=["all", "exclude", "specify"],
        default="all"
    )
    if scan_scope == "all":
        console.print(
            "All subscriptions will be scanned.")
        monitored_subscriptions = available_subscriptions.keys()
    elif scan_scope == "exclude":
        console.print(
            "[dim]You can choose to exclude specific subscriptions from being scanned by providing their subscription IDs.[/dim]")
        excluded_subscriptions_input = Prompt.ask(
            "Excluded Subscription IDs (comma-separated)"
        )
        # Validate each subscription ID exists
        excluded_subs = {}
        for sub_id in [s.strip() for s in excluded_subscriptions_input.split(",")]:
            if sub_id not in available_subscriptions:
                console.print(
                    f"[red]Warning: Subscription {sub_id} not found in available subscriptions[/red]")
            else:
                excluded_subs[sub_id] = available_subscriptions[sub_id]

        monitored_subscriptions = set(
            available_subscriptions.keys()) - set(excluded_subs.keys())
        console.print(f"Excluding the following subscriptions:")
        print_subscriptions(excluded_subs)

    elif scan_scope == "specify":
        console.print(
            "[dim]You can choose to specify a set of subscriptions to scan by providing their subscription IDs.[/dim]")
        specified_subscriptions_input = Prompt.ask(
            "Specified Subscription IDs (comma-separated)"
        )
        # Validate each subscription ID exists
        specified_subs = {}
        for sub_id in [s.strip() for s in specified_subscriptions_input.split(",")]:
            if sub_id not in available_subscriptions:
                console.print(
                    f"[red]Warning: Subscription {sub_id} not found in available subscriptions[/red]")
            else:
                specified_subs[sub_id] = available_subscriptions[sub_id]

        monitored_subscriptions = specified_subs.keys()
        console.print(f"Only the following subscriptions will be scanned:")
        print_subscriptions(specified_subs)
    return monitored_subscriptions


def enumerate_subscriptions(credential: DefaultAzureCredential) -> Dict[str, str]:
    """
    Enumerate all subscriptions accessible to the credential.

    Args:
        credential: Azure credential object

    Returns:
        Dictionary mapping subscription IDs to their names
    """
    try:
        subscription_client = SubscriptionClient(credential)
        subscriptions = {
            sub.subscription_id: sub.display_name
            for sub in subscription_client.subscriptions.list()}
        return subscriptions
    except Exception as e:
        console.print(f"[red]Error enumerating subscriptions: {str(e)}[/red]")
        raise


def print_subscriptions(subscriptions: Dict[str, str]):
    """
    Print subscriptions in a formatted table.

    Args:
        subscriptions: Dictionary mapping subscription IDs to their names
    """
    table = Table(box=HEAVY_EDGE)

    # Add columns
    table.add_column("Subscription Name", style="cyan")
    table.add_column("Subscription ID", style="green")

    # Sort by subscription name and add rows
    for subscription_id, subscription_name in sorted(subscriptions.items(), key=lambda x: x[1].lower()):
        table.add_row(subscription_name, subscription_id)

    console.print(table)


def print_vm_counts(vm_counts_by_sub: Dict[str, Dict[str, int]], subscription_id_to_name: Dict[str, str]) -> int:
    """
    Print VM counts in a formatted table and return the total VM count.

    Args:
        vm_counts_by_sub: Dictionary mapping subscription IDs to their region-wise VM counts
    """
    table = Table(box=HEAVY_EDGE)

    # Add columns
    table.add_column("Subscription", style="cyan")
    table.add_column("Region", style="magenta")
    table.add_column("VM Count", style="green", justify="right")

    # Add rows
    total_vms = 0
    # Sort subscriptions by name
    sorted_subs = sorted(vm_counts_by_sub.items(),
                         key=lambda x: subscription_id_to_name[x[0]].lower())

    subscriptions_with_no_vms = {}
    for sub_id, regions in sorted_subs:
        sub_name = subscription_id_to_name[sub_id]
        # Sort regions alphabetically
        sorted_regions = sorted(regions.items(), key=lambda x: x[0].lower())

        if len(sorted_regions) == 0:
            subscriptions_with_no_vms[sub_id] = sub_name
            # TODO: print a warning that the subscription has no VMs
            continue

        if len(sorted_regions) == 1:
            # Single region - show both subscription name and ID
            region, count = sorted_regions[0]
            table.add_row(sub_name, region, str(count))
            table.add_row(sub_id, "", "")
            total_vms += count
        else:
            # Multiple regions
            printed_subscription_name = False
            printed_subscription_id = False
            for region, count in sorted_regions:
                if not printed_subscription_name:
                    table.add_row(sub_name, region, str(count))
                    printed_subscription_name = True
                elif not printed_subscription_id:
                    table.add_row(sub_id, region, str(count))
                    printed_subscription_id = True
                else:
                    table.add_row("", region, str(count))
                total_vms += count
        # Add a separator between subscriptions
        table.add_row()

    # Add total
    table.add_row("Total", "", str(total_vms), style="bold")

    console.print(table)
    return total_vms


def compute_quota_requirements(vm_counts_by_sub: Dict[str, Dict[str, int]], batch_size: int = None, use_nat_gateway: bool = True) -> Dict[str, Dict[str, int]]:
    """
    Compute the required regional vCPU and public IP quotas for a tenant based on the number of VMs to be scanned in each region.

    Args:
        vm_counts_by_sub: Dictionary mapping subscription IDs to their region-wise VM counts
    """
    # sum up the vm counts by region
    quota_requirements = {}
    for vm_counts_by_region in vm_counts_by_sub.values():
        for region, vm_count in vm_counts_by_region.items():
            if region not in quota_requirements:
                quota_requirements[region] = {"vm_count": vm_count}
            else:
                quota_requirements[region]["vm_count"] += vm_count

    # compute the regional quota requirements
    for region, quota_requirement in quota_requirements.items():
        # compute the required vcpu quota for each region
        quota_requirement["required_vcpu_quota"] = _required_regional_vcpu_quota(
            quota_requirement["vm_count"], batch_size)
        # if deploying without NAT Gateway, compute the required public IP quota for each region
        if not use_nat_gateway:
            quota_requirement["required_public_ip_quota"] = _required_regional_public_ip_quota(
                quota_requirement["vm_count"])

    return quota_requirements


def _required_regional_vcpu_quota(vm_count: int, batch_size: int = DEFAULT_BATCH_SIZE) -> int:
    """
    Compute the regional vCPU quota requirements given the number of VMs to be scanned.

    Args:
        vm_count: Number of VMs to be scanned
        batch_size: Number of VMs to be scanned in each batch
    """
    vcpu_per_vm = 2 / batch_size
    return math.ceil(vm_count * vcpu_per_vm)


def _required_regional_public_ip_quota(vm_count: int, batch_size: int = DEFAULT_BATCH_SIZE) -> int:
    """
    Compute the regional public IP quota requirements given the number of VMs to be scanned.

    Args:
        vm_count: Number of VMs to be scanned
        batch_size: Number of VMs to be scanned in each batch
    """
    return math.ceil(vm_count / batch_size)


def print_quota_requirements(quota_requirements: Dict[str, Dict[str, int]]):
    """
    Print the quota requirements in a formatted table.
    """
    should_print_public_ip_quota = "required_public_ip_quota" in quota_requirements[list(
        quota_requirements.keys())[0]]

    table = Table(box=HEAVY_EDGE)

    table.add_column("Region", style="magenta")
    table.add_column("VM count", style="green", justify="right")
    table.add_column("Required vCPU Quota", style="blue", justify="right")
    if should_print_public_ip_quota:
        table.add_column("Required Public IP Quota",
                         style="blue", justify="right")

    for region, quota_requirements in quota_requirements.items():
        if should_print_public_ip_quota:
            table.add_row(region, str(quota_requirements["vm_count"]), str(
                quota_requirements["required_vcpu_quota"]), str(quota_requirements["required_public_ip_quota"]))
        else:
            table.add_row(region, str(quota_requirements["vm_count"]), str(
                quota_requirements["required_vcpu_quota"]))

    console.print(table)


@app.command()
def main(
    integration_type: Optional[str] = typer.Option(
        None,
        help="Integration type: tenant or subscription"
    ),
    scanning_subscription: Optional[str] = typer.Option(
        None,
        "--scanning-subscription",
        "-s",
        help="Subscription ID where scanner resources will be deployed"
    ),
    regions: Optional[str] = typer.Option(
        None,
        "--regions",
        "-r",
        help="Comma-separated list of Azure regions where VMs are located"
    ),
    use_nat_gateway: Optional[bool] = typer.Option(
        None,
        "--use-nat-gateway",
        "-n",
        help="Use NAT Gateway for optimized networking (recommended for 1000+ VMs)"
    )
):
    """
    Preflight check for Azure Agentless Scanner deployment.
    If no arguments are provided, runs in interactive mode.
    """

    # Determine if we should run in interactive mode
    is_interactive = not all([
        integration_type,
        scanning_subscription,
        regions,
        use_nat_gateway is not None
    ])

    credential = DefaultAzureCredential()

    if is_interactive:
        config = prompt_for_config(credential)
    else:
        config = PreflightConfig(
            integration_type=integration_type,
            scanning_subscription=scanning_subscription,
            regions=regions.split(","),
            use_nat_gateway=use_nat_gateway
        )

    # Print configuration for verification
    console.print("\n[bold]Configuration Summary[/bold]")
    console.print(f"Integration Type: {config.integration_type}")
    console.print(f"Scanning Subscription ID: {config.scanning_subscription}")
    console.print(
        f"Monitored Subscriptions: {', '.join(config.monitored_subscriptions)}")
    console.print(f"Target Regions: {', '.join(config.regions)}")
    console.print(
        f"Using NAT Gateway: {'Yes' if config.use_nat_gateway else 'No'}\n")

    # TODO: Implement validation logic here


if __name__ == "__main__":
    app()
