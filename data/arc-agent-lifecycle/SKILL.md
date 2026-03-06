---
name: agent-lifecycle
description: Manage the lifecycle of autonomous agents and their skills. Version configurations, plan upgrades, track retirement, and maintain change history across agent environments.
user-invocable: true
metadata: {"openclaw": {"emoji": "🔄", "os": ["darwin", "linux"], "requires": {"bins": ["python3"]}}}
---

# Agent Lifecycle Manager

Track your agent's evolution from deployment to retirement. Version configurations, plan skill upgrades, and maintain a complete change history.

## Why This Exists

Agents evolve constantly — new skills installed, old ones retired, configurations changed, models swapped. Without lifecycle tracking, you cannot answer: "What was my agent running last Tuesday?" or "What changed when things broke?"

## Commands

### Snapshot current agent state
```bash
python3 {baseDir}/scripts/lifecycle.py snapshot --name "pre-upgrade"
```

### Compare two snapshots
```bash
python3 {baseDir}/scripts/lifecycle.py diff --from "pre-upgrade" --to "post-upgrade"
```

### List all snapshots
```bash
python3 {baseDir}/scripts/lifecycle.py list
```

### Rollback to a snapshot
```bash
python3 {baseDir}/scripts/lifecycle.py rollback --to "pre-upgrade" --dry-run
```

### Track a skill retirement
```bash
python3 {baseDir}/scripts/lifecycle.py retire --skill old-skill --reason "Replaced by new-skill v2"
```

### View change history
```bash
python3 {baseDir}/scripts/lifecycle.py history --limit 20
```

## What It Tracks

- **Installed skills**: Name, version, install date, last used
- **Configuration state**: Environment vars, model assignments, feature flags
- **Change events**: Installs, updates, removals, config changes
- **Retirement log**: Why skills were removed, what replaced them
- **Snapshots**: Point-in-time captures of full agent state

## Data Storage

Lifecycle data is stored in `~/.openclaw/lifecycle/` as JSON files.
