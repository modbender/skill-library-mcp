---
name: task-father
description: Generator for file-based task state machines (registry + task folders + lifecycle state + queue files + cron specs/jobs) for long-running work.
---

# task-father

Create and manage durable, file-based task state machines under the OpenClaw workspace.

Target filesystem shape:

- `TASK_REGISTRY.md` (global index)
- `tasks/<task_slug>/`
  - `TASK.md` (front matter + purpose/decisions/blockers/changelog + capabilities)
  - `TODOS.md` (checklist)
  - `scripts/`
  - `crons/`
  - `artifacts/`
  - optional queue-state files (`queue.jsonl`, `done.jsonl`, `failed.jsonl`, `lock.json`)

## Prerequisites

Run on host where OpenClaw is running:

- `python3 --version`
- `openclaw status`
- `openclaw cron --help`

## Configuration (portable)

Skill-local config files:

- Example (shareable): `config.env.example`
- Real machine config: `config.env`

Keys:

- `WORKSPACE_DIR` (default: `/home/miles/.openclaw/workspace`)
- `TASKS_DIR` (default: `tasks`)
- `REGISTRY_FILE` (default: `TASK_REGISTRY.md`)
- `DEFAULT_AGENT_ID` (default: `main`)
- `DEFAULT_CRON_TZ` (default: `America/Indianapolis`)

## Initialization / Installation / Onboarding

### Preferred (chat-first)

Answer in chat:

1) task slug (filesystem-safe)
2) task title
3) task purpose
4) optional skills/plugins/tools expected for this task
5) whether queue files are needed
6) whether a cron job should be created now

Then run:

- `python3 scripts/task_father.py init <slug> --title "..." --purpose "..." --skills "a,b" --plugins "x,y" --tools "read,write,exec"`
- optional queue mode:
  - `python3 scripts/task_father.py enable-queue <slug>`
- optional cron setup:
  - `python3 scripts/task_father.py cron-add <slug> --cron "*/10 * * * *" --message "<worker prompt>" --name "task-<slug>"`

### Optional (terminal)

- `cp config.env.example config.env`
- Edit `config.env`
- Initialize task:
  - `python3 scripts/task_father.py init <slug> --title "..."`

## Lifecycle commands

- Set task status (updates `state.json` + changelog):
  - `python3 scripts/task_father.py set-state <slug> active`
- Append changelog entry:
  - `python3 scripts/task_father.py log <slug> "blocked by API quota"`
- Enable queue files:
  - `python3 scripts/task_father.py enable-queue <slug>`
- Add cron:
  - `python3 scripts/task_father.py cron-add <slug> --cron "*/5 * * * *" --message "..." --name "task-<slug>"`
- Remove cron:
  - `python3 scripts/task_father.py cron-rm <slug> --name "task-<slug>"`

## Task documentation contract

Each task must contain:

1) `TASK.md` with front matter and sections:
- Purpose
- Important Decisions
- Blockers
- Capabilities (skills/plugins/tools)
- Change Log (timestamp + short description)

2) `TODOS.md` with checklist items.

3) If queue-style long processing is used:
- `queue.jsonl`, `done.jsonl`, `failed.jsonl`, `lock.json`.

4) Scripts under:
- `<task_folder>/scripts/`

5) Cron files under:
- `<task_folder>/crons/`

## Reproducibility notes

- Keep machine-specific values in `config.env`, not in `SKILL.md`.
- Keep logs append-only where possible.
- Use small resumable batches for long work.
