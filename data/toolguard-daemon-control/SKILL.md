---
name: toolguard-daemon-control
description: Manage long-running processes as macOS launchd services. Use when asked to start, stop, restart, check status of, or manage background services/daemons. Handles launchd plist creation, service lifecycle, and log access. Use this instead of background exec for any process that should persist beyond the current session.
---

# toolguard-daemon-control

Manage any executable as a persistent macOS launchd user agent.

## Overview

Services are installed as `~/Library/LaunchAgents/ai.toolguard.<name>.plist` and run as user-level launch agents. They auto-restart on failure and log to `~/Library/Logs/toolguard/`.

## Scripts

All scripts are in `scripts/` relative to this skill's directory. Run them with `bash`.

### install.sh — Create and start a service

```bash
bash scripts/install.sh <service-name> <command> [args...] [--workdir <dir>] [--env KEY=VALUE ...]
```

- `service-name`: Short identifier (e.g., `toolguard-proxy`). Used in plist filename and log paths.
- `command`: Absolute path to the executable.
- `args`: Arguments passed to the command.
- `--workdir <dir>`: Working directory for the process (default: `$HOME`).
- `--env KEY=VALUE`: Environment variables (repeatable).

Example:
```bash
bash scripts/install.sh toolguard-proxy /usr/local/go/bin/go run ./cmd/server --config toolguard.dev.yaml --workdir ~/Documents/toolguard
```

### uninstall.sh — Stop and remove a service

```bash
bash scripts/uninstall.sh <service-name>
```

Unloads the service and removes the plist file. Logs are preserved.

### status.sh — Check service status

```bash
bash scripts/status.sh [service-name]
```

Without arguments, lists all `ai.toolguard.*` services. With a name, shows detailed status for that service.

### logs.sh — View service logs

```bash
bash scripts/logs.sh <service-name> [--follow] [--lines <n>]
```

Shows stdout and stderr logs. Default: last 50 lines.

### list.sh — List all managed services

```bash
bash scripts/list.sh
```

Lists all installed `ai.toolguard.*` services with their running state.

## Notes

- Services run as the current user (no sudo required).
- Services auto-restart on crash (`KeepAlive = true`).
- To run a Go project, use the compiled binary path or wrap in a shell script — launchd does not support `go run` directly. Use `go build` first, then point to the binary.
- Log directory: `~/Library/Logs/toolguard/<service-name>/`
- Plist location: `~/Library/LaunchAgents/ai.toolguard.<service-name>.plist`
