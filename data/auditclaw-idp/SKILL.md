---
name: auditclaw-idp
description: Identity provider compliance checks for auditclaw-grc. 8 read-only checks across Google Workspace (MFA, admin audit, inactive users, passwords) and Okta (MFA, password policy, inactive users, session policy).
version: 1.0.0
user-invocable: true
homepage: https://www.auditclaw.ai
source: https://github.com/avansaber/auditclaw-idp
metadata: {"openclaw":{"type":"executable","install":{"pip":"scripts/requirements.txt"},"requires":{"bins":["python3"],"env":[],"optionalEnv":["GOOGLE_WORKSPACE_SA_KEY","GOOGLE_WORKSPACE_ADMIN_EMAIL","OKTA_ORG_URL","OKTA_API_TOKEN"]}}}
---
# AuditClaw IDP

Companion skill for auditclaw-grc. Collects compliance evidence from Google Workspace and Okta identity providers using read-only API calls.

**8 checks | Read-only API access | Evidence stored in shared GRC database**

## Security Model
- **Read-only access**: Google Workspace uses `admin.directory.user.readonly` scope only. Okta uses `okta.users.read`, `okta.factors.read`, `okta.policies.read` scopes only. No write/modify permissions.
- **Credentials**: Uses standard env vars for each provider. No credentials stored by this skill.
- **Dependencies**: Google API client + requests (all pinned in requirements.txt)
- **Data flow**: Check results stored as evidence in `~/.openclaw/grc/compliance.sqlite` via auditclaw-grc

## Prerequisites
- **Google Workspace:** Service account JSON with domain-wide delegation, admin email for impersonation
- **Okta:** API token (SSWS) with read-only scopes
- `pip install -r scripts/requirements.txt`
- auditclaw-grc skill installed and initialized

## Environment Variables

### Google Workspace (optional; skip if not configured)
- `GOOGLE_WORKSPACE_SA_KEY`: Path to service account JSON file
- `GOOGLE_WORKSPACE_ADMIN_EMAIL`: Super admin email to impersonate

### Okta (optional; skip if not configured)
- `OKTA_ORG_URL`: Okta organization URL (e.g., https://mycompany.okta.com)
- `OKTA_API_TOKEN`: Okta API token

## Commands
- "Run IDP evidence sweep": Run all checks for configured providers
- "Check Google Workspace MFA": Run Google MFA check
- "Check Okta password policies": Run Okta password policy check
- "Show IDP integration health": Last sync, errors, evidence count

## Usage
All evidence is stored in the shared GRC database at ~/.openclaw/grc/compliance.sqlite
via the auditclaw-grc skill's db_query.py script.

To run a full evidence sweep (all configured providers):
```
python3 scripts/idp_evidence.py --db-path ~/.openclaw/grc/compliance.sqlite --all
```

To run checks for a specific provider:
```
python3 scripts/idp_evidence.py --db-path ~/.openclaw/grc/compliance.sqlite --provider google
python3 scripts/idp_evidence.py --db-path ~/.openclaw/grc/compliance.sqlite --provider okta
```

To run specific checks:
```
python3 scripts/idp_evidence.py --db-path ~/.openclaw/grc/compliance.sqlite --checks google_mfa,okta_mfa
```

## Check Categories (8)

| Check | Provider | What It Verifies |
|-------|----------|-----------------|
| **google_mfa** | Google Workspace | All active users have 2SV enrolled + enforced |
| **google_admins** | Google Workspace | Super admin count 2-4, all with 2SV |
| **google_inactive** | Google Workspace | No active users with lastLoginTime > 90 days |
| **google_passwords** | Google Workspace | All users have passwordStrength == "STRONG" |
| **okta_mfa** | Okta | All active users have at least 1 MFA factor enrolled |
| **okta_passwords** | Okta | Password policy: minLength>=12, history>=5, maxAttempts<=5, maxAge<=90 |
| **okta_inactive** | Okta | No active users with lastLogin > 90 days |
| **okta_sessions** | Okta | MFA required, session lifetime <= 12h, idle <= 1h |

## Evidence Storage
Each check produces evidence items stored with:
- `source: "idp"`
- `type: "automated"`
- `control_id`: Mapped to relevant SOC2/ISO/NIST/HIPAA controls
- `description`: Human-readable finding summary
- `file_content`: JSON details of the check result

## Setup Guide

AuditClaw supports two identity providers. Configure one or both.

### Google Workspace Setup

**Step 1: Enable Admin SDK API**
Go to Google Cloud Console → APIs & Services → Library → Enable "Admin SDK API"

**Step 2: Create Service Account**
IAM & Admin → Service Accounts → Create. Enable domain-wide delegation.

**Step 3: Grant OAuth Scopes**
In Google Admin → Security → API controls → Domain-wide delegation, add the service account with:
- `https://www.googleapis.com/auth/admin.directory.user.readonly`
- `https://www.googleapis.com/auth/admin.reports.audit.readonly`

**Step 4: Set Environment Variables**
- GOOGLE_WORKSPACE_SA_KEY=/path/to/service-account.json
- GOOGLE_WORKSPACE_ADMIN_EMAIL=admin@yourdomain.com

### Okta Setup

**Step 1: Create API Token**
Okta Admin → Security → API → Tokens → Create Token. Name: auditclaw-scanner

**Step 2: Required Permissions**
The token inherits the creating admin's permissions. Needs read access to: users, factors, policies.
Scopes: `okta.users.read`, `okta.factors.read`, `okta.policies.read`

**Step 3: Set Environment Variables**
- OKTA_ORG_URL=https://mycompany.okta.com
- OKTA_API_TOKEN=your-token-here

### Verify Connection
Run: `python3 {baseDir}/scripts/idp_evidence.py --test-connection`

The exact permissions are documented in `scripts/idp-permissions.json`. Show with:
  python3 {baseDir}/../auditclaw-grc/scripts/db_query.py --action show-policy --provider idp
