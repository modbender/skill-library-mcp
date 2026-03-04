---
name: nanobot-overstory-bridge
displayName: OverClaw Bridge
description: Seamless bidirectional bridge between nanobot (Ollama Mistral orchestrator) and overstory (Claude Code agent swarm). Routes tasks through the OverClaw gateway (port 18800) to overstory for subagent coordination, syncs memory.
version: 1.1.0
---

# OverClaw Bridge (nanobot-overstory)

The critical integration layer in the **OverClaw** stack. Connects **nanobot** (lightweight AI backend powered by Ollama Mistral) to **overstory** (Claude Code agent swarm system) through the **OverClaw HTTP gateway on port 18800**. nanobot handles task intake and orchestration; overstory handles all subagent creation, coordination, worktree management, and execution.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        nanobot                              │
│  (Ollama Mistral orchestrator — task intake & routing)      │
└──────────────────────┬──────────────────────────────────────┘
                       │  task_router.py
                       │  (classify → capability → overstory format)
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              nanobot-overstory Bridge                        │
│                                                             │
│  ┌──────────────┐  ┌────────────────┐  ┌────────────────┐  │
│  │ task_router   │  │ session_bridge │  │ memory_sync    │  │
│  │ .py           │  │ .py            │  │ .py            │  │
│  │               │  │                │  │                │  │
│  │ route_task()  │  │ create_mapping │  │ sync_to_over() │  │
│  │ translate()   │  │ get_agent()    │  │ sync_from()    │  │
│  │ capability()  │  │ cleanup()      │  │ prune()        │  │
│  └──────┬───────┘  └───────┬────────┘  └───────┬────────┘  │
│         │                  │                    │           │
│         └──────────┬───────┴────────────────────┘           │
│                    │                                        │
│           overstory_client.py                               │
│           (subprocess wrapper around `overstory` CLI)       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                       overstory                             │
│  (Claude Code agent swarm — subagent lifecycle & execution) │
│                                                             │
│  coordinator → supervisor → agents (worktrees)              │
│  mail system, merge, inspect, status                        │
└─────────────────────────────────────────────────────────────┘
```

## Components

### overstory_client.py

Python wrapper around the `overstory` CLI binary. Provides a clean `OverstoryClient` class with methods for every overstory operation: `sling`, `status`, `inspect`, `mail_send`, `mail_read`, `coordinator_start`, `supervisor_start`, `merge`, and `list_agents`.

### task_router.py

Translates nanobot task descriptions into overstory-compatible formats. Maps task intent to overstory capabilities:

| Task Pattern | Capability |
|---|---|
| Research, trends, analysis | `researcher` |
| Social media, posting, tweets | `social-media-manager` |
| Blog, article, content | `blogger` |
| Code, build, fix, implement | `builder` |
| Explore, find, search | `scout` |
| Logs, memory, notes | `scribe` |
| Review, merge | `reviewer` |

### session_bridge.py

Maintains a persistent mapping between nanobot session IDs and overstory agent names. Uses SQLite at `~/.nanobot/session_bridge.db` for thread-safe, persistent storage. Supports stale mapping cleanup.

### memory_sync.py

Bidirectional memory synchronization. Pushes nanobot's `MEMORY.md` context to overstory agents before task execution, and pulls agent insights back into nanobot's memory after completion.

## Usage

### From Python

```python
from overstory_client import OverstoryClient
from task_router import TaskRouter
from session_bridge import SessionBridge
from memory_sync import MemorySync

client = OverstoryClient()
router = TaskRouter(client)
bridge = SessionBridge()
memory = MemorySync()

# Route a task from nanobot to overstory
result = router.route_task("Research trending AI papers this week")
# result: {"capability": "researcher", "agent_name": "researcher-abc123", ...}

# Check agent status
status = client.status("researcher-abc123")

# Send inter-agent mail
client.mail_send("coordinator", "researcher-abc123", "Priority update needed")

# Sync memory before/after
memory.sync_to_overstory()
memory.sync_from_overstory({"insight": "Found 3 key papers on reasoning"})
```

### From CLI

```bash
# Route a task
python3 scripts/task_router.py route --task "Build a REST API for the dashboard" --json

# Check overstory status
python3 scripts/overstory_client.py status --json
python3 scripts/overstory_client.py status --agent researcher-abc123 --json

# Spawn an agent
python3 scripts/overstory_client.py sling \
  --capability builder \
  --name "api-builder" \
  --description "Build REST API for dashboard" --json

# Sync memory
python3 scripts/memory_sync.py sync --direction to_overstory --json
python3 scripts/memory_sync.py sync --direction from_overstory --json

# List session mappings
python3 scripts/session_bridge.py list --json

# Clean up stale mappings
python3 scripts/session_bridge.py cleanup --max-age 24 --json
```

## Requirements

- Python 3.9+
- `overstory` CLI installed and on PATH (or set `OVERSTORY_BIN` env var)
- OverClaw gateway running on port 18800 (`scripts/start-overclaw.sh`)
- Ollama with Mistral model
- SQLite3 (bundled with Python)

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `NANOBOT_GATEWAY_URL` | `http://localhost:18800` | OverClaw gateway URL |
| `OVERCLAW_PORT` | `18800` | OverClaw gateway port |
| `OVERSTORY_BIN` | `overstory` | Path to overstory binary |
| `NANOBOT_WORKSPACE` | `/Users/ghost/.openclaw/workspace` | Workspace root |
| `NANOBOT_SKILLS_DIR` | `<workspace>/skills` | Skills directory |
| `NANOBOT_MEMORY_PATH` | `<workspace>/MEMORY.md` | Path to MEMORY.md |
| `SESSION_BRIDGE_DB` | `~/.nanobot/session_bridge.db` | Session mapping database |
| `BRIDGE_LOG_LEVEL` | `INFO` | Logging verbosity |

> **Note for existing nanobot/OpenClaw users:** OverClaw runs on port **18800**, separate from the legacy OpenClaw gateway (18789) and nanobot default (18790). No conflicts.

## Integration Flow

1. **nanobot receives task** from user via TUI/API
2. **task_router** classifies the task and determines the overstory capability
3. **session_bridge** creates a mapping between nanobot session and upcoming overstory agent
4. **memory_sync** pushes relevant context to overstory
5. **overstory_client** spawns the agent via `overstory sling`
6. **overstory** manages the agent lifecycle (worktree, execution, mail)
7. On completion, **overstory_client** retrieves results via `inspect`/`status`
8. **memory_sync** pulls insights back into nanobot memory
9. **session_bridge** marks the mapping as completed
10. **nanobot** delivers the result to the user
