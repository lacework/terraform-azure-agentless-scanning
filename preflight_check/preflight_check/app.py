import typer
from typing import Annotated, Optional, List
from azure.identity import DefaultAzureCredential

from preflight_check.core import AzureClientFactory, QuotaService, SubscriptionService
from preflight_check.core import DeploymentConfig, Region, IntegrationType, Subscription
from preflight_check.core import PreflightCheck

from preflight_check import cli


app = typer.Typer()


class App:
    """Orchestrates the preflight check process"""

    _azure_client_factory: AzureClientFactory
    _subscriptions: SubscriptionService
    _quotas: QuotaService

    available_subscriptions: List[Subscription]
    deployment_config: Optional[DeploymentConfig] = None

    def __init__(self):
        credential = DefaultAzureCredential()
        azure_client_factory = AzureClientFactory(credential)
        self._subscriptions = SubscriptionService(azure_client_factory)
        self._quotas = QuotaService(azure_client_factory)
        # enumerate all subscriptions available to the authenticated Azure principal
        self.available_subscriptions = self._subscriptions.get_subscriptions()

    def configure(self, integration_type: IntegrationType, scanning_subscription: str, monitored_subscriptions: str, region_names: str, use_nat_gateway: bool):
        """Configure deployment based on provided args or interactive prompts"""
        args = [
            integration_type,
            scanning_subscription,
            monitored_subscriptions,
            region_names,
            use_nat_gateway
        ]
        # If no arguments provided, prompt for deployment config interactively
        if all(arg is None for arg in args):
            self._prompt_deployment_config()
        # If some but not all arguments provided, error out
        elif not all(arg is not None for arg in args):
            self._print_cli_args_error()
            raise typer.Exit(1)
        # Otherwise, create the deployment config using provided args
        else:
            try:
                scanning_subscription = self._subscriptions.get_subscription(
                    scanning_subscription.strip())
                monitored_subscriptions = [self._subscriptions.get_subscription(
                    sub_id.strip()) for sub_id in monitored_subscriptions.strip().split(",")]
                for sub in monitored_subscriptions:
                    cli.console.print(
                        f"[dim]Enumerating VMs in {sub.name}...[/dim]")
                    self._subscriptions.get_subscription_vms(sub)
                valid_region_names = set(
                    region_name for sub in monitored_subscriptions
                    for region_name in sub.regions.keys())
                selected_region_names = [region_name.strip() for region_name in region_names.strip().split(
                    ",") if region_name.strip() in valid_region_names]
            except ValueError as e:
                cli.console.print(f"[red]Error: {e}[/red]")
                raise typer.Exit(1)
            self.deployment_config = DeploymentConfig(
                integration_type=integration_type,
                scanning_subscription=scanning_subscription,
                monitored_subscriptions=monitored_subscriptions,
                regions=selected_region_names,
                use_nat_gateway=use_nat_gateway
            )

    def run(self):
        """Run the preflight check"""
        cli.console.print("Getting usage quota limits...")
        usage_quota_limits = {
            region: self._quotas.get_quota_limits(
                self.deployment_config.scanning_subscription.id, region)
            for region in self.deployment_config.regions
        }
        preflight_check = PreflightCheck(
            self.deployment_config, usage_quota_limits)
        cli.print_preflight_check(preflight_check)

    def _prompt_deployment_config(self):
        available_subscriptions = self._subscriptions.get_subscriptions()
        scanning_subscription = cli.prompt_scanning_subscription(
            available_subscriptions)
        (monitored_subscriptions, integration_type) = cli.prompt_monitored_subscriptions(
            available_subscriptions)

        # Enumerate VMs in all monitored subscriptions
        for sub in monitored_subscriptions:
            cli.console.print(f"[dim]Enumerating VMs in {sub.name}...[/dim]")
            self._subscriptions.get_subscription_vms(sub)

        # Show all VM counts together
        cli.print_vm_counts(monitored_subscriptions)

        # Get deployment regions and show filtered VM counts
        selected_region_names = cli.prompt_regions(monitored_subscriptions)

        # Filter subscriptions to only include selected regions
        for sub in monitored_subscriptions:
            sub.regions = {
                region_name: region
                for region_name, region in sub.regions.items()
            }

        # Show filtered VM counts
        cli.console.print("\n[bold]Filtered VM Counts[/bold]")
        cli.console.print(
            f"[dim]The following is the updated VM count based on the user-selected regions:[/dim]\n{', '.join(selected_region_names)}")
        cli.print_vm_counts(monitored_subscriptions)

        # Get NAT Gateway preference
        use_nat_gateway = cli.prompt_nat_gateway()

        self.deployment_config = DeploymentConfig(
            integration_type=integration_type,
            scanning_subscription=scanning_subscription,
            monitored_subscriptions=monitored_subscriptions,
            regions=selected_region_names,
            use_nat_gateway=use_nat_gateway
        )

    def _print_cli_args_error(self):
        cli.console.print(
            "[red]Error: When running in non-interactive mode, all arguments must be provided.[/red]")
        cli.console.print("Required arguments:")
        cli.console.print("  --integration-type [tenant|subscription]")
        cli.console.print("  --scanning-subscription SUBSCRIPTION_ID")
        cli.console.print(
            "  --monitored-subscriptions SUBSCRIPTION_ID1,SUBSCRIPTION_ID2,...")
        cli.console.print("  --regions REGION1,REGION2,...")
        cli.console.print("  --nat-gateway [true|false]")


@app.command()
def main(
    integration_type: Annotated[
        Optional[IntegrationType],
        typer.Option(
            "--integration-type",
            "-i",
            help="Integration type: tenant or subscription"
        )
    ] = None,
    scanning_subscription: Annotated[
        Optional[str],
        typer.Option(
            "--scanning-subscription",
            "-s",
            help="Subscription ID where scanner resources will be deployed"
        )
    ] = None,
    monitored_subscriptions: Annotated[
        Optional[str],
        typer.Option(
            "--monitored-subscriptions",
            "-m",
            help="Subscription IDs of the subscriptions to monitor with AWLS"
        )
    ] = None,
    regions: Annotated[
        Optional[str],
        typer.Option(
            "--regions",
            "-r",
            help="Azure regions (comma-separated) where scanner will be deployed"
        )
    ] = None,
    use_nat_gateway: Annotated[
        Optional[bool],
        typer.Option(
            "--nat-gateway/--no-nat-gateway",
            "-n/-N",
            help="Use NAT Gateway for optimized networking (recommended for 1000+ VMs)"
        )
    ] = None,
):
    """
    Preflight check for Azure Agentless Scanner deployment.
    """
    try:
        app = App()
        app.configure(integration_type, scanning_subscription,
                      monitored_subscriptions, regions, use_nat_gateway)
        app.run()
    except typer.Exit:
        raise
    except Exception as e:
        cli.console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)
