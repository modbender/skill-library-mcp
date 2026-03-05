---
name: claude-watchdog
description: Monitor the Claude API for outages and latency spikes with rich Telegram alerts. Status monitoring, latency probes, and automatic recovery notifications.
homepage: https://github.com/gisk0/claude-watchdog
metadata:
  openclaw:
    emoji: "🐕"
    requires:
      bins: [python3, crontab, curl]
      env:
        - TELEGRAM_BOT_TOKEN
        - TELEGRAM_CHAT_ID
        - TELEGRAM_TOPIC_ID
        - OPENCLAW_GATEWAY_TOKEN
        - OPENCLAW_GATEWAY_PORT
        - MONITOR_MODEL
        - PROBE_MODEL
        - PROBE_AGENT_ID
    primaryEnv: TELEGRAM_BOT_TOKEN
    setup:
      script: scripts/setup.sh
      interactive: true
      validates: TELEGRAM_BOT_TOKEN
---

# Claude Watchdog 🐕

Monitor the Anthropic/Claude API for outages and latency spikes. Sends rich alerts to Telegram — no agent tokens consumed for status checks.

## What It Does

### Status Monitor (`status-check.py`)
- Polls `status.claude.com` every 15 minutes via cron
- Alerts with incident name, latest update text, per-component status
- Tags incidents as "(not our model)" if e.g. Haiku is affected but you use Sonnet
- Sends all-clear on recovery
- **Zero token cost**

### Latency Probe (`latency-probe.py`)
- Sends a minimal request through OpenClaw's local gateway every 15 minutes
- Measures real end-to-end latency to Anthropic API
- Maintains rolling baseline (median of last 20 samples)
- Alerts with 🟡/🟠/🔴 severity based on spike magnitude
- Sends all-clear when latency recovers
- **~$0.000001 per probe**

## Setup

Run the interactive setup script:

```bash
bash /path/to/skills/claude-watchdog/scripts/setup.sh
```

You'll need:
1. **Telegram Bot Token** — from [@BotFather](https://t.me/BotFather)
2. **Telegram Chat ID** — send a message to your bot, then check `https://api.telegram.org/bot<TOKEN>/getUpdates`
3. **OpenClaw Gateway Token** — run:
   ```bash
   python3 -c "from pathlib import Path; import json; print(json.load(open(Path.home() / '.openclaw/openclaw.json'))['gateway']['auth']['token'])"
   ```
4. **Gateway Port** — default `18789`

The setup script writes config, installs cron jobs, and runs an initial check.

To uninstall (removes cron jobs, optionally config/state):
```bash
bash /path/to/skills/claude-watchdog/scripts/setup.sh --uninstall
```

## Config

Stored in `~/.openclaw/skills/claude-watchdog/claude-watchdog.env`. To reconfigure, either re-run `setup.sh` or edit this file directly — changes take effect on the next cron run (within 15 minutes).

```
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
OPENCLAW_GATEWAY_TOKEN=...
OPENCLAW_GATEWAY_PORT=18789
MONITOR_MODEL=sonnet
PROBE_MODEL=openclaw
PROBE_AGENT_ID=main
```

| Variable | Default | Description |
|----------|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | *(required)* | Telegram bot token from @BotFather |
| `TELEGRAM_CHAT_ID` | *(required)* | Target chat for alerts |
| `OPENCLAW_GATEWAY_TOKEN` | *(required)* | Auth token for the local OpenClaw gateway |
| `OPENCLAW_GATEWAY_PORT` | `18789` | Port the OpenClaw gateway listens on |
| `MONITOR_MODEL` | `sonnet` | Model name to match in status incidents (e.g. "sonnet", "haiku") |
| `PROBE_MODEL` | `openclaw` | Model alias sent to the gateway for latency probes. `openclaw` uses the gateway's default model routing |
| `PROBE_AGENT_ID` | `main` | Value of the `x-openclaw-agent-id` header sent with probes |
| `FILTER_KEYWORDS` | *(none)* | Comma-separated keywords to filter out of status alerts (e.g. "skills,Artifacts,Memory"). Empty = receive all alerts |

Scripts also accept these as environment variables (env file takes priority).

### Security Note

The env file contains sensitive tokens (Telegram bot token, gateway token). The setup script sets permissions to `600` (owner-only read/write). If you create or edit the file manually, ensure restricted permissions:

```bash
chmod 600 ~/.openclaw/skills/claude-watchdog/claude-watchdog.env
```

## Alert Examples

**Status incident:**
```
🟠 Anthropic Status: Partially Degraded Service

📌 Elevated error rates on Claude 3.5 Haiku (not our model)
Status: Investigating
Update: "We are investigating increased error rates..."

Components:
  🟠 API: partial outage

🔗 https://status.claude.com
```

**Latency spike:**
```
🟡 Anthropic API — High Latency Detected

Current: 12.3s
Baseline: 3.1s (median of last 19 samples)
Ratio: 4.0×

Slow responses are expected right now.
```

**Recovery:**
```
✅ Anthropic API — Latency Back to Normal

Current: 2.8s
Baseline: 3.1s
Was: 12.3s when alert fired
```

## State & Logs

All state and log files are stored in `~/.openclaw/skills/claude-watchdog/`:

| File | Purpose |
|------|---------|
| `claude-watchdog-status.json` | Status check state |
| `claude-watchdog-latency.json` | Latency probe state & samples |
| `claude-watchdog-status.log` | Status check log |
| `claude-watchdog-latency.log` | Latency probe log |

## Tuning Thresholds

Edit constants at the top of `latency-probe.py`:

| Constant | Default | Meaning |
|----------|---------|---------|
| `ALERT_MULTIPLIER` | 2.5 | Alert if latency > N× baseline median |
| `ALERT_HARD_FLOOR` | 10.0s | Always alert above this absolute threshold |
| `RECOVER_MULTIPLIER` | 1.5 | Clear alert when below N× baseline |
| `BASELINE_WINDOW` | 20 | Rolling sample window size |
| `BASELINE_MIN_SAMPLES` | 5 | Minimum samples before alerting starts |
| `PROBE_TIMEOUT` | 45s | Give up on probe after this long |

## Requirements

- Python 3.10+ (stdlib only, no pip dependencies)
- OpenClaw gateway running locally
- Telegram bot with access to the target chat
