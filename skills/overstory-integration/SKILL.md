---
name: overstory-integration
displayName: overstory Integration
description: Integrates overstory Claude Code agent swarm with nanobot orchestrator. Manages agent lifecycle, SQLite mail bridge, and git worktree coordination.
version: 1.0.0
---

# overstory Integration

## Description

Integrates overstory's Claude Code agent swarm system with the nanobot orchestrator. Provides agent lifecycle management, an inter-agent SQLite mail bridge, and git worktree coordination for parallel agent workstreams.

## Architecture

```
┌──────────────┐       ┌───────────────────┐
│   nanobot     │──────▶│ overstory_wrapper │──▶ overstory CLI (tmux sessions)
│  orchestrator │       └───────────────────┘
│               │       ┌───────────────────┐
│               │──────▶│ agent_lifecycle    │──▶ SQLite (agent_lifecycle.db)
│               │       └───────────────────┘
│               │       ┌───────────────────┐
│               │──────▶│   mail_bridge     │──▶ SQLite (.overstory/mail.db)
└──────────────┘       └───────────────────┘
```

- **overstory_wrapper.py** — Thin wrapper around the `overstory` CLI. Spawns agents via tmux, manages worktrees, installs hooks.
- **agent_lifecycle.py** — Tracks agent state (spawned → running → completed/failed/terminated) in a local SQLite database. Provides async monitoring and cleanup.
- **mail_bridge.py** — Thread-safe message bridge using overstory's native SQLite mail format. Supports direct messages, broadcasts, and threaded conversations.

## Requirements

- Python 3.9+
- `overstory` CLI installed and on PATH (or set `OVERSTORY_BIN`)
- git (for worktree management)
- tmux (overstory uses tmux for agent sessions)
- No external Python dependencies (stdlib only)

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `OVERSTORY_BIN` | `overstory` | Path to overstory binary |
| `OVERSTORY_WORKSPACE` | current directory | Workspace root for overstory operations |

## Commands

### Initialize workspace

```bash
python3 scripts/overstory_wrapper.py init --workspace /path/to/project
```

### Spawn an agent

```bash
python3 scripts/overstory_wrapper.py sling \
  --task-id TASK-42 \
  --capability code \
  --name builder-alice \
  --description "Implement auth module" \
  --worktree
```

### Check status

```bash
python3 scripts/overstory_wrapper.py status
python3 scripts/overstory_wrapper.py status --agent builder-alice --verbose
```

### Inspect agent transcript

```bash
python3 scripts/overstory_wrapper.py inspect --agent builder-alice --lines 100
```

### Kill an agent

```bash
python3 scripts/overstory_wrapper.py kill --agent builder-alice
```

### Worktree management

```bash
python3 scripts/overstory_wrapper.py list-worktrees
python3 scripts/overstory_wrapper.py cleanup-worktree --agent builder-alice
```

### Agent lifecycle

```bash
python3 scripts/agent_lifecycle.py spawn --task "Fix login bug" --capability code --name bug-fixer
python3 scripts/agent_lifecycle.py list-active --json
python3 scripts/agent_lifecycle.py wait --agent bug-fixer --timeout 1800
python3 scripts/agent_lifecycle.py cleanup --max-age 24
```

### Mail bridge

```bash
python3 scripts/mail_bridge.py send --from orchestrator --to builder-alice --subject "Priority change" --body "Switch to auth module"
python3 scripts/mail_bridge.py read --agent builder-alice --unread
python3 scripts/mail_bridge.py broadcast --from orchestrator --channel @all --message "Stand down"
python3 scripts/mail_bridge.py create-thread --agents orchestrator,builder-alice --subject "Auth design"
python3 scripts/mail_bridge.py reply --thread THREAD-ID --from builder-alice --body "Done with phase 1"
```

## Usage as Python Module

```python
from overstory_wrapper import OverstoryWrapper
from agent_lifecycle import AgentLifecycle
from mail_bridge import MailBridge

wrapper = OverstoryWrapper("/path/to/workspace")
wrapper.init()

lifecycle = AgentLifecycle()
agent = lifecycle.spawn_agent(task="Build API", capability="code", name="api-builder")

bridge = MailBridge("/path/to/workspace")
bridge.send("orchestrator", "api-builder", "Context", "Here are the specs...")
```

## Database Schemas

### agent_lifecycle.db (~/.nanobot/agent_lifecycle.db)

| Column | Type | Description |
|---|---|---|
| id | INTEGER PRIMARY KEY | Auto-increment |
| agent_name | TEXT UNIQUE | Agent identifier |
| capability | TEXT | Agent capability (code, research, etc.) |
| status | TEXT | spawned/running/completed/failed/terminated |
| task | TEXT | Task description |
| result | TEXT | Final output (nullable) |
| start_time | REAL | Unix timestamp |
| end_time | REAL | Unix timestamp (nullable) |
| timeout | INTEGER | Max runtime in seconds |

### mail.db (.overstory/mail.db)

| Column | Type | Description |
|---|---|---|
| id | INTEGER PRIMARY KEY | Auto-increment |
| thread_id | TEXT | Thread identifier (nullable) |
| from_agent | TEXT | Sender agent name |
| to_agent | TEXT | Recipient agent name |
| subject | TEXT | Message subject |
| body | TEXT | Message body |
| priority | TEXT | normal/high/urgent |
| read | INTEGER | 0=unread, 1=read |
| created_at | REAL | Unix timestamp |
