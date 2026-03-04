---
name: watchclaw
description: "Auto-recovery watchdog for OpenClaw gateway. Monitors health, detects bad config changes, and recovers via git stash/revert. Supports native and Docker restart modes with pluggable alerts."
metadata:
  {
    "openclaw":
      {
        "emoji": "🦞",
        "requires": { "bins": ["watchclaw"] },
        "install":
          [
            {
              "id": "curl",
              "kind": "shell",
              "command": "curl -fsSL https://raw.githubusercontent.com/jarvis4wang/watchclaw/main/install.sh | bash",
              "bins": ["watchclaw"],
              "label": "Install watchclaw (curl)",
            },
          ],
      },
  }
---

# watchclaw

OpenClaw gateway watchdog — auto-recovery from bad config changes.

## What It Does

watchclaw monitors your OpenClaw gateway and automatically recovers from bad configurations:
- **Health polling** — checks gateway HTTP endpoint every N seconds
- **Config change detection** — detects uncommitted or new commits in your config repo
- **Auto-recovery** — stashes uncommitted changes (U1) or reverts bad commits (U2) via git
- **Probation** — validates stability after config changes before promoting to known-good
- **Pluggable alerts** — iMessage, webhook, or custom command on failure/recovery

## Usage

```bash
# Start watching (background daemon)
watchclaw --config /path/to/watchclaw.conf start

# Start in foreground (for debugging)
watchclaw --config /path/to/watchclaw.conf start --foreground

# Check status
watchclaw --config /path/to/watchclaw.conf status

# Follow logs
watchclaw --config /path/to/watchclaw.conf logs -f

# Stop
watchclaw --config /path/to/watchclaw.conf stop
```

## Config

Create a `.conf` file (see `watchclaw.conf.example`):

```bash
GATEWAY_PORT=18790
GATEWAY_CONFIG_DIR="$HOME/.openclaw"
POLL_INTERVAL_SEC=10
HEALTH_TIMEOUT_SEC=5
GATEWAY_TLS=0              # Use https for health check
MAX_RETRIES=3
ALERT_HOOK="imsg"           # imsg | webhook | command | none
ALERT_IMSG_TO="user@me.com"
RESTART_MODE="native"       # native | docker
```

## Recovery Modes

| Scenario | Detection | Recovery |
|----------|-----------|----------|
| Uncommitted config change breaks gateway | Health check fails + dirty openclaw.json | `git stash` → restart |
| Bad commit breaks gateway | Health check fails + new commit | `git revert` → restart |
| Config change during healthy operation | HEAD ≠ known-good in HEALTHY state | Enter probation, monitor |

## Docker Mode

For containerized OpenClaw (e.g., 飞书/Feishu bot):

```bash
RESTART_MODE="docker"
DOCKER_CONTAINER="openclaw-feishu"
```

## Requirements

- `bash` 4+, `git`, `curl`
- OpenClaw gateway config must be in a git repo
- `python3` or `node` for JSON validation
