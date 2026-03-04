# Task Engine — Phase 5: Polish + Production

## What This Is
An OpenClaw skill for multi-agent task orchestration. Read `DESIGN.md` for full design.

## Current State
Phase 0–4 are COMPLETE. These files exist and work — DO NOT rewrite them:
- `scripts/engine/models.py` (262 lines) — dataclasses
- `scripts/engine/state_machine.py` (84 lines) — transitions
- `scripts/engine/task_store.py` (383 lines) — CRUD + atomic writes
- `scripts/engine/checker.py` (307 lines) — heartbeat check, stuck/overdue detection
- `scripts/engine/discord_formatter.py` (377 lines) — Discord message formatting
- `scripts/engine/dispatcher.py` (258 lines) — agent selection + dispatch context
- `scripts/task_engine.py` (600+ lines) — CLI with all commands
- `config/settings.yaml` — configuration
- `references/agent-capabilities.md` — agent roster
- `SKILL.md` — skill definition (needs enhancement)

## Your Task: Phase 5 — Polish + Production Readiness

### 1. Implement `rebuild-index` recovery command

Add to task_engine.py:
```bash
python3 scripts/task_engine.py rebuild-index
```

Scans `tasks/*/task.json` files, reconstructs `index.json` from scratch. Useful for recovery if index gets corrupted. Should:
- Walk all `tasks/TASK-*/task.json` files (skip archive/)
- Build index entries from each task.json
- Write new index.json atomically
- Report what was found/rebuilt

### 2. Add `--json` output to ALL CLI commands

Every command should support `--json` for programmatic use:
```bash
python3 scripts/task_engine.py create "Task" --priority P1 --json
python3 scripts/task_engine.py transition TASK-001 approve --json
python3 scripts/task_engine.py dispatch TASK-001 "Work" --agent claude-code --type dev --json
python3 scripts/task_engine.py subtask TASK-001 subtask_01 start --progress 50 --json
python3 scripts/task_engine.py archive TASK-001 --json
python3 scripts/task_engine.py auto-dispatch TASK-001 --json  # already outputs JSON
python3 scripts/task_engine.py rebuild-index --json
```

JSON output format:
```json
{"ok": true, "task_id": "TASK-001", "status": "PLANNING", "message": "Created TASK-001"}
```
On error:
```json
{"ok": false, "error": "Invalid transition: PLANNING → complete"}
```

### 3. Create `references/state-transitions.md`

Full reference doc for all valid state transitions:

```markdown
# State Transitions Reference

## Task States
| From | Event | To | Notes |
|------|-------|-----|-------|
| PLANNING | approve | APPROVED | Requires plan |
| PLANNING | reject | REJECTED | Terminal |
...

## Subtask States
| From | Event | To | Notes |
...

## Auto-Transitions
| Condition | Action |
...
```

### 4. Error handling hardening

Review and harden error handling in all modules:
- JSON parse errors → skip task, log warning, continue
- Missing files → graceful skip with warning
- Invalid state in JSON → log and skip, don't crash
- Circular dependency detection in dispatch
- All CLI commands should catch exceptions and return clean error messages (not tracebacks)

### 5. Add pytest test suite

Create `tests/` directory with:

```
tests/
├── conftest.py          # shared fixtures (tmp tasks dir, sample tasks)
├── test_state_machine.py  # all valid/invalid transitions
├── test_task_store.py     # CRUD, atomic writes, index management
├── test_checker.py        # stuck, overdue, auto-transition detection
├── test_dispatcher.py     # agent selection, readiness, context building
├── test_discord_formatter.py  # all format_* functions
└── test_cli.py            # end-to-end CLI tests via subprocess
```

**conftest.py fixtures:**
```python
@pytest.fixture
def tasks_dir(tmp_path):
    """Temporary tasks directory."""
    d = tmp_path / "tasks"
    d.mkdir()
    return d

@pytest.fixture
def sample_task(tasks_dir):
    """Create a sample task with subtasks for testing."""
    # Use task_store functions to create real task files
```

**test_state_machine.py:**
- Test all valid transitions (task + subtask)
- Test all invalid transitions raise/return error
- Test auto-transition conditions
- Test check_auto_transition with various subtask combinations

**test_task_store.py:**
- Create task → verify files exist
- Read/save round-trip
- Index create/update/rebuild
- Subtask CRUD
- Atomic write (verify no partial writes)
- List tasks with filters
- Archive task

**test_checker.py:**
- No active tasks → all_ok
- Active task, healthy → no alerts
- Stuck subtask (3+ beats, no progress) → stuck alert
- Overdue task → overdue alert
- Auto-transition triggers correctly

**test_dispatcher.py:**
- select_agent by type
- select_agent with preferred override
- build_dispatch_context includes deps
- check_dispatch_readiness with met/unmet deps
- get_active_agent_count accuracy

**test_discord_formatter.py:**
- All format_* functions produce non-empty strings
- Progress bar renders correctly at 0%, 50%, 100%
- Alert format includes human ping
- Digest format handles empty/single/multiple tasks

**test_cli.py:**
- Full lifecycle via subprocess: create → approve → dispatch → start → done → archive
- --json flag on each command
- rebuild-index recovery
- Error cases return non-zero exit code

### 6. Update SKILL.md

Enhance the existing SKILL.md with:
- Auto-dispatch section with examples
- notify command section
- Discord formatting section
- Agent capabilities summary
- Troubleshooting (rebuild-index, common errors)

### Key Paths
- Skill root: `/home/zeron/.openclaw/workspace/skills/task-engine/`
- Runtime tasks dir: `/home/zeron/.openclaw/workspace/tasks/`
- Tests: `/home/zeron/.openclaw/workspace/skills/task-engine/tests/`

### DO NOT
- Do NOT rewrite existing working core logic
- Do NOT install packages beyond pytest (already available)
- Do NOT explore filesystem beyond this skill directory
- Do NOT make API calls

### When Done
Run the full test suite:
```bash
cd /home/zeron/.openclaw/workspace/skills/task-engine
python3 -m pytest tests/ -v

# Also run the end-to-end manual test:
rm -rf /home/zeron/.openclaw/workspace/tasks
python3 scripts/task_engine.py create "E2E test" --priority P1 --json
python3 scripts/task_engine.py transition TASK-001 approve --json
python3 scripts/task_engine.py dispatch TASK-001 "Dev work" --agent claude-code --type dev --json
python3 scripts/task_engine.py subtask TASK-001 subtask_01 start --progress 100 --json
python3 scripts/task_engine.py subtask TASK-001 subtask_01 done --json
python3 scripts/task_engine.py check --json
python3 scripts/task_engine.py notify digest
python3 scripts/task_engine.py auto-dispatch TASK-001 --dry-run
python3 scripts/task_engine.py archive TASK-001 --json
python3 scripts/task_engine.py rebuild-index --json
```
