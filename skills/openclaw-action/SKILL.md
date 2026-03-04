---
name: openclaw-action
description: "GitHub Action for automated security scanning of agent workspaces. Detects exposed secrets, prompt/shell injection, and data exfiltration patterns in PRs and commits."
user-invocable: false
metadata: {"openclaw":{"emoji":"🛡️","requires":{"bins":["python3"]},"os":["darwin","linux","win32"]}}
---

# OpenClaw Security Action

GitHub Action that scans agent skills for security issues on every PR.

## What It Scans

| Scanner | What It Catches |
|---------|-----------------|
| **sentry** | API keys, tokens, passwords, credentials in code |
| **bastion** | Prompt injection markers, shell injection patterns |
| **egress** | Suspicious network calls, data exfiltration patterns |

## Quick Start

Add to `.github/workflows/security.yml`:

```yaml
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
        with:
          workspace: '.'
          fail-on-findings: 'true'
```

## Inputs

| Input | Default | Description |
|-------|---------|-------------|
| `workspace` | `.` | Path to scan |
| `fail-on-findings` | `true` | Fail the check if issues found |
| `scan-secrets` | `true` | Enable secret scanning |
| `scan-injection` | `true` | Enable injection scanning |
| `scan-egress` | `true` | Enable egress scanning |

## Outputs

| Output | Description |
|--------|-------------|
| `findings-count` | Total number of issues found |
| `has-critical` | `true` if critical/high severity issues |

## Philosophy

This action **detects and alerts only**. It will:
- Flag security issues in PR checks
- Annotate specific lines with findings
- Generate a summary report

It will NOT:
- Automatically modify your code
- Quarantine or delete files
- Make any changes to your repository

For automated remediation, see [OpenClaw Pro](https://github.com/sponsors/AtlasPA).

## Requirements

- Python 3.8+ (auto-installed by action)
- No external dependencies
