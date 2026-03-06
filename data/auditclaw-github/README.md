# auditclaw-github

Companion skill for [AuditClaw GRC](https://github.com/avansaber/auditclaw-grc) that runs automated GitHub security checks and stores evidence in the shared compliance database.

## Checks (9)

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

## Requirements

- Python 3.10+
- `PyGithub>=2.1.0`
- GitHub personal access token with `repo`, `read:org`, `security_events` scopes
- [auditclaw-grc](https://github.com/avansaber/auditclaw-grc) skill installed and initialized

## Quick Start

```bash
pip install -r scripts/requirements.txt
export GITHUB_TOKEN="your-token-here"

# Test connectivity
python3 scripts/github_evidence.py --test-connection

# Run all checks
python3 scripts/github_evidence.py \
  --db-path ~/.openclaw/grc/compliance.sqlite \
  --org your-org \
  --all

# Run specific checks
python3 scripts/github_evidence.py \
  --db-path ~/.openclaw/grc/compliance.sqlite \
  --org your-org \
  --checks branch_protection,secret_scanning
```

## Tests

```bash
pip install pytest
python3 -m pytest tests/ -v
```

## License

MIT License. See [LICENSE](LICENSE) for details.
