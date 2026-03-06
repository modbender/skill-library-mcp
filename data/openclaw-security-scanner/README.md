# OpenClaw Security Scanner

A comprehensive, local-only security assessment tool for OpenClaw installations.

## Philosophy

- **🔒 Local-only** — Zero network calls. No data leaves your machine. No telemetry, no phoning home.
- **👀 Read-only by default** — Only observes and reports. Changes require explicit `--fix` flag.
- **👤 Owner-only** — Designed to be run by the OpenClaw owner on their own machine.

## Quick Start

```bash
# Make executable
chmod +x oc-security-scan.sh

# Run scan
./oc-security-scan.sh

# Run with auto-fix (prompts before each change)
./oc-security-scan.sh --fix

# Save report to file
./oc-security-scan.sh --report

# Machine-readable output
./oc-security-scan.sh --json

# Combine flags
./oc-security-scan.sh --fix --report --json
```

## What It Checks

| Category | Checks | Severity Range |
|---|---|---|
| **OpenClaw Configuration** | Gateway bind address, token strength, config permissions, exec security mode, browser exposure, tool permissions | CRITICAL–INFO |
| **Network Exposure** | Public-facing ports, firewall status, SSH config, WAN exposure | CRITICAL–INFO |
| **Credential Hygiene** | Plaintext API keys, secrets file permissions, .gitignore coverage, sensitive data in memory files | CRITICAL–WARNING |
| **OS Hardening** | Disk encryption, auto-updates, OS currency, admin usage | HIGH–INFO |
| **Agent Guardrails** | RULES.md existence, memory permissions, external message controls, elevated exec | HIGH–INFO |

## Output

```
🔴 CRITICAL  — Immediate action required. Active exploit risk.
🟡 WARNING   — Should be fixed. Reduces attack surface.
🟢 PASS      — Check passed. No action needed.
⚪ INFO      — Informational. Context for the operator.
```

A summary score (0–100) is printed at the end.

## Auto-Fix

With `--fix`, the scanner offers to remediate safe, reversible issues:

- Tightening file permissions (config, secrets, memory)
- Creating missing `.gitignore` entries
- Suggesting (not applying) config changes for critical settings

Every fix prompts for confirmation. Nothing is changed silently.

## Requirements

- macOS or Linux
- Standard unix tools (`stat`, `lsof`, `grep`, `awk`, etc.)
- OpenClaw CLI (optional — scanner works without it but skips some checks)
- No root required (notes when root would enable deeper checks)

## Security

This script itself contains no secrets, makes no network connections, and writes nothing to disk unless `--report` is specified (writes to the current directory). It is safe to commit to version control.
