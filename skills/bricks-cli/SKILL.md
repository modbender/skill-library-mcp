---
name: bricks-cli
description: Manage BRICKS workspace via CLI. Use for device status, screenshots, control, monitoring, group operations, application management, module management, and project initialization and deployment. Triggers on: device management, digital signage control, BRICKS workspace tasks, app/module updates, project setup.
---

# BRICKS CLI

CLI for BRICKS Workspace API — manage devices, apps, modules, and media.

## Installation (if not yet)

```bash
# Validate installed
which bricks

# npm
npm i -g @fugood/bricks-cli
# Bun
bun add -g @fugood/bricks-cli
```

## Authentication

```bash
# Login with one-time passcode (get from https://control.bricks.tools)
bricks auth login <passcode>

# Check auth status
bricks auth status

# Switch profiles
bricks auth list
bricks auth use <profile>
```

## Device Management

### List & Info

```bash
# List all devices
bricks device list
bricks device list -j              # JSON output
bricks device list -k "lobby"      # Filter by keyword

# Get device details
bricks device get <device-id>
bricks device get <device-id> -j   # JSON output
```

### Control

```bash
# Refresh device (reload app)
bricks device refresh <device-id>

# Clear device cache
bricks device clear-cache <device-id>

# Send control command
bricks device control <device-id> <type>
bricks device control <device-id> <type> -p '{"key":"value"}'
```

### Screenshot

```bash
# Take and save screenshot
bricks device screenshot <device-id>
bricks device screenshot <device-id> -o /tmp/screen.png

# Fetch existing screenshot (no new capture)
bricks device screenshot <device-id> --no-take
```

### Monitor (Interactive-tty needed)

```bash
# Monitor all devices (polls every 60s)
bricks device monitor

# Monitor specific group
bricks device monitor -g <group-id>

# Custom interval
bricks device monitor -i 30
```

## Device Groups

```bash
# List groups
bricks group list

# Get group details
bricks group get <group-id>

# List devices in group with status
bricks group devices <group-id>

# Dispatch action to all devices in group
bricks group dispatch <group-id> <action>

# Refresh all devices in group
bricks group refresh <group-id>

# Monitor group
bricks group monitor <group-id>
```

## Applications

```bash
# List apps
bricks app list

# Get app details
bricks app get <app-id>

# Update app
bricks app update <app-id>

# Bind devices to app
bricks app bind <app-id>

# Quick property edit
bricks app short-edit <app-id>

# Pull source files
bricks app project-pull <app-id>

# Initialize local project from app
bricks app project-init <app-id>
bricks app project-init <app-id> -o ./my-app
bricks app project-init <app-id> -y          # Skip prompts, use defaults
bricks app project-init <app-id> --no-git    # Skip git init
```

## Modules

```bash
bricks module list
bricks module get <module-id>
bricks module update <module-id>
bricks module short-edit <module-id>
bricks module release <module-id>

# Initialize local project from module
bricks module project-init <module-id>
bricks module project-init <module-id> -o ./my-module -y
```

### Project Init Options

Both `app` and `module` support these flags:
- `-o, --output <dir>` — output directory
- `-y, --yes` — skip prompts, use defaults
- `--no-git` — skip git initialization
- `--no-install` — skip `bun install`
- `--no-github-actions` — skip GitHub Actions workflow
- `--no-agents` — skip AGENTS.md
- `--no-claude` — skip CLAUDE.md
- `--gemini` — include GEMINI.md (off by default)

## Media Flow

```bash
bricks media boxes              # List media boxes
bricks media box <box-id>       # Box details
bricks media files <box-id>     # Files in box
bricks media file <file-id>     # File details
```

## Config

```bash
bricks config show              # Show current config
bricks config endpoint          # Show API endpoint
bricks config endpoint beta     # Switch to beta endpoint
```

## Interactive Mode (Interactive-tty needed)

```bash
bricks interactive    # or: bricks i
```

## DevTools (LAN Discovery)

```bash
# Scan LAN for DevTools servers via UDP broadcast
bricks devtools scan
bricks devtools scan -t 5000           # Custom timeout (ms)
bricks devtools scan -j                # JSON output
bricks devtools scan --verify          # Verify each server via HTTP

# Show connection URLs for a device
bricks devtools open <address>
bricks devtools open <address> -p 19853   # Custom port
bricks devtools open <address> --verify   # Verify reachable first
```

Devices must have "Enable LAN Discovery" turned on in Advanced Settings (on by default).

## MCP Server

```bash
bricks mcp start      # Start MCP server (STDIO mode)
```

### Bridging Device MCP to Local CLI

Use [mcporter](https://mcporter.dev) to bridge a device's MCP endpoint as a local MCP server (STDIO), so tools like Claude Code can connect to it:

```bash
# Bridge a device's MCP endpoint (requires passcode as Bearer token)
npx mcporter --url http://<device-ip>:19851/mcp --header "Authorization: Bearer <passcode>"
```

## Rules

- `connect-local-device` — Deploy the current app to a local LAN device, then monitor status, debug, and run automations via MCP

## Tips

- Use `-j` or `--json` on most commands for JSON output
- Device IDs are UUIDs — use `device list` to find them
- Get workspace token from: https://control.bricks.tools → Workspace Settings → API Token
