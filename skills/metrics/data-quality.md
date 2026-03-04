# Data Quality Gates

Use this checklist before computing formulas or shipping reports.

## Core Quality Checks

Run in this order:

1. Completeness: expected rows and fields are present.
2. Freshness: data timestamp is within allowed latency.
3. Uniqueness: keys are not duplicated unexpectedly.
4. Consistency: units and value scales match definitions.
5. Reconciliation: segment sums match top-line totals.

## Drift Detection

Detect drift for each critical metric:

- Definition drift: source logic changed without version note.
- Distribution drift: value profile shifted beyond expected band.
- Pipeline drift: refresh latency or missing partitions increased.

## Scorecard Template

| Check | Status | Severity | Owner | Action |
|-------|--------|----------|-------|--------|
| Freshness | pass/fail | warning/critical | name | response |
| Completeness | pass/fail | warning/critical | name | response |
| Reconciliation | pass/fail | warning/critical | name | response |

## Release Rule

If any critical quality check fails:

- Block report publication.
- Publish incident summary instead of metric values.
- Route owner to investigation workflow.

## Incident Note Template

- Metric affected:
- Check failed:
- Suspected root cause:
- Immediate mitigation:
- ETA for fix:
- Confidence in current numbers:
