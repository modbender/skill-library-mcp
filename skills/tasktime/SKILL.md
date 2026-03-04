---
name: tasktime
description: CLI task timer for AI agents — benchmark learning progression with auto-save logs and visualizations. Integrates with ClawVault for persistent memory.
metadata:
  openclaw:
    requires:
      bins: [tasktime]
    install:
      - id: node
        kind: node
        package: "@versatly/tasktime"
        bins: [tasktime, tt]
        label: Install TaskTime CLI (npm)
---

# tasktime Skill

CLI task timer for AI agents — benchmark learning progression with auto-save logs and visualizations.

**Part of the [ClawVault](https://clawvault.dev) ecosystem** for AI agent memory.

## Installation

```bash
npm install -g @versatly/tasktime
```

## Quick Reference

### Timer Commands
```bash
tasktime start "Task description" --category coding   # Start timing
tasktime stop --notes "What I learned"                # Stop and save
tasktime status                                       # Show current task
tasktime now                                          # One-liner for prompts
```

### History & Search
```bash
tasktime history                    # Recent tasks (alias: tt ls)
tasktime history -n 20              # Last 20 tasks
tasktime history -c coding          # Filter by category
tasktime search "auth"              # Full-text search
tasktime categories                 # List all categories
```

### Reports & Charts
```bash
tasktime report                     # Full report with charts
tasktime report --days 30           # Last 30 days
tasktime chart --type bar           # Bar chart
tasktime chart --type spark         # Sparkline
tasktime chart --type line          # Line chart
```

### ClawVault Integration

**Auto-save on stop (v1.2.0+):** Every completed task is automatically saved to [ClawVault](https://clawvault.dev):

```bash
tasktime start "Build API" -c coding
# ... do the work ...
tasktime stop --notes "Finished in record time"
# ✅ Completed: Build API
# 🐘 Saved to ClawVault              ← automatic!
```

**Manual sync and export:**
```bash
tasktime sync                       # Sync full report to ClawVault
tasktime sync --days 30             # Sync last 30 days
tasktime export                     # Export as markdown
tasktime stop --no-vault            # Skip auto-save for one task
```

### Demo Data
```bash
tasktime seed                       # Seed sample data (empty DB only)
```

## Use Cases for Agents

### Benchmarking Learning
Track how long similar tasks take over time to measure learning progression:

```bash
tt start "Implement OAuth flow" -c auth
# ... do the work ...
tt stop --notes "Used passport.js, took 20min less than last time"
```

### Sync to ClawVault
Persist task data to your agent's memory vault:

```bash
# After completing work
tasktime sync

# Or pipe export to clawvault
tasktime export | clawvault store --category research --title "Task Report"
```

Learn more: [clawvault.dev](https://clawvault.dev)

### Category-Based Analytics
Group tasks to understand time allocation:

```bash
tt report --days 7
# Shows time breakdown by category: coding, research, testing, docs, etc.
```

### Quick Status for Prompts
Add current task to your shell prompt:

```bash
PS1='$(tasktime now) \$ '
# Shows: ⏱️ Build API (23m) $
```

## Data Storage

- Location: `~/.tasktime/tasks.json`
- Format: JSON (portable, human-readable)
- No external dependencies or databases

## Related

- [ClawVault](https://clawvault.dev) — Memory system for AI agents
- [OpenClaw](https://openclaw.ai) — AI agent platform

## Aliases

- `tasktime` → Full command
- `tt` → Short alias (same functionality)
