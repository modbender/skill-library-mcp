---
name: duely
description: Track recurring maintenance tasks from the command line. Use when scheduling, checking, and logging periodic tasks like backups, reviews, or any repeating chore. Shows overdue items and keeps an execution log.
metadata:
  openclaw:
    emoji: "🔁"
    os: ["darwin"]
    requires:
      bins: ["duely"]
    install:
      - id: brew
        kind: brew
        formula: halbotley/tap/duely
        bins: ["duely"]
        label: "Install duely (brew)"
---

# duely

A CLI for tracking recurring maintenance tasks. Know what's due, mark it done, and keep a log.

## Why duely?

- **Simple recurring tasks** — No calendar overhead for maintenance chores
- **Overdue alerts** — See what you've been putting off
- **Execution log** — Know when things last ran

## Installation

```bash
brew tap halbotley/tap
brew install duely
```

## Commands

### Add a recurring task

```bash
duely add backups --name "Database backups" --every 1d
duely add vault-review --name "Vault review" --every 3d
duely add oil-change --name "Oil change" --every 90d --start 2025-06-01
```

Intervals: `12h`, `1d`, `3d`, `1w`, `30d`, `90d`, etc.

### List all tasks

```bash
duely list
```

### Show tasks that are due now

```bash
duely due
```

Shows overdue tasks with ⚠️ warnings.

### Mark a task as done

```bash
duely run backups
duely run backups --notes "Full backup completed"
```

### Skip a task (reschedule without running)

```bash
duely skip vault-review
duely skip vault-review --reason "On vacation"
```

### View execution log

```bash
duely log
```

### Remove a task

```bash
duely remove old-task
```

## Agent Integration

duely works well with agent heartbeats or cron-triggered checks:

```bash
# Check for due tasks and act on them
duely due
# After completing the task:
duely run <task-id> --notes "Completed by agent"
```

## Notes

- Task IDs must be lowercase with no spaces
- `--start` defaults to now if not specified
- `--every` accepts hours (h), days (d), and weeks (w)
- Data stored locally in `~/.duely/`
