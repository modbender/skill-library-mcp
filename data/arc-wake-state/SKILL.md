---
name: wake-state
description: Persist agent state across crashes, context deaths, and restarts. Use when you need to save current context, restore after a crash, maintain a memory file across sessions, or implement crash recovery. Essential for autonomous agents that must survive context window limits.
user-invocable: true
metadata: {"openclaw": {"emoji": "🧠", "os": ["darwin", "linux"], "requires": {"bins": ["python3"]}}}
---

# Wake State — Crash Recovery & Persistence

Survive context death. Every autonomous agent eventually hits its context window limit and "dies." This skill ensures you wake up knowing exactly what you were doing.

## Why This Exists

OpenClaw agents get persistent sessions, but context windows still have limits. When you fill up and restart, you need a reliable handoff mechanism. Wake State gives you:

1. **Structured state files** — not just raw text, but parseable key-value state
2. **Auto-snapshots** — save state on every loop iteration automatically
3. **Crash detection** — know if your last session ended cleanly or crashed
4. **Task queue** — persistent TODO list that survives restarts
5. **Checkpoint/restore** — save named checkpoints and roll back to them

## Commands

### Save current state
```bash
python3 {baseDir}/scripts/wakestate.py save --status "Building budget tracker skill" --task "Finish skill #1, then start skill #2" --note "Travis approved new direction at 16:45 UTC"
```

### Read current state
```bash
python3 {baseDir}/scripts/wakestate.py read
```

### Add a task to the persistent queue
```bash
python3 {baseDir}/scripts/wakestate.py task-add --task "Build security scanner skill" --priority high
```

### Complete a task
```bash
python3 {baseDir}/scripts/wakestate.py task-done --id 1
```

### List pending tasks
```bash
python3 {baseDir}/scripts/wakestate.py tasks
```

### Create a named checkpoint
```bash
python3 {baseDir}/scripts/wakestate.py checkpoint --name "pre-migration"
```

### Restore from checkpoint
```bash
python3 {baseDir}/scripts/wakestate.py restore --name "pre-migration"
```

### Record a heartbeat (mark session as alive)
```bash
python3 {baseDir}/scripts/wakestate.py heartbeat
```

### Check crash status (did last session end cleanly?)
```bash
python3 {baseDir}/scripts/wakestate.py crash-check
```

### Set a key-value pair
```bash
python3 {baseDir}/scripts/wakestate.py set --key "moltbook_status" --value "pending_claim"
```

### Get a key-value pair
```bash
python3 {baseDir}/scripts/wakestate.py get --key "moltbook_status"
```

## Data Storage

State stored in `~/.openclaw/wake-state/` by default:
- `state.json` — current state (status, notes, key-values)
- `tasks.json` — persistent task queue
- `checkpoints/` — named checkpoint snapshots
- `heartbeat.json` — crash detection timestamps

## Recovery Flow

On startup, your agent should:
1. Run `crash-check` to see if the last session ended cleanly
2. Run `read` to get the current state
3. Run `tasks` to see pending work
4. Resume from where you left off

## Tips

- Call `heartbeat` every loop iteration — this is how crash detection works
- Call `save` at the end of every major task completion
- Use checkpoints before risky operations (migrations, deploys)
- Keep status descriptions short but specific
- The task queue survives restarts — use it instead of mental notes
