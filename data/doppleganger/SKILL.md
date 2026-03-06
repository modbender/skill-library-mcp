---
name: doppleganger
displayName: Doppleganger
description: Prevents duplicate subagent sessions running the same task. Saves tokens and reduces lag—no more "multiple Spidermen" doing the same work.
version: 1.0.0
---

# Doppleganger

## Description

Prevents duplicate subagent sessions running the same task. Saves tokens and reduces lag—no more "multiple Spidermen" doing the same work.

# Doppleganger

**One task, one agent.** Doppleganger stops duplicate subagent sessions from running the same task. That prevents token overspend, UI lag, and the chaos of five identical "task completed" announcements.


## Usage

- The orchestrator **already runs** a duplicate check before `sessions_spawn` (see delegate rule); Doppleganger is the named skill for that behavior.
- User says: "prevent duplicate agents", "stop dopplegangers", "why are so many agents doing the same thing?"
- You want a single entry point to **check** whether a task is already running before spawning.

```bash
python3 /Users/ghost/.openclaw/workspace/skills/doppleganger/scripts/doppleganger.py check "<task string>" [--json]
python3 /Users/ghost/.openclaw/workspace/skills/doppleganger/scripts/doppleganger.py guard --task "<task>" [--json]
```

**JSON output:**

- `{"duplicate": false, "doppleganger_ok": true}` → safe to spawn.
- `{"duplicate": true, "reason": "running", "sessionId": "...", "key": "...", "doppleganger_ok": true}` → do not spawn; reply that the task is already running.

**Exit codes:** 0 = no duplicate (or check ok). 1 = error. 2 = duplicate detected.


## What it does

- **check** / **guard** — Given a task string (the same one you would pass to `sessions_spawn`), returns whether that task is already running. If yes, the orchestrator must not spawn again.
- Uses the subagent-tracker's `check-duplicate` under the hood (one source of truth for runs/sessions).


## Orchestrator

The delegate rule runs a duplicate check before every `sessions_spawn`; that check can be implemented by calling Doppleganger (or subagent-tracker `check-duplicate`) with the router's task string. If `duplicate: true`, do not call `sessions_spawn`.


## Name

"Doppleganger" = the duplicate agent doing the same thing. One Spiderman is enough.
