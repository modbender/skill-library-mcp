---
name: codespace-manager
description: Create, manage, and access isolated cloud development environments (codespaces) powered by code-server, Docker, and Cloudflare Tunnel. Pre-installed with Bun, uv, and OpenCode. Use when the user wants to (1) create a new dev environment or codespace, (2) start/stop/restart/delete a codespace, (3) set up an isolated coding workspace, (4) launch a remote VS Code environment, (5) manage development containers, (6) open a browser-based IDE, or mentions codespace, code-server, remote development, dev environment, or cloud IDE.
---

# Codespace Manager

Manage isolated code-server development environments, similar to GitHub Codespaces. Each codespace runs in its own Docker container with a full VS Code editor accessible via browser through Cloudflare Tunnel.

## Pre-installed Tools

The custom Docker image includes:
- **code-server** (VS Code in browser)
- **Bun** — JS/TS runtime + package manager
- **uv** — Python package manager + virtual environments
- **OpenCode** — AI coding assistant (CLI)
- **git, curl, wget, build-essential**

## First-Time Setup

Before creating any codespace, build the Docker image once:

```bash
bash scripts/codespace.sh setup
```

This builds `codespace-manager:latest` from `assets/Dockerfile.txt`. Only needed once per host.

## Commands

Script location: `scripts/codespace.sh` (relative to this skill's directory)

```bash
# One-time image build
codespace setup

# Create codespace (optionally clone a repo and/or init OpenCode config)
codespace create <name>
codespace create <name> --git <repo-url>
codespace create <name> --opencode
codespace create <name> --git <repo-url> --opencode

# Lifecycle
codespace start <name>       # Start and get Cloudflare Tunnel URL
codespace stop <name>        # Stop container and tunnel
codespace restart <name>     # Stop then start (new URL)
codespace delete <name>      # Remove container + data (irreversible!)

# Info
codespace list               # List all codespaces with status
codespace status <name>      # Detailed status of one codespace
codespace logs <name>        # View container logs
codespace url <name>         # Regenerate tunnel URL

# Config
codespace password <pass>    # Set default password for new codespaces
```

## Password Management

- Default password: `codespace`
- Set a custom default: `codespace password <your-password>`
- Override per-session via environment: `CODESPACE_PASSWORD=mypass codespace create foo`
- Each codespace saves its password at creation time

## Natural Language → Command Mapping

| User says | Command |
|---|---|
| "create a codespace called myapp" | `codespace create myapp` |
| "create a codespace with opencode" | `codespace create <name> --opencode` |
| "set up a dev environment for this repo" | `codespace create <name> --git <url> --opencode` |
| "start / launch / open myapp" | `codespace start myapp` |
| "stop / shut down myapp" | `codespace stop myapp` |
| "delete / remove myapp" | `codespace delete myapp` (confirm with user first!) |
| "list my codespaces" / "show environments" | `codespace list` |
| "get the URL for myapp" | `codespace url myapp` |
| "set password to xyz" | `codespace password xyz` |
| "create a python project" | `codespace create <name> --opencode` (uv is pre-installed) |
| "create a node/bun project" | `codespace create <name> --opencode` (bun is pre-installed) |

## Architecture

- Each codespace = isolated Docker container (`codespace-manager:latest`)
- Project files persist at `~/codespaces/<name>/project` on the host
- Exposed via **Cloudflare Quick Tunnel** (free, auto HTTPS, temporary URL)
- Each codespace gets a deterministic port (9000-9999, based on name hash)

## Important Notes

1. Run `codespace setup` before first use — it builds the Docker image
2. Quick Tunnel URLs are temporary — they change on restart
3. `codespace delete` is irreversible — confirm with user before executing
4. Container data (outside `/home/coder/project`) does not persist across delete/recreate
5. Requires: Docker, cloudflared, jq installed on the host

## OpenCode Config

When `--opencode` is used, a `opencode.json` is created in the project root with:
```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "anthropic/claude-sonnet-4-5",
  "autoupdate": true
}
```

Users can edit this file in code-server to change the model or add provider keys.
