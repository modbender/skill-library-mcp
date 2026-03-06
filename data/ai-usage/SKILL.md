---
name: ai-usage
description: |
  Check AI usage across Anthropic and other providers.
  Use when:
  1. User asks about AI usage, token usage, or quota
  2. User says "what's my AI usage" or "how much have I used"
  3. User asks about Anthropic/Claude usage or limits
  4. User asks about costs or spending on AI
  5. Monitoring usage during heartbeats (daily check)
---

# AI Usage Check

## Quick Start

```bash
python3 scripts/usage_check.py           # Pretty report with gauges
python3 scripts/usage_check.py --json    # JSON output for scripting
```

## Requirements

- **Python 3.10+** (no pip dependencies — stdlib only)
- **Claude Code** installed and authenticated (`claude` CLI in PATH) — for Anthropic quota
- **OpenClaw** installed — for session log token/cost stats

## What It Shows

**Anthropic (real quota from OAuth API):**
- Weekly utilization % with reset countdown
- 5-hour rolling window %
- Model-specific weekly (Sonnet, Opus) when available
- Extra usage spend vs monthly limit

**Other Providers (from OpenClaw session logs):**
- Token counts and call counts per model
- Auto-detects any provider OpenClaw routes through (Ollama, OpenAI, etc.)

**OpenClaw Anthropic breakdown:**
- Per-model token counts and equivalent API cost

## How It Works

- **Anthropic quota:** `GET https://api.anthropic.com/api/oauth/usage` using Claude Code's OAuth token from `~/.claude/.credentials.json` (requires `user:profile` scope)
- **Token auto-refresh:** If the token is expired, the script automatically refreshes it by invoking `claude --print -p "ok"` (Claude Code refreshes its own OAuth token on any invocation), then re-reads the updated credentials file. If Claude Code isn't installed, Anthropic quota is skipped gracefully.
- **Session stats:** Parses `~/.openclaw/agents/main/sessions/*.jsonl` for per-provider/model token and cost data

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENCLAW_SESSIONS_DIR` | `~/.openclaw/agents/main/sessions` | OpenClaw session log directory |
| `CLAUDE_CREDENTIALS_PATH` | `~/.claude/.credentials.json` | Claude Code credentials file |

## Tips

- Run via **Haiku** or a lightweight model for heartbeat/background checks — the script just needs to execute, no reasoning required
- Use `--json` for programmatic consumption (cron jobs, dashboards, alerts)
- Works with any Anthropic subscription tier (Pro, Max, Team, etc.)
