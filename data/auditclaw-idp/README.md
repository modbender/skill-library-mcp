# auditclaw-idp

Identity provider compliance checks for [AuditClaw GRC](https://github.com/avansaber/auditclaw-grc). Covers **Google Workspace** and **Okta** in a single skill.

## Quick Start

```bash
pip install -r scripts/requirements.txt

# Google Workspace
export GOOGLE_WORKSPACE_SA_KEY=/path/to/sa-key.json
export GOOGLE_WORKSPACE_ADMIN_EMAIL=admin@yourcompany.example

# Okta
export OKTA_ORG_URL=https://mycompany.okta.com
export OKTA_API_TOKEN=00abc...

# Run all checks for configured providers
python3 scripts/idp_evidence.py --db-path ~/.openclaw/grc/compliance.sqlite --all
```

## Checks

| # | Check | Provider | Description |
|---|-------|----------|-------------|
| 1 | google_mfa | Google Workspace | MFA enrollment and enforcement for all active users |
| 2 | google_admins | Google Workspace | Super admin count (2-4) and MFA status |
| 3 | google_inactive | Google Workspace | Users inactive > 90 days |
| 4 | google_passwords | Google Workspace | Password strength audit |
| 5 | okta_mfa | Okta | MFA factor enrollment for all active users |
| 6 | okta_passwords | Okta | Password policy compliance (length, history, lockout, age) |
| 7 | okta_inactive | Okta | Users inactive > 90 days |
| 8 | okta_sessions | Okta | Session policy (MFA requirement, lifetime, idle timeout) |

## Testing

```bash
python3 -m pytest tests/ -v
```

All tests use `unittest.mock`; no real API credentials needed.

## License

MIT. See [LICENSE](LICENSE).
