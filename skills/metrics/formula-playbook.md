# Formula Playbook

Use this playbook to design robust formulas and avoid silent drift.

## Formula Spec Template

For each formula, document:

- Formula name
- Version
- Input metrics
- Exact equation
- Null and zero handling
- Output unit
- Expected range
- Failure modes
- Backfill policy

## Formula Categories

| Category | Purpose | Example |
|----------|---------|---------|
| Base ratio | Compare two aligned quantities | conversion_rate = converted / qualified |
| Efficiency | Relate output to cost | revenue_per_employee |
| Quality index | Weighted composite health signal | support_quality_index |
| Trend velocity | Measure direction and speed | week_over_week_delta |
| Forecast helper | Project near-term outcomes | run_rate_projection |

## Governance Rules

- Version every formula change, even small edits.
- Keep old and new formulas side by side during transition periods.
- Annotate why the change happened and expected directional impact.
- Mark metrics as "not comparable" across periods when formulas changed.

## Guardrail Patterns

Use guardrails to prevent invalid outputs:

- Denominator zero -> return null and explanation.
- Missing input over threshold -> block report publication.
- Outlier surge over defined z-score -> add anomaly flag.
- Unit mismatch -> fail fast and request normalization.

## Example Formula Block

```text
name: creator_efficiency_index
version: v1.2.0
equation: (qualified_leads * avg_deal_value) / content_hours
null_policy: block_if_missing_input_gt_5_percent
expected_range: 0 to 10000
change_reason: aligned lead qualification criteria with sales SLA
```

## Formula Review Checklist

- Equation answers the intended business question.
- Inputs are available at the target cadence.
- Unit conversions are explicit.
- Edge cases are defined.
- Version note is logged.
