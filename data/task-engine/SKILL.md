---
name: task-engine
description: "Multi-agent task orchestration engine with state machine tracking. Use when complex multi-step projects need automated monitoring, multi-agent collaboration, and Discord-based progress tracking."
---

# Task Engine

Orchestrates multi-step projects across multiple agents (Claude Code, Eva, others) using a state machine with JSON-based persistence. Each task has subtasks dispatched to agents, tracked via heartbeat, and reported through Discord.

## CLI Commands

All commands run from the skill root:

```bash
cd /home/zeron/.openclaw/workspace/skills/task-engine
```

All commands support `--json` for machine-readable output:
```json
{"ok": true, "task_id": "TASK-001", "status": "PLANNING", "message": "Created TASK-001"}
```

### Create a task

```bash
python3 scripts/task_engine.py create "Implement feature X" --priority P0 --plan "3 phases: models, API, tests"
python3 scripts/task_engine.py create "Feature Y" --priority P1 --json
```

### View status

```bash
python3 scripts/task_engine.py status                    # All active tasks (table)
python3 scripts/task_engine.py status TASK-001           # Detailed single task
python3 scripts/task_engine.py status TASK-001 --json    # Machine-readable
python3 scripts/task_engine.py status --all              # Include terminal tasks
```

### Transition task state

```bash
python3 scripts/task_engine.py transition TASK-001 approve --note "Plan approved" --json
python3 scripts/task_engine.py transition TASK-001 block --note "Waiting on API key"
python3 scripts/task_engine.py transition TASK-001 complete --note "All verified" --json
```

### Dispatch subtask to an agent

```bash
python3 scripts/task_engine.py dispatch TASK-001 "Implement auth models" \
    --agent claude-code --type dev --json
python3 scripts/task_engine.py dispatch TASK-001 "Run integration tests" \
    --agent eva --type test --deps subtask_01,subtask_02
```

Dispatching the first subtask auto-transitions APPROVED -> IN_PROGRESS.

### Update subtask progress

```bash
python3 scripts/task_engine.py subtask TASK-001 subtask_01 start --progress 30 --json
python3 scripts/task_engine.py subtask TASK-001 subtask_01 done --note "Models complete" --json
python3 scripts/task_engine.py subtask TASK-001 subtask_02 fail --note "Schema mismatch" --json
```

### Check tasks (heartbeat integration)

```bash
python3 scripts/task_engine.py check              # Check all active tasks (verbose)
python3 scripts/task_engine.py check TASK-001      # Check one task
python3 scripts/task_engine.py check --quiet       # Minimal output for cron
python3 scripts/task_engine.py check --json        # Machine-readable JSON
python3 scripts/task_engine.py check --discord     # Discord-formatted digest
```

### Archive completed task

```bash
python3 scripts/task_engine.py archive TASK-001 --json    # Only works on terminal tasks
```

### Auto-dispatch

Auto-dispatch scans subtasks and dispatches ready ones to appropriate agents:

```bash
python3 scripts/task_engine.py auto-dispatch TASK-001             # Dispatch ready subtasks
python3 scripts/task_engine.py auto-dispatch TASK-001 --dry-run   # Preview without acting
python3 scripts/task_engine.py auto-dispatch --all                # All active tasks
python3 scripts/task_engine.py auto-dispatch TASK-001 --subtask subtask_02  # Specific subtask
python3 scripts/task_engine.py auto-dispatch TASK-001 --subtask subtask_01 --show-context  # View dispatch context
```

Output is always JSON with `dispatches` and `skipped` arrays.

### Notify (Discord formatting)

Generate Discord-formatted notification messages:

```bash
python3 scripts/task_engine.py notify digest               # Full heartbeat digest
python3 scripts/task_engine.py notify TASK-001 created     # Task creation message
python3 scripts/task_engine.py notify TASK-001 status      # Status update with progress
python3 scripts/task_engine.py notify TASK-001 transition   # Last transition
python3 scripts/task_engine.py notify TASK-001 completed    # Completion summary
python3 scripts/task_engine.py notify TASK-001 alert --type stuck --subtask-id subtask_01
```

### Rebuild index (recovery)

Reconstruct `index.json` from task directories if it gets corrupted:

```bash
python3 scripts/task_engine.py rebuild-index         # Scan and rebuild
python3 scripts/task_engine.py rebuild-index --json  # Machine-readable output
```

## Heartbeat Integration

Add step 4.3 to the heartbeat's `cmd_beat()` function, after the ongoing.json check:

```python
# 4.3 Task Engine check
logger.info("[4.3/8] Task Engine check")
try:
    import sys
    sys.path.insert(0, str(Path("/home/zeron/.openclaw/workspace/skills/task-engine/scripts")))
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

The check is cheap (~300-500 tokens per heartbeat for 1-3 active tasks). It reads index.json first, then only loads task/subtask files for active tasks.

## State Machine

```
PLANNING ──approve──> APPROVED ──start──> IN_PROGRESS ──test──> TESTING ──review──> REVIEW ──complete──> COMPLETED
    │                                         │  │                 │  │                │
    │reject                              block│  │fail        reopen│  │fail       reopen│ fail
    v                                         v  v                 v  v                v   v
 REJECTED                                BLOCKED FAILED      IN_PROGRESS FAILED   IN_PROGRESS FAILED
                                           │
                                      unblock│
                                           v
                                      IN_PROGRESS
```

Terminal states: COMPLETED, FAILED, REJECTED.

See `references/state-transitions.md` for the full transition table.

### Subtask states

```
PENDING -> ASSIGNED -> IN_PROGRESS -> DONE
                │            │
                │block       │fail / block
                v            v
             BLOCKED      FAILED / BLOCKED
```

### Auto-transitions (checked by heartbeat)

| Condition | Action |
|-----------|--------|
| All `type: dev` subtasks DONE | Task -> TESTING |
| All `type: test` subtasks DONE | Task -> REVIEW |
| First subtask dispatched | Task APPROVED -> IN_PROGRESS |
| Any subtask FAILED | Alert for human intervention |
| Subtask stuck 3+ heartbeats | Alert via Discord |
| Task past ETA | Alert as overdue |

## Discord Formatting

The `discord_formatter.py` module generates formatted messages for Discord notifications. All formatting is pure string generation — no API calls.

Available formats:
- **Task created**: New task announcement with priority and plan
- **Status update**: Progress bars and subtask tree
- **Transition**: State change with emoji indicators
- **Alert**: Urgent stuck/overdue/failed alerts with human ping
- **Completion summary**: Final report with subtask results
- **Heartbeat digest**: Full summary of all active tasks

Progress bars render as: `[████░░░░░░] 40%`

## Agent Capabilities

| Agent | Key | Best For | Max Parallel |
|-------|-----|----------|--------------|
| Claude Code | `claude-code` | Dev, refactor, debug, docs | 3 |
| Eva | `eva` | Test, validate, system-ops | 1 |

Agent selection priority:
1. Preferred agent (if specified and capable)
2. Match by `preferred_types`
3. Match by broader `capabilities`
4. Fallback to Eva

See `references/agent-capabilities.md` for full details.

## Troubleshooting

### Corrupted index.json

```bash
python3 scripts/task_engine.py rebuild-index --json
```

Scans all `tasks/TASK-*/task.json` files and reconstructs the index. Skips invalid/unreadable files.

### Common errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Invalid transition: X + 'event'` | Transition not allowed from current state | Check `references/state-transitions.md` |
| `Task TASK-XXX not found` | Task doesn't exist or was archived | Check `tasks/` and `tasks/archive/` |
| `Cannot archive: not terminal` | Task must be COMPLETED/FAILED/REJECTED | Transition to terminal state first |
| `Agent at capacity` | Max parallel instances reached | Wait for running subtasks to complete |
| `Dependency not DONE` | Blocked by incomplete subtask | Complete blocking subtask first |

### JSON parse errors

The engine handles corrupt JSON files gracefully:
- During `check`: skips bad tasks, logs warning, continues
- During `rebuild-index`: skips unreadable files, reports in output
- All CLI commands catch exceptions and return clean error messages (not tracebacks)

## Data Location

- Task files: `/home/zeron/.openclaw/workspace/tasks/TASK-NNN/`
- Index: `/home/zeron/.openclaw/workspace/tasks/index.json`
- Archive: `/home/zeron/.openclaw/workspace/tasks/archive/`
- Config: `/home/zeron/.openclaw/workspace/skills/task-engine/config/settings.yaml`
- Agent reference: `/home/zeron/.openclaw/workspace/skills/task-engine/references/agent-capabilities.md`
- State transitions: `/home/zeron/.openclaw/workspace/skills/task-engine/references/state-transitions.md`
