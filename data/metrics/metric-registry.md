# Metric Registry Guide

Use this guide to define scalable metric contracts.

## Metric Contract Template

For every metric, record:

- Metric name
- Business question answered
- Owner
- Time grain (hourly, daily, weekly, monthly)
- Numerator definition
- Denominator definition (if ratio)
- Required dimensions
- Data source and refresh latency
- Data quality risks
- Review cadence

## Dimension Taxonomy

Use a fixed taxonomy so metrics stay reusable:

| Dimension Class | Examples |
|-----------------|----------|
| Time | date, week, month, quarter |
| Entity | user, account, team, region |
| Acquisition | channel, campaign, source |
| Product | feature, plan, lifecycle stage |
| Commercial | price tier, contract type, ACV band |

If a new request fits an existing class, extend values, not schema.

## Naming Rules

- Use plain names: `activation_rate`, `gross_revenue_retention`, `avg_resolution_time`.
- Keep suffixes consistent: `_count`, `_rate`, `_share`, `_amount`, `_index`.
- Never reuse a retired metric name without a version qualifier.

## Registry Health Check

Run this check before adding a metric:

1. Does this metric map to a decision?
2. Is there one owner?
3. Are numerator and denominator explicit?
4. Can the same question be answered with an existing metric + dimension?
5. Is refresh latency acceptable for the decision cadence?

If any answer is no, redesign before adding.

## Domain Examples

- Social media: engagement rate by platform and content type.
- Product: activation rate by onboarding path.
- Sales: win rate by segment and rep.
- Operations: SLA breach rate by queue and severity.
- Personal systems: weekly habit completion rate by category.
