---
name: LLM Cost Guard — Token Budget & Spend Monitor
description: Track, budget, and alert on LLM API spending in real-time. Prevents
  runaway costs for AI agents, multi-user apps, and homelab automation.
---

# LLM Cost Guard — Token Budget & Spend Monitor

Track, budget, and alert on LLM API spending in real-time. Prevents runaway costs for AI agents, multi-user apps, and homelab automation.

## What It Does

- **Real-time cost tracking** — records every LLM call (tokens in/out, model, cost)
- **Budget enforcement** — blocks requests when daily/monthly budgets are exceeded
- **Per-user quotas** — free tier vs pro tier controls
- **Daily spend reports** — delivered via WhatsApp/Telegram/Discord
- **Alerts** — warns at 80% budget usage, blocks at 100%
- **Multi-model pricing** — OpenAI, Anthropic, Groq, Ollama (Feb 2026 rates)

## Quick Start

After install, configure your daily budget:

```
set budget daily 5.00
```

Then register API calls via the tracker:

```bash
# Log an LLM call
llm-cost-guard log --model gpt-4o --input-tokens 1500 --output-tokens 800 --user alice

# Check current spend
llm-cost-guard status

# View full report
llm-cost-guard report
```

## Commands

| Command | Description |
|---------|-------------|
| `llm-cost-guard status` | Current spend vs budget |
| `llm-cost-guard report` | Full breakdown by user/model/day |
| `llm-cost-guard set-limit daily <USD>` | Set daily spend limit |
| `llm-cost-guard set-limit user <key> <USD>` | Set per-user limit |
| `llm-cost-guard reset` | Reset counters (e.g., start of new period) |
| `llm-cost-guard watch` | Live tail of all LLM calls |
| `llm-cost-guard log` | Record a manual LLM usage entry |

## Configuration

```json
{
  "dailyCostLimit": 5.00,
  "monthlyCostLimit": 50.00,
  "perUserDailyCostLimit": 1.00,
  "defaultModel": "gpt-4o-mini",
  "alertAt": 0.8,
  "alertChannel": "whatsapp",
  "dataPath": "~/.openclaw/workspace/llm-cost-guard-data.json"
}
```

## Supported Models (Built-in Pricing)

| Provider | Models |
|----------|--------|
| **OpenAI** | gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-3.5-turbo, o1, o1-mini, o3-mini |
| **Anthropic** | claude-3-5-sonnet, claude-3-5-haiku, claude-3-opus, claude-sonnet-4, claude-haiku-4 |
| **Groq** | llama-3.3-70b, llama-3.1-8b, mixtral-8x7b, gemma2-9b |
| **Ollama** | Local models (free, $0 tracked) |

## OpenClaw Cron Integration

The skill auto-installs a daily cron job to:
1. Send a morning spend summary
2. Alert if yesterday's spend exceeded budget
3. Reset daily counters at midnight UTC

```bash
# Manually add cron
openclaw cron add "0 8 * * *" "llm-cost-guard report --send-to whatsapp"
```

## Use Cases

### Homelab AI Automation
You run multiple OpenClaw agents with different API budgets. This skill tracks each agent's spend independently and warns you before the bill arrives.

### Multi-User Chatbot
Users get a free daily quota (e.g., $0.50/day). This skill enforces it, returning a friendly 429 when exceeded.

### Cost Audit
Run `llm-cost-guard report --period month` to see your full monthly AI spend breakdown by model and user.

## Data Storage

All data stored locally at `~/.openclaw/workspace/llm-cost-guard-data.json`. No external services. No telemetry.

## Why Zero Dependencies?

Every dependency is a potential VirusTotal flag, a supply chain risk, and a maintenance burden. This skill uses only Node.js stdlib and OpenClaw's built-in tools.

## Source & Issues

- **Source:** https://github.com/mariusfit/llm-token-budget
- **Issues:** https://github.com/mariusfit/llm-token-budget/issues
- **Author:** [@mariusfit](https://github.com/mariusfit)
