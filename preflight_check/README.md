# Azure Agentless Scanner Preflight Check

A validation tool to ensure your Azure environment is properly configured for deploying the Lacework Agentless Scanner.

## Overview

This tool performs prerequisite checks to validate:

1. **IAM Permissions**
   - Scanning subscription permissions
   - Monitored subscription permissions 
   - Microsoft Graph API permissions (for service principals)

2. **Resource Quotas**
   - vCPU quotas
   - Public IP address quotas

## Prerequisites
- Authenticated Azure CLI or Azure Service Principal credentials
- [`uv` package manager](https://docs.astral.sh/uv/getting-started/installation/)

## Usage

### Interactive Mode

```bash
uv run preflight_check.py
```

The script will prompt for:
- Integration type (tenant-level or subscription-level)
- Scanning subscription ID
- Deployment regions
- Number of VMs to be scanned
- NAT Gateway preference

### Non-Interactive Mode

```bash
uv run preflight_check.py \
  --integration-type tenant \
  --subscription <SCANNING_SUB_ID> \
  --regions eastus,westus \
  --vm-count 100 \
  --nat-gateway true
```

### Authentication

The script supports two authentication methods:

1. **Azure CLI Authentication**
   ```bash
   az login
   ```

2. **Service Principal Authentication**
   ```bash
   export AZURE_CLIENT_ID="<your-client-id>"
   export AZURE_TENANT_ID="<your-tenant-id>"
   export AZURE_CLIENT_SECRET="<your-client-secret>"
   ```

## Output

The script provides:
- Real-time CLI feedback with validation results
- Detailed error messages and remediation steps
- JSON report file (`preflight_report.json`)

### Sample Output

```
🔍 Azure Preflight Check for Deployment
--------------------------------------
Integration Type: Tenant-Level
Scanning Subscription: ********-****-****-****-************
Deployment Regions: eastus, westus
VMs to be Scanned: 100
Using NAT Gateway: Yes

Checking IAM Permissions...
✅ Scanning subscription permissions verified
✅ Monitored subscriptions permissions verified
✅ Microsoft Graph permissions verified

Checking Resource Quotas...
✅ vCPU quota sufficient in eastus (50 required, 100 available)
✅ vCPU quota sufficient in westus (50 required, 100 available)
✅ NAT Gateway deployment selected - no public IP quota check required

📊 Summary: All checks passed! Ready for deployment.
💾 Detailed report saved to preflight_report.json
```
