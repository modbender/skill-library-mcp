---
name: clawguardian
description: One layer in a multi-layer security stack for OpenClaw agents. Intercepts prompt injection, exfiltration attempts, tool abuse, and social engineering before they reach the model. Use alongside OpenClaw's built-in capability restrictions for defense-in-depth.
version: 2.3.4
homepage: https://github.com/bluemax30001/guardian
metadata:
  openclaw:
    requires:
      bins:
        - python3
      env:
        required: []
        optional:
          - GUARDIAN_WORKSPACE
          - GUARDIAN_CONFIG
          - OPENCLAW_WORKSPACE
          - OPENCLAW_CONFIG_PATH
        never_required:
          - STRIPE_SECRET_KEY
          - STRIPE_WEBHOOK_SECRET
    permissions:
      - read_workspace
      - write_workspace
      - shell_optional
      - network_optional
    optional_capabilities:
      - name: dashboard_http_server
        description: "Local HTTP dashboard on port 8080 (serve.py). Disabled by default. Start manually or via systemd — never auto-starts on install."
        enabled_by_default: false
        how_to_enable: "python3 scripts/serve.py --port 8080"
      - name: billing_stripe
        description: "Pro tier Stripe billing integration. Completely inactive unless STRIPE_* env vars are set. Safe to ignore for free tier."
        enabled_by_default: false
        how_to_enable: "Set pro_tier.enabled=true in config.json and set STRIPE_* env vars"
      - name: webhook_integration
        description: "Inbound webhook endpoint for external threat reports. Disabled by default."
        enabled_by_default: false
        how_to_enable: "Configure webhook section in config.json"
      - name: cron_jobs
        description: "Periodic scanning cron jobs. Opt-in only — run onboard.py --setup-crons explicitly."
        enabled_by_default: false
        how_to_enable: "python3 scripts/onboard.py --setup-crons"
    install_transparency:
      activation_marker: ".guardian-activate-pending written by install.sh. Delete this file to prevent auto-onboarding on next OpenClaw load."
      data_egress: "None by default. All scan data stays in local guardian.db. Webhooks and HTTP server are opt-in."
      credentials: "No credentials required. Stripe keys only needed for optional Pro billing."
      audit_exports: "audit_exports/ directory is excluded from all published packages (.clawhubignore). Never shipped."
      definitions: "definitions/*.json contain threat-detection regex patterns — these are detection signatures, not attack payloads. Equivalent to antivirus virus definition databases."
---

# Guardian

**One layer in a multi-layer security stack for OpenClaw agents.**

Real agent security requires multiple layers: OpenClaw's built-in capability restrictions and
approval gates handle what the agent *can do*. Guardian handles what the agent *sees* —
intercepting malicious inputs before they reach the model.

Guardian provides signature-based pre-model scanning for prompt injection, credential
exfiltration attempts, tool abuse patterns, and social engineering attacks. It is not a complete
security solution on its own. Use it alongside OpenClaw's tool allowlists, approval gates, and
sandboxed execution for defense-in-depth.

Guardian provides two scanning modes:

- **Real-time pre-scan** — checks each incoming message before it reaches the model
- **Batch scan** — periodic sweep of workspace files and conversation logs

All data stays local. Cron setup is optional via `scripts/onboard.py --setup-crons`.

Scan results are stored in a SQLite database (`guardian.db`).

## Installation

```bash
cd ~/.openclaw/skills/guardian
./install.sh
```

## Install mechanism and review
This package includes executable scripts (including `install.sh`) and Python modules.
Review `install.sh` before running in production.
`install.sh` performs local setup/validation; optional helper `onboard.py` is opt-in for cron setup.

## Onboarding checklist
1) Optional: `python3 scripts/onboard.py --setup-crons` (scanner/report/digest crons)
2) `python3 scripts/admin.py status` (confirm running)
3) `python3 scripts/admin.py threats` (confirm signatures loaded; should show 0/blocked)
4) Optional: review `config.json` scan_paths and threshold for your environment

### First-load / self-activation
After `install.sh` completes, it writes `.guardian-activate-pending` to the workspace root
(`~/.openclaw/workspace/.guardian-activate-pending`). When OpenClaw detects this marker on
next load, it triggers `onboard.py` automatically for the self-activation flow. The marker is
removed once `onboard.py` has run. If you prefer manual onboarding, simply delete the marker
before reloading (`rm ~/.openclaw/workspace/.guardian-activate-pending`).

## Scan scope and privacy
Guardian scans configured workspace paths to detect threats. Depending on `scan_paths`, this can include other skill/config files in your OpenClaw workspace.
If you handle sensitive files, set narrow `scan_paths` in `config.json`.

## Quick Start

```bash
# Check status
python3 scripts/admin.py status

# Scan recent threats
python3 scripts/guardian.py --report --hours 24

# Full report
python3 scripts/admin.py report
```

## Admin Commands

```bash
python3 scripts/admin.py status          # Current status
python3 scripts/admin.py enable          # Enable scanning
python3 scripts/admin.py disable         # Disable scanning
python3 scripts/admin.py threats         # List detected threats
python3 scripts/admin.py threats --clear # Clear threat log
python3 scripts/admin.py dismiss INJ-004 # Dismiss a signature
python3 scripts/admin.py allowlist add "safe phrase"
python3 scripts/admin.py allowlist remove "safe phrase"
python3 scripts/admin.py update-defs     # Update threat definitions
```

Add `--json` to any command for machine-readable output.

## Python API

```python
from core.realtime import RealtimeGuard

guard = RealtimeGuard()
result = guard.scan_message(user_text, channel="telegram")
if guard.should_block(result):
    return guard.format_block_response(result)
```

## Environment variables read
- `GUARDIAN_WORKSPACE` (optional workspace override)
- `OPENCLAW_WORKSPACE` (optional fallback workspace override)
- `GUARDIAN_CONFIG` (optional guardian config path)
- `OPENCLAW_CONFIG_PATH` (optional OpenClaw config path)

## Configuration

Edit `config.json`:

| Setting | Description |
|---|---|
| `enabled` | Master on/off switch |
| `severity_threshold` | Blocking threshold: `low` / `medium` / `high` / `critical` |
| `scan_paths` | Paths to scan (`["auto"]` for common folders) |
| `db_path` | SQLite location (`"auto"` = `<workspace>/guardian.db`) |

## How It Works

Guardian loads threat signatures from `definitions/*.json` files. Each signature has
an ID, regex pattern, severity level, and category. Incoming text is matched against
all active signatures. Matches above the configured severity threshold are blocked
and logged to the database.

Signatures cover: prompt injection, credential patterns (API keys, tokens),
data exfiltration attempts, tool abuse patterns, and social engineering tactics.

### Source Trust Levels

Guardian assigns every scan a trust level based on the source channel and message role. There are four levels: **0 – internal** (cron jobs, workspace files, system prompts) is never blocked; **1 – owner** (Telegram) is flagged for review but never blocked; **2 – semi-trusted** (email, unknown sources) is blocked only when the threat score reaches 70 or above; **3 – external** (webhooks) is blocked at a lower threshold of 50 or above. The role of the message can adjust the effective trust level: `system` messages shift one step toward internal, while `tool` results shift one step toward external. This prevents false positives on internal/cron content that may legitimately reference injection-like phrases (for example, in log output or documentation).
