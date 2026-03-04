---
name: clawctl
description: Coordination layer for OpenClaw agent fleets (tasks, messaging, activity feed, dashboard).
metadata: {"openclaw":{"emoji":"🛰️","requires":{"bins":["clawctl"]}}}
---

# Setup

```bash
clawctl init                        # create the database
export CLAW_AGENT=your-name         # set identity (falls back to $USER with warning)
export CLAW_DB=~/.openclaw/clawctl.db  # optional, this is the default
```

# Operational Rhythm

Follow this pattern every session:

1. `clawctl checkin` — register presence, see unread count
2. `clawctl inbox --unread` — read messages before picking up work
3. `clawctl next` — find highest-priority actionable task (or `clawctl list --mine`)
4. `clawctl claim <id>` then `clawctl start <id>` — take ownership and begin
5. `clawctl msg <agent> "update" --task <id>` — coordinate during work
6. `clawctl done <id> -m "what I did"` then `clawctl next` — complete and move on

Only claim tasks assigned to you or matching your role. Completing an already-done task is a safe no-op.

# Decision Tree

| Situation | Command |
|-----------|---------|
| New task | `clawctl add "Subject" -d "Details"` |
| Find work | `clawctl next` then `clawctl claim <id>` |
| Blocked | `clawctl block <id> --by <blocker-id>` and notify via `clawctl msg` |
| Finished | `clawctl done <id> -m "Result"` |
| Hand off | `clawctl msg <agent> "Ready for you" --task <id> --type handoff` |
| Ready for review | `clawctl review <id>` |
| Catch up | `clawctl feed --last 20` or `clawctl summary` |
| Link artifacts | Add `--meta '{"note":"path/to/file"}'` to `done`, `claim`, `start`, or `block` |

# Task Statuses

```
pending → claimed → in_progress → done
                  ↘ blocked ↗    ↘ cancelled
                  ↘ review  ↗
```

`list` excludes done/cancelled by default. Use `--all` for history (newest first).

# Commands

## Tasks

| Command | Description |
|---------|-------------|
| `add SUBJECT` | Create task. `-d` desc, `-p 0\|1\|2` priority, `--for AGENT` assign, `--parent ID` |
| `list` | Active tasks. `--mine`, `--status STATUS`, `--owner AGENT`, `--all` |
| `next` | Highest-priority actionable task for current agent |
| `claim ID` | Claim task. `--force` overrides ownership, `--meta JSON` |
| `start ID` | Begin work (in_progress). `--meta JSON` |
| `done ID` | Complete. `-m` note, `--force`, `--meta JSON` |
| `review ID` | Mark ready for review. `--meta JSON` |
| `cancel ID` | Cancel task. `--meta JSON` |
| `block ID --by OTHER` | Mark blocked. `--meta JSON` |
| `board` | Kanban board grouped by status |

## Messages

| Command | Description |
|---------|-------------|
| `msg AGENT BODY` | Send message. `--task ID`, `--type TYPE` (comment, status, handoff, question, answer, alert) |
| `broadcast BODY` | Alert all agents |
| `inbox` | Read messages. `--unread` for unread only |

## Fleet

| Command | Description |
|---------|-------------|
| `checkin` | Heartbeat — update presence, report unread count |
| `register NAME` | Register agent. `--role TEXT` |
| `fleet` | All agents with status and current task |
| `whoami` | Identity, role, and DB path |

## Monitoring

| Command | Description |
|---------|-------------|
| `feed` | Activity log. `--last N`, `--agent NAME`, `--meta` |
| `summary` | Fleet overview with counts and recent events |
| `dashboard` | Web UI. `--port INT`, `--stop`, `--verbose` |
