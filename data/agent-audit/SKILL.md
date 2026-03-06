---
name: agent-audit
description: >
  Audit your AI agent setup for performance, cost, and ROI. Scans OpenClaw config, cron jobs,
  session history, and model usage to find waste and recommend optimizations.
  Works with any model provider (Anthropic, OpenAI, Google, xAI, etc.).
  Use when: (1) user says "audit my agents", "optimize my costs", "am I overspending on AI",
  "check my model usage", "agent audit", "cost optimization", (2) user wants to know which
  cron jobs are expensive vs cheap, (3) user wants model-task fit recommendations,
  (4) user wants ROI analysis of their agent setup, (5) user says "where am I wasting tokens".
---

# Agent Audit

Scan your entire OpenClaw setup and get actionable cost/performance recommendations.

## What This Skill Does

1. **Scans config** — reads OpenClaw config to map models to agents/tasks
2. **Analyzes cron history** — checks every cron job's model, token usage, runtime, success rate
3. **Classifies tasks** — determines complexity level of each task
4. **Calculates costs** — per agent, per cron, per task type using provider pricing
5. **Recommends changes** — with confidence levels and risk warnings
6. **Generates report** — markdown report with specific savings estimates

## Running the Audit

```bash
python3 {baseDir}/scripts/audit.py
```

Options:
```bash
python3 {baseDir}/scripts/audit.py --format markdown    # Full report (default)
python3 {baseDir}/scripts/audit.py --format summary     # Quick summary only
python3 {baseDir}/scripts/audit.py --dry-run             # Show what would be analyzed
python3 {baseDir}/scripts/audit.py --output /path/to/report.md  # Save to file
```

## How It Works

### Phase 1: Discovery
- Read OpenClaw config (`~/.openclaw/openclaw.json` or similar)
- List all cron jobs and their configurations
- List all agents and their default models
- Detect provider (Anthropic, OpenAI, Google, xAI) from model names

### Phase 2: History Analysis
- Pull cron job run history (last 7 days by default)
- Calculate per-job: avg tokens, avg runtime, success rate, model used
- Pull session history where available
- Calculate total token spend by model tier

### Phase 3: Task Classification
Classify each task into complexity tiers:

| Tier | Examples | Recommended Models |
|------|----------|-------------------|
| **Simple** | Health checks, status reports, reminders, notifications | Cheapest tier (Haiku, GPT-4o-mini, Flash, Grok-mini) |
| **Medium** | Content drafts, research, summarization, data analysis | Mid tier (Sonnet, GPT-4o, Pro, Grok) |
| **Complex** | Coding, architecture, security review, nuanced writing | Top tier (Opus, GPT-4.5, Ultra, Grok-2) |

Classification signals:
- **Simple**: Short output (<500 tokens), low thinking requirement, repetitive pattern, status/health tasks
- **Medium**: Medium output, some reasoning needed, creative but templated, research tasks
- **Complex**: Long output, multi-step reasoning, code generation, security-critical, tasks that previously failed on weaker models

### Phase 4: Recommendations
For each task where the model tier doesn't match complexity:

```
⚠️ RECOMMENDATION: Downgrade "Knox Bot Health Check" from opus to haiku
   Current: anthropic/claude-opus-4 ($15/M input, $75/M output)
   Suggested: anthropic/claude-haiku ($0.25/M input, $1.25/M output)
   Reason: Simple status check averaging 300 output tokens
   Estimated savings: $X.XX/month
   Risk: LOW — task is simple pattern matching
   Confidence: HIGH
```

### Safety Rules — NEVER Recommend Downgrading:
- Coding/development tasks
- Security reviews or audits
- Tasks that have previously failed on weaker models
- Tasks where the user explicitly chose a higher model
- Complex multi-step reasoning tasks
- Anything the user flagged as critical

### Phase 5: Report Generation
Output a clean markdown report with:
1. **Overview** — total agents, crons, monthly spend estimate
2. **Per-agent breakdown** — model, usage, cost
3. **Per-cron breakdown** — model, frequency, avg tokens, cost
4. **Recommendations** — sorted by savings potential
5. **Total potential savings** — monthly estimate
6. **One-liner config changes** — exact model strings to swap

## Model Pricing Reference

See [references/model-pricing.md](references/model-pricing.md) for current pricing across all providers.
Update this file when prices change.

## Task Classification Details

See [references/task-classification.md](references/task-classification.md) for detailed heuristics
on how tasks are classified into complexity tiers.

## Important Notes

- This skill is **read-only** — it never changes your config automatically
- All recommendations include risk levels and confidence scores
- When unsure about a task's complexity, it defaults to keeping the current model
- The audit should be re-run periodically (monthly) as usage patterns change
- Token counts are estimates based on cron history — actual costs depend on your provider's billing
