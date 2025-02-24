import typer
from typing import Optional, List
from azure.identity import DefaultAzureCredential

from preflight_check.models import IntegrationType, DeploymentConfig
from preflight_check.services.azure import AzureService
from preflight_check import cli

app = typer.Typer()

DEFAULT_BATCH_SIZE = 4


class PreflightCheck:
    """Orchestrates the preflight check process"""
    available_subscriptions = []

    def __init__(self):
        self.credential = DefaultAzureCredential()
        self.azure = AzureService(self.credential)
        # enumerate all subscriptions available to the authenticated Azure principal
        self.available_subscriptions = self.azure.list_subscriptions()

    def run_interactive(self) -> DeploymentConfig:
        """Run preflight check in interactive mode"""
        # First check if we have permissions to run the script
        missing_permissions = self.azure.check_permissions()
        if missing_permissions:
            cli.console.print(
                "[red]Error: Missing required permissions:[/red]")
            for perm in missing_permissions:
                cli.console.print(f"  - {perm}")
            raise typer.Exit(1)

        # Get integration type
        integration_type = cli.prompt_integration_type()

        # Get scanning subscription
        scanning_sub = cli.prompt_scanning_subscription(
            self.available_subscriptions)

        # Get monitored subscriptions based on integration type
        if integration_type == IntegrationType.SUBSCRIPTION:
            monitored_subs = [scanning_sub]
        else:
            monitored_subs = cli.prompt_monitored_subscriptions(
                self.available_subscriptions)

        # Enumerate VMs in all monitored subscriptions
        for sub in monitored_subs:
            cli.console.print(f"[dim]Enumerating VMs in {sub.name}...[/dim]")
            self.azure.get_subscription_vms(sub)

        # Show all VM counts together
        cli.print_vm_counts(monitored_subs)

        # Get deployment regions and show filtered VM counts
        selected_regions = cli.prompt_regions(monitored_subs)

        # Get NAT Gateway preference
        use_nat = cli.prompt_nat_gateway()

        # Show quota requirements
        cli.print_quota_requirements(
            scanning_sub.name,
            selected_regions,
            monitored_subs,
            use_nat,
            DEFAULT_BATCH_SIZE
        )

        return DeploymentConfig(
            integration_type=integration_type,
            scanning_subscription=scanning_sub,
            monitored_subscriptions=monitored_subs,
            use_nat_gateway=use_nat
        )


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
        help="Azure regions (comma-separated) where scanner will be deployed"
    ),
    use_nat_gateway: Optional[bool] = typer.Option(
        None,
        "--nat-gateway",
        "-n",
        help="Use NAT Gateway for optimized networking (recommended for 1000+ VMs)"
    )
):
    """
    Preflight check for Azure Agentless Scanner deployment.
    """
    try:
        checker = PreflightCheck()

        # Determine if we should run in interactive mode
        # If no arguments provided, run in interactive mode
        if all(arg is None for arg in [
            integration_type,
            scanning_subscription,
            regions,
            use_nat_gateway
        ]):
            config = checker.run_interactive()
        # If some but not all arguments provided, error out
        elif not all([
            integration_type,
            scanning_subscription,
            regions,
            use_nat_gateway is not None
        ]):
            cli.console.print(
                "[red]Error: When running in non-interactive mode, all arguments must be provided.[/red]")
            cli.console.print("Required arguments:")
            cli.console.print("  --integration-type [tenant|subscription]")
            cli.console.print("  --scanning-subscription SUBSCRIPTION_ID")
            cli.console.print("  --regions REGION1,REGION2,...")
            cli.console.print("  --nat-gateway [true|false]")
            raise typer.Exit(1)
        else:
            # TODO: Implement non-interactive mode
            cli.console.print(
                "[red]Non-interactive mode not yet implemented[/red]")
            raise typer.Exit(1)

        # TODO: Generate and save report

    except typer.Exit:
        raise
    except Exception as e:
        cli.console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)
