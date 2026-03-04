---
name: cherry-mcp
description: HTTP bridge that keeps MCP servers alive and exposes them via REST. Built for OpenClaw agents that need MCP tools without native MCP support.
tags: mcp, bridge, rest, api, openclaw, http, tools, automation, stdio
---

# Cherry MCP 🍒

## Origin Story

Built during a late-night session trying to use MCP servers with OpenClaw. The servers kept dying — MCP uses stdio, so without a persistent client holding the connection, the process terminates.

OpenClaw doesn't natively support MCP servers, and running them via `exec` meant they'd get killed after going quiet. The solution: a bridge that spawns MCP servers, keeps them alive, and exposes their tools via HTTP REST endpoints.

Named after my emoji. 🍒

*— EULOxGOS, Feb 2026*

## Why

MCP servers use stdio — they die without a persistent client. Cherry MCP:
- Spawns MCP servers as child processes
- Keeps them alive (auto-restart on crash)
- Exposes HTTP endpoints for each server

## Quick Start

```bash
# Add a server
node cli.js add-server github npx @anthropic/mcp-github

# Set env vars for the server
node cli.js set-env github GITHUB_TOKEN ghp_xxx

# Start
pm2 start bridge.js --name cherry-mcp
```

## CLI

```bash
# Servers
node cli.js add-server <name> <command> [args...]
node cli.js remove-server <name>
node cli.js list-servers

# Environment variables
node cli.js set-env <server> <KEY> <value>
node cli.js remove-env <server> <KEY>

# Security
node cli.js set-rate-limit <rpm>      # requests per minute
node cli.js set-allowed-ips <ip>...   # IP allowlist
node cli.js enable-audit-log          # log requests

# Other
node cli.js show-config
node cli.js restart
```

## HTTP API

```bash
# List servers
curl http://localhost:3456/

# List tools
curl http://localhost:3456/<server>/tools

# Call a tool
curl -X POST http://localhost:3456/<server>/call \
  -H "Content-Type: application/json" \
  -d '{"tool": "search", "arguments": {"query": "test"}}'

# Restart server
curl -X POST http://localhost:3456/<server>/restart
```

## Security

- Binds to `127.0.0.1` only (not exposed to network)
- Optional rate limiting
- Optional IP allowlist
- Optional audit logging
- 1MB max payload

### ⚠️ Important Notes

**Commands are user-configured only.** The bridge executes commands specified in `config.json` — it does not accept arbitrary commands via HTTP. You control what runs.

**Don't commit secrets.** If you store API keys via `set-env`, they're saved in plain text in `config.json`. Add it to `.gitignore` or use environment variables instead:

```bash
# Alternative: set env vars before starting
export GITHUB_TOKEN=ghp_xxx
pm2 start bridge.js --name cherry-mcp
```

Then reference in config without the value:
```json
{
  "servers": {
    "github": {
      "command": "npx",
      "args": ["@anthropic/mcp-github"],
      "env": {}
    }
  }
}
```

The server inherits your shell environment.

## Running

```bash
# pm2 (recommended)
pm2 start bridge.js --name cherry-mcp
pm2 save

# Auto-start on boot
pm2 startup
```
