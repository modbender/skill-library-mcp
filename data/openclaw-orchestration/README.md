# @openclaw/orchestration

[![Tests](https://img.shields.io/badge/tests-13%20passing-brightgreen)]() [![Node](https://img.shields.io/badge/node-%3E%3D18-blue)]() [![License: MIT](https://img.shields.io/badge/license-MIT-yellow)]()

> Multi-agent task queue with collision-safe claiming and dependency chains.

A SQLite-backed task orchestration system designed for multi-agent environments. Agents register capabilities, claim tasks atomically, and chain dependencies — all with automatic timeout detection, retry logic, and `.md` interchange output.

## Features

- **Task queue** — create, claim, complete, fail, and retry tasks
- **Collision-safe claiming** — atomic SQLite transactions prevent double-claims
- **Dependency chains** — tasks can depend on other tasks completing first
- **Timeout & retry** — configurable timeouts with automatic sweep and retry
- **Agent registry** — register agents with capabilities and concurrency limits
- **Priority levels** — high, medium, low task prioritization
- **Interchange output** — regenerate `.md` files for cross-skill visibility
- **Backup & restore** — full database backup and recovery

## Quick Start

```bash
cd skills/orchestration
npm install

# Register an agent
node src/cli.js agent register researcher --capabilities "search,summarize" --max-concurrent 3

# Create a task
node src/cli.js task create "Research competitor pricing" --priority high --timeout 30

# Claim and complete
node src/cli.js task claim <task-id> --agent researcher
node src/cli.js task complete <task-id> --summary "Found 5 competitors"

# Sweep stale tasks
node src/cli.js sweep
```

## CLI Reference

### Task Management

```bash
orch task create <title> [options]
  --desc <description>       Task description
  --priority <high|medium|low>  Priority (default: medium)
  --timeout <minutes>        Timeout in minutes (default: 60)
  --depends-on <ids>         Comma-separated dependency task IDs
  --created-by <agent>       Creating agent (default: cli)
  --max-retries <n>          Max retries (default: 3)

orch task list [options]
  --status <status>          Filter by status
  --agent <name>             Filter by assigned agent

orch task claim <task-id> --agent <name>
orch task complete <task-id> [--result-path <path>] [--summary <text>]
orch task fail <task-id> [--reason <text>]
orch task retry <task-id>
```

### Agent Management

```bash
orch agent register <name> [--capabilities <list>] [--max-concurrent <n>]
orch agent list
orch agent status <name>
```

### Utilities

```bash
orch sweep              # Timeout stale tasks, retry eligible ones
orch refresh            # Regenerate interchange .md files
orch backup [--output <path>]
orch restore <backup-file>
```

## Architecture

SQLite database (`data/`) stores tasks, agents, and state transitions. Tasks flow through `pending → in_progress → completed|failed` with atomic claiming via SQL transactions. The sweep command handles timeouts and auto-retries.

## .md Interchange

Running `orch refresh` generates `.md` status files that other skills and agents can read to understand current task state, agent load, and queue health — all via `@openclaw/interchange`.

## Testing

```bash
npm test
```

13 tests covering task lifecycle, collision-safe claiming, dependency resolution, timeout/retry logic, and agent management.

## Part of the OpenClaw Ecosystem

Orchestration coordinates work across agents. It uses `@openclaw/interchange` for `.md` output, and its task results can feed into `monitoring` for success rate tracking and cost analysis.

## License

MIT
