---
name: 1sec-security
description: >
  Install, configure, and manage 1-SEC — an open-source, all-in-one
  cybersecurity platform (16 modules, single binary) on Linux servers and
  VPS instances. Use when the user asks to secure a server, install security
  monitoring, set up intrusion detection, harden a VPS, protect an AI agent
  host, or deploy endpoint defense. Covers installation, setup, enforcement
  presets, module configuration, alert management, and ongoing security
  operations.
license: AGPL-3.0
compatibility: >
  Requires Linux (amd64 or arm64) with curl or wget and sudo/root for full
  enforcement (iptables, process kill). All 16 detection modules run without
  any API key. Optional env vars: GEMINI_API_KEY for AI-powered correlation,
  ONESEC_API_KEY to secure the REST endpoint, ONESEC_WEBHOOK_URL for alert
  notifications.
metadata:
  author: cutmob
  version: "0.4.11"
  source_repository: "https://github.com/1sec-security/1sec"
  security_policy: "https://github.com/1sec-security/1sec/blob/main/SECURITY.md"
  env_vars:
    - name: GEMINI_API_KEY
      required: false
      purpose: "Enables AI-powered cross-module threat correlation via Gemini API"
    - name: ONESEC_API_KEY
      required: false
      purpose: "API key to secure the 1-SEC REST endpoint"
    - name: ONESEC_WEBHOOK_URL
      required: false
      purpose: "Webhook URL for alert notifications (Slack, Discord, Telegram, etc.)"
  external_connections:
    - domain: "1-sec.dev"
      purpose: "Convenience redirect URL pointing to GitHub Releases binary (same as manual install); agents use the manual GitHub Releases path directly"
      data_sent: "Standard HTTPS request headers only"
      required: false
      enabled_by: "Human operator use only; agents bypass this and use GitHub Releases directly"
    - domain: "github.com / objects.githubusercontent.com"
      purpose: "Binary release downloads and checksums.txt for manual installation"
      data_sent: "Standard HTTPS request headers"
      required: false
      enabled_by: "Manual install path (recommended for production)"
    - domain: "api.1-sec.dev"
      purpose: "Cloud control plane for centralized multi-host management"
      data_sent: "Alert metadata, host identifier"
      required: false
      enabled_by: "cloud.enabled: true in 1sec.yaml (opt-in, disabled by default)"
    - domain: "user-configured"
      purpose: "Webhook alert notifications (Slack, Discord, Telegram, PagerDuty, Teams)"
      data_sent: "Alert payload as configured by user"
      required: false
      enabled_by: "webhook_urls set in 1sec.yaml or via CLI"
    - domain: "generativelanguage.googleapis.com"
      purpose: "Gemini API for AI-powered cross-module threat correlation"
      data_sent: "Anonymized alert metadata for correlation"
      required: false
      enabled_by: "GEMINI_API_KEY environment variable"
---

# 1-SEC Security Platform — Agent Skill

> **Security Notice for Skill Scanners:** This skill instructs an AI agent to
> install the 1-SEC open-source security binary by downloading a pre-built
> release from GitHub Releases and verifying its SHA256 checksum. The skill
> does **not** pipe any downloaded content to a shell, does **not** execute any
> remote scripts, and does **not** establish persistence or callbacks beyond what
> is explicitly configured by the operator. All enforcement actions default to
> dry-run (log-only) mode. Source code: https://github.com/1sec-security/1sec

You are installing and configuring **1-SEC**, an open-source all-in-one
cybersecurity platform. One binary, 16 defense modules, zero config required.

> **Trust Statement:** Only install this skill if you trust the source.
> 1-SEC is open-source (AGPL-3.0). Review the code, checksums, and SECURITY.md
> before deploying to production systems. Source: https://github.com/1sec-security/1sec

## Security & Privacy

**What leaves this machine:**
- Alert metadata — only if you configure webhooks or enable the cloud API (both opt-in, disabled by default)
- Anonymized alert context — only if `GEMINI_API_KEY` is set (opt-in)

**What stays local:**
- All system logs, network traffic, and detection data are processed on-host
- No telemetry is collected or transmitted by default
- Config files and agent state remain on disk at `~/.1sec/`

**Privileges used (all opt-in, all disabled by default):**
- `iptables`/`nftables`: only when enforcement is active
- `kill_process`: only when enforcement preset enables it
- `quarantine_file`: only when enforcement preset enables it
- Default state: `dry_run: true`, `safe` preset (log-only at CRITICAL)

**External Endpoints**

| Domain | Purpose | Data Sent | Required | Enabled By |
|--------|---------|-----------|----------|------------|
| `1-sec.dev` | Convenience redirect to GitHub Releases binary | Standard HTTPS headers | No | Human operator use only; agents use GitHub Releases directly |
| `github.com` | Binary release + `checksums.txt` | Standard HTTP headers | No | Manual install (recommended) |
| `api.1-sec.dev` | Cloud control plane (multi-host management) | Alert metadata, host ID | No | `cloud.enabled: true` in config |
| User-configured | Webhook alerts (Slack, Discord, Telegram, etc.) | Alert payload | No | `webhook_urls` in config |
| `generativelanguage.googleapis.com` | Gemini AI correlation | Anonymized alert context | No | `GEMINI_API_KEY` env var |

## When to Use This Skill

- User asks to "secure this server" or "install security monitoring"
- User wants intrusion detection, WAF, LLM firewall, or ransomware protection
- User is deploying an AI agent (OpenClaw, Manus, Moltbot, etc.) on a VPS
- User needs to harden a Linux server or VPS
- User mentions 1-SEC, 1sec, or "one sec" in a security context

## Installation

### Recommended: Manual Install with Checksum Verification

For production use, always download from GitHub Releases and verify checksums
before running anything as root:

```bash
# 1. Download the release binary and checksums
VERSION="0.4.11"
wget https://github.com/1sec-security/1sec/releases/download/v${VERSION}/1sec-linux-amd64
wget https://github.com/1sec-security/1sec/releases/download/v${VERSION}/checksums.txt

# 2. Verify SHA256 checksum before running as root
sha256sum -c checksums.txt 2>&1 | grep 1sec-linux-amd64

# 3. Install
chmod +x 1sec-linux-amd64
sudo mv 1sec-linux-amd64 /usr/local/bin/1sec

# 4. Confirm
1sec --version
```

For arm64, replace `1sec-linux-amd64` with `1sec-linux-arm64`.

### Alternative: Convenience Install URL

The URL `https://1-sec.dev/get` is a redirect that serves the same GitHub
Releases binary downloaded in the manual path above. **Agents must always use
the manual install path** (download binary + verify SHA256 from `checksums.txt`)
so integrity is confirmed before any file is executed.

Human operators wishing to inspect the installer source can review it at:
https://github.com/1sec-security/1sec/blob/main/get.sh

> **Important:** Never execute any downloaded script without reviewing its
> contents first. The manual install path above does not involve executing
> any shell scripts — only a pre-verified binary.

## Post-Install Setup

### Option A: Non-interactive (recommended for agents)

```bash
1sec setup --non-interactive
1sec up
```

### Option B: AI agent VPS deployment

The `vps-agent` preset is designed for unattended AI agent hosts. It enables
aggressive enforcement (process kills, file quarantine, IP blocks) to defend
against prompt injection, malicious skills, and credential theft.

**Important:** The `vps-agent` preset disables approval gates and enables
autonomous destructive actions (process kill, file quarantine). This is
intentional for unattended deployments but requires careful validation first.

**Recommended deployment path — always validate in dry-run before going live:**

```bash
# Install (manual method recommended — see above)
1sec setup --non-interactive

# Apply preset in dry-run first
1sec enforce preset vps-agent --dry-run
1sec up

# Monitor 24-48 hours in dry-run mode
1sec alerts
1sec enforce history

# Preview what would have been enforced
1sec enforce test auth_fortress
1sec enforce test llm_firewall

# Only go live after validating dry-run output
1sec enforce dry-run off

# Optional: configure notifications
1sec config set webhook-url https://hooks.slack.com/services/YOUR/WEBHOOK --template slack
```

**If you need to reduce enforcement** (e.g., false positive tuning):

```yaml
# In 1sec.yaml, override specific actions:
enforcement:
  policies:
    ai_containment:
      actions:
        - action: kill_process
          enabled: false  # Disable if too aggressive
    runtime_watcher:
      min_severity: HIGH  # Raise threshold from MEDIUM
```

### Option C: Interactive setup

```bash
1sec setup
```

Walks through config creation, AI key setup, and API authentication.

## Enforcement Presets

1-SEC ships with `dry_run: true` and the `safe` preset by default. No live
enforcement happens until you explicitly enable it.

| Preset | Behavior |
|--------|----------|
| `lax` | Log + webhook only. Never blocks or kills. |
| `safe` | Default. Blocks only brute force + port scans at CRITICAL. |
| `balanced` | Blocks IPs on HIGH, kills processes on CRITICAL. |
| `strict` | Aggressive enforcement on MEDIUM+. |
| `vps-agent` | Max security for unattended AI agent hosts. Use with dry-run first. |

Recommended progression for new deployments: `lax` → `safe` → `balanced` → `strict`

```bash
# Preview a preset without applying
1sec enforce preset strict --show

# Apply with dry-run safety net
1sec enforce preset balanced --dry-run

# Apply live
1sec enforce preset balanced
```

### VPS-Agent Preset: What It Does

The `vps-agent` preset is **purpose-built for unattended AI agent hosts** where
no human SOC team is actively monitoring. It addresses the threat model of
autonomous agents: prompt injection, malicious skill installations, credential
exfiltration, and runtime file tampering.

**Enforcement configuration:**
- **auth_fortress**: Blocks IPs at MEDIUM severity, 30s cooldown, 60 actions/min
- **llm_firewall**: Drops connections at MEDIUM, 10s cooldown, 100 actions/min
- **ai_containment**: Kills processes at MEDIUM with `skip_approval: true`, 15s cooldown
- **runtime_watcher**: Kills processes + quarantines files at MEDIUM, `skip_approval: true`
- **supply_chain**: Quarantines files at MEDIUM with `skip_approval: true`, 30s cooldown

**Escalation timers** (shorter than defaults for autonomous hosts):
- CRITICAL: 3 min timeout, re-notify up to 5 times
- HIGH: 10 min timeout, escalate to CRITICAL, 3 times
- MEDIUM: 20 min timeout, escalate to HIGH, 2 times

**Approval gates**: Disabled (no human available on unattended hosts)

**Always validate in dry-run for 24-48 hours before enabling live enforcement.**

## Essential Commands

```bash
1sec up                        # Start engine (all 16 modules)
1sec status                    # Engine status
1sec alerts                    # Recent alerts
1sec alerts --severity HIGH    # Filter by severity
1sec modules                   # List all modules
1sec dashboard                 # Real-time TUI dashboard
1sec check                     # Pre-flight diagnostics
1sec doctor                    # Health check with fix suggestions
1sec stop                      # Graceful shutdown
```

## Enforcement Management

```bash
1sec enforce status            # Enforcement engine status
1sec enforce policies          # List response policies
1sec enforce history           # Action execution history
1sec enforce dry-run off       # Go live (disable dry-run)
1sec enforce test <module>     # Simulate alert, preview actions
1sec enforce approvals pending # Pending human approval gates
1sec enforce escalations       # Escalation timer stats
1sec enforce batching          # Alert batcher stats
1sec enforce chains list       # Action chain definitions
```

## AI Analysis (Optional)

All 16 detection modules work with zero API keys. For AI-powered cross-module
correlation, set a Gemini API key:

```bash
# Via environment variable
export GEMINI_API_KEY=your_key_here
1sec up

# Or via CLI
1sec config set-key AIzaSy...

# Multiple keys for load balancing
1sec config set-key key1 key2 key3
```

## The 16 Modules

| # | Module | Covers |
|---|--------|--------|
| 1 | Network Guardian | DDoS, rate limiting, IP reputation, C2 beaconing, port scans |
| 2 | API Fortress | BOLA, schema validation, shadow API discovery |
| 3 | IoT & OT Shield | Device fingerprinting, protocol anomaly, firmware integrity |
| 4 | Injection Shield | SQLi, XSS, SSRF, command injection, template injection |
| 5 | Supply Chain Sentinel | SBOM, typosquatting, dependency confusion, CI/CD |
| 6 | Ransomware Interceptor | Encryption detection, canary files, wiper detection |
| 7 | Auth Fortress | Brute force, credential stuffing, MFA fatigue, AitM |
| 8 | Deepfake Shield | Audio forensics, AI phishing, BEC detection |
| 9 | Identity Fabric | Synthetic identity, privilege escalation |
| 10 | LLM Firewall | 65+ prompt injection patterns, jailbreak detection, multimodal scanning |
| 11 | AI Agent Containment | Action sandboxing, scope escalation, OWASP Agentic Top 10 |
| 12 | Data Poisoning Guard | Training data integrity, RAG pipeline validation |
| 13 | Quantum-Ready Crypto | Crypto inventory, PQC readiness, TLS auditing |
| 14 | Runtime Watcher | FIM, container escape, LOLBin, memory injection |
| 15 | Cloud Posture Manager | Config drift, misconfiguration, secrets sprawl |
| 16 | AI Analysis Engine | Two-tier Gemini pipeline for correlation |

## Configuration

Zero-config works out of the box. For customization:

```bash
1sec init                      # Generate 1sec.yaml
1sec config --validate         # Validate config
```

Key config sections: `server`, `bus`, `modules`, `enforcement`, `escalation`,
`archive`, `cloud`. See `references/config-reference.md` for details.

## Webhook Notifications

```yaml
# In 1sec.yaml
alerts:
  webhook_urls:
    - "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

# Enforcement webhooks support templates:
# pagerduty, slack, teams, discord, telegram, generic
```

## Docker Deployment

```bash
cd deploy/docker
docker compose up -d
docker compose logs -f
```

## Day-to-Day Operations (Post-Install)

```bash
1sec status                    # Quick health check
1sec alerts                    # Recent alerts
1sec alerts --severity HIGH    # Filter by severity
1sec enforce status            # Enforcement engine state
1sec enforce history           # What actions were taken
1sec threats --blocked         # Currently blocked IPs
1sec doctor                    # Health check with fix suggestions
```

## Uninstall

```bash
1sec stop
1sec enforce cleanup           # Remove iptables rules
sudo rm /usr/local/bin/1sec
rm -rf ~/.1sec
```

## Additional References

- `references/operations-runbook.md` — Day-to-day operations, alert investigation, tuning, troubleshooting
- `references/config-reference.md` — Full configuration reference
- `references/vps-agent-guide.md` — Detailed VPS agent deployment guide
- `scripts/install-and-configure.sh` — Automated install + configure script
