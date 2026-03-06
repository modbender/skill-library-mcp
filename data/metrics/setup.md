# Setup - Metrics

Read this when `~/metrics/memory.md` does not exist or is empty.

Start naturally by asking what the user wants to measure first and what decision those metrics should improve.

## Integration First

Early in the conversation, confirm activation behavior:

- Should this support activate whenever the user discusses KPIs, dashboards, formulas, tracking, or reporting?
- Should it proactively suggest missing metrics and quality checks, or respond only when asked?
- Should metric decisions be logged by default for future sessions?

If the user declines setup details, continue immediately and set integration to `declined`.

## Capture the Minimum Useful Baseline

Collect only high-impact baseline context:

- Domain focus: business, product, marketing, operations, finance, personal, or mixed.
- Primary outcome goals for the next review period.
- Current data sources and update frequency.
- Main reporting audience: operator, manager, executive, client, or mixed.
- Current pain point: unclear definitions, data inconsistency, noisy alerts, or slow reporting.

Ask one focused question at a time. Prioritize fast usefulness over exhaustive intake.

## First-Session Output

Before ending setup, deliver one actionable artifact:

- A metric registry starter with 5-10 high-value metrics.
- A first formula catalog with clear contracts and owners.
- A reporting cadence plan with daily, weekly, and monthly outputs.
- An alert policy draft with severity tiers and response ownership.

## Persistence Rules

When memory is enabled:

- Create `~/metrics/memory.md` from `memory-template.md`.
- Update `last` after meaningful progress.
- Keep notes short, decision-oriented, and version-aware.
- Never store secrets, credentials, or unrelated personal data.
