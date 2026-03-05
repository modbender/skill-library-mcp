# KPI Tracker Skill

Track, analyze, and report on Key Performance Indicators for any business.

## What It Does

When activated, this skill helps you:
- Define and categorize KPIs (revenue, ops, marketing, customer success)
- Set targets and thresholds (green/yellow/red)
- Generate weekly/monthly KPI reports in markdown
- Flag KPIs that are off-track with root cause prompts
- Store historical data in a simple JSON file for trend analysis

## Usage

Tell your agent: "Track these KPIs" or "Give me a KPI report" or "Which metrics are off track?"

### Setup

Create `kpi-config.json` in your workspace:

```json
{
  "kpis": [
    {
      "name": "Monthly Recurring Revenue",
      "category": "revenue",
      "unit": "$",
      "target": 50000,
      "redBelow": 35000,
      "yellowBelow": 45000
    },
    {
      "name": "Customer Churn Rate",
      "category": "customer",
      "unit": "%",
      "target": 3,
      "redAbove": 7,
      "yellowAbove": 5
    }
  ]
}
```

### Recording Data

Say: "Record MRR at $42,000 for this week"

The agent stores entries in `kpi-data.json`:
```json
{
  "entries": [
    { "kpi": "Monthly Recurring Revenue", "value": 42000, "date": "2026-02-13", "note": "Post-launch week" }
  ]
}
```

### Reports

Say: "KPI report" and the agent generates a formatted status board:

```
📊 KPI Report — Week of Feb 10, 2026

🟢 Monthly Recurring Revenue: $48,200 (target: $50,000) — 96.4%
🔴 Customer Churn Rate: 8.1% (target: 3%) — needs attention
🟡 Lead Conversion Rate: 11% (target: 15%) — trending up from 9%

⚠️ Action needed on 1 red, 1 yellow KPI
```

### Trend Analysis

Say: "Show MRR trend" — the agent reads historical entries and summarizes direction, velocity, and whether you'll hit target at current pace.

## How the Agent Should Behave

1. Read `kpi-config.json` for KPI definitions
2. Read/write `kpi-data.json` for historical values
3. When asked for a report: calculate status for each KPI, format with color indicators
4. When a KPI is red: proactively suggest investigation areas
5. When recording: validate the value makes sense (e.g., churn can't be negative)

## File Locations

- Config: `kpi-config.json` (workspace root or custom path)
- Data: `kpi-data.json` (same directory as config)
- Reports: generated on-demand, optionally saved to `reports/kpi-YYYY-MM-DD.md`

## Pro Tip

Pair this with a cron job to generate weekly KPI reports automatically. For deeper business intelligence and pre-built industry KPI templates, check out [AfrexAI Context Packs](https://afrexai-cto.github.io/context-packs/) — drop-in configurations that include KPI frameworks for 10+ industries.
