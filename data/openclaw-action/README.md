# OpenClaw Security Action

GitHub Action for automated security scanning of agent workspaces. Catches secrets, injection attacks, and exfiltration patterns before they land in your repo.

## Why This Exists

Agent skill marketplaces have a supply chain security problem. Since January 2026, 341+ malicious skills have been identified on ClawHub and similar registries — trojanized utilities with reverse shells, credential stealers, and silent data exfiltration.

This action brings the [OpenClaw Security Suite](https://github.com/AtlasPA/openclaw-security) into your CI pipeline, scanning skills before they can cause damage.

## Quick Start

```yaml
# .github/workflows/security.yml
name: Security Scan
on:
  pull_request:
    paths:
      - 'skills/**'
      - '.openclaw/**'
  push:
    branches: [main]

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: AtlasPA/openclaw-action@v1
```

That's it. PRs touching your skills directory will now be scanned.

## What It Catches

### Secret Exposure (sentry)
- API keys (AWS, GCP, GitHub, Stripe, OpenAI, etc.)
- Hardcoded passwords and tokens
- Private keys and certificates
- High-entropy strings that look like credentials

### Injection Attacks (bastion)
- Prompt injection markers (`[SYSTEM]`, `<|im_start|>`)
- Shell injection patterns (`eval()`, `exec()`, `subprocess` with `shell=True`)
- Unicode homoglyphs and directional overrides
- Hidden instructions in HTML comments

### Data Exfiltration (egress)
- Suspicious `requests.post()` and `urllib` calls
- Hardcoded IP addresses and short-lived domains
- Credential-to-network data flows
- DNS exfiltration patterns

## Configuration

### Inputs

| Input | Default | Description |
|-------|---------|-------------|
| `workspace` | `.` | Path to scan (repository root by default) |
| `fail-on-findings` | `true` | Fail the check if any security issues are found |
| `scan-secrets` | `true` | Run secret/credential scanning |
| `scan-injection` | `true` | Run prompt/shell injection scanning |
| `scan-egress` | `true` | Run data exfiltration scanning |

### Outputs

| Output | Description |
|--------|-------------|
| `findings-count` | Total number of security findings |
| `has-critical` | `true` if critical/high severity issues were found |

### Example: Custom Configuration

```yaml
- uses: AtlasPA/openclaw-action@v1
  with:
    workspace: './agent-skills'
    fail-on-findings: 'true'
    scan-secrets: 'true'
    scan-injection: 'true'
    scan-egress: 'false'  # Skip egress scanning
```

### Example: Weekly Full Scan

```yaml
name: Weekly Security Audit
on:
  schedule:
    - cron: '0 9 * * 1'  # Every Monday at 9am

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: AtlasPA/openclaw-action@v1
        id: scan
      - name: Create issue on findings
        if: steps.scan.outputs.has-critical == 'true'
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: 'Security scan found critical issues',
              body: 'The weekly security scan found critical issues. Check the workflow run for details.',
              labels: ['security']
            })
```

## Trust Model

This action is designed to be auditable:

- **No binaries** — All logic is plain-text Python, readable in [scripts/scan.py](scripts/scan.py)
- **No dependencies** — Python stdlib only. No `pip install`, no supply chain risk
- **No network calls** — Scanners run locally. Nothing phones home
- **No persistence** — Downloads fresh scanner scripts each run, doesn't cache or store anything

The scanner scripts are fetched directly from the individual tool repositories:
- [openclaw-sentry](https://github.com/AtlasPA/openclaw-sentry)
- [openclaw-bastion](https://github.com/AtlasPA/openclaw-bastion)
- [openclaw-egress](https://github.com/AtlasPA/openclaw-egress)

## Philosophy

**This action detects and alerts only.**

It will:
- Flag security issues as PR check failures
- Annotate specific lines in the PR diff
- Generate a summary report in the job summary

It will NOT:
- Modify, quarantine, or delete any files
- Make commits or push changes
- Take any automated remediation action

For automated countermeasures (quarantine malicious skills, redact exposed secrets, block suspicious network patterns), see the [Pro tools via GitHub Sponsors](https://github.com/sponsors/AtlasPA).

## Related Tools

- [openclaw-security](https://github.com/AtlasPA/openclaw-security) — Meta-installer for the full 11-tool suite
- [openclaw-warden](https://github.com/AtlasPA/openclaw-warden) — File integrity monitoring
- [openclaw-sentinel](https://github.com/AtlasPA/openclaw-sentinel) — Pre-install supply chain scanning

## License

MIT
