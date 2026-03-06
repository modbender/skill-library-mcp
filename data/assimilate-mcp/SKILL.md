---
name: assimilate-mcp
description: Control Assimilate Live FX / SCRATCH — professional color grading, compositing, and virtual production software — via MCP. 88 tools across 14 categories.
homepage: https://github.com/amac-roguelabs/assimilate-mcp
metadata: {"clawdbot":{"emoji":"🎨","requires":{"bins":["npx"]},"install":[{"id":"node","kind":"node","package":"assimilate-mcp","bins":["assimilate-mcp"],"label":"Install assimilate-mcp"}]}}
---

# Assimilate MCP

Control [Assimilate Live FX / SCRATCH](https://assimilateinc.com) — professional color grading, compositing, and virtual production software — via MCP. Complete 1:1 integration of the [Assimilate REST API](https://github.com/Assimilate-Inc/Assimilate-REST) with 88 tools across 14 categories.

## Prerequisites

- [Assimilate Live FX or SCRATCH](https://assimilateinc.com) with REST API enabled
- [Node.js](https://nodejs.org) v18+
- Live FX HTTP server enabled: **System Settings → General → Enable HTTP Server** (default port 8080)

## Setup

### MCPorter

```bash
mcporter config add assimilate --command npx --args '["-y", "assimilate-mcp"]'
mcporter list assimilate
```

### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "assimilate": {
      "command": "npx",
      "args": ["-y", "assimilate-mcp"]
    }
  }
}
```

### Claude Code

```bash
claude mcp add assimilate -- npx -y assimilate-mcp
```

## Configuration

| Flag | Env Var | Default | Description |
|------|---------|---------|-------------|
| `--host` | `ASSIMILATE_HOST` | `127.0.0.1` | Live FX host |
| `--port` | `ASSIMILATE_PORT` | `8080` | REST API port |
| `--key` | `ASSIMILATE_KEY` | — | Authorization key |
| `--timeout` | `ASSIMILATE_TIMEOUT` | `30000` | HTTP timeout (ms) |

Example with custom port:

```json
{
  "mcpServers": {
    "assimilate": {
      "command": "npx",
      "args": ["-y", "assimilate-mcp", "--port=9090"]
    }
  }
}
```

## Tools (88)

| Category | Count | Key Tools |
|----------|:-----:|-----------|
| **System** | 8 | `get_system` `check_connection` `list_users` `select_user` |
| **Projects** | 7 | `list_projects` `enter_project` `create_project` |
| **Groups** | 9 | `list_groups` `get_current_group` `create_group` |
| **Constructs** | 10 | `list_constructs` `create_construct` `enter_construct` |
| **Slots** | 5 | `list_slots` `get_slot` `set_slot` `create_slot` |
| **Versions** | 5 | `list_versions` `get_version` `set_version` |
| **Shots** | 7 | `get_shot` `set_shot` `create_shot` `import_media` |
| **Inputs** | 4 | `get_inputs` `get_input` `set_input` |
| **Color Grading** | 5 | `get_grade` `set_grade` `get_framing` `set_framing` |
| **Player** | 8 | `enter_timeline` `set_playmode` `enter_shot` `exit_player` |
| **Render** | 10 | `start_render` `stop_render` `get_render_status` |
| **Outputs** | 6 | `list_outputs` `create_output` `set_output` |
| **Snapshots** | 2 | `render_snapshot` `get_shot_metadata` |
| **Files** | 2 | `list_directory` `find_media` |

## Usage Examples

Talk to your AI assistant in natural language:

- *"What projects are available?"*
- *"Import the ARRIRAW files from /Volumes/Shuttle/Day_14"*
- *"Warm up the gamma on this shot"*
- *"Set up ProRes 4444 output and render the timeline"*
- *"Take a snapshot of this frame"*

### MCPorter CLI

```bash
mcporter call assimilate.check_connection
mcporter call assimilate.list_projects
mcporter call 'assimilate.enter_project(name: "Commercial_Nike_Q3")'
mcporter call assimilate.get_grade
```

## Remote Access

Live FX accepts connections on localhost by default. For remote machines, use an SSH tunnel:

```bash
ssh -f -N -L 8080:127.0.0.1:8080 user@livefx-host
```

## Links

- [GitHub](https://github.com/amac-roguelabs/assimilate-mcp)
- [npm](https://www.npmjs.com/package/assimilate-mcp)
- [Assimilate REST API](https://github.com/Assimilate-Inc/Assimilate-REST)
- [Assimilate Inc](https://assimilateinc.com)
