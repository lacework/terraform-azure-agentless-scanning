import typer
from typing import Annotated, Optional, List
from azure.identity import DefaultAzureCredential

from preflight_check.models import DeploymentConfig, IntegrationType, Subscription, Region
from preflight_check.services import AzureClientFactory, SubscriptionService
from preflight_check import cli

app = typer.Typer()

DEFAULT_BATCH_SIZE = 4


class PreflightCheck:
    """Orchestrates the preflight check process"""

    _azure_client_factory: AzureClientFactory
    _subscriptions: SubscriptionService

    available_subscriptions: List[Subscription]
    deployment_config: Optional[DeploymentConfig] = None

    def __init__(self):
        credential = DefaultAzureCredential()
        azure_client_factory = AzureClientFactory(credential)
        self._subscriptions = SubscriptionService(azure_client_factory)
        # enumerate all subscriptions available to the authenticated Azure principal
        self.available_subscriptions = self._subscriptions.get_subscriptions()

    def configure(self, integration_type: IntegrationType, scanning_subscription: str, monitored_subscriptions: List[str], regions: List[str], use_nat_gateway: bool):
        """Configure deployment based on provided args or interactive prompts"""
        args = [
            integration_type,
            scanning_subscription,
            monitored_subscriptions,
            regions,
            use_nat_gateway
        ]
        # If no arguments provided, prompt for deployment config interactively
        if all(arg is None for arg in args):
            self.prompt_deployment_config()
        # If some but not all arguments provided, error out
        elif not all(arg is not None for arg in args):
            self._print_cli_args_error()
            raise typer.Exit(1)
        # Otherwise, create the deployment config using provided args
        else:
            try:
                scanning_sub = self._subscriptions.get_subscription(
                    scanning_subscription)
                monitored_subs = [self._subscriptions.get_subscription(
                    sub_id) for sub_id in monitored_subscriptions]
            except ValueError as e:
                cli.console.print(f"[red]Error: {e}[/red]")
                raise typer.Exit(1)
            self.deployment_config = DeploymentConfig(
                integration_type=integration_type,
                scanning_subscription=scanning_sub,
                monitored_subscriptions=monitored_subs,
                regions=regions,
                use_nat_gateway=use_nat_gateway
            )

    def prompt_deployment_config(self):
        """Prompt for deployment configuration interactively"""
        # Get integration type
        integration_type = cli.prompt_integration_type()

        # Get scanning subscription
        scanning_sub = cli.prompt_scanning_subscription(
            self._subscriptions.get_subscriptions(), integration_type)

        # Get monitored subscriptions based on integration type
        if integration_type == IntegrationType.SUBSCRIPTION:
            monitored_subs = [scanning_sub]
        else:
            monitored_subs = cli.prompt_monitored_subscriptions(
                self._subscriptions.get_subscriptions())

        # Enumerate VMs in all monitored subscriptions
        for sub in monitored_subs:
            cli.console.print(f"[dim]Enumerating VMs in {sub.name}...[/dim]")
            self._subscriptions.get_subscription_vms(sub)

        # Show all VM counts together
        cli.print_vm_counts(monitored_subs)

        # Get deployment regions and show filtered VM counts
        selected_regions = cli.prompt_regions(monitored_subs)

        # Get NAT Gateway preference
        use_nat = cli.prompt_nat_gateway()

        self.deployment_config = DeploymentConfig(
            integration_type=integration_type,
            scanning_subscription=scanning_sub,
            monitored_subscriptions=monitored_subs,
            regions=selected_regions,
            use_nat_gateway=use_nat
        )

    def run(self):
        """Run the preflight check"""
        self.check_quotas()
    def check_quotas(self):
        cli.print_quota_requirements(
            self.deployment_config.scanning_subscription.name,
            self.deployment_config.regions,
            self.deployment_config.monitored_subscriptions,
            self.deployment_config.use_nat_gateway,
            DEFAULT_BATCH_SIZE,
        )
    def _print_cli_args_error(self):
        cli.console.print(
            "[red]Error: When running in non-interactive mode, all arguments must be provided.[/red]")
        cli.console.print("Required arguments:")
        cli.console.print("  --integration-type [tenant|subscription]")
        cli.console.print("  --scanning-subscription SUBSCRIPTION_ID")
        cli.console.print("  --regions REGION1,REGION2,...")
        cli.console.print("  --nat-gateway [true|false]")
        cli.console.print(
            "  --monitored-subscriptions SUBSCRIPTION_ID1,SUBSCRIPTION_ID2,... (required when --integration-type=tenant)")


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
            "--nat-gateway",
            "-n",
            help="Use NAT Gateway for optimized networking (recommended for 1000+ VMs)"
        )
    ] = None,
):
    """
    Preflight check for Azure Agentless Scanner deployment.
    """
    try:
        checker = PreflightCheck()
        checker.configure(integration_type, scanning_subscription,
                          monitored_subscriptions, regions, use_nat_gateway)
        checker.run()
    except typer.Exit:
        raise
    except Exception as e:
        cli.console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)
