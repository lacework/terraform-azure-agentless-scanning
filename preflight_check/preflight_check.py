import typer
from rich.console import Console
from rich.prompt import Prompt, Confirm
from typing import Optional, List, Dict
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.subscription import SubscriptionClient

# Initialize rich console for pretty output
console = Console()
app = typer.Typer()


class PreflightConfig:
    def __init__(
        self,
        integration_type: str,
        scanning_subscription: str,
        regions: List[str],
        vm_count: int,
        use_nat_gateway: bool
    ):
        self.integration_type = integration_type
        self.scanning_subscription = scanning_subscription
        self.regions = regions
        self.vm_count = vm_count
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

    subscriptions: List[str] = []

    # Scanning Subscription
    console.print("\n[bold]Scanning Subscription[/bold]")
    if integration_type == "tenant":
        console.print(
            "[dim]This is where the AWLS scanning resources will be deployed.[/dim]")
    else:
        console.print(
            "[dim]This is the subscription that you'd like AWLS to scan.[/dim]")
    scanning_sub = Prompt.ask("Subscription ID").strip()

    if integration_type == "tenant":
        # List Monitored Subscriptions
        console.print(
            "\n[dim]Enumerating subscriptions in the tenant...[/dim]")
        monitored_subscriptions = enumerate_subscriptions(credential)
        monitored_subscriptions_default = ",".join(monitored_subscriptions)
        console.print("\n[bold]Monitored Subscriptions[/bold]")
        console.print(
            "[dim]These are the subscriptions that you'd like AWLS to scan.[/dim]")
        monitored_subscriptions_input = Prompt.ask(
            "Subscription ID (comma-separated)",
            default=monitored_subscriptions_default)
        subscriptions = [s.strip()
                         for s in monitored_subscriptions_input.split(",")]
    else:
        subscriptions.append(scanning_sub)

    # Enumerate VMs for each subscription
    all_detected_regions = set()
    detected_vm_counts_by_sub: Dict[str, Dict[str, int]] = {}
    for sub in subscriptions:
        detected_vm_count = 0
        console.print(f"\n[dim]Enumerating VMs in subscription {sub}...[/dim]")
        try:
            vm_count_by_region = enumerate_instances_in_subscription(
                credential,
                sub)
            total_vm_count = sum(vm_count_by_region.values())

            # Show breakdown by region
            console.print("[bold]VMs detected in subscription {sub}:[/bold]")
            for region, count in vm_count_by_region.items():
                console.print(f"  {region}: {count} VMs")
            console.print(f"Total VMs detected in {sub}: {total_vm_count}")
            detected_vm_counts_by_sub[sub] = vm_count_by_region
            all_detected_regions.update(vm_count_by_region.keys())

        except Exception as e:
            console.print(
                "[red]Failed to enumerate VMs in subscription {sub}.[/red]")
            console.print(f"[dim]Error: {str(e)}[/dim]")

    # Regions
    console.print("\n[bold]Deployment Regions[/bold]")
    console.print(
        "[dim]Enter the Azure regions that you'd like to monitor.[/dim]")
    console.print("[dim]The scanner will be deployed in these regions.[/dim]")

    # Use detected regions as default if available
    regions_default = ",".join(
        all_detected_regions) if all_detected_regions else None
    regions_input = Prompt.ask(
        "Azure regions (comma-separated)",
        default=regions_default
    )
    regions = [r.strip() for r in regions_input.split(",")]

    # Only count VMs in the specified regions
    detected_vm_count = sum([sum([instances_by_region.get(
        region, 0) for region in regions]) for instances_by_region in detected_vm_counts_by_sub.values()])

    # VM Count
    console.print("\n[bold]VM Count[/bold]")
    if detected_vm_count > 0:
        console.print(
            f"We've detected {detected_vm_count} VMs across the specified subscriptions and regions that would be scanned by AWLS.")
        console.print("[dim]You can provide your own count if needed.[/dim]")
    else:
        console.print(
            "[dim]Please enter the number of VMs to be scanned.[/dim]")
    vm_count = int(Prompt.ask(
        "Number of VMs",
        default=str(detected_vm_count) if detected_vm_count > 0 else None
    ))

    # NAT Gateway
    console.print("\n[bold]Network Configuration[/bold]")
    console.print(
        "[dim]We recommend deploying AWLS with a NAT Gateway, but you can opt out if you prefer.[/dim]")
    use_nat = Confirm.ask(
        "Use NAT Gateway?",
        default=True
    )

    return PreflightConfig(
        integration_type=integration_type,
        scanning_subscription=scanning_sub,
        regions=regions,
        vm_count=vm_count,
        use_nat_gateway=use_nat
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

        return instances_by_region

    except Exception as e:
        console.print(
            f"[red]Error enumerating VMs in subscription {subscription_id}: {str(e)}[/red]")
        raise


def enumerate_subscriptions(credential: DefaultAzureCredential) -> List[str]:
    """
    Enumerate all subscriptions accessible to the credential.

    Args:
        credential: Azure credential object

    Returns:
        List of subscription IDs
    """
    try:
        subscription_client = SubscriptionClient(credential)
        return [sub.subscription_id for sub in subscription_client.subscriptions.list()]
    except Exception as e:
        console.print(f"[red]Error enumerating subscriptions: {str(e)}[/red]")
        raise


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
    vm_count: Optional[int] = typer.Option(
        None,
        "--vm-count",
        "-v",
        help="Number of VMs to be scanned (will be auto-detected if not provided)"
    ),
    nat_gateway: Optional[bool] = typer.Option(
        None,
        "--nat-gateway",
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
        vm_count is not None,
        nat_gateway is not None
    ])

    credential = DefaultAzureCredential()

    if is_interactive:
        config = prompt_for_config(credential)
    else:
        config = PreflightConfig(
            integration_type=integration_type,
            scanning_subscription=scanning_subscription,
            regions=regions.split(","),
            vm_count=vm_count,
            use_nat_gateway=nat_gateway
        )

    # Print configuration for verification
    console.print("\n[bold]Configuration Summary:[/bold]")
    console.print(f"Integration Type: {config.integration_type}")
    console.print(f"Scanning Subscription ID: {config.scanning_subscription}")
    console.print(f"Target Regions: {', '.join(config.regions)}")
    console.print(f"VMs to be Scanned: {config.vm_count}")
    console.print(
        f"Using NAT Gateway: {'Yes' if config.use_nat_gateway else 'No'}\n")

    # TODO: Implement validation logic here


if __name__ == "__main__":
    app()
