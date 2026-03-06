---
name: Metrics
slug: metrics
version: 1.0.0
homepage: https://clawic.com/skills/metrics
description: Capture, normalize, and report metrics across any domain with reusable dimensions, programmable formulas, and scalable reporting workflows.
changelog: Initial release with metric registry design, formula governance, and automation-ready reporting workflows.
metadata: {"clawdbot":{"emoji":"📊","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## Setup

On first use, read `setup.md` for integration behavior and memory initialization.

## When to Use

Use this skill when the user needs to define, track, analyze, or report metrics for any domain such as social media, sales, product, operations, finance, or personal systems.

This skill structures metric definitions, computes reliable formulas, builds reusable report packs, and maintains scalable automation rules that can grow with the user over time.

## Architecture

Working memory lives in `~/metrics/`. See `memory-template.md` for base structure and status behavior.

```
~/metrics/
├── memory.md              # HOT: goals, active metrics, reporting cadence
├── registry/              # WARM: metric contracts and dimension dictionaries
├── formulas/              # WARM: formula specs with version history
├── reports/               # WARM: report outputs by cadence and stakeholder
├── automations/           # WARM: scheduled checks and alert policies
└── archive/               # COLD: retired metrics and old report cycles
```

## Quick Reference

Load only the file needed for the current task to keep context focused.

| Topic | File |
|-------|------|
| Setup and integration | `setup.md` |
| Memory schema | `memory-template.md` |
| Metric contract design | `metric-registry.md` |
| Formula design and governance | `formula-playbook.md` |
| Report cadences and templates | `reporting-pack.md` |
| Automation and alerting patterns | `automation-patterns.md` |
| Data validation and quality gates | `data-quality.md` |

## Core Rules

### 1. Define a Metric Contract Before Any Calculation
Every metric must have one clear contract: business meaning, numerator, denominator, source tables, update latency, and owner.

Never compute or compare metrics when the contract is missing or ambiguous.

### 2. Separate Raw Signals from Derived Metrics
Raw events are evidence. Metrics are interpreted aggregates. Keep them separate.

Store and reason in this order:
1. Raw signal
2. Normalized base metric
3. Derived metric
4. Decision recommendation

### 3. Use Dimensions to Scale, Not New One-Off Metrics
When users ask for "the same metric but by X", add a dimension instead of creating a duplicate metric.

Common high-value dimensions:
- Time grain
- Source/channel
- Segment/persona
- Geography
- Product or workflow stage

### 4. Version Formulas and Annotate Breaking Changes
Formulas evolve. Comparability fails when formula changes are not tracked.

For every formula update, store:
- version
- change reason
- impact expectation
- backfill policy
- first report date with new logic

### 5. Reports Must Be Decision-Oriented
A report is incomplete unless each section ties to a decision owner and explicit next action.

Minimum output block for every report:
- What changed
- Why it changed
- What to do now
- Who owns the action
- When to review again

### 6. Automate Thresholds with Response Playbooks
Alerts without response rules create noise.

Each threshold must include:
- trigger condition
- severity level
- owner
- first response action
- escalation condition

### 7. Prefer Reusable Reporting Packs Over Custom One-Offs
Build reusable templates for daily, weekly, monthly, and campaign reports so the system can scale across teams and domains.

Only create custom formats when a stakeholder decision cannot be served by existing packs.

## Common Traps

- Mixing different metric definitions under one name -> trend lines become invalid.
- Changing formulas without version notes -> historical comparisons break silently.
- Reporting totals without segment cuts -> root causes remain hidden.
- Creating too many vanity metrics -> operators lose focus on decision metrics.
- Sending alerts without action ownership -> teams ignore notifications.
- Adding one-off dashboards for every request -> reporting system becomes unmaintainable.

## Security & Privacy

**Data that leaves your machine:**
- None by default.

**Data that stays local:**
- Metrics context and definitions under `~/metrics/`.
- Formula versions, report logs, and alert policies stored locally.

**This skill does NOT:**
- Access files outside `~/metrics/` for memory storage.
- Send metrics to third-party APIs by default.
- Create background automations without explicit user confirmation.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `analytics` — metric analysis patterns and interpretation workflows.
- `dashboard` — KPI visualization design and reporting layouts.
- `report` — structured reporting outputs for stakeholders.
- `sql` — query generation for metric extraction pipelines.
- `excel-xlsx` — spreadsheet-based metric operations and exports.

## Feedback

- If useful: `clawhub star metrics`
- Stay updated: `clawhub sync`
