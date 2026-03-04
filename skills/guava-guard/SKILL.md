---
name: guava-guard
description: Runtime security guard for OpenClaw agents. Warns on dangerous tool call patterns. For full static scanning, use guard-scanner.
metadata:
  clawdbot:
    emoji: "🛡️"
---

# GuavaGuard 🛡️

**Runtime security monitoring for your OpenClaw agent.**

GuavaGuard watches tool calls in real-time and warns when it detects dangerous patterns — reverse shells, credential exfiltration, sandbox escapes, and more.

## Quick Start

```bash
# 1. Install
clawhub install guava-guard

# 2. Enable the runtime hook
openclaw hooks install skills/guava-guard/hooks/guava-guard
openclaw hooks enable guava-guard

# 3. Restart gateway, then verify:
openclaw hooks list   # Should show 🍈 guava-guard as ✓ ready
```

That's it. GuavaGuard is now monitoring your agent's tool calls.

## What It Detects (12 runtime patterns)

| Pattern | Severity | Example |
|---------|----------|---------|
| Reverse shell | 🔴 CRITICAL | `/dev/tcp/`, `nc -e`, `socat TCP` |
| Credential exfiltration | 🔴 CRITICAL | Secrets → webhook.site, ngrok, requestbin |
| Guardrail disabling | 🔴 CRITICAL | `exec.approval = off` (CVE-2026-25253) |
| macOS Gatekeeper bypass | 🔴 CRITICAL | `xattr -d quarantine` |
| ClawHavoc AMOS | 🔴 CRITICAL | `socifiapp`, Atomic Stealer indicators |
| Base64 → shell | 🔴 CRITICAL | `base64 -d \| bash` |
| Download → shell | 🔴 CRITICAL | `curl \| bash`, `wget \| sh` |
| Cloud metadata SSRF | 🔴 CRITICAL | `169.254.169.254` |
| Known malicious IP | 🔴 CRITICAL | `91.92.242.30` |
| DNS exfiltration | 🟠 HIGH | `nslookup $secret`, `dig @attacker` |
| SSH key access | 🟠 HIGH | `.ssh/id_*`, `.ssh/authorized_keys` |
| Crypto wallet access | 🟠 HIGH | `wallet seed`, `mnemonic`, `seed phrase` |

## Current Limitation

> **Warning**: OpenClaw's hook API does not yet support blocking tool execution.
> GuavaGuard currently **warns only** — it cannot prevent dangerous calls.
> When a cancel API is added, blocking will be enabled automatically.
> See: [Issue #18677](https://github.com/openclaw/openclaw/issues/18677)

## Audit Log

All detections are logged to `~/.openclaw/guava-guard/audit.jsonl` (JSON lines format).

## Want Full Static Scanning? (Recommended Default)

GuavaGuard handles **runtime** monitoring. For comprehensive **static** scanning of skill packages before installation, use **guard-scanner** first:

```bash
# 1) Pre-install safety gate
npx guard-scanner ./skills --self-exclude --verbose

# 2) Then enable runtime monitoring
openclaw hooks enable guava-guard
```

- 186+ detection patterns / 20 threat categories
- HTML dashboard, SARIF, JSON output
- Zero dependencies
- MIT licensed

**GitHub**: https://github.com/koatora20/guard-scanner
**ClawHub**: `clawhub install guard-scanner`

## Born From a Real Incident

A real agent compromise overwrote core behavior files through a malicious skill install path.
GuavaGuard exists to detect dangerous runtime tool-call patterns early and leave an auditable trail.

## License

MIT. Zero dependencies. 🍈
