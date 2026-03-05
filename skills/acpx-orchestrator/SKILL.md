---
name: acpx
description: Enhanced terminal AI agent orchestrator with parallel execution, health checks, and workflow presets.
version: 4.0.6
author: qriiz112
email: christianovianto@gmail.com
homepage: https://github.com/qriiz112/acpx-orchestrator
license: MIT
binaries: [acpx]
install: npm install -g acpx
---

# acpx v4.0 - Agent Orchestrator

Enhanced CLI wrapper di atas acpx dengan fitur orchestration: parallel, health check, workflows.

## ⚠️ Warnings & Security Notes

| Item | Status | Description |
|------|--------|-------------|
| **Required Binary** | ✅ | `acpx` (installed via npm) |
| **Optional Binaries** | ℹ️ | `opencode`, `pi`, `kimi`, `kilo`, `codex`, `claude`, `gemini` |
| **File Write** | ⚠️ | Agents write files to **current directory** |
| **Install Command** | ⚠️ | `npm install -g acpx` — verify package on npm/GitHub first |
| **Credentials** | ✅ | No credentials or env vars requested |
| **Persistence** | ✅ | `always: false`, autonomous invocation allowed |

### Security Considerations

- **Scope:** This orchestrator spawns subagents and executes arbitrary tasks via CLI
- **File Access:** Agents can create/modify files in the working directory
- **Review Tasks:** Treat task files and agent commands as untrusted input unless reviewed
- **Install Risk:** npm packages can execute install scripts — prefer sandboxed installs

## Quick Start

```bash
# Discover agents
acpx discover

# Health check
acpx health

# Run single agent
acpx run opencode "Fix bug"

# Run workflow
acpx workflow review
```

## Commands

| Command | Description | Example |
|---------|-------------|---------|
| `discover` | List installed agents | `acpx discover` |
| `health` | Test all agents | `acpx health` |
| `run` | Run single agent | `acpx run opencode "task"` |
| `parallel` | Run agents **simultaneously** (independent tasks only) | `acpx parallel tasks.txt [cwd]` |
| `batch` | Run agents **sequentially** (for dependent tasks) | `acpx batch tasks.txt [cwd]` |
| `watch` | Watch agent status | `acpx watch opencode` |
| `kill` | Kill agent sessions | `acpx kill opencode` |
| `workflow` | Run preset workflow | `acpx workflow review` |
| `json` | Run with JSON output | `acpx json opencode "task" \| jq` |
| `exec` | Direct acpx passthrough | `acpx exec opencode "task"` |

## Workflows

| Workflow | Description |
|----------|-------------|
| `review` | Code review dengan JSON output |
| `refactor` | Safe refactoring dengan diff |
| `test` | Generate pytest tests |
| `debug` | Deep investigation (600s timeout) |

## Batch File Format

```bash
# tasks.txt
opencode exec 'Fix auth.py'
pi exec 'Create tests'
kimi --print --yolo --prompt 'Review changes'
```

```bash
acpx parallel tasks.txt [cwd]  # Run parallel (INDEPENDENT tasks only!)
acpx batch tasks.txt [cwd]     # Run sequential (for dependent tasks)
```

**⚠️ Important:**
- Agents write files to **current directory** by default
- `parallel` = tasks run **simultaneously** → use for **independent** tasks
- `batch` = tasks run **one-by-one** → use for **dependent** tasks
- Use full paths or specify working directory as 2nd argument

**Example tasks.txt:**
```
# Task 1: Create file
opencode exec 'Create app.js with Express server'

# Task 2: Review file (depends on task 1)
kimi --print --yolo --prompt 'Review app.js'
```

Run with: `acpx batch tasks.txt` (sequential, task 2 waits for task 1)

## Spawn via OpenClaw

```javascript
// Health check
sessions_spawn(
  task="acpx health",
  label="health-check",
  runtime="subagent",
  mode="run"
)

// Run workflow
sessions_spawn(
  task="acpx workflow review",
  label="review",
  runtime="subagent",
  mode="run"
)

// Parallel tasks
sessions_spawn(
  task="acpx parallel tasks.txt",
  label="parallel-jobs",
  runtime="subagent",
  mode="run"
)

// JSON output
sessions_spawn(
  task="acpx json opencode 'List functions'",
  label="json-task",
  runtime="subagent",
  mode="run"
)
```

## Helper Scripts

- `acpx` - Main orchestrator CLI
- `acpx-batch` - Legacy sequential runner
- `acpx-workflow` - Legacy workflow presets
- `acpx-discover` - Legacy discovery

## Changelog

- **v4.0.0** - Enhanced orchestrator: parallel, health check, workflows, json output
- **v3.1.0** - Simple CLI wrapper
- **v3.0.0** - Generic auto-discovery
- **v2.0.0** - Async multi-agent patterns
- **v1.0.0** - Initial wrapper
