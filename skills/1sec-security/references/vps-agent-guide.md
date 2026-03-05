# VPS Agent Deployment Guide

Detailed guide for deploying 1-SEC on a VPS hosting an autonomous AI agent
(OpenClaw, Manus, Moltbot, or similar).

## Threat Model

AI agent VPS instances face a specific threat profile:

- **Exposed gateway port** — the agent's API/chat endpoint is internet-facing
- **Prompt injection** — #1 attack vector via chat channels, emails, PDFs, browsed pages
- **Malicious skill/plugin installs** — supply chain attacks via SKILL.md files
- **Credential exfiltration** — stealing API keys, tokens, .env files
- **Agent scope escalation** — agent spawning sub-agents with inherited permissions
- **Runtime file tampering** — SOUL.md, MEMORY.md, .env modification
- **C2 beaconing** — compromised agent phoning home to attacker infrastructure

## Recommended Setup

```bash
# 1. Install (download from GitHub Releases with checksum verification)
VERSION="0.4.11"
wget https://github.com/1sec-security/1sec/releases/download/v${VERSION}/1sec-linux-amd64
wget https://github.com/1sec-security/1sec/releases/download/v${VERSION}/checksums.txt
sha256sum -c checksums.txt 2>&1 | grep 1sec-linux-amd64
chmod +x 1sec-linux-amd64
sudo mv 1sec-linux-amd64 /usr/local/bin/1sec

# 2. Setup (non-interactive for agent deployments)
1sec setup --non-interactive

# 3. Apply vps-agent preset in dry-run first
1sec enforce preset vps-agent --dry-run

# 4. Start engine
1sec up

# 5. Monitor for a few hours, review alerts
1sec alerts --severity HIGH
1sec enforce history

# 6. When satisfied, go live
1sec enforce dry-run off
```

## What the VPS-Agent Preset Does

### Critical modules (aggressive enforcement)

- **Auth Fortress** — blocks gateway auth attacks at MEDIUM, disables compromised
  accounts at HIGH. 30s cooldown, 60 actions/min. Escalation enabled with 3min
  timeout on CRITICAL (auto-escalates unacknowledged alerts).
- **LLM Firewall** — drops prompt injection connections at MEDIUM, blocks
  persistent attackers at HIGH. 10s cooldown, 100 actions/min.
- **AI Agent Containment** — kills processes violating containment at MEDIUM
  (`skip_approval: true`), blocks shadow AI endpoints at HIGH. 15s cooldown.
- **Runtime Watcher** — kills tampering processes (`skip_approval: true`),
  quarantines modified agent files (SOUL.md, MEMORY.md, .env) immediately.
- **Supply Chain Sentinel** — quarantines suspicious skills/plugins at MEDIUM
  (`skip_approval: true`), kills malicious skill processes at HIGH, blocks C2
  IPs for 24h.

### High priority modules

- **Network Guardian** — blocks scans and C2 beaconing, drops exfiltration.
- **API Fortress** — blocks API abuse on the agent gateway.
- **Injection Shield** — drops command injection attempts via agent tool execution.
- **Identity Monitor** — disables escalated or synthetic identities.

### Medium priority (still enabled, higher thresholds)

- Ransomware — kills processes and quarantines files at HIGH (`skip_approval: true`).
- Data Poisoning — quarantines poisoned memory files at MEDIUM (`skip_approval: true`).

### Lower priority (log + notify only)

- IoT Shield, Deepfake Shield, Quantum Crypto, Cloud Posture — these are less
  relevant for a single-VPS agent but still monitored.

## Escalation Timers

The vps-agent preset enables escalation with aggressive timeouts because
autonomous agent hosts typically have no human SOC team watching:

| Severity | Timeout | Escalates To | Re-notify | Max |
|----------|---------|-------------|-----------|-----|
| CRITICAL | 3 min   | CRITICAL    | Yes       | 5   |
| HIGH     | 10 min  | CRITICAL    | Yes       | 3   |
| MEDIUM   | 20 min  | HIGH        | Yes       | 2   |

## Approval Gates

Disabled by default for the vps-agent preset. Autonomous agent hosts can't
wait for human approval. Critical actions (kill_process, quarantine_file) on
the most important modules have `skip_approval: true`.

If you want approval gates for non-critical actions, enable them:

```yaml
enforcement:
  approval_gate:
    enabled: true
    require_approval: ["disable_user"]
    auto_approve_above: "CRITICAL"
    ttl: 5m
```

## Webhook Notifications

Configure at least one notification channel so the agent operator gets alerted.
1-SEC supports native templates for all major platforms:

```yaml
alerts:
  webhook_urls:
    - "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

Supported templates: `pagerduty`, `slack`, `teams`, `discord`, `telegram`, `generic`.

### Telegram example

```yaml
# In enforcement policy webhook actions:
params:
  url: "https://api.telegram.org/botYOUR_BOT_TOKEN/sendMessage"
  template: "telegram"
  chat_id: "-1001234567890"
```

### Discord example

```yaml
params:
  url: "https://discord.com/api/webhooks/YOUR/WEBHOOK"
  template: "discord"
```

### Slack example

```yaml
params:
  url: "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
  template: "slack"
```

## Monitoring Commands

```bash
1sec status                    # Engine overview
1sec dashboard                 # Real-time TUI
1sec alerts --severity HIGH    # High+ alerts
1sec enforce status            # Enforcement stats
1sec enforce history           # Action log
1sec enforce escalations       # Unacknowledged alert timers
1sec enforce batching          # Alert storm stats
1sec correlator                # Cross-module attack chains
1sec threats --blocked         # Blocked IPs
```

## Responding to Alerts

When an alert fires on a VPS agent host, follow this workflow:

### 1. Identify the alert

```bash
1sec alerts --severity HIGH
1sec alerts get <alert-id>
```

### 2. Check what enforcement did

```bash
1sec enforce history --module <module-name>
1sec threats --blocked
```

### 3. Decide: real threat or false positive?

```bash
# If false positive:
1sec alerts false-positive <alert-id>

# If real threat, enforcement already acted (vps-agent preset is aggressive).
# Check that the source is blocked:
1sec threats --blocked

# Review the correlator for multi-module attack chains:
1sec correlator
```

### 4. If enforcement is too aggressive

```bash
# Temporarily pause enforcement while investigating
1sec enforce dry-run on

# Or disable a specific module's enforcement
1sec enforce disable <module-name>

# When done, re-enable
1sec enforce dry-run off
1sec enforce enable <module-name>
```

## Tuning for Your Agent

Different AI agents have different profiles. Tune based on what you see:

```bash
# If llm_firewall is too noisy (many false positives on legitimate prompts):
1sec config set enforcement.policies.llm_firewall.min_severity HIGH

# If auth_fortress blocks legitimate API clients:
1sec config set enforcement.policies.auth_fortress.cooldown_seconds 120

# If you want to switch to a less aggressive preset:
1sec enforce preset balanced

# Preview before switching:
1sec enforce preset balanced --show
```

## Upgrading 1-SEC

```bash
# The binary checks for updates once per day on launch.
# To force an update:
1sec selfupdate

# Or download and verify manually from GitHub Releases:
VERSION="0.5.0"  # replace with target version
wget https://github.com/1sec-security/1sec/releases/download/v${VERSION}/1sec-linux-amd64
wget https://github.com/1sec-security/1sec/releases/download/v${VERSION}/checksums.txt
sha256sum -c checksums.txt 2>&1 | grep 1sec-linux-amd64
chmod +x 1sec-linux-amd64
sudo mv 1sec-linux-amd64 /usr/local/bin/1sec

# Restart after update:
1sec stop
1sec up
```

## Uninstalling

```bash
1sec stop
rm /usr/local/bin/1sec    # or ~/.local/bin/1sec
rm -rf ~/.1sec            # config and data
```
