---
name: sentinel-shield
description: Runtime security for OpenClaw agents. Monitors tool calls, enforces rate limits, scans for prompt injection, and alerts on suspicious behavior. Protect your gateway token and agent session from infostealers and session hijacking.
homepage: https://sentinel-algo.com/shield
triggers:
  - sentinel status
  - check security
  - security audit
  - recent alerts
  - sentinel shield
  - run security check
  - check for threats
  - agent security
metadata:
  emoji: "🛡️"
  category: security
  tags:
    - security
    - monitoring
    - rate-limiting
    - injection-detection
    - audit-logging
---

# Sentinel Shield — Runtime Security for OpenClaw Agents

*Everyone else secures the model. We secure the agent.*

Sentinel Shield is a lightweight security layer for OpenClaw agents. It monitors what your agent **does** — not just what it says — and alerts you before damage is done.

## What It Protects Against

- **Stolen gateway tokens** — Rate limiting + anomaly detection catches unauthorized sessions
- **Prompt injection** — Scans inbound content for 16+ injection pattern signatures  
- **Session hijacking** — Behavioral fingerprinting flags sessions that don't match your patterns
- **Runaway agents** — 50-call/60s sliding window kills runaway loops automatically
- **Silent exfiltration** — File integrity monitoring on critical OpenClaw files

## Quick Commands

### Status Check
```bash
node {baseDir}/scripts/sentinel.js status
```
Returns current health, active session stats, and recent alert summary.

### Security Audit
```bash
node {baseDir}/scripts/sentinel.js audit
```
Full audit: file integrity, rate limit state, injection scanner status, anomaly log.

### Recent Alerts
```bash
node {baseDir}/scripts/sentinel.js alerts [--hours 24]
```
Shows alerts from the last N hours (default: 24).

### Rate Limit Status
```bash
node {baseDir}/scripts/sentinel.js ratelimit
```
Shows current call counts per window for all monitored tools.

### Kill Switch
```bash
node {baseDir}/scripts/sentinel.js kill
```
Emergency stop. Terminates active rate counters, logs kill event, sends Telegram alert.

### Run Injection Scan
```bash
node {baseDir}/scripts/sentinel.js scan --text "some content to check"
```
Manually scan text for injection signatures.

### Initialize / Reset Baselines
```bash
node {baseDir}/scripts/sentinel.js init
```
Establishes file integrity baselines for critical OpenClaw files.

## Configuration

Edit `{baseDir}/config/shield.json` to customize:

```json
{
  "rateLimit": {
    "maxCalls": 50,
    "windowSeconds": 60,
    "alertThreshold": 40
  },
  "telegram": {
    "enabled": true,
    "botToken": "YOUR_BOT_TOKEN",
    "chatId": "YOUR_CHAT_ID"
  },
  "monitoredFiles": [
    "~/.openclaw/openclaw.json",
    "~/.openclaw/credentials",
    "~/.ssh/authorized_keys",
    "/etc/passwd"
  ],
  "injectionScanning": true,
  "alertLevel": "medium"
}
```

## Setup (Telegram Alerts)

1. Create a Telegram bot via @BotFather → copy the token
2. Message your bot to get your chat ID: `https://api.telegram.org/bot<TOKEN>/getUpdates`
3. Add both to `{baseDir}/config/shield.json`

## How to Use in Agent Sessions

When you see a suspicious message or want to verify your session is clean:

**User:** "Run a security check"
**Action:** Run `node {baseDir}/scripts/sentinel.js status`

**User:** "Show me recent security alerts"  
**Action:** Run `node {baseDir}/scripts/sentinel.js alerts`

**User:** "Scan this text for injection: [text]"
**Action:** Run `node {baseDir}/scripts/sentinel.js scan --text "[text]"`

**User:** "Emergency stop sentinel"
**Action:** Run `node {baseDir}/scripts/sentinel.js kill`

## Alert Levels

| Level | Trigger | Action |
|-------|---------|--------|
| INFO | Normal activity logged | Write to log only |
| MEDIUM | Rate limit >80% | Log + Telegram |
| HIGH | Rate limit hit, injection detected | Log + Telegram + kill option |
| CRITICAL | File integrity violation | Log + Telegram + alert all channels |

## Files Monitored (Default)

- `~/.openclaw/openclaw.json` — Gateway auth token (THE critical file)
- `~/.openclaw/credentials` — Stored credentials
- `~/.ssh/authorized_keys` — SSH access control
- `/etc/passwd` — System user accounts
- `/etc/sudoers` — Privilege escalation paths

## Version History

- **v0.2.0** — Rate limiting (50/60s sliding window), Telegram alerts, clawhub distribution
- **v0.1.0** — File integrity monitoring, process scanning, injection detection (16 patterns)
