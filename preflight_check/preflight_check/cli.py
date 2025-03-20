from typing import List, Tuple
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.box import HEAVY_EDGE

from .core.models import IntegrationType, Subscription
from .core.preflight_check import PreflightCheck, QuotaChecks, AuthChecks, AuthCheck

console = Console()


def prompt_scanning_subscription(available_subs: List[Subscription]) -> Subscription:
    """Prompt user to choose scanning subscription"""
    console.print(f"\n[bold]Available Subscriptions:[/bold]")
    print_subscriptions(available_subs)
    console.print("\n[bold]Scanning Subscription[/bold]")
    console.print(
        "[dim]What subscription do you want to deploy the AWLS scanner resources to?[/dim]")
    sub_id = Prompt.ask("Subscription ID",
                        choices=[sub.id for sub in available_subs],
                        show_choices=False)

    # Find the subscription in our list of available subscriptions
    for sub in available_subs:
        if sub.id == sub_id:
            console.print(
                f"[green]Selected scanning subscription: {sub.name}[/green]")
            return sub
    raise ValueError(f"Subscription {sub_id} not found")


def prompt_monitored_subscriptions(available_subs: List[Subscription]) -> Tuple[List[Subscription], IntegrationType]:
    """Prompt user to choose which subscriptions to monitor"""
    console.print("\n[bold]Monitored Subscriptions[/bold]")
    console.print("[dim]Choose which subscriptions to be monitored.[/dim]")

    scan_scope = Prompt.ask(
        "Scan scope",
        choices=["all", "exclude", "specify"],
        default="all"
    )

    if scan_scope == "all":
        console.print("[dim]All subscriptions will be monitored.[/dim]")
        return (available_subs, IntegrationType.TENANT)

    elif scan_scope == "exclude":
        console.print(
            "[dim]Select subscriptions to exclude from monitoring.[/dim]")
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
        return (monitored_subs, IntegrationType.TENANT)

    else:  # specify
        console.print("[dim]Select specific subscriptions to monitor.[/dim]")
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
            "\n[bold]Only the following subscriptions will be monitored:[/bold]")
        print_subscriptions(specified_subs)
        return (specified_subs, IntegrationType.SUBSCRIPTION)


def prompt_nat_gateway() -> bool:
    """Prompt user about NAT Gateway usage"""
    console.print("\n[bold]Network Configuration[/bold]")
    console.print(
        "[dim]We recommend deploying AWLS with a NAT Gateway, but you can opt out if you prefer.[/dim]")
    console.print(
        "[dim]For more details on deploying with/without a NAT Gateway, please refer to the Lacework FortiCNAPP docs:\nhttps://docs.fortinet.com/document/lacework-forticnapp/24.4.0/new-features/13869/integrating-agentless-workload-security-with-azure?preview_token=44849b8a6bf658c3c2b3#:~:text=deploy%20the%20Agentless%20scanning%20integration%20with%20a%20NAT%20gateway.[/dim]")
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


def prompt_regions(subscriptions: List[Subscription]) -> List[str]:
    """
    Prompt user to choose deployment regions.
    Default to regions where VMs were detected.
    Returns list of selected region names.
    """
    # Get unique regions across all subscriptions
    detected_regions = set(
        region_name for sub in subscriptions
        for region_name in sub.regions.keys())
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
    selected_regions = []
    for region_input in regions_input.strip().split(","):
        if region_input.strip() in detected_regions:
            selected_regions.append(region_input.strip())
        else:
            console.print(
                f"[yellow]Warning: Region {region_input.strip()} not found[/yellow]")
    console.print(
        f"[green]The following regions will be monitored:[/green] {', '.join(selected_regions)}")
    return selected_regions


def print_quota_checks(quota_checks: QuotaChecks):
    """Display usage quota checks across all regions in a table format"""
    quota_checks_by_region = quota_checks.quota_checks
    scanning_subscription = quota_checks.subscription

    console.print(f"\n[bold]Usage Quota Limits[/bold]")
    console.print(
        f"Here are the configured and required usage quota limits for subscription [bold]{scanning_subscription.name}[/bold]:\n")

    # Create quota requirements table
    table = Table(show_header=True, header_style="bold", box=HEAVY_EDGE)
    table.add_column("Region", style="bold cyan")
    table.add_column("VM Count", style="cyan")
    table.add_column("Quota", style="magenta")
    table.add_column("Configured Limit", style="")
    table.add_column("Current Usage", style="")
    table.add_column("Required Limit", style="")
    table.add_column("Status", style="")

    # Sort regions alphabetically
    region_names = sorted(quota_checks_by_region.keys())

    for region_name in region_names:
        checks = quota_checks_by_region[region_name]

        # # Sort checks by display name
        # checks.sort(key=lambda c: c.display_name)

        for i, check in enumerate(checks):
            # Only show the region name for the first check of each region
            region_display = region_name if i == 0 else ""

            vm_count = str(check.region.vm_count) if i == 0 else ""

            # Determine status symbol and style
            status = "✅" if check.success else "❌"

            # Add row to table
            table.add_row(
                region_display,
                vm_count,
                check.display_name,
                str(check.configured_limit),
                str(check.current_usage),
                str(check.required_quota),
                status
            )
        # Add a blank row between regions (unless it's the last region)
        if region_name != region_names[-1]:
            table.add_row("", "", "", "", "", "")

    console.print(table)

    # Print summary and help message
    if quota_checks.all_checks_pass():
        console.print(
            "\n[green]✅ All configured usage quota limits are sufficient![/green]")
    else:
        console.print(
            "\n[yellow]⚠️ Some configured usage quota limits are not sufficient.[/yellow]")
        console.print(
            "Please request quota increases at: https://portal.azure.com/#blade/Microsoft_Azure_Capacity/QuotaRequestBlade")


def print_auth_checks(auth_checks: AuthChecks):
    """Display auth checks across all subscriptions in a table format"""
    scanning_subscription_auth_check = auth_checks.scanning_subscription
    monitored_subscriptions_auth_checks = auth_checks.monitored_subscriptions

    # print scanning subscription auth check
    console.print(f"\n[bold]Scanning Subscription Authorization Checks[/bold]")
    print_auth_check_table([scanning_subscription_auth_check])

    # print monitored subscriptions auth checks
    console.print(
        f"\n[bold]Monitored Subscriptions Authorization Checks[/bold]")
    print_auth_check_table(monitored_subscriptions_auth_checks)


def print_auth_check_table(auth_checks: List[AuthCheck]):
    """Display auth checks across all subscriptions in a table format"""
    table = Table(show_header=True, header_style="bold", box=HEAVY_EDGE)
    table.add_column("Subscription", style="bold cyan")
    table.add_column("Required Permission", style="magenta")
    table.add_column("Status", style="")

    print(f'auth_checks (type: {type(auth_checks)}): {auth_checks}')

    for auth_check in auth_checks:
        printed_subscription_name = False
        for check in auth_check.checked_permissions:
            subscription_name = ""
            if not printed_subscription_name:
                subscription_name = auth_check.subscription.name
                printed_subscription_name = True
            status = "✅" if check.is_granted else "❌"
            table.add_row(
                subscription_name,
                str(check.required_permission),
                status
            )

    console.print(table)



def print_preflight_check(preflight_check: PreflightCheck):
    """Print the preflight check results"""
    print_quota_checks(preflight_check.usage_quota_checks)
    print_auth_checks(preflight_check.auth_checks)
