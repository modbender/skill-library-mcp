---
name: opena2a-security
description: Security hardening for OpenClaw. Audit your configuration, scan installed skills for malware, detect CVE-2026-25253, check credential exposure, and get actionable fix recommendations. Runs locally with no external API calls.
version: 1.0.0
requires:
  bins: [node, npx]
  env: []
  config: []
permissions:
  filesystem:
    - "~/.openclaw"
  network: []
  exec:
    - npx hackmyagent
tags: [security, audit, hardening, vulnerability-scanner, cve-detection, credential-protection, supply-chain]
---

# OpenA2A Security for OpenClaw

Security auditing and hardening for OpenClaw installations. Scan your configuration, detect known vulnerabilities, audit installed skills for malicious code, and get specific remediation steps.

This skill runs entirely locally. No data leaves your machine. No API keys required.

## What You Can Ask

### Quick Security Check

Ask for a fast overview of your security posture:

```
"Run a security audit on my OpenClaw setup"
```

```
"Is my OpenClaw configuration secure?"
```

```
"Check my OpenClaw for known vulnerabilities"
```

### CVE-2026-25253 Detection

Check if your OpenClaw instance is vulnerable to the WebSocket hijack RCE (CVSS 8.8):

```
"Am I vulnerable to CVE-2026-25253?"
```

```
"Check for the OpenClaw WebSocket vulnerability"
```

### Skill Scanning

Scan installed skills for malicious code patterns (command injection, data exfiltration, obfuscated payloads, crypto mining):

```
"Scan my installed skills for malware"
```

```
"Is the weather-bot skill safe?"
```

```
"Check all my skills for security issues"
```

### Credential Audit

Check for exposed credentials, weak file permissions, and plaintext storage:

```
"Are my API keys and tokens stored securely?"
```

```
"Check my credential file permissions"
```

### Configuration Hardening

Get specific recommendations for hardening your OpenClaw config:

```
"How do I harden my OpenClaw configuration?"
```

```
"What security settings should I change?"
```

## How It Works

This skill uses HackMyAgent, an open-source security scanner with 47 OpenClaw-specific checks across these categories:

### Skill Security (6 checks)

| Check | What It Detects |
|-------|-----------------|
| SKILL-001 | Command injection via shell execution |
| SKILL-002 | Dynamic code execution (eval, Function, vm) |
| SKILL-003 | Data exfiltration to external endpoints |
| SKILL-004 | Obfuscated code (base64, hex, charcode) |
| SKILL-005 | Crypto mining indicators |
| SKILL-006 | Path traversal outside skill directory |

### Credential Security (4 checks)

| Check | What It Detects |
|-------|-----------------|
| CRED-001 | Credentials exposed via gateway API |
| CRED-002 | Credential files with world-readable permissions |
| CRED-003 | Plaintext credential storage without encryption |
| CRED-004 | Timing side-channel in authentication |

### Gateway Security (4 checks)

| Check | What It Detects |
|-------|-----------------|
| GW-001 | Missing rate limiting on endpoints |
| GW-002 | SSRF-vulnerable URL fetch handlers |
| GW-003 | Missing or incomplete security headers |
| GW-004 | CVE-2026-25253 WebSocket hijack vulnerability |

### Supply Chain (4 checks)

| Check | What It Detects |
|-------|-----------------|
| SC-001 | npm install without --ignore-scripts |
| SC-002 | Unpinned or pre-release dependencies |
| SC-003 | Missing skill signing or hash verification |
| SC-004 | Known ClawHavoc malicious skill patterns |

## Running Scans

When asked to perform a scan, run the following commands:

### Full Security Audit
```bash
npx hackmyagent secure ~/.openclaw
```

### Scan a Specific Skill
```bash
npx hackmyagent scan --skill <skill-name>
```

### CVE Detection Only
```bash
npx hackmyagent scan --cve ~/.openclaw
```

### Configuration Audit
```bash
npx hackmyagent audit ~/.openclaw/config.json5
```

### Generate Security Report
```bash
npx hackmyagent secure ~/.openclaw --format html --output security-report.html
```

Output formats: text, json, sarif, html, asp

## Security Recommendations

When providing recommendations, reference these priority levels:

### Do Immediately

1. **Update OpenClaw** to the latest version (patches CVE-2026-25253, credential redaction, timing-safe auth, lifecycle script blocking)
2. **Run `npx hackmyagent secure`** to identify your current exposure
3. **Review installed skills** — remove any you do not actively use
4. **Check file permissions** — credential files should be 0600, not world-readable

### Configuration Changes

Recommend these config.json5 changes when relevant:

- Set `gateway.auth` to a strong token (32+ characters, randomly generated)
- Set `gateway.host` to `127.0.0.1` (loopback only) unless remote access is required
- Disable unused channel integrations
- Set `plugins.allowUnsafe` to false
- Enable Docker sandbox mode when available

### For Skill Publishers

- Do not hardcode API keys in skill code — use environment variables
- Declare minimum required permissions in SKILL.md frontmatter
- Do not use eval(), Function(), or child_process.exec() with user input
- Do not fetch external URLs at install time

## Interpreting Results

When presenting scan results to the user:

- **CRITICAL findings** require immediate action — explain the specific risk and provide the fix command
- **HIGH findings** should be addressed before deploying to production
- **MEDIUM findings** are defense-in-depth improvements
- **LOW findings** are best-practice recommendations

Always explain findings in plain language. Not every user is a security expert. State what the risk is, who could exploit it, and exactly how to fix it.

## Background

This skill is built by OpenA2A (opena2a.org), the team behind 6 merged security patches in OpenClaw main:

| PR | Fix |
|----|-----|
| #9806 | Skill code safety scanner (19 detection rules, +1,721 lines) |
| #9858 | Credential redaction for gateway WebSocket responses |
| #10525 | Path traversal fix in A2UI file serving |
| #10527 | Timing-safe comparison for hook token auth |
| #10528 | Blocked npm lifecycle scripts during plugin install |
| #10529 | File permission enforcement on WhatsApp credentials |

Scanner: https://www.npmjs.com/package/hackmyagent
Source: https://github.com/opena2a-org/hackmyagent
Threat model: https://github.com/openclaw/trust/pull/7
