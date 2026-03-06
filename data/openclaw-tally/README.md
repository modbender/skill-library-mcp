# OpenClaw Tally

> Tokens tell you how much you paid. Tasks tell you what you got.

**Task-level efficiency analytics for OpenClaw.** Stop counting tokens — start measuring what actually got done and what it cost.

## 🛠️ Installation

### 1. Ask OpenClaw (Recommended)
Tell OpenClaw: *"Install the openclaw-tally skill."* The agent will handle the installation and configuration automatically.

### 2. Manual Installation (CLI)
If you prefer the terminal, run:
```bash
clawhub install openclaw-tally
```

## Quick Start

```bash
# 1. Install dependencies
npm install

# 2. Initialize the database
npm run migrate

# 3. Start using in OpenClaw
#    The skill hooks into message-post automatically.
#    Use /tasks commands to view analytics.
```

## Security & Privacy

- **Local only**: All data stays on your machine. No external network calls.
- **No message content stored**: Only metadata (token count, model, session_id).
- **Sandboxed writes**: Database is hardcoded to `~/.openclaw/tally/tally.db`.
- **Hook scope**: Registered on `message-post` — processes every message's metadata only.

## Core Concepts

### Task

A unit of user intent — from a simple question ("What time is it in Tokyo?") to a multi-day campaign ("Scan job market daily"). Every dollar spent is attributed to a task.

### TES (Task Efficiency Score)

```
TES = quality_score / (normalized_cost × complexity_weight)
```

Higher is better. A TES > 2.0 means excellent value; < 0.5 means you're overpaying.

### Complexity Levels

- **L1 (Reflex)**: Single-turn Q&A, no tools
- **L2 (Routine)**: Multi-turn or 1–3 tool calls
- **L3 (Mission)**: Multiple tools + file I/O + external APIs
- **L4 (Campaign)**: Sub-agents + cron + cross-session continuity

## CLI Commands

- `/tasks list [--level L3] [--status completed]` — List recent tasks
- `/tasks stats [--period 30d]` — Summary statistics
- `/tasks this-week` — This week's task summary
- `/tasks show <task_id>` — Task detail view
- `/tasks report --dimension model` — Model efficiency breakdown
- `/tasks cron-health` — Cron job health check

## Architecture

Three-layer design:

1. **Task Detector** — Identifies task boundaries from message stream
2. **Task Ledger** — Attributes token costs to task IDs (SQLite)
3. **Analytics Engine** — Computes TES and powers dashboards/reports

## Full Specification

See [PRD.md](./PRD.md) for the complete product requirements document.

## License

MIT © Jony Jing
