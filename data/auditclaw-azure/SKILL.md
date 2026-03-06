---
name: auditclaw-azure
description: Azure compliance evidence collection for auditclaw-grc. 12 read-only checks across storage, NSG, Key Vault, SQL, compute, App Service, and Defender for Cloud.
version: 1.0.1
user-invocable: true
homepage: https://www.auditclaw.ai
source: https://github.com/avansaber/auditclaw-azure
metadata: {"openclaw":{"type":"executable","install":{"pip":"scripts/requirements.txt"},"requires":{"bins":["python3"],"env":["AZURE_SUBSCRIPTION_ID","AZURE_CLIENT_ID","AZURE_CLIENT_SECRET","AZURE_TENANT_ID"]}}}
---
# AuditClaw Azure

Companion skill for auditclaw-grc. Collects compliance evidence from Azure subscriptions using read-only API calls.

**12 checks | Reader + Security Reader roles only | Evidence stored in shared GRC database**

## Security Model
- **Read-only access**: Requires only Reader + Security Reader roles (subscription-level). No write/modify permissions.
- **Credentials**: Uses `DefaultAzureCredential` (service principal env vars, `az login`, or managed identity). No credentials stored by this skill.
- **Dependencies**: Azure SDK packages (all pinned in requirements.txt)
- **Data flow**: Check results stored as evidence in `~/.openclaw/grc/compliance.sqlite` via auditclaw-grc

## Prerequisites
- Azure credentials configured (service principal or `az login`)
- `pip install -r scripts/requirements.txt`
- auditclaw-grc skill installed and initialized

## Commands
- "Run Azure evidence sweep": Run all checks, store results in GRC database
- "Check Azure storage security": Run storage-specific checks
- "Check Azure network security": Run NSG checks
- "Check Azure Key Vault": Run Key Vault checks
- "Check Azure SQL compliance": Run SQL Server checks
- "Check Azure VM encryption": Run compute checks
- "Check Azure App Service": Run App Service checks
- "Check Azure Defender": Run Defender for Cloud checks
- "Show Azure integration health": Last sync, errors, evidence count

## Usage
All evidence is stored in the shared GRC database at ~/.openclaw/grc/compliance.sqlite
via the auditclaw-grc skill's db_query.py script.

To run a full evidence sweep:
```
python3 scripts/azure_evidence.py --db-path ~/.openclaw/grc/compliance.sqlite --all
```

To run specific checks:
```
python3 scripts/azure_evidence.py --db-path ~/.openclaw/grc/compliance.sqlite --checks storage,network,keyvault
```

To list available checks:
```
python3 scripts/azure_evidence.py --list-checks
```

## Check Categories (7 files, 12 findings)

| Check | What It Verifies |
|-------|-----------------|
| **storage** | HTTPS-only transfer, TLS 1.2+, public blob access disabled, network default deny |
| **network** | NSG no unrestricted SSH (port 22), no unrestricted RDP (port 3389) |
| **keyvault** | Soft delete + purge protection enabled |
| **sql** | Server auditing enabled, TDE encryption on all databases |
| **compute** | VM disk encryption (encryption at host) |
| **appservice** | HTTPS-only + TLS 1.2+ |
| **defender** | Defender plans enabled (Standard tier) for critical resource types |

## Authentication
Uses `DefaultAzureCredential` from `azure-identity`. Supports:
- Service principal: `AZURE_CLIENT_ID` + `AZURE_TENANT_ID` + `AZURE_CLIENT_SECRET`
- Azure CLI: `az login`
- Managed identity (when running in Azure)

Minimum roles: **Reader** + **Security Reader** (subscription-level)

## Evidence Storage
Each check produces evidence items stored with:
- `source: "azure"`
- `type: "automated"`
- `control_id`: Mapped to relevant SOC2/ISO/HIPAA controls
- `description`: Human-readable finding summary
- `file_content`: JSON details of the check result

## Setup Guide

When a user asks to set up Azure integration, guide them through these steps:

### Step 1: Create Service Principal
```
az ad sp create-for-rbac --name auditclaw-scanner --role Reader --scopes /subscriptions/<SUBSCRIPTION_ID>
```

### Step 2: Add Security Reader Role
```
az role assignment create --assignee <APP_ID> --role "Security Reader" --scope /subscriptions/<SUBSCRIPTION_ID>
```

Only 2 roles needed: **Reader** + **Security Reader** (subscription-level).

### Step 3: Configure Credentials
Set environment variables from the service principal output:
- AZURE_CLIENT_ID (appId)
- AZURE_CLIENT_SECRET (password)
- AZURE_TENANT_ID (tenant)
- AZURE_SUBSCRIPTION_ID

### Step 4: Verify Connection
Run: `python3 {baseDir}/scripts/azure_evidence.py --test-connection`

The exact roles are documented in `scripts/azure-roles.json`. Show with:
  python3 {baseDir}/../auditclaw-grc/scripts/db_query.py --action show-policy --provider azure
