from typing import Annotated

import typer
from azure.identity import DefaultAzureCredential

from preflight_check import cli
from preflight_check.core import (
    AuthService,
    AzureClientFactory,
    DeploymentConfig,
    IntegrationType,
    PreflightCheck,
    QuotaService,
    Subscription,
    SubscriptionService,
    UsageQuotaLimit,
)

app = typer.Typer()


class App:
    """Orchestrates the preflight check process"""

    _azure_client_factory: AzureClientFactory
    _subscriptions: SubscriptionService
    _quotas: QuotaService
    _auth: AuthService
    available_subscriptions: list[Subscription]
    deployment_config: DeploymentConfig | None = None

    def __init__(self) -> None:
        credential = DefaultAzureCredential()
        azure_client_factory = AzureClientFactory(credential)
        self._subscriptions = SubscriptionService(azure_client_factory)
        self._quotas = QuotaService(azure_client_factory)
        self._auth = AuthService(azure_client_factory)
        # enumerate all subscriptions available to the authenticated Azure principal
        self.available_subscriptions = self._subscriptions.get_subscriptions()

    def configure(
        self,
        integration_type: IntegrationType | None,
        scanning_subscription_input: str | None,
        monitored_subscriptions_input: str | None,
        region_names: str | None,
        use_nat_gateway: bool | None,
    ) -> None:
        """Configure deployment based on provided args or interactive prompts"""
        args = [
            integration_type,
            scanning_subscription_input,
            monitored_subscriptions_input,
            region_names,
            use_nat_gateway,
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
                    scanning_subscription_input.strip()
                )
                monitored_subscriptions = [
                    self._subscriptions.get_subscription(sub_id.strip())
                    for sub_id in monitored_subscriptions_input.strip().split(",")
                ]
                for sub in monitored_subscriptions:
                    cli.console.print(
                        f"[dim]Enumerating VMs in {sub.name}...[/dim]")
                    self._subscriptions.get_subscription_vms(sub)
                valid_region_names = {
                    region_name for sub in monitored_subscriptions for region_name in sub.regions
                }
                selected_region_names = [
                    region_name.strip()
                    for region_name in region_names.strip().split(",")
                    if region_name.strip() in valid_region_names
                ]
            except ValueError as e:
                cli.console.print(f"[red]Error: {e}[/red]")
                raise typer.Exit(1) from e
            self.deployment_config = DeploymentConfig(
                integration_type=integration_type,
                scanning_subscription=scanning_subscription,
                monitored_subscriptions=monitored_subscriptions,
                regions=selected_region_names,
                use_nat_gateway=use_nat_gateway
            )

    def run(self) -> None:
        """Run the preflight check"""
        usage_quota_limits = self._get_usage_quota_limits()
        permissions = self._get_permissions()
        preflight_check = PreflightCheck(
            self.deployment_config, usage_quota_limits, permissions)
        cli.print_preflight_check(preflight_check)

    def _prompt_deployment_config(self) -> None:
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
                if region_name in selected_region_names
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

    def _get_usage_quota_limits(self) -> dict[str, dict[str, UsageQuotaLimit]]:
        cli.console.print("Getting usage quota limits...")
        if not self.deployment_config:
            raise RuntimeError("Deployment config not set")
        return {
            region: self._quotas.get_quota_limits(
                self.deployment_config.scanning_subscription.id, region
            )
            for region in self.deployment_config.regions
        }

    def _get_permissions(self) -> dict[str, list[str]]:
        cli.console.print("Getting permissions...")
        if not self.deployment_config:
            raise RuntimeError("Deployment config not set")
        # Get permissions for scanning subscription and monitored subscriptions
        permissions = {
            subscription.id: self._auth.get_permissions_for_subscription(subscription.id)
            for subscription in [
                *self.deployment_config.monitored_subscriptions,
                self.deployment_config.scanning_subscription,
            ]
        }
        # Get permissions for the root management group
        root_management_group_id = self._auth.get_root_management_group_id()
        permissions[root_management_group_id] = self._auth.get_permissions_for_root_management_group(
            self.deployment_config.scanning_subscription.id)
        return permissions

    def _print_cli_args_error(self) -> None:
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
        IntegrationType | None,
        typer.Option("--integration-type", "-i", help="Integration type: tenant or subscription"),
    ] = None,
    scanning_subscription: Annotated[
        str | None,
        typer.Option(
            "--scanning-subscription",
            "-s",
            help="Subscription ID where scanner resources will be deployed",
        ),
    ] = None,
    monitored_subscriptions: Annotated[
        str | None,
        typer.Option(
            "--monitored-subscriptions",
            "-m",
            help="Subscription IDs of the subscriptions to monitor with AWLS",
        ),
    ] = None,
    regions: Annotated[
        str | None,
        typer.Option(
            "--regions", "-r", help="Azure regions (comma-separated) where scanner will be deployed"
        ),
    ] = None,
    use_nat_gateway: Annotated[
        bool | None,
        typer.Option(
            "--nat-gateway/--no-nat-gateway",
            "-n/-N",
            help="Use NAT Gateway for optimized networking (recommended for 1000+ VMs)",
        ),
    ] = None,
) -> None:
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
        raise typer.Exit(1) from e
