# Unitask Agent

Start finishing tasks instead of just organizing them: connect any AI agent to Unitask (unitask.app) to manage and do your tasks with secure prioritization, tags, time blocks and more.

Unitask is now in **public beta**. Anyone can sign up at `https://unitask.app` and create a scoped API token.

## What it does

- Read tasks
- Create/update tasks (including subtasks via `parent_id`)
- Move subtasks between parent tasks
- Merge parent tasks (with preview first)
- Create/edit/delete tags
- Add/remove tags on tasks
- Soft-delete tasks
- Time-block your day (writes `scheduled_start` + `duration_minutes`)

## Setup

1. Sign up at `https://unitask.app` (public beta) if you do not already have an account.
2. In Unitask: `Dashboard -> Settings -> API` create an API token with scopes you need.
3. In your AI app / MCP client config, store token as `UNITASK_API_KEY` (never paste tokens in chat).

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

## Safety

- Use the smallest scope needed.
- Scope guidance: `read` for retrieval, `write` for create/update, `delete` only when required.
- Keep `dry_run=true` first for compound actions (move/merge/timeblock apply).
- Confirm deletes unless user explicitly requested deletion.
