---
name: session-cost
description: Analyze OpenClaw session logs to report token usage, costs, and performance metrics grouped by model. Use when the user asks about API spending, token usage, session costs, or wants a usage summary.
metadata: {"openclaw":{"emoji":"📊","requires":{"bins":["node"]}}}
---

# Session Cost

Analyze OpenClaw session logs for token usage, costs, and performance metrics grouped by model.

**Note:** Currently limited to the `main` agent (default path: `~/.openclaw/agents/main/sessions/`). If other agents are added in the future, this could be modified to accept an `--agent` parameter to specify which agent's sessions to analyze.

## Quick Start

```bash
# Summary of all sessions (default path: ~/.openclaw/agents/main/sessions/)
node scripts/session-cost.js

# Show all session details
node scripts/session-cost.js --details

# Show details for a specific session
node scripts/session-cost.js --details abc123
```

## Options

- `--path <dir>` — Directory to scan for `.jsonl` files (default: `~/.openclaw/agents/main/sessions/`)
- `--offset <time>` — Only include sessions from the last N units (`30m`, `2h`, `7d`)
- `--provider <name>` — Filter by model provider (`anthropic`, `openai`, `ollama`, etc.)
- `--details [session-id]` — Show per-session details. Optionally pass a session ID to show just that session (looks for `<id>.jsonl`)
- `--table` — Show details in compact table format (use with `--details`)
- `--format <type>` — Output format: `text` (default), `json`, or `discord`
- `--json` — Shorthand for `--format json` (backwards compat)
- `--help`, `-h` — Show help message

## Examples

```bash
# Last 24 hours summary
node scripts/session-cost.js --offset 24h

# Last 7 days, JSON output
node scripts/session-cost.js --offset 7d --json

# Discord-friendly format (for bots/chat)
node scripts/session-cost.js --format discord

# Discord format with filters
node scripts/session-cost.js --format discord --offset 24h --provider anthropic

# Filter by provider
node scripts/session-cost.js --provider anthropic

# All sessions in compact table format
node scripts/session-cost.js --details --table

# Custom path with details
node scripts/session-cost.js --path /other/dir --details

# Single session detail
node scripts/session-cost.js --details 9df7a399-8254-411b-a875-e7337df73d29

# Anthropic sessions from last 24h in table format
node scripts/session-cost.js --provider anthropic --offset 24h --details --table
```

## Output Format

### Text Summary (Default)

```
Found 42 .jsonl files, 42 matched

====================================================================================================
SUMMARY BY MODEL
====================================================================================================

anthropic/claude-sonnet-4-5-20250929
--------------------------------------------------------------------------------
  Sessions: 30
  Tokens:   1,234,567 (input: 900,000, output: 334,567)
  Cache:    read: 500,000 tokens, write: 200,000 tokens
  Cost:     $12.3456
    Input:       $5.4000
    Output:      $5.0185
    Cache read:  $1.5000  (included in total, discounted rate)
    Cache write: $0.4271  (included in total)
```

### Text Details (`--details`)

Shows per-session breakdown (session ID, model, duration, timestamps, tokens, cache, cost) followed by the model summary.

### Table Format (`--details --table`)

Compact table view with columns: Session, Model, Duration, Tokens, Cache (read/write), Cost.

```
SESSION DETAILS
=============================================================================================================================
Model                           Duration  Tokens        Cache          Cost        Session
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
anthropic/claude-sonnet-4.5     45 min    128.5K        15.2K / 8.1K   $0.3245     abc123def456
anthropic/claude-opus-4         12 min    45.3K         2.1K / 1.5K    $0.8921     xyz789abc012
```

### JSON (`--format json`)

```json
{
  "models": {
    "anthropic/claude-sonnet-4-5-20250929": {
      "sessions": 30,
      "tokens": { "input": 900000, "output": 334567, "total": 1234567 },
      "cache": { "read": 500000, "write": 200000 },
      "cost": { "total": 12.3456, "input": 5.4, "output": 5.0185, "cacheRead": 1.5, "cacheWrite": 0.4271 }
    }
  },
  "grandTotal": { ... }
}
```

### Discord (`--format discord`)

Optimized for chat platforms (Discord, Slack, etc.) - concise, markdown-friendly, no tables:

```
💰 **Usage Summary**
(last 24h)

**Total Cost:** $12.34
**Total Tokens:** 1.2M
**Sessions:** 42

**By Provider:**
• anthropic: $10.50 (950K tokens)
• openai: $1.84 (250K tokens)

**Top Models:**
• anthropic/claude-sonnet-4.5: $8.20 (800K tokens)
• openai/gpt-4o: $1.84 (250K tokens)
• anthropic/claude-opus-4: $2.30 (150K tokens)
```

## Output Fields

- **Sessions** — Number of session files analyzed
- **Tokens** — Total, input, and output token counts
- **Cache** — Cache read and write token counts
- **Cost** — Total cost broken down by input, output, cache read, and cache write
- **Duration** — Session duration in minutes (details mode)
- **Timestamps** — First and last activity timestamps (details mode)
