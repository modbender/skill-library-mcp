---
name: mindgraph-context
description: "Pulls relevant context from mindgraph-server and injects it into the agent's bootstrap files at session start."
metadata: { "openclaw": { "emoji": "🧠", "events": ["agent:bootstrap"], "requires": { "bins": ["node"] } } }
---

# MindGraph Context Hook

At session bootstrap, queries the local mindgraph-server and injects a formatted
context block into the agent's BOOTSTRAP.md file.

## Behavior by session type

**Main session:**
Runs 3 fixed queries — active Goals, non-completed Projects, hard Constraints.
~600 tokens. No task query needed.

**Sub-agent / cron:**
Runs task-specific context query (FTS + semantic via mindgraph-bridge.js) if a
`.mindgraph-task-<id>.tmp` file exists, then appends the same fixed queries.

## What gets injected

```
## MindGraph Context

### 🎯 Active Goals
- **Income Generation** [high] (50%): ...

### 📁 Active Projects
- **Thumos Care** [active]: ...

### 🚫 Hard Constraints (N)
- Do not use em dashes...
```

## Requirements

- `mindgraph-server` must be running at localhost:18790
- `mindgraph-client.js` and `mindgraph-bridge.js` must be in the workspace
- `mindgraph.json` must exist at `~/.openclaw/mindgraph.json`

## Failure mode

If the server is down or unreachable, the hook exits silently — the session
proceeds normally without injected context. Never blocks a session start.
