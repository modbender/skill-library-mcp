---
name: cost-governor
version: 1.0.0
description: Pre-flight cost estimation for subagent spawns and approval gates. Prevents API overspend and surprise billing. Budget control for sessions_spawn calls. Daily spend tracking. Essential for multi-agent OpenClaw deployments.
homepage: https://clawhub.com
changelog: Initial release - Pre-flight gates, historical multipliers, spend tracking
metadata:
  openclaw:
    emoji: "💰"
    requires:
      bins: []
    os:
      - linux
      - darwin
      - win32
---

# Cost Governor - Subagent Cost Control

Pre-flight cost checks before spawning subagents. Tracks spend. Gates expensive operations. **Prevents surprise $300+ bills.**

## Files Included

- `SKILL.md` — This file (agent instructions)
- `README.md` — Human-readable setup guide  
- `cost-tracking-template.md` — Copy this to `notes/cost-tracking.md` to get started
- `lib/cost-tracker.js` — Core estimation and logging library
- `bin/cost-summary.js` — CLI: daily/monthly spend summary

## Problem Solved

You spawn a subagent for "research passive income ideas" on Opus. 30 minutes later: $12 gone. This skill estimates cost **before** execution, requires approval for expensive tasks (>$0.50), and tracks all spend.

## When to Use

- **Before spawning any subagent** — estimate cost, log it
- **Daily spend review** — summarize costs vs budget
- **Post-task reconciliation** — compare estimated vs actual

## Core Rules

1. **Every subagent spawn >$0.50 estimated requires explicit user approval**
2. **All spawns get logged** to `$WORKSPACE/notes/cost-tracking.md`
3. **Estimates use multipliers** from historical data (see Cost Model)
4. **No silent expensive operations** — always surface cost before execution

## Cost Model

Based on historical data from `cost-tracking.md`:

| Task Type | Base Estimate | Multiplier | Effective Estimate |
|-----------|--------------|------------|-------------------|
| Creative (open-ended) | Token estimate | **7.5x** | Apply to all creative tasks |
| Research (bounded) | Token estimate | **3x** | Web search + synthesis |
| Technical (structured) | Token estimate | **2x** | Code, config, structured output |
| Simple (template) | Token estimate | **1.5x** | Fill-in, short responses |

**Model cost rates (approximate per 1K tokens):**
- Claude Opus: ~$0.075 input / $0.375 output
- Claude Sonnet: ~$0.003 input / $0.015 output
- GPT-4: ~$0.03 input / $0.06 output
- Grok 4.1 Fast Reasoning: ~$0.003 input / $0.015 output
- Claude Haiku 4.5: ~$0.0008 input / $0.004 output

### Estimation Formula

```
estimated_cost = (estimated_output_tokens / 1000) * output_rate * task_multiplier
```

**Example:**
- Task: Creative writing (5000 tokens estimated on Opus)
- Calculation: (5000 / 1000) * $0.375 * 7.5 = **$14.06**
- Action: **Require approval** (>$0.50 threshold)

## Setup

1. Create cost tracking file:
```bash
mkdir -p ~/.openclaw/workspace/notes
touch ~/.openclaw/workspace/notes/cost-tracking.md
```

2. Add header to `cost-tracking.md`:
```markdown
# Cost Tracking Log

| Date | Task | Model | Est. | Actual | Ratio | Notes |
|------|------|-------|------|--------|-------|-------|
```

3. Set your daily budget (optional):
```bash
echo "DAILY_BUDGET=20.00" >> ~/.openclaw/workspace/.env
```

## Usage

### Pre-Flight Check (Before Spawning)

```
User: "Research passive income methods"
Agent: Checking cost... Estimated $3.50 (Research task, Opus, ~3K tokens * 3x multiplier). Approve?
User: Yes
Agent: [spawns, logs to cost-tracking.md]
```

### Daily Spend Dashboard

Run manually or via cron:

```markdown
## Daily Spend — 2026-02-21
| Task | Model | Est. | Actual | Ratio |
|------|-------|------|--------|-------|
| PassiveIncomeResearch | Opus | $3.50 | $4.20 | 1.2x |
| AIHardwareResearch | Sonnet | $0.80 | $0.65 | 0.8x |
**Total:** $4.30 est / $4.85 actual
**Budget remaining:** $15.15 / $20.00 daily
```

### Post-Task Reconciliation

After each subagent completes:
1. Check actual cost (if available via `/status`)
2. Log to `cost-tracking.md`
3. Update multipliers if ratio is consistently off

## Triggers

- **Pre-spawn gate**: Before `sessions_spawn`, estimate and log. If >$0.50, ask user.
- **Cron (daily, optional)**: Summarize daily spend, flag overruns.
- **Post-task**: Log actual cost, update multipliers if data available.

## Approval Gate Flow

1. Estimate cost using model + task type + multiplier
2. If estimate ≤ $0.50 → proceed, log silently
3. If estimate > $0.50 → present estimate to user, wait for "approve" / "yes"
4. Log decision (approved/rejected/modified) to tracking file

## Budget Alerts

Set a daily budget cap. When spend exceeds it, the agent stops spawning and notifies you.

**Setup:**
Add to your workspace config or mention it in system prompt:
> "Daily API budget: $XX. Stop spawning subagents if estimated total exceeds this."

**Cron-based daily summary (optional):**
Add to your cron:
```bash
# Daily cost summary at 11 PM
0 23 * * * node ~/.openclaw/workspace/skills/cost-governor/bin/cost-summary.js --daily
```

## Anti-Patterns (What NOT to Do)

- ❌ Spawning Opus for simple lookups (use Sonnet or Haiku)
- ❌ Open-ended creative tasks without cost ceiling ("write a novel")
- ❌ Multiple subagents when one suffices
- ❌ Skipping post-task reconciliation
- ❌ Ignoring consistent ratio mismatches (update multipliers!)

## Advanced: Custom Multipliers

Edit multipliers in your cost-tracking.md header:

```markdown
## Multipliers (Updated 2026-02-21)
- Creative: 10x (our tasks run long)
- Research: 2.5x (bounded queries)
```

Agent reads these on each check.

## Integration with Other Skills

- **sessions_spawn**: Always run cost check before spawning
- **AGENTS.md**: Log cost in agent entry ("Last used: $X.XX")
- **Cron jobs**: Wrap expensive recurring tasks with cost gates

## Troubleshooting

**Q: Estimates are consistently off**
A: Update multipliers in cost-tracking.md based on actual ratios.

**Q: How do I get actual costs?**
A: Use `/status` after subagent completes, or check provider dashboard.

## Why This Matters

Real story from r/LocalLLM (Jan 2026):
> "Left my OpenClaw agent running overnight. Spawned 8 research subagents on Opus. Woke up to $340 API bill. This skill would've saved me."

Don't be that person.

---

**Author:** OpenClaw Community  
**License:** MIT  
**Requires:** OpenClaw with subagent support, `notes/` directory
