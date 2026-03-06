# AuditClaw GRC

AI-native GRC (Governance, Risk and Compliance) skill for [OpenClaw](https://openclaw.ai).
Manage SOC 2, ISO 27001, HIPAA, and 10+ more compliance frameworks from your chat.

## Features

- **13 Compliance Frameworks**: SOC 2, ISO 27001, HIPAA, GDPR, PCI DSS, NIST CSF, CCPA, HITRUST, CIS Controls, CMMC 2.0, FedRAMP, ISO 42001, SOX ITGC
- **97 Database Actions**: Full CRUD for frameworks, controls, evidence, risks, incidents, policies, vendors, assets, vulnerabilities, training, access reviews, and more
- **Compliance Scoring**: Weighted scoring with historical trend tracking across all active frameworks
- **Cross-Framework Mapping**: Evidence collected for one framework automatically satisfies overlapping controls in others
- **Real-time Drift Detection**: Monitors compliance drift and alerts when scores drop
- **Auto-generated Trust Center**: Public-facing compliance status page
- **AI-generated Policies**: Framework-aligned policy documents tailored to your organisation
- **Canvas Dashboard**: Web-based GRC dashboard with real-time metrics

## Companion Skills

AuditClaw works with companion skills for cloud evidence collection (each is a separate repo):

| Skill | Checks | Repo |
|-------|--------|------|
| **auditclaw-aws** | 15 automated AWS checks | [auditclaw-aws](https://github.com/avansaber/auditclaw-aws) |
| **auditclaw-github** | 9 automated GitHub checks | [auditclaw-github](https://github.com/avansaber/auditclaw-github) |
| **auditclaw-azure** | 12 automated Azure checks | [auditclaw-azure](https://github.com/avansaber/auditclaw-azure) |
| **auditclaw-gcp** | 12 automated GCP checks | [auditclaw-gcp](https://github.com/avansaber/auditclaw-gcp) |
| **auditclaw-idp** | 8 IDP checks (Google Workspace + Okta) | [auditclaw-idp](https://github.com/avansaber/auditclaw-idp) |

## Installation

1. Copy this skill to your OpenClaw skills folder:
   ```bash
   cp -r . ~/clawd/skills/auditclaw-grc/
   ```

2. Install Python dependencies:
   ```bash
   pip install -r scripts/requirements.txt
   ```

3. Initialise the database:
   ```bash
   python3 scripts/init_db.py
   ```

4. Start a conversation with your OpenClaw agent and say:
   ```
   Activate SOC 2
   ```

## Testing

```bash
pip install -r requirements-dev.txt
python3 -m pytest tests/ -v
```

431 tests covering all 97 actions, edge cases, error handling, pagination, and cross-table relationships.

## Project Structure

```
auditclaw-grc/
├── scripts/           # Core Python scripts
│   ├── db_query.py    # 97-action database interface
│   ├── init_db.py     # Database initialisation + migrations
│   ├── compliance_score.py
│   ├── drift_detector.py
│   ├── generate_dashboard.py
│   ├── generate_trust_center.py
│   ├── credential_store.py
│   └── auth_provider.py
├── assets/            # Framework JSON files + policy templates
├── references/        # Documentation for actions, schema, integrations
├── skills/            # Mini-skills (browser checks, reports, etc.)
├── tests/             # 431 unit tests
├── SKILL.md           # OpenClaw skill instructions
└── LICENSE            # MIT
```

## Authentication

AuditClaw uses modern, secure authentication for all cloud integrations:

- **AWS**: IAM Roles with AssumeRole (no static access keys)
- **GitHub**: GitHub App tokens (no personal access tokens)
- **Azure**: Certificate-based service principals (no client secrets)
- **GCP**: Service account impersonation (no key files)
- **IDP**: OAuth 2.0 / domain-wide delegation

## Website

[auditclaw.ai](https://auditclaw.ai)

## License

[MIT](LICENSE) - Copyright (c) 2026 AvanSaber Inc., Nikhil Jathar
