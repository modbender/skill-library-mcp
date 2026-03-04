---
name: task-tracker
description: Proactive task state management. Use on EVERY task start, progress update, completion, or failure. Tracks what was requested, what's running (background processes, SSH sessions), what's done, and what's next. Survives session resets. Triggers automatically — not user-invoked.
---

# Task Tracker

Maintain a live task state file so context survives session resets/compaction.

## State File

`memory/tasks.md` — single source of truth.

## When to Write

1. **Task received** → add entry with status `🔄 进行中`
2. **Background process started** → record session ID, PID, server, command
3. **Progress update** → update status/notes
4. **Task completed** → mark `✅ 完成`, record results/links
5. **Task failed** → mark `❌ 失败`, record error
6. **Session start** → read `memory/tasks.md` to resume awareness

## Format

```markdown
# Active Tasks

## [task-id] Short description
- **Status**: 🔄 进行中 | ✅ 完成 | ❌ 失败 | ⏸️ 暂停
- **Requested**: YYYY-MM-DD HH:MM
- **Updated**: YYYY-MM-DD HH:MM
- **Background**: session-id (PID) on server-name — `command`
- **Notes**: progress details, partial results
- **Result**: final output, links, summary

# Completed (recent)
<!-- Move completed tasks here, keep last 10, prune older -->
```

## Rules

- Update the file BEFORE reporting to user (write-first)
- Include enough detail to resume without prior conversation context
- For background processes: always record session ID + what server + what command
- For multi-step tasks: update after each step
- Keep it concise — this isn't a log, it's a state snapshot
- **Size limit: keep under 50 lines / 2KB** — this file is read every session start
- Completed tasks: collapse to one-line summary, reference daily notes for details
- Prune completed tasks older than 3 days
- If Active is empty, write （无） to make it obvious
