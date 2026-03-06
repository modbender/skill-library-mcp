---
name: "Stock Market"
slug: stock-market
version: "1.0.0"
homepage: https://clawic.com/skills/stock-market
description: "Analyze stock market setups with thesis checks, catalyst mapping, risk controls, and explicit trade or no-trade decisions."
changelog: "Initial release with a market briefing workflow, watchlist template, and risk controls for disciplined stock analysis."
metadata: {"clawdbot":{"emoji":"📈","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## Setup

If `~/stock-market/` does not exist or is empty, explain that local planning files can be created for this skill and follow `setup.md`.

## When to Use

User needs stock market analysis, watchlist planning, or trade decision support. Handles pre-market briefings, thesis validation, catalyst tracking, and risk-managed execution planning.

## Architecture

Memory lives in `~/stock-market/`. See `memory-template.md` for structure.

```
~/stock-market/
├── memory.md         # Status, constraints, and recurring preferences
├── watchlist.md      # Active tickers and setup notes
├── briefing-log.md   # Pre-market and post-market summaries
└── risk-rules.md     # Position sizing and risk guardrails
```

## Quick Reference

| Topic | File |
|-------|------|
| Setup and integration | `setup.md` |
| Memory template | `memory-template.md` |
| Analysis workflow | `analysis-framework.md` |
| Watchlist structure | `watchlist-template.md` |
| Risk controls | `risk-playbook.md` |
| Daily briefing format | `briefing-template.md` |

## Core Rules

### 1. Define Market Objective First
Set the objective before analysis: intraday trade, swing setup, position build, or no-trade monitoring. Every recommendation must match the selected horizon.

### 2. Separate Facts, Assumptions, and Narrative
Tag each statement as market data, inferred assumption, or narrative hypothesis. If the thesis depends on assumptions, list the proof needed before execution.

### 3. Anchor Every Setup to Catalyst and Timing
Document the nearest catalyst window (earnings, macro release, company event, sector move) and timing risk. Avoid entries without a clear catalyst or structural setup.

### 4. Convert Thesis into Trigger and Invalidation
Do not leave analysis as commentary. Define entry trigger, invalidation level, and expected path so the outcome can be judged objectively.

### 5. Enforce Position Risk Before Opportunity
Use `risk-playbook.md` before selecting size. If position risk, liquidity, or volatility exceeds limits, downgrade size or mark no-trade.

### 6. Keep a Living Watchlist with Priority
Maintain a ranked watchlist in `watchlist-template.md` format: setup quality, catalyst proximity, and risk-adjusted upside. Re-rank after major market events.

### 7. Close the Loop with Post-Action Review
After each trade or no-trade call, log what happened in `briefing-template.md` format and update `~/stock-market/memory.md` with reusable lessons.

## Stock Market Traps

- Treating broad market direction as enough evidence -> low conviction entries with weak asymmetric upside.
- Ignoring macro event timing -> avoidable stop-outs during high volatility windows.
- Confusing price momentum with thesis quality -> chasing late moves without defined invalidation.
- Oversizing after a winning streak -> risk concentration and emotional decision drift.
- Skipping no-trade outcomes in logs -> repeated mistakes with no learning loop.

## Security & Privacy

**Data that leaves your machine:**
- None by default. This skill is designed for local analysis and planning artifacts.

**Data that stays local:**
- Watchlists, briefings, and user preferences in `~/stock-market/`.

**This skill does NOT:**
- Place broker orders automatically.
- Execute trades without explicit user approval.
- Access files outside `~/stock-market/` for memory storage.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `trading` — structure trade execution plans and operational checklists.
- `economics` — interpret macro indicators and policy signals impacting markets.
- `market-research` — build market landscape analysis for sectors and themes.
- `business-intelligence` — convert market data into dashboards and decision reporting.

## Feedback

- If useful: `clawhub star stock-market`
- Stay updated: `clawhub sync`
