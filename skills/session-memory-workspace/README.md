# session-memory

OpenClaw skill: write session summaries into daily memory files and search session history so the agent can recall and cite past conversations.

## Features

- **Session → memory**: Run `session-to-memory.js` for a date to generate or update `memory/YYYY-MM-DD.md` with a "Session summary" section. OpenClaw’s memory/citation search will then include that day’s chat.
- **Session search**: Run `session-search.js` with a query (and optional date range) to get JSON snippets from past sessions. Use this to answer “what did we say about X?” or to prepare context.

## Requirements

- Node.js (no extra npm deps)
- Sessions at `~/.openclaw/agents/main/sessions/` (default agent)
- Workspace with `memory/` directory (e.g. `~/.openclaw/workspace/memory/`)

## Usage (agent)

From the workspace root:

```bash
# Summarize 2026-02-27 into memory/2026-02-27.md
node skills/session-memory/scripts/session-to-memory.js --date 2026-02-27 --append

# Search sessions for "discord"
node skills/session-memory/scripts/session-search.js --query "discord" --since 2026-02-26 --limit 10
```

See `SKILL.md` for full usage and when the agent should use this skill.

## Version

1.0.0
