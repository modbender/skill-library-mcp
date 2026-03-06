---
name: openclaw-tally
description: "Tokens tell you how much you paid. Tasks tell you what you got. Tally tracks every OpenClaw task from start to finish — cost, complexity, and efficiency score."
version: "0.3.1"
metadata:
  {"openclaw": {"emoji": "📊", "runtime": "node", "requires": {"anyBins": ["node", "npm"]}}}
---

# OpenClaw Tally

Reframes AI usage from token-counting to task-completion economics. Instead of "how many tokens?", answer "how much to get X done, and was it worth it?"

## 🛠️ Installation

### 1. Ask OpenClaw (Recommended)
Tell OpenClaw: *"Install the openclaw-tally skill."* The agent will handle the installation and configuration automatically.

### 2. Manual Installation (CLI)
If you prefer the terminal, run:
```bash
clawhub install openclaw-tally
```

## Security & Privacy Declaration

- **Hook**: This skill registers a `message-post` hook and processes **every message**.
- **Local only**: All processing is purely local. No data is sent to any external server.
- **Message content**: The task detector reads message text to identify task boundaries (start/complete/fail signals) using regex pattern matching. **No message text is stored** — only metadata (token count, model, session_id, complexity score) is persisted to the database.
- **Sandboxed storage**: SQLite database defaults to `~/.openclaw/tally/tally.db`. A custom path can be provided for testing.
- **Native dependency**: Requires `better-sqlite3` (native Node.js addon). Installation runs `npm install` which triggers a native build step.
- **Permissions**: No network access. No exec permissions. Filesystem limited to `~/.openclaw/tally/`.

## What It Does

- **Detects tasks** automatically from message streams (Layer 1: Task Detector)
- **Attributes costs** across sessions, sub-agents, and cron triggers (Layer 2: Task Ledger)
- **Computes TES** (Task Efficiency Score) per task, model, and cron (Layer 3: Analytics Engine)

## Commands

- `/tasks list` — Show recent tasks with status, cost, and TES
- `/tasks stats` — Summary statistics for a time period
- `/tasks this-week` — This week's task summary
- `/tasks show <task_id>` — Show task detail
- `/tasks report --dimension model` — Model efficiency report
- `/tasks cron-health` — Cron efficiency and health check

## Complexity Levels

- **L1 (Reflex)**: Single-turn, text-only, no tools
- **L2 (Routine)**: Multi-turn or 1–3 tool calls
- **L3 (Mission)**: Multiple tools + file I/O + external APIs
- **L4 (Campaign)**: Sub-agents + cron + cross-session

## TES (Task Efficiency Score)

```
TES = quality_score / (normalized_cost × complexity_weight)
```

- **> 2.0** 🟢 Excellent
- **1.0–2.0** 🟡 Good
- **0.5–1.0** 🟠 Below average
- **< 0.5** 🔴 Poor
- **0.0** ⚫ Failed

## Usage

When the skill is installed, it automatically hooks into `message-post`. Use the `/tasks` commands above to query analytics. All data is stored locally in `~/.openclaw/tally/tally.db`.

See [PRD.md](./PRD.md) for the full product specification.
