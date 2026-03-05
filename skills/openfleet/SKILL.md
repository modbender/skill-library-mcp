---
name: openfleet
description: "Manage your OpenFleet multi-agent workspace — create tasks, assign agents, trigger pulse cycles, manage automations, and monitor activity. Full bidirectional control over your autonomous agent fleet."
homepage: https://openfleet.sh
metadata:
  openclaw:
    emoji: "\u25C7"
    requires:
      bins:
        - npx
      env:
        - OPENFLEET_API_KEY
    primaryEnv: OPENFLEET_API_KEY
---

# OpenFleet

Autonomous multi-agent orchestration from your terminal. Create tasks, manage agents, trigger work cycles, and monitor everything — without leaving OpenClaw.

## Setup

1. Get your API key from the [OpenFleet Dashboard](https://app.openfleet.sh) → Developer Settings
2. Set the env var:
   ```
   export OPENFLEET_API_KEY=ofk_your_key_here
   ```
3. Install the skill:
   ```
   clawhub install openfleet
   ```

### Quick verify

Ask your agent: *"List my OpenFleet tasks"*

## 20 Available Tools

### Tasks

| Tool | Description |
|------|-------------|
| `openfleet_list_tasks` | List tasks — filter by status, priority, or free-text search |
| `openfleet_create_task` | Create a task (starts in INBOX, auto-assigned to best agent) |
| `openfleet_get_task` | Get full task details by ID |
| `openfleet_update_task` | Update title, description, status, priority, or tags |
| `openfleet_delete_task` | Archive (soft-delete) a task |
| `openfleet_unblock_task` | Unblock a BLOCKED task with resolution context |
| `openfleet_approve_task` | Approve a REVIEW task → moves to DONE |
| `openfleet_add_comment` | Add a comment visible to agents during execution |

### Agents

| Tool | Description |
|------|-------------|
| `openfleet_list_agents` | List all agents with status, health, and token usage |
| `openfleet_get_agent` | Get full agent details by ID |
| `openfleet_create_agent` | Create a new agent (LEAD, SPECIALIST, or INTERN) |

### Automations

| Tool | Description |
|------|-------------|
| `openfleet_list_automations` | List recurring task automations |
| `openfleet_create_automation` | Create a scheduled automation (hourly → monthly) |
| `openfleet_toggle_automation` | Toggle an automation on/off |
| `openfleet_trigger_automation` | Fire an automation immediately |

### System

| Tool | Description |
|------|-------------|
| `openfleet_trigger_pulse` | Trigger an agent work cycle (health check + assignment + execution) |
| `openfleet_get_workspace` | Get workspace info and configuration |
| `openfleet_parse_input` | Parse natural language into a structured task |
| `openfleet_install_template` | Install a workspace template (e.g. saas-startup, content-pipeline) |
| `openfleet_list_activities` | List recent activity feed entries |

## Usage Examples

### Create a task
```
Create an OpenFleet task: "Build a landing page with hero section, pricing table, and contact form" with HIGH priority and tags frontend, react
```

### Check agent status
```
List my OpenFleet agents and show who is working on what
```

### Trigger a pulse
```
Trigger an OpenFleet pulse to assign queued tasks and start agent work
```

### Manage blocked tasks
```
Show me all BLOCKED tasks in OpenFleet and unblock the one about API keys with the message "Key has been added to environment"
```

### Create a recurring automation
```
Create a daily OpenFleet automation called "Morning standup report" that generates a summary task every morning
```

## MCP Server Details

This skill wraps the `@open-fleet/mcp-server` npm package, which exposes a standard MCP stdio server.

**Manual MCP setup** (if not using ClawHub):
```bash
npx @open-fleet/mcp-server setup
```

The setup wizard auto-detects Claude Code, Cursor, and Windsurf and configures MCP automatically.

**Direct npx invocation** (for custom configs):
```bash
OPENFLEET_API_KEY=ofk_xxx npx -y @open-fleet/mcp-server
```

## OpenClaw + OpenFleet Integration

When you connect OpenFleet with an OpenClaw gateway, this skill completes the **bidirectional link**:

| Direction | What it does |
|-----------|-------------|
| **OpenFleet → OpenClaw** | OpenFleet sends tasks to your gateway for execution |
| **OpenClaw → OpenFleet** | This skill lets OpenClaw manage tasks, agents, and pulse |

### Full setup

1. Start your OpenClaw gateway: `openclaw gateway`
2. Expose it: `cloudflared tunnel --url http://localhost:18789`
3. Connect the tunnel URL + token in [OpenFleet Settings](https://app.openfleet.sh)
4. Install this skill: `clawhub install openfleet`

## Resources

- [OpenFleet Dashboard](https://app.openfleet.sh)
- [API Documentation](https://app.openfleet.sh/docs)
- [GitHub](https://github.com/open-fleet)
- [SDK](https://www.npmjs.com/package/@open-fleet/sdk)
