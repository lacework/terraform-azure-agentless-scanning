import typer
from rich.console import Console
from rich.prompt import Prompt, Confirm
from typing import Optional, List

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

def prompt_for_config() -> PreflightConfig:
    """Interactive prompt for configuration values with user-friendly messages"""
    console.print("\n🔍 [bold]Preflight Check for Azure AWLS Deployment[/bold]")
    console.print("-" * 40)

    # Integration Type
    console.print("\n[bold]Integration Type[/bold]")
    console.print("[dim]Choose whether to deploy the scanner at the tenant level or subscription level.[/dim]")
    integration_type = Prompt.ask(
        "Integration type",
        choices=["tenant", "subscription"]
    )
    
    # Scanning Subscription
    console.print("\n[bold]Scanning Subscription[/bold]")
    console.print("[dim]This is where the AWLS scanning resources will be deployed.[/dim]")
    scanning_sub = Prompt.ask("Subscription ID")
    
    # Regions
    console.print("\n[bold]Deployment Regions[/bold]")
    console.print("[dim]Enter the Azure regions where your VMs are located.[/dim]")
    console.print("[dim]The scanner will be deployed in these regions.[/dim]")
    regions_input = Prompt.ask(
        "Azure regions (comma-separated)",
    )
    regions = [r.strip() for r in regions_input.split(",")]
    
    # VM Count - This will be replaced with automatic enumeration
    detected_vm_count = 100
    console.print("\n[bold]VM Count[/bold]")
    console.print(f"We've detected {detected_vm_count} VMs in your environment that would be scanned by AWLS.")
    console.print("[dim]You can provide your own count if needed.[/dim]")
    vm_count = int(Prompt.ask(
        "Number of VMs",
        default=detected_vm_count
    ))
    
    # NAT Gateway
    console.print("\n[bold]Network Configuration[/bold]")
    console.print("We recommend deploying AWLS with a NAT Gateway, but you can opt out if you prefer.")
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

@app.command()
def main(
    integration_type: Optional[str] = typer.Option(
        None, 
        help="Integration type: tenant or subscription"
    ),
    subscription: Optional[str] = typer.Option(
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
        subscription,
        regions,
        vm_count is not None,
        nat_gateway is not None
    ])

    if is_interactive:
        config = prompt_for_config()
    else:
        config = PreflightConfig(
            integration_type=integration_type,
            scanning_subscription=subscription,
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
    console.print(f"Using NAT Gateway: {'Yes' if config.use_nat_gateway else 'No'}\n")

    # TODO: Implement validation logic here

if __name__ == "__main__":
    app()
