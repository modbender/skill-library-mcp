# Session State Tracker

Robust state persistence for OpenClaw using lifecycle hooks. Survive compaction and restarts automatically.

## Features

- **Automatic**: Hooks handle state saving and re-anchoring without agent intervention.
- **Schema-validated**: YAML frontmatter with strict types and atomic writes.
- **Local-only**: No external network calls.
- **CLI + Tools**: `session-state` command and `session_state_*` tools for manual control.
- **Zero config** beyond enabling the skill (optional: session indexing for discovery).

---

## Installation

```bash
clawhub install qsmtco/session-state-tracker
```

Or copy the skill to `skills/session-state-tracker/` and enable in `openclaw.json`:

```json
"skills": { "entries": { "session-state-tracker": { "enabled": true } } }
```

Then restart the gateway.

---

## How It Works

1. **Session start** → `session-start` hook injects fresh state summary (<24h old) into context.
2. **During work** → You may manually call `session_state_write` to update state.
3. **Near compaction** → `pre-compaction` hook automatically saves current state (via quick discovery if needed).
4. **After compaction** → `post-compaction` hook injects `[State Anchor]` reminder.
5. **Restart** → Cycle repeats; state persists.

No custom `memoryFlush.prompt` or AGENTS.md rules are needed; hooks are fully automatic.

---

## Tools

- `session_state_read` – read current state
- `session_state_write` – update fields (auto-timestamps, validates)
- `session_state_discover` – rebuild state from session transcripts (requires indexing)

---

## CLI

```bash
session-state show              # Display state
session-state set <key> <value> # Update a field
session-state refresh           # Rediscover from sessions
session-state clear             # Reset
```

---

## File Format

`SESSION_STATE.md` (workspace root):

```markdown
---
project: "my-project"
task: "Current task"
status: "active"          # active | blocked | done | in-progress
last_action: "Latest update"
next_steps:
  - "Step 1"
  - "Step 2"
updated: "2026-02-14T23:20:00.000Z"
---

## Context
Optional freeform notes.
```

---

## Requirements

- OpenClaw >= 2026.2.0 (for plugin hooks)
- Node.js 18+
- Optional: session transcript indexing (`memorySearch.experimental.sessionMemory = true`) for discovery

Runtime dependency: `js-yaml` (installed automatically by clawhub).

---

## Troubleshooting

- Hooks not firing? Verify skill is enabled and `openclaw.plugin.json` is present. Restart gateway.
- Discovery returns empty? Enable session indexing in config and ensure recent conversation exists.
- Write failures? Check workspace permissions; writes are atomic with `.tmp` cleanup.

---

**Set it, forget it, focus on the work.**