---
name: auditclaw-github
description: GitHub compliance evidence collection for auditclaw-grc. 9 read-only checks covering branch protection, secret scanning, 2FA, Dependabot, deploy keys, audit logs, webhooks, CODEOWNERS, and CI/CD security.
version: 1.0.1
user-invocable: true
homepage: https://www.auditclaw.ai
source: https://github.com/avansaber/auditclaw-github
metadata: {"openclaw":{"type":"executable","install":{"pip":"scripts/requirements.txt"},"requires":{"bins":["python3"],"env":["GITHUB_TOKEN"]}}}
---
# AuditClaw GitHub

Companion skill for auditclaw-grc. Collects compliance evidence from GitHub organizations using read-only API calls.

**9 checks | Read-only token permissions | Evidence stored in shared GRC database**

## Security Model
- **Read-only access**: Uses fine-grained personal access token with read-only repository and organization permissions. No write access.
- **Credentials**: Uses `GITHUB_TOKEN` env var. No credentials stored by this skill.
- **Dependencies**: `PyGithub==2.8.1` (pinned)
- **Data flow**: Check results stored as evidence in `~/.openclaw/grc/compliance.sqlite` via auditclaw-grc

## Prerequisites
- GitHub personal access token with read-only permissions (or classic token with `repo`, `read:org`, `security_events`)
- Set as `GITHUB_TOKEN` environment variable
- `pip install -r scripts/requirements.txt`
- auditclaw-grc skill installed and initialized

## Commands
- "Run GitHub evidence sweep": Run all checks, store results in GRC database
- "Check branch protection": Verify branch protection rules
- "Check secret scanning": Review secret scanning alerts
- "Check Dependabot alerts": Review dependency vulnerability alerts
- "Show GitHub integration health": Last sync, errors, evidence count

## Usage
All evidence is stored in the shared GRC database at ~/.openclaw/grc/compliance.sqlite
via the auditclaw-grc skill's db_query.py script.

To run a full evidence sweep:
```
python3 scripts/github_evidence.py --db-path ~/.openclaw/grc/compliance.sqlite --org my-org --all
```

To run specific checks:
```
python3 scripts/github_evidence.py --db-path ~/.openclaw/grc/compliance.sqlite --org my-org --checks branch_protection,secret_scanning
```

## Check Categories (9)

| Check | What It Verifies |
|-------|-----------------|
| **branch_protection** | Default branch protection rules, required reviews, status checks |
| **secret_scanning** | Secret scanning enabled, active alert count |
| **dependabot** | Dependabot alerts by severity, auto-fix PRs |
| **two_factor** | Organization-level 2FA enforcement |
| **deploy_keys** | Deploy key audit, read-only vs read-write |
| **audit_log** | Admin audit log accessibility |
| **webhooks** | Webhook security (HTTPS, secrets configured) |
| **codeowners** | CODEOWNERS file present in repositories |
| **ci_cd** | GitHub Actions security, workflow permissions |

## Evidence Storage
Each check produces evidence items stored with:
- `source: "github"`
- `type: "automated"`
- `control_id`: Mapped to relevant SOC2/ISO/HIPAA controls
- `description`: Human-readable finding summary
- `file_content`: JSON details of the check result

## Setup Guide

When a user asks to set up GitHub integration, guide them through these steps:

### Step 1: Create Fine-Grained Personal Access Token
Direct user to: GitHub → Settings → Developer Settings → Personal Access Tokens → Fine-grained tokens

### Step 2: Configure Token Permissions
- Name: `auditclaw-grc`
- Expiration: 90 days (recommended)
- Resource owner: Select their organization
- Repository access: All repositories (or specific repos)
- Permissions (all READ-ONLY):
  - **Repository:** Contents, Administration, Secret scanning alerts, Dependabot alerts, Code scanning alerts, Actions, Webhooks
  - **Organization:** Members (read), Administration (read)

**Classic token alternative:** If fine-grained tokens unavailable, use scopes: `repo`, `read:org`, `security_events`

### Step 3: Set Token
Set as GITHUB_TOKEN environment variable.

### Step 4: Verify Connection
Run: `python3 {baseDir}/scripts/github_evidence.py --test-connection`

The exact permissions are documented in `scripts/github-permissions.json`. Show with:
  python3 {baseDir}/../auditclaw-grc/scripts/db_query.py --action show-policy --provider github
