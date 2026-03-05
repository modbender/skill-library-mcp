# auditclaw-gcp

GCP compliance evidence collection companion skill for the AuditClaw GRC platform.

## Overview

This skill runs automated security checks against a Google Cloud Platform project and stores evidence in the shared GRC database. It supports 9 check categories producing 12 individual findings mapped to SOC 2, ISO 27001, and HIPAA controls.

## Quick Start

```bash
# Install dependencies
pip install -r scripts/requirements.txt

# Set up authentication (one of):
gcloud auth application-default login
# or
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# Set project
export GCP_PROJECT_ID=my-project-id

# Run all checks
python3 scripts/gcp_evidence.py --db-path ~/.openclaw/grc/compliance.sqlite --all

# Run specific checks
python3 scripts/gcp_evidence.py --db-path ~/.openclaw/grc/compliance.sqlite --checks storage,iam

# List available checks
python3 scripts/gcp_evidence.py --list-checks
```

## Checks

| Check | Findings | CIS Benchmark |
|-------|----------|--------------|
| storage | Uniform bucket access, public prevention | 5.1 |
| firewall | No unrestricted ingress (SSH/RDP/all) | 3.6, 3.7 |
| iam | SA key rotation, SA admin privilege | 1.5, 1.7 |
| logging | Audit logs enabled, export sink exists | 2.1, 2.2 |
| kms | Key rotation <= 90 days | 1.10 |
| dns | DNSSEC on public zones | 3.3 |
| bigquery | No public dataset access | 7.1 |
| compute | No default SA with cloud-platform | 4.1, 4.2 |
| cloudsql | SSL enforcement, no public IP | 6.4, 6.5 |

## Testing

```bash
python3 -m pytest tests/ -v
```

All tests use `unittest.mock.MagicMock` -- no GCP credentials required.
