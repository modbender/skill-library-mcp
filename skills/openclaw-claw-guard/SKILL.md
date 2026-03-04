---
name: claw-guard
description: System-level watchdog for OpenClaw gateway restarts and sub-agent task PIDs. Monitors registered PIDs and optional log/directory freshness. Auto-reverts config on failed gateway restarts. Requires explicit registration — does NOT auto-discover. Use when running long background tasks or before gateway restarts.
---

# ClawGuard — Task & Gateway Watchdog

A lightweight service that monitors **registered** events:

1. **Sub-agent task PIDs** — if PID dies → notify and remove. If log/dir stale → alert and remove.
2. **Gateway restarts** — if restart fails → revert config backups (newest to oldest) → retry → notify.

**ClawGuard only monitors what is explicitly registered.** It does not auto-discover.

## Install

```bash
cd <skill-dir>
bash scripts/install.sh
```

Installs:
- **Daemon**: systemd user service (Linux) or launchd agent (macOS) — `Restart=always`, auto-starts on boot
- **CLI**: `claw-guard` in `~/.local/bin/`
- **Data**: `~/.openclaw/workspace/tools/claw-guard/`

## OpenClaw Integration (Recommended)

### 1. Auto-register gateway restarts

Add `ExecStartPre` to your gateway service so every restart (manual, crash, or `Restart=always`) is automatically registered:

```ini
# ~/.config/systemd/user/openclaw-gateway.service
[Service]
ExecStartPre=/home/<user>/.local/bin/claw-guard register-restart
ExecStart=...
```

Then reload: `systemctl --user daemon-reload`

Now every gateway restart automatically:
- Snapshots the current config (rotates up to 5 backups)
- Watches for the gateway to come back
- If it fails → reverts config backups newest-to-oldest → notifies default channel

**No manual `claw-guard register-restart` needed — systemd handles it.**

### 2. Add task execution rules to AGENTS.md

Add these rules so the agent always registers its work:

```markdown
## Task Execution Rules (MANDATORY)

### Sub-agent requirement
- **Any exec/tool call that might take >5s → sub-agent** (`sessions_spawn`).
  Main agent stays responsive.
- **Complex or unpredictable tasks → always sub-agent.** Even if they might
  be fast. If you can't guarantee it won't block, delegate it.
- **Only run in main agent** if certain it won't block I/O (quick file reads,
  short `grep`, `git status`, `claw-guard status`, etc.)

### ClawGuard registration (MANDATORY for all sub-agents)
Every sub-agent and background process **must** be registered:
```bash
claw-guard register --id "<descriptive-id>" --pid <PID> \
  --target "<channel where task was requested>" \
  --log "/path/to/logfile" --timeout 180 \
  --command "<what it does>"
```
- `--target`: same channel/room where the user asked for the task
- `--log` and `--timeout`: optional but recommended for long tasks
- If PID dies → claw-guard notifies the target channel and removes the entry
- If log goes stale → claw-guard notifies and removes

### Gateway restarts
- **Never restart the gateway while tasks are running** — it kills all sub-agents
- Gateway service has `ExecStartPre=claw-guard register-restart` — automatic
- No manual registration needed for restarts
```

### 3. How it works end-to-end

**Sub-agent task flow:**
1. User requests a long-running task
2. Agent spawns sub-agent → gets PID
3. Agent runs: `claw-guard register --id "task-name" --pid $PID --target "room:..." --command "..."`
4. If PID dies → claw-guard notifies the target channel → agent confirms result with user
5. If log goes stale → claw-guard alerts → agent investigates

**Gateway restart flow:**
1. Gateway restarts (manual, crash, or auto)
2. `ExecStartPre` runs `claw-guard register-restart` → config backed up
3. Gateway starts successfully → claw-guard logs `✅ Gateway restart succeeded` → watch cleared
4. Gateway fails to start → claw-guard tries config backups → notifies default channel

## CLI Reference

### Register a task

```bash
claw-guard register --id "benchmark-q8" --pid 12345 \
  --target "room:!abc:server" \
  --log "/path/to/task.log" --timeout 180 \
  --command "python3 benchmark.py"

# Or watch a directory for new file creation:
claw-guard register --id "export-gguf" --pid 12345 \
  --target "room:!abc:server" \
  --watch-dir "/path/to/output/" --timeout 300 \
  --command "export_gguf.py"
```

| Flag | Required | Description |
|------|----------|-------------|
| `--id` | yes | Unique task identifier |
| `--pid` | yes | Process ID to watch |
| `--target` | yes | Notification target (see formats below) |
| `--log` | no | Log file path — checks mtime only |
| `--watch-dir` | no | Directory — checks newest file mtime |
| `--timeout` | no | Stale threshold in seconds (default: 180) |
| `--command` | no | Description included in notifications |

### Register a gateway restart

```bash
claw-guard register-restart [--target "room:!abc:server"]
```

No `--target` needed — sends to OpenClaw's default channel. Pass `--target` to override.

### Manage

```bash
claw-guard status          # Show tasks, restart watch, config backups
claw-guard remove --id X   # Remove a task
claw-guard clear-done      # Remove completed/gone tasks
```

## Behavior

### Check cycle (every 15s)

1. **Gateway restart**: if registered and gateway not active after 30s → revert + retry + notify
2. **PID check**: if PID gone → notify target → remove entry
3. **Log/dir freshness**: if mtime exceeds timeout → notify target → remove entry

### Deduplication

After notifying, the registered entry is **removed from the registry**. Once removed, it can't fire again. No dedup tracking needed.

### Restart / reboot behavior

On service restart or system reboot:
- **All registered tasks are cleared** — nothing carries over
- **Config backups persist** on disk (only thing that survives)

This is by design: after a reboot, all monitored processes are gone anyway. The agent must re-register any new tasks.

## Notification Targets

Any format `openclaw message send --target` accepts:
- `room:!roomId:server` (Matrix)
- `telegram:chatid`
- `discord:#channel`
- `slack:#channel`

Gateway restart alerts with no `--target` are sent without a target flag, letting OpenClaw route to the default channel.

## Design Principles

- **Registration-based, not auto-discovery** — only watches what's explicitly registered
- **Notify once, then remove** — no duplicate alerts, no stale state
- **In-memory state** — registry clears on service restart (clean slate)
- **Disk persistence only for config backups** — the only thing worth keeping across restarts
- **Cross-platform** — Linux (systemd) and macOS (launchd)
- **Minimal overhead** — ~7MB RAM, negligible CPU
