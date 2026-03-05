---
name: security-scanner
description: Run a comprehensive local security scan on your OpenClaw installation. Checks config, network exposure, credentials, OS hardening, and agent guardrails. Scores your setup and offers auto-fixes. Everything stays local — no data leaves your machine.
---

# Security Scanner

Run a local security assessment on any OpenClaw installation.

## Usage

The skill provides a bash script that scans your OpenClaw setup and reports findings with severity levels.

### Quick scan (read-only)

```bash
bash "$(dirname "$0")/oc-security-scan.sh"
```

### Auto-fix issues

```bash
bash "$(dirname "$0")/oc-security-scan.sh" --fix
```

### Save a report

```bash
bash "$(dirname "$0")/oc-security-scan.sh" --report
```

### JSON output

```bash
bash "$(dirname "$0")/oc-security-scan.sh" --json
```

## What It Checks

- **OpenClaw Configuration** — bind address, token strength, config permissions, exec security mode
- **Network Exposure** — listening ports, firewall status, public interface exposure
- **Credential Hygiene** — plaintext secrets, file permissions, .gitignore patterns
- **OS Hardening** — disk encryption, auto-updates, OS version, root usage
- **Agent Guardrails** — RULES.md, memory file permissions, safety constraints

## Output

Color-coded terminal output with severity levels:
- 🔴 CRITICAL — immediate action required
- 🟡 WARNING — should be addressed
- 🟢 PASS — looks good
- ⚪ INFO — informational

Ends with a security score out of 100 (A-F grade).

## Security Philosophy

- **Local only** — zero external network calls, nothing phones home
- **Read-only by default** — only modifies files when `--fix` is explicitly passed
- **Owner-operated** — designed to be run by the OpenClaw owner on their own machine
- **No dependencies** — standard unix tools + openclaw CLI only
