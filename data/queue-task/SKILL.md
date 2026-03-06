---
name: queue-task
description: Durable queue-task helper for resumable, idempotent batch jobs in task-father task folders.
---

# queue-task

Use this skill for durable long-running queue jobs with resumable batches.

Layout (task-father only):

- `<WORKSPACE_DIR>/<TASKS_DIR>/<slug>/...`

State files:
- `queue.jsonl`
- `progress.json`
- `done.jsonl`
- `failed.jsonl`
- `lock.json`

## Prerequisites

- `python3 --version`
- `openclaw status`
- `openclaw cron --help`

## Configuration (portable)

Skill-local config:

- Example: `config.env.example`
- Real machine config: `config.env`

Keys:

- `WORKSPACE_DIR`
- `TASKS_DIR`
- `BATCH_SIZE`
- `LOCK_STALE_MINUTES`
- `CRON_EXPR`
- `CRON_TZ`
- `DELIVERY_MODE`
- `AGENT_ID`

## Initialization / Installation / Onboarding

### Preferred (chat-first)

Provide:
1) task slug
2) batch size
3) lock stale minutes
4) schedule and timezone

Then initialize:

- `python3 scripts/queue_task.py init <slug>`

Smoke test:

- `python3 scripts/queue_task.py status <slug>`

### Optional (terminal)

- `cp config.env.example config.env`
- Edit `config.env`
- Run init/status commands above.

## Commands

- Init files:
  - `python3 scripts/queue_task.py init <slug>`
- Status:
  - `python3 scripts/queue_task.py status <slug>`
- Clear stale lock:
  - `python3 scripts/queue_task.py clear-stale-lock <slug>`
- Print worker template:
  - `python3 scripts/queue_task.py print-supervisor-template`

## Usage notes

- Prefer append-only JSONL logs.
- Process small batches.
- Update `progress.json` after each item.
- Keep idempotency keys task-defined.
- Use lock file to avoid concurrent runs.
