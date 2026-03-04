---
name: clawkeeper
description: Tasks and habits that live in a plain markdown file on your machine. Free, private, and claw-native.
metadata: {"openclaw": {"requires": {"bins": ["clawkeeper"], "env": ["CLAWKEEPER_DIR"]}, "primaryEnv": "CLAWKEEPER_DIR", "install": [{"id": "npm", "kind": "node", "package": "clawkeeper", "bins": ["clawkeeper"], "label": "Install via npm"}]}}
---

# ClawKeeper CLI

Manage the user's tasks and habits via the ClawKeeper CLI. All data is stored as markdown at the path set by `CLAWKEEPER_DIR` (defaults to `~/.clawkeeper/`).

```bash
clawkeeper <entity> <command> [--flags]
```

If `CLAWKEEPER_DIR` is set in your environment, the CLI reads and writes data there. This allows multiple agents to share the same task list.

## Tasks

```bash
clawkeeper task list
clawkeeper task add --text "Buy groceries"
clawkeeper task add --text "Buy groceries" --due-date 2026-03-15
clawkeeper task add-subtask --parent-text "Buy groceries" --text "Milk"
clawkeeper task complete --id <id>
clawkeeper task complete --text "Buy groceries"
clawkeeper task uncomplete --id <id>
clawkeeper task edit --text "Old name" --new-text "New name"
clawkeeper task edit --text "Old name" --due-date 2026-04-01
clawkeeper task set-due-date --text "Buy groceries" --due-date 2026-03-15
clawkeeper task set-due-date --text "Buy groceries" --due-date none
clawkeeper task delete --text "Buy groceries"
clawkeeper task add-note --text "Buy groceries" --note "Check prices first"
clawkeeper task edit-note --text "Buy groceries" --note "Check prices first" --new-note "Compare at two stores"
clawkeeper task delete-note --text "Buy groceries" --note "Check prices first"
```

## Habits

```bash
clawkeeper habit list
clawkeeper habit add --text "Meditate" --interval 24
clawkeeper habit edit --text "Meditate" --new-text "Morning meditation" --interval 12
clawkeeper habit delete --text "Meditate"
clawkeeper habit complete --text "Meditate"
clawkeeper habit add-note --text "Meditate" --note "Felt calm today"
clawkeeper habit edit-note --text "Meditate" --note "Felt calm today" --new-note "Felt calm, 10 min session"
clawkeeper habit delete-note --text "Meditate" --note "Felt calm today"
```

## State

```bash
clawkeeper state show
```

## Proactive Checks (Heartbeat)

When running periodic checks, use `clawkeeper state show` to review the user's habits and tasks:

- **Missed habits**: If a habit hasn't been completed for more than 2x its interval, ask about it gently. People forget — a nudge helps more than a lecture.
- **Building streaks**: When a habit's completion count is climbing, acknowledge the momentum briefly.
- **Recent notes**: If the user added reflections or notes recently, reference them for continuity. It shows you're paying attention.
- **Stale tasks**: Tasks sitting open for a long time might need to be broken down, re-prioritized, or dropped.

Tone: supportive collaborator, not drill sergeant. If nothing needs attention, reply `HEARTBEAT_OK`.

## Notes

- All commands return JSON: `{"ok": true, "data": ...}` on success, `{"ok": false, "error": "..."}` on failure.
- IDs are stable across invocations. Use `--id` for precise lookups or `--text` for fuzzy substring matching.
- When adding a task, the response includes the new task's `id` for subsequent operations.
