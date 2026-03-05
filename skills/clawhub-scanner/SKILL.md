---
name: clawhub-scanner
description: "Scan installed ClawHub skills for malware, credential theft, prompt injection, and security risks. Detects known C2 infrastructure, obfuscated payloads, and data exfiltration patterns from the ClawHavoc campaign."
---

# clawhub-scanner

Security scanner for ClawHub skills. Checks installed skills against known malicious patterns, IoCs, and suspicious behaviors.

## Usage

When the user asks to scan skills, check for malware, or audit their ClawHub installations:

```bash
# Scan all installed skills
clawhub-scanner scan

# Scan a specific skill
clawhub-scanner scan --skill ~/.openclaw/skills/some-skill

# JSON output for automation
clawhub-scanner scan --json

# Include low-severity findings
clawhub-scanner scan --verbose
```

## What It Detects

- **Critical:** Known C2 server IPs and malicious domains (ClawHavoc campaign)
- **High:** eval(), credential harvesting (SSH/AWS/browser/wallets), data exfiltration (Discord/Telegram webhooks), obfuscated payloads
- **Medium:** Prompt injection, broad filesystem access, clipboard harvesting
- **Low:** Outbound HTTP, WebSocket connections

## Install

Requires the npm package:

```bash
npm install -g @elvatis_com/clawhub-scanner
```

## Exit Codes

- 0 = clean
- 1 = high-severity findings
- 2 = critical findings
