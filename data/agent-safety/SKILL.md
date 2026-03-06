---
name: agent-safety
description: Outbound safety for autonomous AI agents — scans YOUR output before it leaves the machine. Git pre-commit hooks that automatically block commits containing API keys, tokens, PII, or secrets. Unlike inbound scanners (Skillvet, IronClaw), this protects against what YOU accidentally publish. Use when committing to git repos, publishing to GitHub, or running periodic system health checks. Automated enforcement at the git level — not prompts.
---

# Agent Safety

Automated safety tools for autonomous AI agents. The principle: **don't rely on prompts for safety — automate enforcement.**

All scripts are in this skill's `scripts/` directory. When OpenClaw loads this skill, resolve paths relative to this file's location.

## Pre-Publish Security Scan

Scans files for secrets, PII, and internal paths before publishing.

```bash
bash scripts/pre-publish-scan.sh <file-or-directory>
```

**Detects:**
- API keys (AWS, GitHub, Anthropic, OpenAI, generic patterns)
- Private keys (PEM blocks), Bearer tokens, hardcoded passwords
- Email addresses, phone numbers, SSNs, credit card patterns
- Physical addresses, name fields
- Home directory paths, internal config paths

**Exit 0** = clean. **Exit 1** = blocking issues found, do not publish.

## Git Pre-Commit Hook

Install once per repo. Automatically scans staged files on every commit:

```bash
bash scripts/install-hook.sh <repo-path>
```

- Scans staged content (what's being committed, not working tree)
- Blocks commit if secrets or SSNs found
- Flags PII for review
- Only bypassed with explicit `git commit --no-verify`

**Install this on every repo you work with.** It's the real guardrail.

## Health Check

System monitoring for disk, workspace, security, and updates:

```bash
bash scripts/health-check.sh
```

**Checks:** Disk usage, workspace size, memory file growth, OpenClaw version, macOS updates, firewall status, SIP status.

Run periodically (every few heartbeats). Watch for warnings.

## Rules

1. Run pre-publish scan before ANY external publish action
2. Install pre-commit hook on EVERY repo you work with
3. Blocking issues (secrets, SSNs) must be fixed — no override
4. Review items (emails, paths) need human judgment
5. If a secret was ever committed, it's compromised — rotate immediately
