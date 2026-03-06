---
name: codex-autopilot
description: |
  tmux + launchd multi-project Codex CLI automation system. Watchdog-driven loop that monitors multiple Codex sessions in tmux, auto-nudges idle sessions, handles permissions, manages context compaction, runs incremental code reviews, and dispatches tasks from a queue.
  Use when managing multiple concurrent Codex CLI coding sessions, automating development workflows, or orchestrating parallel AI-assisted coding across projects.
  Triggers: autopilot, watchdog, codex automation, tmux codex, multi-project codex, auto-nudge codex, codex session management.
---

# Codex Autopilot

Automated multi-project Codex CLI orchestration via tmux + launchd on macOS.

## Overview

Codex Autopilot runs a watchdog loop that monitors multiple Codex CLI sessions in tmux windows. It detects idle sessions, auto-nudges them to continue, handles permission prompts, rotates logs, dispatches tasks from a queue, and sends notifications via Discord/Telegram.

## Installation

```bash
git clone https://github.com/imwyvern/AIWorkFlowSkill.git ~/.autopilot
cd ~/.autopilot
cp config.yaml.example config.yaml
# Edit config.yaml with your project paths, Telegram bot token, and Discord channels
```

### Dependencies

- **macOS** with launchd (for scheduled execution)
- **tmux** — session multiplexer for Codex windows
- **Codex CLI** (`codex`) — OpenAI's coding agent
- **python3** — for state cleanup and PRD verification scripts
- **yq** — YAML processor for config parsing
- **jq** — JSON processor for state management
- **bash 4+** — for associative arrays in scripts

Install dependencies via Homebrew:
```bash
brew install tmux yq jq
```

### launchd Setup

Use `install.sh` to register the launchd plist:
```bash
./install.sh
```

This creates a LaunchAgent that runs the watchdog on a configurable interval.

## Core Components

### watchdog.sh
Main loop engine. On each tick:
1. Iterates through configured project tmux windows
2. Captures current Codex output via `codex-status.sh`
3. Determines if session is active, idle, or stuck
4. Dispatches appropriate action (nudge, permission grant, task from queue)
5. Enforces cooldowns, daily send limits, and loop detection

### codex-status.sh
Captures and analyzes tmux pane content. Detects:
- Codex activity state (working / idle / waiting for permission)
- Permission prompts requiring approval
- Context compaction signals
- Error states and crashes

### tmux-send.sh
Sends keystrokes or text to a specific tmux window. Handles:
- Typing text into Codex prompt
- Pressing Enter/keys for permission approval
- Verification polling to confirm send succeeded

### autopilot-lib.sh
Shared function library used by all scripts:
- Telegram notification helpers
- File locking primitives
- Timeout and retry logic
- Logging utilities
- State file read/write

### autopilot-constants.sh
Defines status constants used across scripts (e.g., `STATUS_ACTIVE`, `STATUS_IDLE`, `STATUS_PERMISSION`).

### task-queue.sh
Task queue manager. Supports:
- Enqueuing tasks for specific projects
- Dequeueing next task based on priority
- Task status tracking (pending/running/done/failed)

### discord-notify.sh
Sends formatted notifications to Discord channels via webhook. Supports project-channel routing defined in `config.yaml`.

### Other Scripts

| Script | Purpose |
|--------|---------|
| `auto-nudge.sh` | Nudge logic for idle Codex sessions |
| `auto-check.sh` | Periodic health check across all projects |
| `permission-guard.sh` | Auto-approve or flag permission prompts |
| `incremental-review.sh` | Run code review on recent changes |
| `monitor-all.sh` | Dashboard: show status of all monitored projects |
| `status-sync.sh` | Sync state to status.json for external consumption |
| `rotate-logs.sh` | Log rotation and cleanup |
| `cleanup-state.py` | Remove stale entries from state.json |
| `claude-fallback.sh` | Fallback handler when Codex is unavailable |
| `prd-audit.sh` | Audit PRD completion status |
| `prd-verify.sh` / `prd_verify_engine.py` | Verify PRD items against codebase |
| `codex-token-daily.py` | Track daily token usage |

## Configuration

Edit `config.yaml` (copy from `config.yaml.example`). Key sections:

### Timing Thresholds
```yaml
active_threshold: 120    # seconds — Codex considered "working"
idle_threshold: 360      # seconds — Codex considered "idle", triggers nudge
cooldown: 120            # minimum seconds between sends to same project
```

### Safety Limits
```yaml
max_daily_sends_total: 200   # global daily send cap
max_daily_sends: 50          # per-project daily cap
max_consecutive_failures: 5  # pause project after N failures
loop_detection_threshold: 3  # detect repeated output loops
```

### Multi-Project Scheduler
```yaml
scheduler:
  strategy: "round-robin"    # or "priority"
  max_sends_per_tick: 1
  inter_project_delay: 5     # seconds between project sends
```

### Project Directories
```yaml
project_dirs:
  - "~/project-alpha"
  - "~/project-beta"
```

### Discord Channel Routing
```yaml
discord_channels:
  my-project:
    channel_id: "123456789"
    tmux_window: "my-project"
    project_dir: "/path/to/project"
```

### Telegram Notifications
```yaml
telegram:
  bot_token: "YOUR_BOT_TOKEN"
  chat_id: "YOUR_CHAT_ID"
  status_interval: 1800
```

## Usage

### Adding a Project

1. Start a Codex CLI session in a named tmux window:
   ```bash
   tmux new-window -t autopilot -n my-project
   # In the new window, cd to project and run codex
   ```

2. Add the project path to `config.yaml` under `project_dirs`

3. Optionally create `projects/my-project/tasks.yaml` for task queue:
   ```yaml
   project:
     name: "My Project"
     dir: "~/my-project"
     enabled: true
     priority: 1
   tasks:
     - id: "feature-x"
       name: "Implement feature X"
       prompt: |
         Implement feature X per the spec in docs/feature-x.md
   ```

### Manual Operations

```bash
# Check status of all projects
./scripts/monitor-all.sh

# Manually nudge a specific project
./scripts/auto-nudge.sh my-project

# Send a command to a tmux window
./scripts/tmux-send.sh my-project "codex exec 'fix the tests'"

# Enqueue a task
./scripts/task-queue.sh enqueue my-project "Refactor auth module"

# Run the watchdog once (for testing)
./scripts/watchdog.sh
```

### Python Autopilot (Alternative)

`autopilot.py` provides a Python-based alternative with richer state management:
```bash
python3 autopilot.py --once        # single pass
python3 autopilot.py --daemon      # continuous loop
```

## Directory Structure

```
~/.autopilot/
├── SKILL.md                 # This file
├── config.yaml              # Local config (not in git)
├── config.yaml.example      # Config template
├── scripts/                 # All automation scripts
├── projects/                # Per-project task definitions
├── docs/                    # Additional documentation
├── code-review/             # Code review templates
├── development/             # Development workflow templates
├── doc-review/              # Doc review templates
├── doc-writing/             # Doc writing templates
├── requirement-discovery/   # Requirement discovery templates
├── testing/                 # Testing templates
├── tests/                   # Test suite
├── state/                   # Runtime state (gitignored)
├── logs/                    # Runtime logs (gitignored)
├── task-queue/              # Task queue data (gitignored)
└── archive/                 # Deprecated files
```
