---
name: ai-displacement-monitor
description: Monitor early-warning signals of AI-driven white-collar labor displacement and macro-financial spillovers. Use when you need a practical indicator framework, thresholds, alert logic, and concise risk updates for employment, consumption, and credit stress.
---

# AI Displacement Monitor

Use this skill to produce a structured risk monitor for AI-led labor substitution and downstream financial stress.

## Output Format

Always return:
1. **Signal Board** (10 indicators with latest value, direction, threshold status)
2. **Composite Risk Light** (`GREEN` / `YELLOW` / `ORANGE` / `RED`)
3. **Actionable Notes** (portfolio/risk posture suggestions)
4. **Data Gaps** (missing or stale inputs)

## Indicator Framework

Read `references/thresholds.example.json` and follow its indicator IDs, thresholds, and tiering.

Also apply the "Industrial-Revolution Lens" when interpreting risk:
- Do not evaluate layoffs alone.
- Compare **substitution speed** vs **re-absorption speed** (new demand + new capex).
- If substitution weakens labor but capex/reinvestment accelerates, avoid over-escalating crisis labels.

- **Tier A (Leading labor demand)**: A1-A4
- **Tier B (Labor market confirmation)**: B1-B3
- **Tier C (Spillover: consumption/credit)**: C1-C3

## Composite Rule

- **YELLOW**: Tier A triggered >= 2
- **ORANGE**: Tier A >= 2 and Tier B >= 1
- **RED**: Tier A >= 2 and Tier B >= 1 and Tier C >= 1
- **GREEN**: otherwise

## Weak-Links Interpretation (Jones Lens)

When assessing macro impact, apply a weak-links check:
- Broad automation can still deliver gradual macro gains if key bottleneck tasks remain scarce.
- Do not infer immediate macro collapse from partial task automation alone.
- If bottleneck proxies remain tight (D3 worsening, D4 weak reinvestment), keep risk elevated.
- If bottlenecks ease via reinvestment/capex and purchasing power improves (D1/D2), avoid over-escalation.

## Minimum Quality Rules

- Time-stamp each metric and note frequency mismatch (weekly vs monthly vs quarterly).
- If source coverage is partial, mark confidence as `low` or `medium`.
- Never hide missing data; list it under **Data Gaps**.
- If more than 3 indicators are missing, downgrade confidence by one level.

## Recommended Alert Style

Keep alerts short and decision-oriented:
- "What changed"
- "Why it matters now"
- "What to do next"

## Optional JSON Mode

If user asks for machine-readable output, return:
- `asOf`
- `signals[]` (id, value, unit, threshold, triggered, trend)
- `composite`
- `confidence`
- `gaps[]`
- `notes[]`
