# @elvatis_com/clawhub-scanner

Scan your installed [ClawHub](https://clawhub.com) skills for malware, credential theft, prompt injection, and security risks.

## Why?

ClawHub skills run with full agent permissions. In February 2026 alone, security researchers found:
- **534 skills** with critical vulnerabilities (Snyk)
- **341 skills** distributing the AMOS stealer ("ClawHavoc" campaign)
- **76 confirmed** malicious payloads for credential theft and data exfiltration

This scanner checks your installed skills against known malicious patterns, C2 infrastructure, and suspicious behaviors.

## Install

```bash
npm install -g @elvatis_com/clawhub-scanner
```

## Usage

```bash
# Scan all installed skills
clawhub-scanner scan

# Scan a specific skill
clawhub-scanner scan --skill ~/.openclaw/skills/some-skill

# JSON output for automation
clawhub-scanner scan --json

# Include low-severity findings
clawhub-scanner scan --verbose

# Show scanned directories
clawhub-scanner paths
```

## What It Detects

| Category | Severity | Examples |
|----------|----------|---------|
| **C2 Infrastructure** | Critical | Known malicious IPs (91.92.242.30), ClawHavoc domains |
| **Code Execution** | High | `eval()`, `child_process.exec()`, `process.binding()` |
| **Credential Theft** | High | SSH key access, AWS creds, browser profiles, crypto wallets |
| **Data Exfiltration** | High | Discord/Telegram webhooks, raw IP fetches, DNS tunneling |
| **Obfuscation** | High/Med | Base64+exec combos, large encoded strings, CharCode assembly |
| **Prompt Injection** | Medium | "Ignore previous instructions", system prompt overrides |
| **Network Activity** | Low | Outbound HTTP to unknown domains, WebSocket connections |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Clean (or only low/medium findings) |
| 1 | High-severity findings detected |
| 2 | Critical findings detected |

Use in CI/scripts: `clawhub-scanner scan --quiet || echo "Security issues found!"`

## Scan Locations

By default, scans:
- `~/.openclaw/skills/` (user-installed skills)
- OpenClaw built-in skills directory

## License

MIT - [Elvatis](https://elvatis.com)
