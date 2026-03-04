# Unitask Task Agent

Use Unitask (unitask.app) with AI agents via **hosted MCP** and **scoped API tokens**.

## What it does

- Read tasks
- Create/update tasks (including subtasks via `parent_id`)
- Soft-delete tasks
- Time-block your day (writes `scheduled_start` + `duration_minutes`)

## Setup

1. In Unitask: `Dashboard -> Settings -> API` create an API token with the scopes you want.
2. In your AI app / MCP client config, store the token as `UNITASK_API_KEY` (never paste tokens into chats).

## Hosted MCP endpoint

- URL: `https://unitask.app/api/mcp`
- Header: `Authorization: Bearer <UNITASK_API_KEY>`

## Client configuration examples

### Claude Code (remote HTTP MCP)

Create/edit `~/.claude.json`:

```json
{
  "mcpServers": {
    "unitask": {
      "type": "http",
      "url": "https://unitask.app/api/mcp",
      "headers": {
        "Authorization": "Bearer ${UNITASK_API_KEY}"
      }
    }
  }
}
```

Then set `UNITASK_API_KEY` in your shell environment (or Claude secrets UI, if you use that).

### VS Code (remote HTTP MCP)

Create `.vscode/mcp.json` in your workspace:

```json
{
  "inputs": [
    {
      "id": "unitask_api_key",
      "type": "promptString",
      "description": "Unitask API key",
      "password": true
    }
  ],
  "servers": {
    "unitask": {
      "type": "http",
      "url": "https://unitask.app/api/mcp",
      "headers": {
        "Authorization": "Bearer ${input:unitask_api_key}"
      }
    }
  }
}
```

### Generic (any MCP client that supports HTTP + headers)

- URL: `https://unitask.app/api/mcp`
- Header: `Authorization: Bearer <UNITASK_API_KEY>`

## Safety

- Use the smallest scope needed.
- Preview time-block plans (`apply=false`) before applying.
- Confirm deletes unless the user explicitly requested deletion.
