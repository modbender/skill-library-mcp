---
name: gateway-watchdog
description: Monitor OpenClaw gateway health with a watchdog state machine, Discord alerts, cooldown dedupe, and isolated fallback deployment on macOS. Use when users want gateway failure detection, auto-recovery policy, and low-noise Discord incident notifications.
version: "1.0.2"
metadata:
  {
    "openclaw":
      {
        "emoji": "🚨",
        "requires": { "bins": ["bash", "python3", "openclaw"], "config": ["channels.discord.enabled"] },
      },
  }
---

# Gateway Watchdog (Discord)

Discord-first watchdog for OpenClaw gateway incidents.

## 🛠️ Installation

### 1. Ask OpenClaw (Recommended)
Tell OpenClaw: *"Install the gateway-watchdog skill."* The agent will handle the installation and configuration automatically.

### 2. Manual Installation (CLI)
If you prefer the terminal, run:
```bash
clawhub install gateway-watchdog
```

## Isolation model

- Watchdog data is isolated under `~/.openclaw/watchdogs/gateway-discord/`.
- No edits to `openclaw.json` are required.
- Default mode is read-only monitoring (`GW_WATCHDOG_ENABLE_RESTART=0`).
- Automatic restart is opt-in and bounded by max attempts.

## Files in this skill

- `scripts/gateway-watchdog.sh` - health checks + state machine + Discord notification.
- `scripts/install-launchd.sh` - installs a user LaunchAgent from template.
- `references/com.openclaw.gateway-watchdog.plist.template` - launchd template.
- `references/cron-agent-turn.md` - isolated cron prompt template.

## Health checks

The watchdog checks:

```bash
openclaw gateway status --json
openclaw health --json --timeout <ms>
```

Pass criteria:

- gateway runtime is `running`
- RPC probe is healthy (when present)
- health snapshot returns successfully

Failure classes:

- `runtime_stopped`
- `rpc_probe_failed`
- `health_unreachable`
- `auth_mismatch`
- `config_invalid`

## Quick start (manual run)

```bash
bash "{baseDir}/scripts/gateway-watchdog.sh"
```

Optional env:

```bash
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."
export DISCORD_BOT_TOKEN="discord_bot_token"
export DISCORD_CHANNEL_ID="<your_discord_channel_id>"
export GW_WATCHDOG_SOURCE="manual"
export GW_WATCHDOG_FAIL_THRESHOLD=2
export GW_WATCHDOG_COOLDOWN_SECONDS=300
```

Delivery priority:

1. `DISCORD_WEBHOOK_URL`
2. `DISCORD_BOT_TOKEN + DISCORD_CHANNEL_ID`

## macOS background mode (LaunchAgent)

Install LaunchAgent (does not edit OpenClaw core config):

```bash
bash "{baseDir}/scripts/install-launchd.sh" --interval 30 --load
```

Check status:

```bash
launchctl list | rg "com.openclaw.gateway-watchdog"
```

## OpenClaw cron mode (internal path)

Use isolated job and keep messaging in one channel:

```bash
openclaw cron add \
  --name "gateway-watchdog-internal" \
  --cron "*/1 * * * *" \
  --session isolated \
  --message "Run bash {baseDir}/scripts/gateway-watchdog.sh and report state changes only." \
  --announce \
  --channel discord \
  --to "channel:<your_channel_id>" \
  --best-effort-deliver
```

## Auto-recovery policy (opt-in)

Enable bounded restart:

```bash
export GW_WATCHDOG_ENABLE_RESTART=1
export GW_WATCHDOG_MAX_RESTART_ATTEMPTS=2
```

Safety constraints:

- restart only after failure threshold is met
- max attempts enforced per incident window
- no reinstall or destructive mutation

## Backup and audit artifacts

- state file: `~/.openclaw/watchdogs/gateway-discord/state.json`
- state backups: `~/.openclaw/watchdogs/gateway-discord/backups/state-*.json`
- event log: `~/.openclaw/watchdogs/gateway-discord/events.jsonl`

The script rotates old backups and keeps recent history for rollback/debugging.
