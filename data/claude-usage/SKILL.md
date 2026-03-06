---
name: claude-usage
description: Calculate Claude Max subscription usage from OpenClaw session data. Shows credits consumed, weekly budget percentage, 5-hour rate limit window, and per-session breakdown.
---

# Claude Max Usage Calculator

Track your Claude Max subscription usage based on the reverse-engineered credits system from [she-llac.com/claude-limits](https://she-llac.com/claude-limits).

## When to use

When the user asks about Claude usage, credits, subscription consumption, rate limits, or wants to know how much budget is left.

## Setup (first time)

Ask the user for:
1. **Weekly reset time** — visible on [claude.ai](https://claude.ai) Settings > Usage (e.g. "Resets Mon 2:00 PM")
2. **Plan** — `pro` ($20), `5x` ($100), or `20x` ($200). Default: `5x`

Save it so they never have to repeat:
```bash
python3 {SKILL_DIR}/scripts/claude-usage.py "2026-02-09 14:00" --plan 5x --save
```

## Commands

```bash
# Weekly overview (uses saved config after first --save)
python3 {SKILL_DIR}/scripts/claude-usage.py

# Override plan or timezone
python3 {SKILL_DIR}/scripts/claude-usage.py --plan 20x --tz "America/New_York"

# Top N sessions only
python3 {SKILL_DIR}/scripts/claude-usage.py --top 5

# Single session detail (substring match on key or id)
python3 {SKILL_DIR}/scripts/claude-usage.py --session "main"
python3 {SKILL_DIR}/scripts/claude-usage.py --session "9aadee"

# JSON output
python3 {SKILL_DIR}/scripts/claude-usage.py --json
```

## What it shows

### Weekly overview
- Total credits used vs weekly budget (with progress bar)
- **5-hour sliding window** — warns if approaching the per-5h rate limit
- All sessions ranked by credits consumed
- Model breakdown (Opus/Sonnet/Haiku/non-Claude)

### Single session detail (`--session`)
- Credits consumed and % of weekly budget
- % of total usage (how much of your spending this session accounts for)
- Token breakdown (input/output/cache)
- Per-model detail

## Credits formula

```
credits = (input_tokens + cache_write_tokens) × input_rate + output_tokens × output_rate
```

| Model  | Input rate | Output rate |
|--------|-----------|-------------|
| Haiku  | 2/15      | 10/15       |
| Sonnet | 6/15      | 30/15       |
| Opus   | 10/15     | 50/15       |

Cache reads are **free**. Non-Claude models (Gemini, Codex, etc.) don't consume Claude credits.

## Plan budgets

| Plan | $/month | Credits/5h | Credits/week |
|------|---------|-----------|-------------|
| Pro  | $20     | 550,000   | 5,000,000   |
| 5×   | $100    | 3,300,000 | 41,666,700  |
| 20×  | $200    | 11,000,000| 83,333,300  |

## Requirements

- Python 3.9+
- OpenClaw with session JSONL files (auto-detected at `~/.openclaw/agents/main/sessions/`)
