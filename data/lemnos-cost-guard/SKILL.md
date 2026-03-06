---
name: lemnos-cost-guard
description: "Real-time API cost tracking, context bloat detection, and budget enforcement for OpenClaw agents. Use when setting up cost guardrails, checking daily spend, logging token usage after a task, analyzing context bloat, generating cost reports (daily/weekly/monthly), getting model routing recommendations, or when a user asks about API costs, budget status, or why costs are high."
---

# Lemnos Cost Guard

Track token usage, enforce budgets, detect context bloat, and route to cheaper models.

## Quick Reference

| Script | Purpose |
|--------|---------|
| `scripts/track_cost.py` | Log a cost entry after a task |
| `scripts/cost_report.py` | Generate cost summary |
| `scripts/context_analyzer.py` | Scan workspace for bloat |

Pricing and model routing rules: `references/model_pricing.md`

## Workflow

### After Every Significant Task
Log cost immediately using session delta (session_status before vs after):

```bash
python3 skills/lemnos-cost-guard/scripts/track_cost.py \
  --task "email batch" \
  --input 45000 \
  --output 1200 \
  --model claude-sonnet-4-6
```

Logs to: `logs/cost-YYYY-MM-DD.jsonl`

### Daily Briefing — Cost Summary Block
Run before sending the morning briefing:

```bash
python3 skills/lemnos-cost-guard/scripts/cost_report.py --days 1 --budget 5.00 --format brief
```

Include output verbatim in briefing. Flag anything over 80% of budget.

### Budget Alerts
- **≥80% of $5/day** → warn Nick, pause non-revenue tasks
- **≥100% of $5/day** → hard stop, notify Nick immediately
- **Single call >500K input tokens** → immediate alert
- **I/O ratio >50:1** → context bloat warning, recommend compaction

### Context Bloat Check (run weekly or when costs spike)

```bash
python3 skills/lemnos-cost-guard/scripts/context_analyzer.py \
  --workspace /root/.openclaw/workspace
```

## Context Loading Rules (enforce on every session)

Load ONLY what the current task requires:

| Task | Load |
|------|------|
| Morning briefing | SOUL.md, USER.md, MEMORY.md, HEARTBEAT.md, today's memory |
| Email outreach | MEMORY.md (Lemnos rules only), sent-log.md |
| LinkedIn research | sent-log.md only |
| Crypto/market | MEMORY.md (crypto section only) |
| Heartbeat (nothing to do) | HEARTBEAT.md only |

Do NOT load full MEMORY.md + all skills + all reference files unless the task requires it.

## Model Routing

See `references/model_pricing.md` for full table. Quick rules:
- Simple tasks (format, classify, status check) → Haiku ($0.80/M input)
- Default → Sonnet ($3/M input)  
- Opus → never, unless explicitly requested

## Cost Log Format

Each entry in `logs/cost-YYYY-MM-DD.jsonl`:
```json
{
  "ts": "2026-02-24T18:00:00Z",
  "task": "email batch send",
  "model": "claude-sonnet-4-6",
  "input_tokens": 45000,
  "output_tokens": 1200,
  "ratio": 37.5,
  "cost_usd": 0.153,
  "notes": "batch 1 + batch 2"
}
```

## ClawHub Distribution

Free tier: daily cost tracking + budget alerts
Premium ($40-60/mo): full dashboards, model routing automation, context optimization reports, weekly/monthly rollups

Skill file: `lemnos-cost-guard.skill`
