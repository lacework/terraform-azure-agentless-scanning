from typing import List, Dict
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.box import HEAVY_EDGE

from .models import IntegrationType, Subscription, Region

console = Console()


def prompt_integration_type() -> IntegrationType:
    """Prompt user to choose integration type"""
    console.print("\n[bold]Integration Type[/bold]")
    console.print(
        "[dim]Choose whether to deploy the scanner at the tenant level or subscription level.[/dim]")
    choice = Prompt.ask(
        "Integration type",
        choices=[t.value for t in IntegrationType]
    )
    return IntegrationType(choice)


def prompt_scanning_subscription(available_subs: List[Subscription]) -> Subscription:
    """Prompt user to choose scanning subscription"""
    console.print(f"\n[bold]Available Subscriptions:[/bold]")
    print_subscriptions(available_subs)
    console.print("\n[bold]Scanning Subscription[/bold]")
    console.print(
        "[dim]What subscription should the scanner be deployed to?[/dim]")

    sub_id = Prompt.ask("Subscription ID")
    # Find the subscription in our list
    for sub in available_subs:
        if sub.id == sub_id:
            console.print(
                f"[green]Selected scanning subscription: {sub.name}[/green]")
            return sub
    raise ValueError(f"Subscription {sub_id} not found")


def prompt_monitored_subscriptions(available_subs: List[Subscription]) -> List[Subscription]:
    """Prompt user to choose which subscriptions to monitor"""
    console.print("\n[bold]Monitored Subscriptions[/bold]")
    console.print("[dim]Choose which subscriptions to be scanned.[/dim]")

    scan_scope = Prompt.ask(
        "Scan scope",
        choices=["all", "exclude", "specify"],
        default="all"
    )

    if scan_scope == "all":
        console.print("[dim]All subscriptions will be scanned.[/dim]")
        return available_subs

    elif scan_scope == "exclude":
        console.print(
            "[dim]Select subscriptions to exclude from scanning.[/dim]")
        print_subscriptions(available_subs)

        excluded_ids = Prompt.ask(
            "Excluded Subscription IDs (comma-separated)")
        excluded_subs = []

        for sub_id in [s.strip() for s in excluded_ids.split(",")]:
            for sub in available_subs:
                if sub.id == sub_id:
                    excluded_subs.append(sub)
                    break
            else:
                console.print(
                    f"[yellow]Warning: Subscription {sub_id} not found[/yellow]")

        monitored_subs = [s for s in available_subs if s not in excluded_subs]
        console.print(
            "\n[bold]The following subscriptions will be excluded:[/bold]")
        print_subscriptions(excluded_subs)
        return monitored_subs

    else:  # specify
        console.print("[dim]Select specific subscriptions to scan.[/dim]")
        print_subscriptions(available_subs)

        specified_ids = Prompt.ask(
            "Specified Subscription IDs (comma-separated)")
        specified_subs = []

        for sub_id in [s.strip() for s in specified_ids.split(",")]:
            for sub in available_subs:
                if sub.id == sub_id:
                    specified_subs.append(sub)
                    break
            else:
                console.print(
                    f"[yellow]Warning: Subscription {sub_id} not found[/yellow]")

        console.print(
            "\n[bold]Only the following subscriptions will be scanned:[/bold]")
        print_subscriptions(specified_subs)
        return specified_subs


def prompt_nat_gateway() -> bool:
    """Prompt user about NAT Gateway usage"""
    console.print("\n[bold]Network Configuration[/bold]")
    console.print(
        "[dim]We recommend deploying AWLS with a NAT Gateway, but you can opt out if you prefer.[/dim]")
    return Confirm.ask("Use NAT Gateway?", default=True)


def print_subscriptions(subscriptions: List[Subscription]):
    """Display subscriptions in a table"""
    table = Table(box=HEAVY_EDGE)
    table.add_column("Subscription Name", style="cyan")
    table.add_column("Subscription ID", style="green")

    for sub in sorted(subscriptions, key=lambda s: s.name.lower()):
        table.add_row(sub.name, sub.id)

    console.print(table)


def print_vm_counts(subscriptions: List[Subscription]):
    """Display VM counts by region for all subscriptions"""
    table = Table(box=HEAVY_EDGE)
    table.add_column("Subscription", style="cyan")
    table.add_column("Region", style="magenta")
    table.add_column("VM Count", style="green", justify="right")

    total_vms = 0
    subscriptions_with_no_vms = []

    # Sort subscriptions by name
    for sub in sorted(subscriptions, key=lambda s: s.name.lower()):
        if not sub.regions:
            subscriptions_with_no_vms.append(sub)
            continue

        # Sort regions alphabetically
        sorted_regions = sorted(sub.regions.items())

        if len(sorted_regions) == 1:
            # Single region - show both subscription name and ID
            region_name, region = sorted_regions[0]
            table.add_row(sub.name, region_name, str(region.vm_count))
            table.add_row(sub.id, "", "")
            total_vms += region.vm_count
        else:
            # Multiple regions
            first_region = True
            second_region = True
            for region_name, region in sorted_regions:
                if first_region:
                    table.add_row(sub.name, region_name, str(region.vm_count))
                    first_region = False
                elif second_region:
                    table.add_row(sub.id, region_name, str(region.vm_count))
                    second_region = False
                else:
                    table.add_row("", region_name, str(region.vm_count))
                total_vms += region.vm_count

        # Add separator between subscriptions
        table.add_row()

    # Add total
    table.add_row("Total", "", str(total_vms), style="bold")

    console.print("\n[bold]VM Counts by Region:[/bold]")
    console.print(table)

    if subscriptions_with_no_vms:
        console.print(
            "\n[yellow]Warning: The following subscriptions have no VMs:[/yellow]")
        print_subscriptions(subscriptions_with_no_vms)


def print_quota_requirements(scanning_sub_name: str, selected_regions: List[str], subscriptions: List[Subscription], use_nat: bool, batch_size: int):
    """Display quota requirements across all regions"""
    console.print("\n[bold]Quota Requirements[/bold]")
    console.print(
        f"Please ensure that the usage quotas configured in the subscription {scanning_sub_name} meet the required quotas:")

    table = Table(box=HEAVY_EDGE)
    table.add_column("Region", style="magenta")
    table.add_column("VM Count", style="green", justify="right")
    table.add_column("Required vCPUs", style="blue", justify="right")
    table.add_column("Required Public IPs", style="blue", justify="right")

    # Aggregate VM counts by region across all subscriptions
    for region_name in sorted(selected_regions):
        total_vms = sum(
            sub.regions[region_name].vm_count
            for sub in subscriptions
            if region_name in sub.regions
        )

        # Create aggregated region
        region = Region(
            name=region_name,
            vm_count=total_vms
        )

        table.add_row(
            region.name,
            str(region.vm_count),
            str(region.required_vcpu(batch_size)),
            str(region.required_public_ips(use_nat, batch_size))
        )

    console.print("\n[bold]Required Regional Quotas:[/bold]")
    console.print(table)


def prompt_regions(subscriptions: List[Subscription]) -> List[str]:
    """
    Prompt user to choose deployment regions.
    Default to regions where VMs were detected.
    Returns list of selected region names.
    """
    # Get unique regions across all subscriptions
    detected_regions = set()
    for sub in subscriptions:
        detected_regions.update(sub.regions.keys())

    console.print("\n[bold]Deployment Regions[/bold]")
    console.print(
        "[dim]Enter the Azure regions that you'd like to monitor.[/dim]")
    console.print("[dim]The scanner will be deployed in these regions.[/dim]")

    regions_default = ",".join(
        sorted(detected_regions)) if detected_regions else None
    regions_input = Prompt.ask(
        "Azure regions (comma-separated)",
        default=regions_default
    )
    selected_regions = sorted([r.strip() for r in regions_input.split(",")])

    # Filter subscriptions to only include selected regions
    for sub in subscriptions:
        sub.regions = {
            name: region
            for name, region in sub.regions.items()
            if name in selected_regions
        }

    # Show filtered VM counts
    console.print("\n[bold]Filtered VM Counts[/bold]")
    console.print(
        f"[dim]The following is the updated VM count based on the user-selected regions:[/dim]\n{', '.join(selected_regions)}")
    print_vm_counts(subscriptions)

    return selected_regions
