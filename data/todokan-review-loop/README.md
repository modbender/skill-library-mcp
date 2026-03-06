# Todokan Review Loop Skill

Autonomous review-loop workflow for Todokan boards.

This skill is optimized for recurring bot runs:
- pick tasks in `doing`
- process full comment context
- post a high-quality response comment
- move task to `done` (Review) when appropriate

## Prerequisites

- Todokan API key (`kb_live_...`)
- Todokan MCP configured in OpenClaw (`/mcp` planner endpoint)
- OpenClaw runtime with skill loading enabled

## Local Test (without ClawHub)

```bash
mkdir -p ~/.openclaw/skills
cp -r skills/openclaw/todokan-review-loop ~/.openclaw/skills/todokan-review-loop
```

Then restart OpenClaw.

## Beta Publish (recommended first)

Use a beta slug first, test privately, then publish final slug.

```bash
# from repo root
clawhub login
clawhub publish skills/openclaw/todokan-review-loop --slug todokan-review-loop-beta
```

Install for testing:

```bash
clawhub install todokan-review-loop-beta
```

If beta is good, publish final:

```bash
clawhub publish skills/openclaw/todokan-review-loop --slug todokan-review-loop
```

## Suggested MCP Config

```json
{
  "mcpServers": {
    "todokan": {
      "transport": "streamable-http",
      "url": "https://todokan.com/mcp",
      "headers": {
        "Authorization": "Bearer kb_live_YOUR_API_KEY"
      }
    }
  }
}
```

## Scope Guidance

For this review-loop, planner permissions are typically required because it writes comments and status updates.

Minimum practical scopes:
- `boards:read`
- `tasks:read`
- `tasks:write`
- `comments:read`
- `comments:write`

Optional for extended context:
- `docs:read`

## Notes

- Keep this as a separate skill from the general `todokan` skill.
- Publish silently first (no announcement), verify real bot behavior, then announce.
