---
name: task-specialist
version: 1.1.5
author: OBODA0
homepage: https://github.com/OBODA0/task-specialist-skill
tags: ["task", "management", "sqlite", "workflow", "productivity", "project", "planning", "breakdown", "local", "cli"]
metadata: {"openclaw":{"emoji":"📋","requires":{"bins":["sqlite3","bash"]}}}
description: "A robust, local SQLite-backed task management system designed to elevate your AI agent's project execution. Excellent for both simple tasks and large multi-step projects, managing workflows, and tracking dependencies autonomously without relying on fragile memory."
---

# Task-Specialist

**Local task management with SQLite.** Offline, persistent, zero dependencies beyond `sqlite3` and `bash`.

## Quick Start

```bash
# Install (creates DB only, no PATH changes)
bash install.sh

# Or install AND create easy CLI symlinks in ~/.local/bin
bash install.sh --symlink

# Create and work tasks
task create "Build auth module" --priority=8
task start 1
task-heartbeat 1          # keep-alive ping
task complete 1
```

## Agent Principles

When using the `task-specialist` CLI, follow these principles to ensure high-quality, organized project execution:
- **Decompose First**: Always break large, multi-step requests into smaller, logical subtasks using `task break`.
- **Status Transparency**: Keep task statuses (`start`, `block`, `complete`) updated in real-time so your progress is traceable and accurate.
- **Dependency Management**: Use `task depend` to link tasks that rely on each other, preventing illogical execution order.
- **Document Progress**: Use the `--notes` or `task show` output to keep track of critical information as you move through a project.
## CLI Reference

### Task Lifecycle

```bash
task create "description" [--priority=N] [--parent=ID] [--project=NAME]  # → prints task ID
task start   ID                                          # pending → in_progress
task block   ID "reason"                                 # → blocked (reason in notes)
task complete ID                                         # → done + auto-unblocks dependents
task delete  ID [--force]                                # remove task (--force for parents)
```

**Status flow:** `pending` → `in_progress` → `blocked` → `done`

**Priority:** 1 (low) to 10 (critical). Default: 5.

**Delete:** Refuses if task has subtasks unless `--force` is passed, which cascades the delete to all children and their dependencies.

### Querying

```bash
task list [--status=S] [--parent=ID] [--project=N] [--since=YYYY-MM-DD] [--search="regex"]
task show ID                                # full detail, duration, deps + subtasks
task stuck                                  # in_progress tasks inactive >30min
```

### Subtask Decomposition

```bash
task break PARENT_ID "step 1" "step 2" "step 3"
```

Creates children linked to parent. Auto-chains dependencies: step 2 depends on step 1, step 3 depends on step 2.

### Manual Dependencies

```bash
task depend TASK_ID DEPENDS_ON_ID
```

When starting a task, all dependencies must be `done` or the command is refused with a list of blockers.

When completing a task, any dependent tasks whose deps are now all satisfied are auto-unblocked (`blocked` → `pending`).

### Heartbeat

```bash
task-heartbeat TASK_ID    # update last_updated timestamp
task-heartbeat            # report stalled tasks (no args)
```

Integrate into long-running scripts:

```bash
while work_in_progress; do
  do_work
  task-heartbeat "$TASK_ID"
  sleep 300  # every 5 minutes
done
```

## Schema

```sql
tasks: id, request_text, project, status, priority, parent_id,
       created_at, started_at, completed_at, last_updated, notes

dependencies: task_id, depends_on_task_id (composite PK)
```

## Environment

| Variable | Default | Purpose |
|---|---|---|
| `TASK_DB` | Auto-detected (next to script) | Path to SQLite database |

The DB is auto-located by resolving symlinks back to the real script location. No configuration needed if you used `install.sh`.

## Security

- No `eval()`, no external API calls, no crypto
- Pure SQLite + Bash — passes VirusTotal clean
- **Integer-only validation** on all task IDs via `require_int()` guard before any SQL use
- **Status whitelist**: `task list --status` only accepts `pending`, `in_progress`, `blocked`, `done`
- **Date format enforcement**: `--since` only accepts `YYYY-MM-DD` format via regex check
- **Text inputs** sanitized via single-quote escaping (`sed "s/'/''/g"`)
- **Temp-file SQL delivery**: SQL is written to a temp file and fed to sqlite3 via stdin redirect to avoid all argument-injection vectors
