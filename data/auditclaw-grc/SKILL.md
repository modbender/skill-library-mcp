---
name: auditclaw-grc
description: AI-native GRC (Governance, Risk, and Compliance) for OpenClaw. 97 actions across 13 frameworks including SOC 2, ISO 27001, HIPAA, GDPR, NIST CSF, PCI DSS, CIS Controls, CMMC, HITRUST, CCPA, FedRAMP, ISO 42001, and SOX ITGC. Manages controls, evidence, risks, policies, vendors, incidents, assets, training, vulnerabilities, access reviews, and questionnaires. Generates compliance scores, reports, dashboards, and trust center pages. Runs security header, SSL, and GDPR scans. Connects to AWS, Azure, GCP, GitHub, and identity providers via companion skills.
version: 1.0.0
user-invocable: true
homepage: https://www.auditclaw.ai
source: https://github.com/avansaber/auditclaw-grc
metadata: {"openclaw":{"type":"executable","install":{"pip":"scripts/requirements.txt","post":"python3 scripts/init_db.py"},"requires":{"bins":["python3"],"anyBins":["chromium","google-chrome","brave","chromium-browser"],"env":[],"optionalEnv":["AWS_ACCESS_KEY_ID","GITHUB_TOKEN","AZURE_SUBSCRIPTION_ID","GCP_PROJECT_ID","GOOGLE_APPLICATION_CREDENTIALS","GOOGLE_WORKSPACE_SA_KEY","OKTA_ORG_URL"]},"os":["darwin","linux"]}}
---

# AuditClaw GRC

AI-native GRC assistant for OpenClaw. Manages compliance frameworks, controls, evidence, risks, policies, vendors, incidents, assets, training, vulnerabilities, access reviews, and questionnaires.

**97 actions | 30 tables | 13 frameworks | 990+ controls**

## Security Model

- **Database**: SQLite at `~/.openclaw/grc/compliance.sqlite` with WAL mode, owner-only permissions (0o600)
- **Credentials**: Stored in `~/.openclaw/grc/credentials/` with per-provider directories, owner-only permissions (0o700 dirs, 0o600 files), atomic writes, and secure deletion (overwrite with random bytes before removal). Secrets are never logged or exposed in output. See `scripts/credential_store.py` for implementation.
- **Trust center**: Generates a local HTML file only. Nothing is published externally. The user decides where to host it.
- **Dependencies**: `requests==2.31.0` (pinned) for HTTP header scanning. Cloud integrations optionally use `boto3` (AWS) and `PyJWT` (Azure) via try/except -- these are not required and only activate if installed and credentials are configured.
- **Scans**: All security scans (headers, SSL, GDPR) run locally against user-specified URLs only.
- **No telemetry**: No data is sent to external endpoints. All operations are local or to user-configured cloud accounts only.

### Optional Environment Variables (for cloud integrations)

These are **not required** for core GRC functionality. They are only used when the user explicitly sets up cloud provider integrations via companion skills:

| Variable | Used by |
|----------|---------|
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` | AWS integration (via auditclaw-aws) |
| `GITHUB_TOKEN` | GitHub integration (via auditclaw-github) |
| `AZURE_SUBSCRIPTION_ID` / `AZURE_CLIENT_ID` / `AZURE_CLIENT_SECRET` / `AZURE_TENANT_ID` | Azure integration (via auditclaw-azure) |
| `GCP_PROJECT_ID` / `GOOGLE_APPLICATION_CREDENTIALS` | GCP integration (via auditclaw-gcp) |
| `GOOGLE_WORKSPACE_SA_KEY` / `GOOGLE_WORKSPACE_ADMIN_EMAIL` | Google Workspace (via auditclaw-idp) |
| `OKTA_ORG_URL` / `OKTA_API_TOKEN` | Okta (via auditclaw-idp) |

## Setup

```bash
python3 {baseDir}/scripts/init_db.py
pip install -r {baseDir}/scripts/requirements.txt
```

Database: `~/.openclaw/grc/compliance.sqlite`

## Voice and Formatting

- Present data as formatted summaries, not raw JSON
- Keep messages under 4096 chars. Show top 5-10 rows, offer "Want the full list?"
- Emoji: ✅ complete, ⚠️ at-risk, 🔴 critical, 📊 scores, 📋 reports, 🔒 security
- Include context: "23/43 controls complete (53%)" not just "23"
- After each action, suggest the next logical step

## Activation Triggers

Activate on: compliance, GRC, SOC 2, ISO 27001, HIPAA, GDPR, NIST, PCI DSS, CIS, CMMC, HITRUST, CCPA, FedRAMP, ISO 42001, SOX, ITGC, controls, evidence, risks, audit, gap analysis, security posture, compliance score, framework, security scan.

## Database Operations

All queries go through: `python3 {baseDir}/scripts/db_query.py --action <action> [args]`

Output is JSON. Parse and present as human-readable summaries. For full action reference with all arguments: `{baseDir}/references/db-actions.md`

### Core Actions

| Action | Purpose |
|--------|---------|
| `status` | Overall compliance overview |
| `activate-framework --slug soc2` | Load framework controls |
| `gap-analysis --framework soc2` | Gaps with priority and effort |
| `score-history --framework soc2` | Score trend over time |
| `list-controls --framework soc2 --status in_progress` | Filtered controls |
| `update-control --id 5 --status complete` | Update control (also batch: `--id 1,2,3`) |
| `add-evidence --title "..." --control-ids 1,2,3` | Record evidence |
| `add-risk --title "..." --likelihood 3 --impact 4` | Log a risk |
| `add-vendor --name "..." --criticality high` | Register vendor |
| `add-incident --title "..." --severity critical` | Log incident |
| `generate-report --framework soc2` | HTML compliance report |
| `generate-dashboard` | Dashboard summary + Canvas HTML |
| `export-evidence --framework soc2` | ZIP package for auditors |
| `list-companions` | Show installed companion skills |

### Additional Action Categories

- **Policies**: add, version, submit approval, review, require acknowledgment
- **Training**: add modules, assign, track completion, list overdue
- **Vulnerabilities**: add with CVE/CVSS, track remediation
- **Access Reviews**: create campaigns, add items, approve/revoke
- **Questionnaires**: create templates, send to vendors, record answers, score
- **Incidents**: add actions (timeline), post-incident reviews, summary with MTTR
- **Assets**: register with classification, lifecycle, encryption/backup/patch status
- **Alerts**: add, list, acknowledge, resolve
- **Integrations**: add provider, test connection, setup guide, show policy

## Framework Activation

Run: `python3 {baseDir}/scripts/db_query.py --action activate-framework --slug <slug>`

| Framework | Slug | Controls |
|-----------|------|----------|
| SOC 2 Type II | soc2 | 43 |
| ISO 27001:2022 | iso27001 | 114 |
| HIPAA Security Rule | hipaa | 29 |
| GDPR | gdpr | 25 |
| NIST CSF | nist-csf | 31 |
| PCI DSS v4.0 | pci-dss | 30 |
| CIS Controls v8 | cis-controls | 153 |
| CMMC 2.0 | cmmc | 113 |
| HITRUST CSF v11 | hitrust | 152 |
| CCPA/CPRA | ccpa | 28 |
| FedRAMP Moderate | fedramp | 282 |
| ISO 42001:2023 | iso42001 | 40 |
| SOX ITGC | sox-itgc | 50 |

Framework reference docs: `{baseDir}/references/frameworks/`

## Compliance Score

Run: `python3 {baseDir}/scripts/compliance_score.py [--framework <slug>] [--store]`

Returns score (0-100), health distribution, trend, and drift detection. Use `--store` to save for tracking. Methodology: `{baseDir}/references/scoring-methodology.md`

## Security Scanning

- **Headers**: `python3 {baseDir}/scripts/check_headers.py --url <url>` (CSP, HSTS, X-Frame-Options, etc.)
- **SSL/TLS**: `python3 {baseDir}/scripts/check_ssl.py --domain <domain>` (cert validity, chain, cipher)
- **GDPR**: Browser-based cookie consent check (requires Chromium)

After scans, offer to save results as evidence.

## Reports and Exports

- **Report**: `python3 {baseDir}/scripts/generate_report.py --framework <slug> --format html`
- **Trust center**: `python3 {baseDir}/scripts/generate_trust_center.py [--org-name "Acme Corp"]` (local HTML only)
- **Evidence export**: `python3 {baseDir}/scripts/export_evidence.py --framework <slug>`

## Interactive Flows

### First-Time Setup
When user asks to set up compliance: initialize DB silently, present framework options with control counts and use cases, offer gap analysis after activation.

### Smart Defaults
- Evidence type: infer from context (manual/automated/integration)
- Risk assessment: suggest likelihood/impact with reasoning, confirm before saving
- Bulk operations: list exactly what will change, confirm, report summary

### Proactive Suggestions
After framework activation -> offer gap analysis and cloud integration setup.
After marking controls complete -> offer score recalculation.
After scanning -> offer to save as evidence.
After scoring (< 30%) -> prioritize critical controls. (>= 90%) -> offer audit report.

## Slash Commands

| Command | Action |
|---------|--------|
| `/grc-score` | Quick compliance score |
| `/grc-gaps` | Priority gaps |
| `/grc-scan` | Security scan menu |
| `/grc-report` | Generate report |
| `/grc-risks` | Risk register |
| `/grc-incidents` | Active incidents |
| `/grc-trust` | Generate trust center |

## Scheduled Alerts (Cron)

Register via OpenClaw cron tool:
- Evidence expiry: daily 7 AM
- Score recalc: every 6 hours
- Weekly digest: Monday 8 AM

Always include "Using auditclaw-grc skill" in cron messages for routing.

## Companion Skills

Optional add-ons for automated cloud evidence collection. Evidence flows into the shared GRC database.

| Skill | Checks | Setup |
|-------|--------|-------|
| **auditclaw-aws** | 15 AWS checks (S3, IAM, CloudTrail, VPC, etc.) | `aws configure` with read-only IAM policy |
| **auditclaw-github** | 9 GitHub checks (branch protection, secrets, 2FA, etc.) | `GITHUB_TOKEN` env var |
| **auditclaw-azure** | 12 Azure checks (storage, NSG, Key Vault, etc.) | Service principal with Reader + Security Reader |
| **auditclaw-gcp** | 12 GCP checks (storage, firewall, IAM, etc.) | `GOOGLE_APPLICATION_CREDENTIALS` with Viewer + Security Reviewer |
| **auditclaw-idp** | 8 identity checks (Google Workspace + Okta) | SA key + admin email / Okta API token |

Install: `clawhub install auditclaw-<provider>`

If a user asks to connect a cloud provider, check `list-companions` first. If not installed, guide them to install it.

### Integration Setup

Say "setup aws", "setup github", etc. to get step-by-step guides with exact permissions. Use "test aws connection" to verify before running scans.

## Reference Files

- `{baseDir}/references/db-actions.md` - Full action reference with all arguments
- `{baseDir}/references/schema.md` - Database schema
- `{baseDir}/references/scoring-methodology.md` - Scoring algorithm
- `{baseDir}/references/commands/` - Detailed command guides
- `{baseDir}/references/frameworks/` - Framework reference docs
- `{baseDir}/references/integrations/` - Cloud integration guides
