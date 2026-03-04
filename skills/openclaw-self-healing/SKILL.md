---
name: openclaw-self-healing
version: 3.1.1
description: 4-tier autonomous self-healing and auto-recovery system for OpenClaw Gateway. Monitors gateway health, auto-restarts on crash, detects OAuth token expiry, kills zombie processes, and escalates to Claude Code AI for diagnosis when automated recovery fails. Use when your OpenClaw gateway crashes, stops responding, enters a restart loop, or needs automatic monitoring and recovery. Features watchdog, config validation, exponential backoff, Discord/Telegram alerts. macOS & Linux.
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["tmux", "claude", "jq"] },
        "install":
          [
            {
              "id": "tmux",
              "kind": "brew",
              "package": "tmux",
              "bins": ["tmux"],
              "label": "Install tmux (brew)",
            },
            {
              "id": "claude",
              "kind": "node",
              "package": "@anthropic-ai/claude-code",
              "bins": ["claude"],
              "label": "Install Claude Code CLI (npm)",
            },
            {
              "id": "jq",
              "kind": "brew",
              "package": "jq",
              "bins": ["jq"],
              "label": "Install jq (brew) - for metrics dashboard",
            },
          ],
      },
  }
---

# OpenClaw Self-Healing System

> **"The system that heals itself — or calls for help when it can't."**

A 4-tier autonomous recovery system for [OpenClaw](https://github.com/openclaw/openclaw) Gateway, featuring **AI-powered diagnosis** via Claude Code. Tested in production on macOS + Linux.

## Architecture

```
Level 1: config-watch        → Config file change detection + instant reload
Level 2: Watchdog v4.4       → OAuth detection, zombie kill, exponential backoff
Level 3: Claude Code Doctor  → AI-powered diagnosis & repair (30 min window) 🧠
Level 4: Discord/Telegram    → Human escalation with full context
```

## What's New in v3.1.0

- **Complete healing chain fix** — config-watch → Watchdog → Emergency Recovery now fully connected
- **Installer rewrite** — single `install.sh` covers macOS (LaunchAgent) + Linux (systemd)
- **Watchdog v4.4** — OAuth token expiry detection, zombie process auto-kill, Exponential Backoff
- **Emergency Recovery v2** — persistent learning repo, reasoning logs, multi-model support (Claude Code + Aider)
- **Metrics dashboard** — success rate, MTTR, trending analysis via tmux

## Quick Setup

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/Ramsbaby/openclaw-self-healing/main/install.sh)
```

Or install via ClawHub:

```bash
npx clawhub@latest install openclaw-self-healing
```

## The 4 Tiers in Detail

| Level | Script | Trigger | Action |
|-------|--------|---------|--------|
| L1 | `config-watch.sh` | Config file change | Validate + reload gateway |
| L2 | `gateway-watchdog.sh` | Process down / HTTP fail | Kill zombie → restart → backoff |
| L3 | `emergency-recovery-v2.sh` | 30min continuous failure | Claude Code PTY diagnosis |
| L4 | `emergency-recovery-monitor.sh` | L3 triggered | Discord + Telegram alert |

## Configuration

All settings via environment variables in `~/.openclaw/.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `DISCORD_WEBHOOK_URL` | (none) | Discord webhook for L4 alerts |
| `OPENCLAW_GATEWAY_URL` | `http://localhost:18789/` | Gateway health check URL |
| `HEALTH_CHECK_MAX_RETRIES` | `3` | Restart attempts before L3 escalation |
| `EMERGENCY_RECOVERY_TIMEOUT` | `1800` | Claude recovery timeout (30 min) |

## Verified Recovery Cases

- **OAuth token expiry** — Watchdog v4.4 detects 401 in logs, restarts before agent dies
- **Zombie process** — Preflight detects PID mismatch, SIGKILL + launchctl kickstart
- **Config schema error** — `openclaw doctor --fix` auto-applied on exit_1 pattern
- **Level 3 triggered** — Claude Code diagnosed and fixed broken config in < 15 min

## Links

- **GitHub:** https://github.com/Ramsbaby/openclaw-self-healing
- **Changelog:** https://github.com/Ramsbaby/openclaw-self-healing/blob/main/CHANGELOG.md
- **Linux setup:** https://github.com/Ramsbaby/openclaw-self-healing/blob/main/docs/LINUX_SETUP.md

## License

MIT — built by @ramsbaby + Jarvis 🦞
