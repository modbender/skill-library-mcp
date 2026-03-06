---
name: acpx
description: Enhanced terminal AI agent orchestrator with parallel execution, health checks, and workflow presets.
metadata: {"version": "4.0.0", "author": "Bandit"}
---

# acpx v4.0 - Agent Orchestrator

Enhanced CLI wrapper di atas acpx dengan fitur orchestration: parallel, health check, workflows.

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
| `parallel` | Run agents parallel from file | `acpx parallel tasks.txt` |
| `batch` | Run agents sequential from file | `acpx batch tasks.txt` |
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
acpx parallel tasks.txt  # Run parallel
acpx batch tasks.txt     # Run sequential
```

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
