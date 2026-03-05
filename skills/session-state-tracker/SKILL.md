---
name: session-state-tracker
description: Persistent session state management across compaction and restarts via lifecycle hooks
version: 2.0.0
author: qsmtco
license: MIT
homepage: https://github.com/qsmtco/qrusher/tree/main/skills/session-state-tracker
metadata:
  openclaw:
    requires:
      bins:
        - node
      env: []
    emoji: "🔄"
---

## External Endpoints

This skill does not call any external endpoints. All operations are local to the workspace.

## Security & Privacy

- **Fully local operation**: No network access; all state is stored in `SESSION_STATE.md` within the workspace.
- **File scope**: The skill reads and writes only `SESSION_STATE.md` in the workspace root. No other files are accessed.
- **Session discovery**: The `session_state_discover` tool uses `memory_search`, which may query indexed session transcripts. This is governed by your OpenClaw `memorySearch` configuration (local vector DB). No external API calls are made by the skill itself.
- **No data exfiltration**: Nothing leaves your machine unless you have configured external memory backends separately.

## Model Invocation Note

The skill registers three lifecycle hooks:
- `pre-compaction`: runs automatically before compaction to persist state.
- `post-compaction`: runs automatically after compaction to inject a state reminder.
- `session-start`: runs automatically at session start to load fresh state.

These hooks are triggered by OpenClaw's core; no agent intervention is required. The tools (`session_state_read`, `session_state_write`, `session_state_discover`) are available for manual use when desired.

## Trust Statement

By using this skill, all state management remains local and transparent. The code is open-source and operates solely on your `SESSION_STATE.md` file. Only install if you trust the author and understand the hook automation.

---

## Overview

The Session State Tracker solves context loss during OpenClaw session compaction and restarts by automatically persisting and restoring working state through lifecycle hooks.

### Key Features

- **Automatic state persistence** via OpenClaw hooks (no manual steps during compaction).
- **Schema-validated state file** (`SESSION_STATE.md`) with YAML frontmatter.
- **Atomic writes** to prevent corruption.
- **Discovery tool** to rebuild state from session transcripts if needed.
- **CLI** for manual inspection and updates.
- **Zero external dependencies** beyond Node.js and `js-yaml`.

---

## File Format

`SESSION_STATE.md` (workspace root):

```markdown
---
project: "my-project"
task: "Describe current task"
status: "active"          # active | blocked | done | in-progress
last_action: "Latest update"
next_steps:
  - "Step 1"
  - "Step 2"
updated: "2026-02-14T23:20:00.000Z"
---

## Context
Optional freeform notes, constraints, links, etc.
```

All frontmatter fields are required except `body` (the Context section). Timestamps must be ISO 8601.

---

## Installation

```bash
clawhub install qsmtco/session-state-tracker
```

Or copy the skill folder into `skills/session-state-tracker/` and enable in `openclaw.json`:

```json
"skills": { "entries": { "session-state-tracker": { "enabled": true } } }
```

Then restart the gateway.

---

## Configuration

The skill works out of the box with hooks enabled. Ensure session transcript indexing is active for `session_state_discover` to be effective:

```json
"agents": {
  "defaults": {
    "memorySearch": {
      "sources": ["memory", "sessions"],
      "experimental": { "sessionMemory": true }
    }
  }
}
```

No other configuration required.

---

## Tools

- `session_state_read` – read current state (frontmatter + body)
- `session_state_write` – update fields (auto-timestamps, validates schema)
- `session_state_discover` – synthesize state from recent sessions and write it

---

## CLI

```bash
# Show state
session-state show

# Update a field
session-state set task "New task"
session-state set next_steps '["A","B"]'

# Refresh from session transcripts (requires memory_search)
session-state refresh

# Clear state
session-state clear
```

---

## How It Works

1. **Session start**: `session-start` hook reads `SESSION_STATE.md`; if present and fresh (<24h), injects a summary into the initial system context.
2. **During work**: You may call `session_state_write` to record progress. The file is the single source of truth.
3. **Pre-compaction**: `pre-compaction` hook automatically saves the current state (via discovery if needed) without agent involvement.
4. **Post-compaction**: `post-compaction` hook injects a `[State Anchor]` reminder so the agent re-anchors instantly.
5. **Restart**: The cycle repeats; state persists across restarts.

---

## Migration from v1.x

v2.0.0 introduces lifecycle hooks. No changes to `SESSION_STATE.md` format. To upgrade:
- Install v2.0.0 (or later).
- Ensure the skill is enabled.
- The hooks replace the old `memoryFlush.prompt` convention; you may remove any custom prompt from your config.
- Existing `SESSION_STATE.md` files continue to work unchanged.

---

## Troubleshooting

- Hooks not firing? Verify the skill is enabled and the plugin manifest (`openclaw.plugin.json`) is present. Restart the gateway after installation.
- `session_state_discover` returns empty? Enable session transcript indexing (`memorySearch.experimental.sessionMemory = true`) and ensure recent conversation exists.
- State file not updating? Check file permissions; the skill writes atomically to `SESSION_STATE.md` in the workspace root.

---

**Minimal, reliable, and automatic.**