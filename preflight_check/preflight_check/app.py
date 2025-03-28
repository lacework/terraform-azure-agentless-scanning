from typing import Annotated

import typer
from azure.identity import DefaultAzureCredential

from preflight_check import cli
from preflight_check.core import PreflightCheck, models, services


class App:
    """Orchestrates the preflight check process"""

    _azure_client_factory: services.AzureClientFactory
    _subscriptions: services.SubscriptionService
    _quotas: services.QuotaService
    _auth: services.AuthService
    available_subscriptions: list[models.Subscription]
    deployment_config: models.DeploymentConfig | None = None

    def __init__(self, credential: DefaultAzureCredential, output_path: str) -> None:
        self.output_path = output_path
        azure_client_factory = services.AzureClientFactory(credential)
        self._subscriptions = services.SubscriptionService(azure_client_factory)
        self._quotas = services.QuotaService(azure_client_factory)
        self._auth = services.AuthService(azure_client_factory)
        # enumerate all subscriptions available to the authenticated Azure principal
        self.available_subscriptions = self._subscriptions.get_subscriptions()

    def configure(
        self,
        scanning_subscription_input: str | None,
        monitored_subscriptions_input: str | None,
        excluded_subscriptions_input: str | None,
        regions_input: str | None,
        use_nat_gateway: bool,
    ) -> None:
        """Configure deployment based on provided args or interactive prompts"""
        args = [
            scanning_subscription_input,
            monitored_subscriptions_input,
            excluded_subscriptions_input,
            regions_input,
            use_nat_gateway,
        ]
        # If no arguments provided, prompt for deployment config interactively
        if all(arg is None for arg in args):
            self._prompt_deployment_config()
        # Otherwise, create the deployment config using provided args
        else:
            scanning_subscription = self._get_scanning_subscription(scanning_subscription_input)
            monitored_subscriptions, integration_type = self._get_monitored_subscriptions(
                monitored_subscriptions_input, excluded_subscriptions_input
            )
            for sub in monitored_subscriptions:
                cli.console.print(f"[dim]Enumerating VMs in {sub.name}...[/dim]")
                self._subscriptions.get_subscription_vms(sub)
            selected_regions = self._get_regions(monitored_subscriptions, regions_input)
            self.deployment_config = models.DeploymentConfig(
                integration_type=integration_type,
                scanning_subscription=scanning_subscription,
                monitored_subscriptions=monitored_subscriptions,
                regions=selected_regions,
                use_nat_gateway=use_nat_gateway,
            )

    def run(self) -> None:
        """Run the preflight check"""
        if not self.deployment_config:
            raise RuntimeError("Deployment config not set")
        usage_quota_limits = self._get_usage_quota_limits()
        permissions = self._get_permissions()
        preflight_check = PreflightCheck(self.deployment_config, usage_quota_limits, permissions)
        cli.print_preflight_check(preflight_check)
        cli.output_preflight_check_results_file(preflight_check, self.output_path)

    def _prompt_deployment_config(self) -> None:
        available_subscriptions = self._subscriptions.get_subscriptions()
        scanning_subscription = cli.prompt_scanning_subscription(available_subscriptions)
        (monitored_subscriptions, integration_type) = cli.prompt_monitored_subscriptions(
            available_subscriptions
        )

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
            f"[dim]The following is the updated VM count based on the user-selected regions:[/dim]\n{', '.join(selected_region_names)}"
        )
        cli.print_vm_counts(monitored_subscriptions)

        # Get NAT Gateway preference
        use_nat_gateway = cli.prompt_nat_gateway()

        self.deployment_config = models.DeploymentConfig(
            integration_type=integration_type,
            scanning_subscription=scanning_subscription,
            monitored_subscriptions=monitored_subscriptions,
            regions=selected_region_names,
            use_nat_gateway=use_nat_gateway,
        )

    def _get_scanning_subscription(
        self, scanning_subscription_input: str | None
    ) -> models.Subscription:
        if scanning_subscription_input is not None:
            try:
                return self._subscriptions.get_subscription(scanning_subscription_input.strip())
            except ValueError as e:
                raise typer.BadParameter(
                    "--scanning-subscription must be a valid subscription ID"
                ) from e
        raise typer.BadParameter("--scanning-subscription is required")

    def _get_monitored_subscriptions(
        self,
        monitored_subscriptions_input: str | None,
        excluded_subscriptions_input: str | None,
    ) -> tuple[list[models.Subscription], models.IntegrationType]:
        if monitored_subscriptions_input and excluded_subscriptions_input:
            raise typer.BadParameter(
                "--monitored-subscriptions and --excluded-subscriptions are mutually exclusive"
            )
        if monitored_subscriptions_input:
            return [
                self._subscriptions.get_subscription(sub_id.strip())
                for sub_id in monitored_subscriptions_input.strip().split(",")
            ], models.IntegrationType.SUBSCRIPTION
        if excluded_subscriptions_input:
            return [
                sub
                for sub in self.available_subscriptions
                if sub.id not in excluded_subscriptions_input.strip().split(",")
            ], models.IntegrationType.TENANT
        return self.available_subscriptions, models.IntegrationType.SUBSCRIPTION

    def _get_usage_quota_limits(self) -> dict[str, dict[str, models.UsageQuotaLimit]]:
        cli.console.print("Getting usage quota limits...")
        if not self.deployment_config:
            raise RuntimeError("Deployment config not set")
        return {
            region: self._quotas.get_quota_limits(
                self.deployment_config.scanning_subscription.id, region
            )
            for region in self.deployment_config.regions
        }

    def _get_permissions(self) -> dict[str, list[models.AssignedRole]]:
        cli.console.print("Getting permissions...")
        if not self.deployment_config:
            raise RuntimeError("Deployment config not set")
        # Get permissions for scanning subscription and monitored subscriptions
        subscriptions = [
            *self.deployment_config.monitored_subscriptions,
            self.deployment_config.scanning_subscription,
        ]
        include_root_management_group = (
            self.deployment_config.integration_type == models.IntegrationType.TENANT
        )
        return self._auth.get_all_assigned_roles(subscriptions, include_root_management_group)

    def _get_regions(
        self, monitored_subscriptions: list[models.Subscription], regions_input: str | None
    ) -> list[str]:
        valid_regions = {
            region_name for sub in monitored_subscriptions for region_name in sub.regions
        }
        if not regions_input:
            return list(valid_regions)
        return [
            region_name.strip()
            for region_name in regions_input.strip().split(",")
            if region_name.strip() in valid_regions
        ]


def main(
    scanning_subscription: Annotated[
        str | None,
        typer.Option(
            "--scanning-subscription",
            "-s",
            help="Subscription ID where scanner resources will be deployed",
            rich_help_panel="Deployment Configuration",
        ),
    ] = None,
    monitored_subscriptions: Annotated[
        str | None,
        typer.Option(
            "--monitored-subscriptions",
            "-m",
            help="Subscription IDs (comma-separated) of the subscriptions to be monitored by AWLS; mutually exclusive with --excluded-subscriptions",
            rich_help_panel="Deployment Configuration",
        ),
    ] = None,
    excluded_subscriptions: Annotated[
        str | None,
        typer.Option(
            "--excluded-subscriptions",
            "-e",
            help="Subscription IDs (comma-separated) of the subscriptions to exclude from AWLS monitoring; mutually exclusive with --monitored-subscriptions",
            rich_help_panel="Deployment Configuration",
        ),
    ] = None,
    regions: Annotated[
        str | None,
        typer.Option(
            "--regions",
            "-r",
            help="Azure regions (comma-separated) where scanner will be deployed",
            rich_help_panel="Deployment Configuration",
        ),
    ] = None,
    use_nat_gateway: Annotated[
        bool,
        typer.Option(
            "--nat-gateway/--no-nat-gateway",
            "-n/-N",
            help="Use NAT Gateway for optimized networking (recommended for 1000+ VMs)",
            rich_help_panel="Deployment Configuration",
        ),
    ] = False,
    output_path: Annotated[
        str,
        typer.Option(
            "--output-path",
            "-o",
            help="Path to output the preflight check results",
            rich_help_panel="Output",
        ),
    ] = "./preflight_report.json",
) -> None:
    """
    Preflight check for Azure Agentless Scanner deployment.
    """
    try:
        credential = DefaultAzureCredential()
        app = App(credential, output_path)
        app.configure(
            scanning_subscription,
            monitored_subscriptions,
            excluded_subscriptions,
            regions,
            use_nat_gateway,
        )
        app.run()
    except typer.Exit:
        raise
    except Exception as e:
        cli.console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1) from e
