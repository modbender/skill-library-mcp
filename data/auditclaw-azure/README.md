# auditclaw-azure

Azure compliance evidence collection companion skill for the AuditClaw GRC platform.

## Overview

This skill runs automated security checks against an Azure subscription and stores
evidence in the shared GRC database. It checks storage accounts, network security groups,
Key Vault configuration, SQL Server settings, VM disk encryption, App Service TLS,
and Microsoft Defender for Cloud plans.

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r scripts/requirements.txt
   ```

2. Configure Azure credentials:
   ```bash
   # Option A: Service principal
   export AZURE_SUBSCRIPTION_ID="your-subscription-id"
   export AZURE_CLIENT_ID="your-client-id"
   export AZURE_TENANT_ID="your-tenant-id"
   export AZURE_CLIENT_SECRET="your-client-secret"

   # Option B: Azure CLI
   az login
   export AZURE_SUBSCRIPTION_ID="your-subscription-id"
   ```

3. Run all checks:
   ```bash
   python3 scripts/azure_evidence.py --db-path ~/.openclaw/grc/compliance.sqlite --all
   ```

## Checks

| # | File | Findings | CIS Benchmark |
|---|------|----------|---------------|
| 1 | storage.py | HTTPS-only, TLS 1.2, public blob, network deny | 3.1, 3.15, 3.7, 3.8 |
| 2 | network.py | No open SSH, no open RDP | 6.1, 6.2 |
| 3 | keyvault.py | Soft delete + purge protection | 8.5 |
| 4 | sql.py | Auditing enabled, TDE encryption | 4.1.1, 4.1.5 |
| 5 | compute.py | VM disk encryption at host | 7.4 |
| 6 | appservice.py | HTTPS + TLS 1.2 | 9.2, 9.3 |
| 7 | defender.py | Standard tier plans | 2.1.x |

## Required Azure Roles

- **Reader** (subscription scope)
- **Security Reader** (subscription scope)

All checks use read-only access. No modifications are made to your Azure resources.

## Testing

```bash
python3 -m pytest tests/ -v
```

All tests use `unittest.mock.MagicMock` -- no Azure credentials needed.
