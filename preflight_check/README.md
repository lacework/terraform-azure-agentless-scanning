# Azure Agentless Workload Scanner Preflight Check

A validation tool to ensure your Azure environment is properly configured for deploying the Lacework Agentless Scanner.

## Overview

This tool
1. counts the VMs in your Azure environment, and 
2. validates the following resource quotas (computed based on the number of VMs to be scanned by AWLS):
   - vCPU quotas
   - Public IP address quotas (if deploying without a NAT Gateway)

## Prerequisites
1. [Authenticate Azure CLI](#authentication--authorization)
1. [Install `uv` package manager](https://docs.astral.sh/uv/getting-started/installation/)

## Usage

### Interactive Mode

```bash
uv run -m preflight_check
```

You will be prompted for the following information about how you intend to deploy AWLS:
- Scanning subscription: The subscription where AWLS resources will be deployed
- Monitored subscriptions: You can optionally specify a set of subscriptions that you wish for AWLS to monitor (or you can specify a set of subscriptions to exclude from monitoring - all other subscriptions in the tenant will be monitored)
  - By default, if you do not specify any subscriptions for AWLS to monitor or exclude from monitoring, all subscriptions in the tenant will be monitored by AWLS
- Regions: List of regions AWLS will monitor (and where scanning resources will be deployed)
- NAT Gateway preference: Whether AWLS will be deployed with a NAT Gateway or use public IP addresses for outbound internet access

### Non-Interactive Mode

```bash
 uv run -m preflight_check --help

 Usage: python -m preflight_check [OPTIONS]

 Preflight check for Azure Agentless Workload Scanner deployment.

╭─ Options ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                                                                       │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Deployment Configuration ────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --scanning-subscription    -s                        TEXT  Subscription ID where scanner resources will be deployed               │
│                                                            [default: None]                                                        │
│ --monitored-subscriptions  -m                        TEXT  Subscription IDs (comma-separated) of the subscriptions to be          │
│                                                            monitored by AWLS; mutually exclusive with --excluded-subscriptions    │
│                                                            [default: None]                                                        │
│ --excluded-subscriptions   -e                        TEXT  Subscription IDs (comma-separated) of the subscriptions to exclude     │
│                                                            from AWLS monitoring; mutually exclusive with                          │
│                                                            --monitored-subscriptions                                              │
│                                                            [default: None]                                                        │
│ --regions                  -r                        TEXT  Regions (comma-separated) where AWLS will be deployed - if not         │
│                                                            provided, all regions will be monitored                                │
│                                                            [default: None]                                                        │
│ --nat-gateway              -n  --no-nat-gateway  -N        Use NAT Gateway for optimized networking                               │
│                                                            [default: no-nat-gateway]                                              │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Output ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --output-path  -o      TEXT  Path to output the preflight check results [default: ./preflight_report.json]                        │
│ --no-emoji     -e            Disable emoji rendering in the preflight check output                                                │
│ --debug        -d            Enable debug logging                                                                                 │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

```bash
uv run preflight_check.py \
  --scanning-subscription "scanning-subscription-id" \
  --monitored-subscriptions "monitored-subscription-id-1,monitored-subscription-id-2" \
  --regions "eastus,eastus2,westus,westus2" \
  --no-nat-gateway \
  --output-path "./preflight_report.json"
```

### Sample Output

```
Preflight Check Summary
-----------------------
Scanning Subscription: LaceworkAWLS (********-****-****-****-************)
Monitored Subscriptions:
  - MonitoredSubscription1 (********-****-****-****-************)
  - MonitoredSubscription2 (********-****-****-****-************)
  - MonitoredSubscription3 (********-****-****-****-************)
Regions: eastus, eastus2, westus, westus2
Use NAT Gateway: False


✅ All usage quota limits are sufficient!
✅ All permission checks passed!

💾 Detailed results written to preflight_report.json
```

## Authentication & Authorization

We suggest creating a new Azure service principal to use specifically for deploying AWLS as instructed [here](../service_principal).

### Authenticating with the Service Principal

Once the service principal has been created and assigned the necessary permissions, you can authenticate Azure CLI using the service principal as instructed here: https://learn.microsoft.com/en-us/cli/azure/authenticate-azure-cli-service-principal.