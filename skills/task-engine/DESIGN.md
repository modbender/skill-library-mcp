# Task Engine — Design Document

> Multi-agent task orchestration with state machine tracking, heartbeat monitoring, and Discord integration.
> Designed as an OpenClaw skill for Eva (agent coordinator).

---

## 1. Architecture Overview

```
                          ┌──────────────────────────────────────┐
                          │          Human (主人)                 │
                          │  Approves plans, handles escalations  │
                          └──────────┬──────────┬────────────────┘
                                     │ confirm  │ intervene
                     ┌───────────────▼──────────▼───────────────┐
                     │         Eva (Orchestrator)                │
                     │  Plans · Dispatches · Monitors · Tests    │
                     │                                           │
                     │  ┌─────────────────────────────────────┐  │
                     │  │  task_engine.py  (CLI entry point)   │  │
                     │  │  create│status│dispatch│check│done   │  │
                     │  └──────┬──────────────────────────────┘  │
                     │         │                                  │
                     │  ┌──────▼──────────────────────────────┐  │
                     │  │  State Machine Engine                │  │
                     │  │  JSON files in tasks/<id>/           │  │
                     │  │  task.json + subtask_*.json           │  │
                     │  └──────┬──────────────────────────────┘  │
                     └─────────┼──────────────────────────────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
    ┌─────────▼──────┐ ┌──────▼───────┐ ┌──────▼───────┐
    │  Claude Code   │ │  Eva Agent   │ │  Other Agent │
    │  (dev/code)    │ │  (test/val)  │ │  (docs/etc)  │
    │  Multi-instance│ │  Dual-OS     │ │  As needed   │
    └────────┬───────┘ └──────┬───────┘ └──────┬───────┘
             │                │                │
             └────────────────┼────────────────┘
                              │ results
                              ▼
    ┌─────────────────────────────────────────────────────┐
    │  Heartbeat Integration (every 30 min)               │
    │  heartbeat_run.py beat → task_engine.py check       │
    │  Scans all active tasks, updates state, alerts      │
    └──────────────────────────┬──────────────────────────┘
                               │
                               ▼
    ┌─────────────────────────────────────────────────────┐
    │  Discord Integration                                │
    │  Per-task temp channels · Progress updates          │
    │  🚨 Urgent notifications to human                   │
    └─────────────────────────────────────────────────────┘
```

### Data Flow

```
create task → PLANNING
    │
    ├─ Eva writes plan → task.json (plan field)
    ├─ Human approves  → APPROVED
    │
    ├─ dispatch subtasks → subtask_*.json created
    │   ├─ Claude Code gets dev subtasks
    │   ├─ Eva gets test subtasks
    │   └─ Others get misc subtasks
    │
    ├─ heartbeat check (every 30 min)
    │   ├─ read all active task.json + subtask_*.json
    │   ├─ detect stuck/blocked/overdue
    │   ├─ push status to Discord channel
    │   └─ alert human if intervention needed
    │
    └─ all subtasks done → TESTING → REVIEW → COMPLETED
```

---

## 2. File / Directory Structure

```
task-engine/
├── SKILL.md                          # OpenClaw skill definition
├── scripts/
│   ├── task_engine.py                # CLI entry point (main)
│   ├── engine/
│   │   ├── __init__.py
│   │   ├── state_machine.py          # State transitions + validation
│   │   ├── task_store.py             # CRUD for task.json / subtask files
│   │   ├── dispatcher.py             # Agent dispatch logic
│   │   ├── checker.py                # Heartbeat check integration
│   │   ├── discord_ops.py            # Discord channel lifecycle
│   │   └── models.py                 # Pydantic/dataclass schemas
│   └── templates/
│       └── task_template.json        # Default task.json skeleton
├── references/
│   ├── state-transitions.md          # Full state machine reference
│   └── agent-capabilities.md         # Agent roster + capabilities
└── config/
    └── settings.yaml                 # Engine configuration
```

### Runtime Data (outside skill, in workspace)

```
workspace/
└── tasks/
    ├── index.json                    # Task registry (lightweight)
    ├── TASK-001/
    │   ├── task.json                 # Master task state
    │   ├── subtask_01.json           # Subtask: e.g., implement feature X
    │   ├── subtask_02.json           # Subtask: e.g., write tests
    │   ├── subtask_03.json           # Subtask: e.g., update docs
    │   └── log.jsonl                 # Append-only event log
    ├── TASK-002/
    │   └── ...
    └── archive/                      # Completed/failed tasks moved here
        └── TASK-000/
```

---

## 3. State Machine Definition

### Task States

```
                          ┌──────────┐
                     ┌───►│ BLOCKED  │◄────────────────────┐
                     │    └────┬─────┘                     │
                     │         │ unblock                   │ block
                     │         ▼                           │
┌──────────┐  approve ┌──────────┐  start  ┌─────────────┐│
│ PLANNING ├────────►│ APPROVED ├───────►│ IN_PROGRESS ├┤
└────┬─────┘         └──────────┘        └──────┬──────┘│
     │                                          │       │
     │ reject                          all done │       │ fail
     ▼                                          ▼       ▼
┌──────────┐                            ┌──────────┐ ┌──────────┐
│ REJECTED │                            │ TESTING  │ │  FAILED  │
└──────────┘                            └────┬─────┘ └──────────┘
                                             │                ▲
                                     tests pass              │
                                             ▼                │
                                      ┌──────────┐   fail    │
                                      │  REVIEW  ├───────────┘
                                      └────┬─────┘
                                           │ accept
                                           ▼
                                      ┌───────────┐
                                      │ COMPLETED │
                                      └───────────┘
```

### Subtask States

```
PENDING → ASSIGNED → IN_PROGRESS → DONE
                 │            │
                 │            └──► FAILED
                 └──► BLOCKED
```

### Transition Table — Tasks

| From          | To            | Trigger             | Guard / Side-effect                        |
|---------------|---------------|---------------------|--------------------------------------------|
| PLANNING      | APPROVED      | `approve`           | Human confirms plan                        |
| PLANNING      | REJECTED      | `reject`            | Human rejects plan; terminal               |
| APPROVED      | IN_PROGRESS   | `start`             | At least 1 subtask dispatched              |
| IN_PROGRESS   | TESTING       | `test`              | All dev subtasks DONE                      |
| IN_PROGRESS   | BLOCKED       | `block`             | External dependency; record reason         |
| IN_PROGRESS   | FAILED        | `fail`              | Unrecoverable error; record reason         |
| TESTING       | REVIEW        | `review`            | All test subtasks DONE                     |
| TESTING       | IN_PROGRESS   | `reopen`            | Tests failed → back to dev                 |
| TESTING       | FAILED        | `fail`              | Unrecoverable test failure                 |
| REVIEW        | COMPLETED     | `complete`          | Human accepts final result; terminal       |
| REVIEW        | IN_PROGRESS   | `reopen`            | Human requests changes                     |
| REVIEW        | FAILED        | `fail`              | Rejected at review; terminal               |
| BLOCKED       | IN_PROGRESS   | `unblock`           | Blocker resolved                           |
| BLOCKED       | FAILED        | `fail`              | Blocker unresolvable                       |

Terminal states: `COMPLETED`, `FAILED`, `REJECTED`.

### Transition Table — Subtasks

| From         | To            | Trigger        | Guard / Side-effect                    |
|--------------|---------------|----------------|----------------------------------------|
| PENDING      | ASSIGNED      | `assign`       | Agent identified, dispatch instruction |
| ASSIGNED     | IN_PROGRESS   | `start`        | Agent acknowledges work begun          |
| IN_PROGRESS  | DONE          | `done`         | Agent reports completion + result      |
| IN_PROGRESS  | FAILED        | `fail`         | Agent reports failure + reason         |
| IN_PROGRESS  | BLOCKED       | `block`        | Dependency unmet; record reason        |
| ASSIGNED     | BLOCKED       | `block`        | Pre-start blocker discovered           |
| BLOCKED      | ASSIGNED      | `unblock`      | Blocker resolved; re-queue             |

---

## 4. JSON Schemas

### 4a. `index.json` — Task Registry

Lightweight file scanned by heartbeat to find active tasks without reading every task directory.

```json
{
  "version": 1,
  "tasks": [
    {
      "id": "TASK-001",
      "title": "Implement user auth system",
      "status": "IN_PROGRESS",
      "priority": "P0",
      "created": "2026-02-28T10:00:00",
      "discord_channel_id": "1234567890",
      "subtask_count": 3,
      "subtasks_done": 1
    }
  ]
}
```

### 4b. `task.json` — Master Task State

```json
{
  "$schema": "task-engine/task.v1",
  "id": "TASK-001",
  "title": "Implement user auth system",
  "description": "Add JWT-based auth with login/register/refresh endpoints",
  "priority": "P0",
  "status": "IN_PROGRESS",
  "created": "2026-02-28T10:00:00",
  "updated": "2026-02-28T14:30:00",

  "plan": {
    "summary": "3-phase implementation: models → API → tests",
    "approach": "JWT with refresh tokens, bcrypt password hashing",
    "approved_by": "human",
    "approved_at": "2026-02-28T10:30:00"
  },

  "subtasks": ["subtask_01", "subtask_02", "subtask_03"],

  "discord": {
    "channel_id": "1234567890",
    "channel_name": "task-001-auth",
    "created_at": "2026-02-28T10:00:00"
  },

  "timeline": {
    "eta": "2026-03-02",
    "started_at": "2026-02-28T11:00:00",
    "completed_at": null
  },

  "history": [
    {
      "time": "2026-02-28T10:00:00",
      "event": "created",
      "from_status": null,
      "to_status": "PLANNING",
      "actor": "eva",
      "note": "Task created from user request"
    },
    {
      "time": "2026-02-28T10:30:00",
      "event": "transition",
      "from_status": "PLANNING",
      "to_status": "APPROVED",
      "actor": "human",
      "note": "Plan approved"
    }
  ],

  "metadata": {
    "source_session": "eva-session-abc123",
    "tags": ["backend", "security"],
    "blocked_reason": null
  }
}
```

### 4c. `subtask_*.json` — Subtask State

```json
{
  "$schema": "task-engine/subtask.v1",
  "id": "subtask_01",
  "parent_task": "TASK-001",
  "title": "Implement auth models and JWT utils",
  "description": "Create User model, JWT token generation/validation, password hashing",
  "type": "dev",
  "status": "IN_PROGRESS",
  "priority": "P0",

  "assignment": {
    "agent": "claude-code",
    "instance_id": "cc-session-xyz",
    "assigned_at": "2026-02-28T11:00:00",
    "dispatch_context": "Project root: /home/user/project. Branch: feature/auth. See task plan for architecture decisions."
  },

  "dependencies": [],
  "blocked_by": [],

  "progress": {
    "percent": 75,
    "last_update": "2026-02-28T14:00:00",
    "checkpoint": "Models done, JWT utils 75% complete"
  },

  "result": {
    "status": null,
    "summary": null,
    "artifacts": [],
    "error": null
  },

  "history": [
    {
      "time": "2026-02-28T11:00:00",
      "event": "assigned",
      "actor": "eva",
      "note": "Dispatched to Claude Code"
    },
    {
      "time": "2026-02-28T14:00:00",
      "event": "heartbeat",
      "progress": 75,
      "context": "JWT utils in progress"
    }
  ]
}
```

### 4d. `log.jsonl` — Append-Only Event Log

One JSON object per line. Never modified, only appended. Useful for debugging and audit.

```jsonl
{"time":"2026-02-28T10:00:00","event":"task.created","task":"TASK-001","actor":"eva"}
{"time":"2026-02-28T10:30:00","event":"task.approved","task":"TASK-001","actor":"human"}
{"time":"2026-02-28T11:00:00","event":"subtask.dispatched","task":"TASK-001","subtask":"subtask_01","agent":"claude-code"}
{"time":"2026-02-28T14:00:00","event":"heartbeat.check","task":"TASK-001","status":"IN_PROGRESS","subtasks_done":"1/3"}
```

---

## 5. Python CLI Interface

### Entry Point: `task_engine.py`

```
Usage:
    python task_engine.py create <title> [--priority P0|P1|P2] [--plan <text>]
    python task_engine.py status [<task-id>] [--all] [--json]
    python task_engine.py dispatch <task-id> <subtask-title> --agent <agent> [--deps <ids>]
    python task_engine.py check [<task-id>] [--quiet]
    python task_engine.py transition <task-id> <event> [--note <text>]
    python task_engine.py subtask <task-id> <subtask-id> <event> [--note <text>] [--progress <n>]
    python task_engine.py archive <task-id>
```

### Subcommands

#### `create` — Create a new task

```bash
python task_engine.py create "Implement user auth" --priority P0 --plan "JWT + bcrypt, 3 phases"
```

- Generates next `TASK-NNN` id from `index.json`
- Creates `tasks/TASK-NNN/` directory with `task.json` + empty `log.jsonl`
- Initial status: `PLANNING`
- Creates Discord channel (if enabled)
- Appends to `index.json`
- Returns: task id

#### `status` — View task status

```bash
python task_engine.py status                    # Summary of all active tasks
python task_engine.py status TASK-001           # Detailed view of one task
python task_engine.py status --all              # Include archived/terminal
python task_engine.py status TASK-001 --json    # Machine-readable output
```

- Reads `index.json` for listing, `task.json` for detail
- Shows: status, subtask progress, ETA, last activity, blocked reasons
- Designed for minimal token burn (Eva can call this cheaply)

#### `dispatch` — Create and assign a subtask

```bash
python task_engine.py dispatch TASK-001 "Implement auth models" \
    --agent claude-code \
    --type dev \
    --deps subtask_00 \
    --context "Branch: feature/auth, see plan for schema"
```

- Creates `subtask_NN.json` in the task directory
- Updates `task.json` subtasks array
- If task is `APPROVED`, auto-transitions to `IN_PROGRESS`
- Logs dispatch event

#### `check` — Heartbeat-triggered state check

```bash
python task_engine.py check                     # Check all active tasks
python task_engine.py check TASK-001            # Check specific task
python task_engine.py check --quiet             # Minimal output (for cron)
```

- Scans `index.json` for non-terminal tasks
- For each active task:
  - Read `task.json` + all `subtask_*.json`
  - Detect stuck subtasks (no progress across N heartbeats)
  - Detect overdue tasks (past ETA)
  - Detect blocked chains (subtask blocked → parent may need intervention)
  - Auto-transition if all subtasks of a phase are done
- Push summary to Discord channel
- Return alerts list (consumed by heartbeat_run.py)

#### `transition` — Manually advance task state

```bash
python task_engine.py transition TASK-001 approve --note "Plan looks good"
python task_engine.py transition TASK-001 block --note "Waiting on API key from vendor"
python task_engine.py transition TASK-001 complete --note "All verified"
```

- Validates transition against state machine rules
- Records in history array and log.jsonl
- Updates `index.json` status cache
- Posts to Discord channel

#### `subtask` — Update subtask state

```bash
python task_engine.py subtask TASK-001 subtask_01 done --note "Models complete"
python task_engine.py subtask TASK-001 subtask_02 start --progress 10
python task_engine.py subtask TASK-001 subtask_01 fail --note "Schema incompatible"
```

- Validates subtask transition
- Updates progress and history
- Checks if parent task should auto-transition (e.g., all dev subtasks done → TESTING)

#### `archive` — Move completed task to archive

```bash
python task_engine.py archive TASK-001
```

- Only works on terminal-state tasks (COMPLETED, FAILED, REJECTED)
- Moves directory to `tasks/archive/`
- Removes from `index.json`
- Archives Discord channel (if enabled)

### CLI Architecture (mirrors heartbeat_run.py pattern)

```python
#!/usr/bin/env python3
"""task_engine.py — Task orchestration CLI"""

import sys, os, json, logging, logging.handlers
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
TASKS_DIR = PROJECT_ROOT / "workspace" / "tasks"
LOG_DIR = PROJECT_ROOT / "logs"

def setup_logging(): ...     # Same pattern as heartbeat_run.py
def acquire_lock(): ...      # File lock on .task_engine.lock (Windows: msvcrt)

def cmd_create(args): ...
def cmd_status(args): ...
def cmd_dispatch(args): ...
def cmd_check(args): ...
def cmd_transition(args): ...
def cmd_subtask(args): ...
def cmd_archive(args): ...

def main():
    setup_logging()
    # argparse with subcommands
    parser = argparse.ArgumentParser(prog="task_engine")
    sub = parser.add_subparsers(dest="command")
    # ... register subcommands ...
    args = parser.parse_args()
    # dispatch to cmd_* functions

if __name__ == "__main__":
    main()
```

Platform note: `fcntl` (used in heartbeat_run.py) is Unix-only. Task engine uses `msvcrt` on Windows, `fcntl` on Unix, with a platform-switch wrapper.

---

## 6. Heartbeat Integration Design

### Integration Point

The heartbeat manager's `cmd_beat()` already checks `ongoing.json` at step 3/4. The task engine hooks in at the same phase.

```
heartbeat_run.py beat
    │
    ├── [1-4] existing checks (daily, todo, ongoing, timeout analysis)
    │
    ├── [4.3] NEW: Task Engine check              ◄── integration point
    │   │
    │   ├── python task_engine.py check --quiet
    │   │   ├── scan index.json (< 1KB read)
    │   │   ├── for each active task: read task.json + subtasks
    │   │   ├── run stuck/overdue/blocked detection
    │   │   ├── auto-transition if conditions met
    │   │   ├── push Discord updates
    │   │   └── return: {alerts: [...], summary: {...}}
    │   │
    │   └── merge alerts into heartbeat alerts list
    │
    ├── [5-9] remaining checks (mail, cleanup, git, health, MASTER)
    └── done
```

### Integration in heartbeat_run.py

Add to `cmd_beat()` after the ongoing.json check (step 4):

```python
# 4.3 Task Engine check
logger.info("[4.3/8] Task Engine check")
try:
    from engine.checker import check_all_tasks
    te_result = check_all_tasks()
    if te_result.get("alerts"):
        alerts.extend(te_result["alerts"])
        all_ok = False
    if te_result.get("summary"):
        logger.info("  Tasks: %s", te_result["summary"])
except ImportError:
    logger.debug("  Task engine not installed, skipping")
except Exception as e:
    logger.warning("  Task engine check failed: %s", e)
```

### Token Efficiency Strategy

The heartbeat fires every 30 minutes. Each check must be cheap:

| Operation | Cost | Strategy |
|-----------|------|----------|
| Read `index.json` | ~50 tokens | Single small file, only active task ids+status |
| Skip terminal tasks | 0 | `index.json` has status; skip COMPLETED/FAILED/REJECTED |
| Read active task.json | ~200 tokens/task | Only read if index shows active |
| Stuck detection | ~50 tokens/task | Compare last 2 history entries (progress delta) |
| Discord push | 0 tokens | HTTP call, not LLM |
| Total per heartbeat | ~300-500 tokens | For 1-3 active tasks |

### Stuck Detection (reuses heartbeat pattern)

```python
def detect_stuck(subtask: dict, config: dict) -> str:
    """
    Analyze subtask for stuck state.
    Returns: "normal" | "slow" | "stuck"

    Uses same logic as heartbeat's task_analyzer:
    - Get last N heartbeat entries from history
    - Calculate progress_delta (first vs last)
    - Check if context changed
    - If delta == 0 and no context change across stale_beats → stuck
    """
    history = [h for h in subtask.get("history", []) if h.get("event") == "heartbeat"]
    recent = history[-config.get("stale_beats", 3):]
    if len(recent) < 2:
        return "normal"

    delta = recent[-1].get("progress", 0) - recent[0].get("progress", 0)
    context_changed = recent[-1].get("context") != recent[0].get("context")

    if delta == 0 and not context_changed:
        return "stuck"

    # Check ETA
    eta = subtask.get("assignment", {}).get("eta")
    if eta and datetime.now().isoformat() > eta and delta < config.get("progress_threshold", 5):
        return "slow"

    return "normal"
```

### Auto-Transition Rules (checked every heartbeat)

| Condition | Action |
|-----------|--------|
| All `type: "dev"` subtasks DONE | Transition task → `TESTING` |
| All `type: "test"` subtasks DONE | Transition task → `REVIEW` |
| Any subtask FAILED | Alert human, suggest `block` or `fail` |
| Any subtask stuck for 3+ beats | Alert human via Discord |
| Task ETA passed, still IN_PROGRESS | Alert as overdue |

---

## 7. Discord Channel Management

### Channel Lifecycle

```
Task created (PLANNING)
    │
    ├── Create temp channel: #task-NNN-<slug>
    │   Category: "🏗️ Active Tasks"
    │   Topic: "TASK-NNN: <title> | Status: PLANNING | Priority: P0"
    │
    ├── Pin initial plan message
    │
    ├── Post status updates (heartbeat + transitions)
    │
    ├── Task reaches terminal state
    │   ├── Post completion summary
    │   ├── Move to "📦 Archived Tasks" category
    │   └── OR delete channel (configurable)
    │
    └── Done
```

### Discord Operations (via `message` tool)

All Discord operations use the OpenClaw `message` tool with `channel: "discord"`. The task engine's `discord_ops.py` builds the payloads.

#### Create Task Channel

```python
def create_task_channel(task_id: str, title: str, guild_id: str, category_id: str) -> str:
    """Create a Discord channel for a task. Returns channel_id."""
    slug = title.lower().replace(" ", "-")[:20]
    channel_name = f"task-{task_id[-3:]}-{slug}"

    # Via message tool:
    return {
        "action": "channel-create",
        "channel": "discord",
        "guildId": guild_id,
        "channelName": channel_name,
        "parentId": category_id,       # "Active Tasks" category
        "topic": f"{task_id}: {title} | Status: PLANNING"
    }
```

#### Post Status Update

```python
def post_status_update(channel_id: str, task: dict, subtasks: list) -> dict:
    """Post a heartbeat status update to the task's Discord channel."""
    done = sum(1 for s in subtasks if s["status"] == "DONE")
    total = len(subtasks)
    status = task["status"]

    # Status emoji
    emoji = {"PLANNING": "📝", "APPROVED": "✅", "IN_PROGRESS": "🔨",
             "TESTING": "🧪", "REVIEW": "👀", "COMPLETED": "🎉",
             "FAILED": "❌", "BLOCKED": "🚧"}

    lines = [
        f"**{emoji.get(status, '❓')} Status Update** `{datetime.now().strftime('%m-%d %H:%M')}`",
        f"State: **{status}** · Subtasks: {done}/{total}",
    ]

    for s in subtasks:
        s_emoji = "✅" if s["status"] == "DONE" else "🔨" if s["status"] == "IN_PROGRESS" else "⏳"
        agent = s.get("assignment", {}).get("agent", "unassigned")
        progress = s.get("progress", {}).get("percent", 0)
        lines.append(f"  {s_emoji} `{s['id']}` {s['title'][:30]} ({agent}, {progress}%)")

    return {
        "action": "send",
        "channel": "discord",
        "to": f"channel:{channel_id}",
        "message": "\n".join(lines),
        "silent": True
    }
```

#### Urgent Notification

```python
def send_urgent_alert(channel_id: str, human_user_id: str, alert: str) -> dict:
    """Send an urgent alert that pings the human."""
    return {
        "action": "send",
        "channel": "discord",
        "to": f"channel:{channel_id}",
        "message": f"🚨 **Needs Attention** <@{human_user_id}>\n{alert}"
        # No silent flag — this should notify
    }
```

#### Archive Channel

```python
def archive_task_channel(channel_id: str, archive_category_id: str) -> dict:
    """Move channel to archive category."""
    return {
        "action": "channel-edit",
        "channel": "discord",
        "channelId": channel_id,
        "parentId": archive_category_id,
        "name_prefix": "archived-"
    }
```

### Discord Configuration

In `config/settings.yaml`:

```yaml
discord:
  enabled: true
  guild_id: "YOUR_GUILD_ID"
  active_category_id: "CATEGORY_ID_FOR_ACTIVE"
  archive_category_id: "CATEGORY_ID_FOR_ARCHIVE"
  human_user_id: "YOUR_DISCORD_USER_ID"

  notifications:
    heartbeat_updates: true       # Post status on every heartbeat
    transitions: true             # Post on state transitions
    urgent_ping: true             # @mention human on stuck/blocked/failed
    completion_summary: true      # Post summary on task completion
```

---

## 8. Agent Dispatch Protocol

### Agent Roster

| Agent | Capabilities | Dispatch For | Concurrency |
|-------|-------------|--------------|-------------|
| **Claude Code** | Code, refactor, implement, debug | `type: "dev"` subtasks | Multi-instance parallel |
| **Eva** | Test, validate, system ops, dual-OS | `type: "test"`, `type: "validate"` | Single (orchestrator) |
| **Other agents** | Docs, design, research | `type: "docs"`, `type: "misc"` | As available |

### Dispatch Flow

```
Eva decides to dispatch subtask
    │
    ├── 1. Create subtask_NN.json (status: PENDING)
    │
    ├── 2. Select agent based on subtask type
    │       dev → Claude Code
    │       test → Eva (self)
    │       docs → best available
    │
    ├── 3. Build dispatch context
    │       ├── Task plan summary
    │       ├── Relevant file paths
    │       ├── Branch/workspace info
    │       ├── Dependencies (what must be done first)
    │       └── Acceptance criteria
    │
    ├── 4. Assign (status: ASSIGNED)
    │       ├── Record agent + instance_id in subtask
    │       ├── Post to Discord: "Dispatched subtask_01 → Claude Code"
    │       └── Log event
    │
    ├── 5. Agent works...
    │       ├── Agent updates progress via:
    │       │   python task_engine.py subtask TASK-001 subtask_01 start --progress 30
    │       │   python task_engine.py subtask TASK-001 subtask_01 done --note "Complete"
    │       └── Or: Eva polls / heartbeat detects completion
    │
    └── 6. Subtask completes
            ├── Record result in subtask.json
            ├── Check auto-transition rules
            └── Post to Discord
```

### Dispatch Context Template

When dispatching to Claude Code, the context includes:

```json
{
  "task_id": "TASK-001",
  "subtask_id": "subtask_01",
  "title": "Implement auth models",
  "description": "Create User model with email/password, JWT token generation (access + refresh), bcrypt password hashing utility.",
  "acceptance_criteria": [
    "User model with email, hashed_password, created_at fields",
    "JWT access token (15 min) and refresh token (7 day) generation",
    "Password hash/verify functions using bcrypt",
    "Unit tests for all utilities"
  ],
  "workspace": {
    "project_root": "/home/user/project",
    "branch": "feature/auth",
    "relevant_files": ["src/models/", "src/utils/", "tests/"]
  },
  "constraints": [
    "Use existing SQLAlchemy base from src/db.py",
    "Follow project's existing test patterns in tests/"
  ],
  "report_progress_via": "python task_engine.py subtask TASK-001 subtask_01"
}
```

### Parallel Dispatch

For independent subtasks, dispatch multiple Claude Code instances:

```bash
# Dispatch 3 independent subtasks simultaneously
python task_engine.py dispatch TASK-001 "Implement auth models" --agent claude-code --type dev
python task_engine.py dispatch TASK-001 "Implement auth middleware" --agent claude-code --type dev
python task_engine.py dispatch TASK-001 "Implement auth endpoints" --agent claude-code --type dev --deps subtask_01,subtask_02
```

Subtask 3 depends on 1 and 2, so it will be `BLOCKED` until they complete. Subtasks 1 and 2 run in parallel.

### Agent Progress Reporting

Agents report progress in two ways:

1. **Active reporting**: Agent calls `task_engine.py subtask` CLI directly
2. **Passive detection**: Heartbeat checks for signs of progress:
   - Git commits on the task branch
   - File modifications in relevant directories
   - Agent session still alive

---

## 9. Error Handling

### Error Categories and Responses

| Category | Example | Detection | Response |
|----------|---------|-----------|----------|
| **Agent crash** | Claude Code session dies | Heartbeat: no progress, session gone | Alert human, offer re-dispatch |
| **Subtask stuck** | No progress for 3+ heartbeats | Heartbeat: progress_delta == 0 | Discord alert → human decides |
| **Task overdue** | Past ETA | Heartbeat: datetime check | Discord warning, adjust ETA |
| **Dependency deadlock** | Circular subtask deps | Dispatch-time validation | Reject dispatch, show cycle |
| **State violation** | Invalid transition | State machine guard | Return error, log, no change |
| **File corruption** | Invalid JSON in task.json | JSON parse error | Log error, skip task, alert |
| **Discord failure** | API timeout | HTTP error | Log warning, continue (non-fatal) |
| **Concurrent write** | Two agents update same file | File lock (platform-specific) | Retry with backoff, then fail |

### Resilience Principles

1. **JSON files are source of truth** — Agent restarts don't lose state. Any agent can pick up where another left off by reading the JSON files.

2. **Append-only log** — `log.jsonl` is never modified, only appended. Even if `task.json` gets corrupted, the event log preserves the full history.

3. **Idempotent checks** — `task_engine.py check` can be called any number of times safely. It reads state, applies rules, writes changes atomically.

4. **Atomic writes** — All JSON updates use write-to-temp-then-rename pattern (same as heartbeat's `checker.py`):

```python
def atomic_write(path: Path, data: dict):
    """Write JSON atomically (temp file + rename)."""
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.rename(path)  # atomic on same filesystem
```

5. **Graceful degradation** — Discord failures don't block task progress. Missing subtask files are logged and skipped, not fatal.

6. **Lock scope** — File lock is per-task (not global) to allow concurrent operations on different tasks:

```python
LOCK_DIR = TASKS_DIR / ".locks"

def acquire_task_lock(task_id: str):
    """Per-task file lock."""
    LOCK_DIR.mkdir(exist_ok=True)
    lock_path = LOCK_DIR / f"{task_id}.lock"
    # platform-specific: fcntl on Unix, msvcrt on Windows
    ...
```

### Recovery Procedures

| Situation | Automated Recovery | Manual Recovery |
|-----------|-------------------|-----------------|
| Corrupted `index.json` | Rebuild from `tasks/*/task.json` | `task_engine.py rebuild-index` |
| Orphaned subtask | Heartbeat detects, marks FAILED | Re-dispatch to new agent |
| Stuck for 6+ heartbeats | Auto-mark BLOCKED, alert human | Human decides: retry, reassign, or cancel |
| All subtasks done but task not transitioned | Auto-transition on next check | `task_engine.py transition TASK-001 test` |

---

## 10. Implementation Plan

### Phase 0: Foundation (Day 1)

**Goal**: Core data model and CLI skeleton that can create/read tasks.

- [ ] Create skill directory structure (`task-engine/`)
- [ ] Implement `models.py` — Task and Subtask dataclasses/schemas
- [ ] Implement `task_store.py` — CRUD operations for JSON files
  - `create_task()`, `read_task()`, `update_task()`, `list_tasks()`
  - `create_subtask()`, `read_subtask()`, `update_subtask()`
  - Atomic write helper
  - Index management
- [ ] Implement `state_machine.py` — Transition validation
  - Transition tables (task + subtask)
  - `validate_transition(current, event) → new_state`
  - `apply_transition()` with history recording
- [ ] Implement CLI skeleton (`task_engine.py`)
  - argparse setup with all subcommands
  - `create` and `status` commands working
  - Platform-aware file locking
- [ ] Write `SKILL.md` frontmatter and basic instructions

**Validation**: `create` a task, `status` shows it, JSON files are correct.

### Phase 1: Dispatch + Transitions (Day 2)

**Goal**: Full task lifecycle without external integrations.

- [ ] Implement `dispatch` command — subtask creation + assignment
- [ ] Implement `transition` command — manual state changes
- [ ] Implement `subtask` command — subtask state updates
- [ ] Implement auto-transition logic (all subtasks done → next phase)
- [ ] Implement dependency tracking (blocked_by / blocks)
- [ ] Implement `archive` command
- [ ] Add `log.jsonl` append-only event logging

**Validation**: Full lifecycle test: create → approve → dispatch subtasks → complete subtasks → test → review → complete. All JSON files and logs correct.

### Phase 2: Heartbeat Integration (Day 3)

**Goal**: Automated monitoring via heartbeat cycle.

- [ ] Implement `checker.py` — `check_all_tasks()` function
  - Scan index for active tasks
  - Stuck detection per subtask
  - Overdue detection per task
  - Auto-transition evaluation
  - Return alerts list
- [ ] Implement `check` CLI command
- [ ] Add heartbeat hook in `heartbeat_run.py` (step 4.3)
- [ ] Token-efficient design validation (measure actual token cost)

**Validation**: Create a task with subtasks, run `heartbeat_run.py beat`, verify task engine check runs and produces correct alerts.

### Phase 3: Discord Integration (Day 4)

**Goal**: Real-time Discord notifications and channel management.

- [ ] Implement `discord_ops.py`
  - `create_task_channel()`
  - `post_status_update()`
  - `send_urgent_alert()`
  - `archive_task_channel()`
- [ ] Hook Discord ops into task lifecycle:
  - Channel creation on `create`
  - Status posts on heartbeat `check`
  - Transition notifications
  - Urgent alerts on stuck/blocked/failed
- [ ] Add Discord config to `settings.yaml`
- [ ] Test with real Discord server

**Validation**: Create task → verify channel created. Run heartbeat → verify status posted. Trigger stuck → verify ping sent.

### Phase 4: Multi-Agent Dispatch (Day 5)

**Goal**: Dispatching work to Claude Code and other agents.

- [ ] Implement `dispatcher.py`
  - Agent selection logic based on subtask type
  - Dispatch context builder
  - Parallel dispatch support
- [ ] Write `references/agent-capabilities.md`
- [ ] Implement progress polling for agents that can't self-report
- [ ] Test multi-agent scenario: Claude Code dev + Eva test
- [ ] Write `references/state-transitions.md` (full reference)

**Validation**: Dispatch dev subtask to Claude Code, test subtask to Eva. Verify both progress correctly through lifecycle.

### Phase 5: Polish + Production (Day 6)

**Goal**: Production readiness.

- [ ] Write comprehensive `SKILL.md` body with usage instructions
- [ ] Add `--json` output mode to all CLI commands (for programmatic use)
- [ ] Implement `rebuild-index` recovery command
- [ ] Error handling hardening (all edge cases from Section 9)
- [ ] Add pytest test suite (follow heartbeat's test structure)
  - `test_state_machine.py` — all transitions valid/invalid
  - `test_task_store.py` — CRUD + atomic writes
  - `test_checker.py` — stuck/overdue/auto-transition detection
  - `test_discord_ops.py` — payload construction
- [ ] Performance test: 10 concurrent tasks, heartbeat completes in < 5s
- [ ] Package skill with `package_skill.py`

**Validation**: Full end-to-end test with real agents, Discord, and heartbeat. All pytest tests pass.

---

## Appendix A: Configuration Reference

### `config/settings.yaml`

```yaml
# Task Engine Configuration

tasks:
  workspace_dir: "workspace/tasks"      # Relative to skill root
  id_prefix: "TASK"                      # Task ID prefix
  max_active: 10                         # Max concurrent active tasks
  auto_archive_days: 7                   # Archive completed tasks after N days

heartbeat:
  enabled: true
  stale_beats: 3                         # Heartbeats with 0 progress → stuck
  progress_threshold: 5                  # Minimum progress delta to not be "slow"
  auto_transition: true                  # Auto-advance task state when conditions met

discord:
  enabled: true
  guild_id: ""
  active_category_id: ""
  archive_category_id: ""
  human_user_id: ""
  notifications:
    heartbeat_updates: true
    transitions: true
    urgent_ping: true
    completion_summary: true

agents:
  claude_code:
    enabled: true
    max_parallel: 3                      # Max concurrent Claude Code instances
  eva:
    enabled: true
    subtask_types: ["test", "validate"]
```

### Environment Variables (`config/.env`)

```env
# Discord bot token (or read from openclaw.json)
DISCORD_BOT_TOKEN=

# Override workspace path
TASK_ENGINE_WORKSPACE=
```

---

## Appendix B: Integration with Existing Heartbeat ongoing.json

The task engine is **independent** from the heartbeat's `ongoing.json`. Rationale:

- `ongoing.json` tracks simple human-facing tasks (thesis, projects) with basic WIP/WAIT/DONE states
- Task engine tracks agent-orchestrated tasks with rich subtask trees, dispatch records, and multi-agent coordination
- Different state models (3 states vs 8 states)
- Different update patterns (human-driven vs agent-driven)

However, the heartbeat's health score can incorporate task engine status:

```python
# In health_score.py calculate_score(), add task engine dimension:
task_engine_score = 0
if te_result:
    active = te_result.get("active_count", 0)
    stuck = te_result.get("stuck_count", 0)
    if active == 0:
        task_engine_score = 10  # neutral
    elif stuck == 0:
        task_engine_score = 15  # healthy
    else:
        task_engine_score = max(0, 15 - stuck * 5)  # penalty per stuck task
```

---

## Appendix C: SKILL.md Frontmatter

```yaml
---
name: task-engine
description: "Multi-agent task orchestration engine. Creates tasks with state machine tracking (PLANNING→APPROVED→IN_PROGRESS→TESTING→REVIEW→COMPLETED), dispatches subtasks to Claude Code (dev), Eva (test), or other agents, monitors progress via heartbeat integration, and provides real-time Discord updates. Use when: (1) Complex multi-step projects need orchestration, (2) Multiple agents must collaborate on a task, (3) Task progress needs automated monitoring and status tracking."
---
```
