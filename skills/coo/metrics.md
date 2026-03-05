# Operational Metrics

## Leading vs Lagging Indicators

| Type | Definition | Example |
|------|------------|---------|
| Leading | Predicts future outcomes | Pipeline, activity metrics |
| Lagging | Confirms what happened | Revenue, churn |

**Balance both:** Leading indicators let you act; lagging indicators confirm results.

## Operational Dashboard Design

### Principles

- **Actionable:** Every metric should prompt a question or action
- **Current:** Data fresh enough to be useful
- **Contextual:** Show trends, targets, comparisons
- **Limited:** 5-10 metrics max; more = less attention

### Dashboard Layout

```
┌─────────────────────────────────────┐
│  North Star Metric      [Target]   │
├─────────────────────────────────────┤
│  Health Indicators (3-5)           │
│  ● Metric 1: [value] [trend]       │
│  ● Metric 2: [value] [trend]       │
│  ● Metric 3: [value] [trend]       │
├─────────────────────────────────────┤
│  Alerts / Items Needing Attention  │
└─────────────────────────────────────┘
```

## Key Operational Metrics by Function

### General Operations

| Metric | Formula | Target |
|--------|---------|--------|
| Process cycle time | End time - Start time | Decreasing |
| Throughput | Units completed / Time period | Increasing |
| Error rate | Errors / Total transactions | < X% |
| Capacity utilization | Actual output / Max output | 70-85% |

### Customer Operations

| Metric | Formula | Target |
|--------|---------|--------|
| Response time | Time to first response | < X hours |
| Resolution time | Time to close ticket | < X hours |
| CSAT | Survey score | > X |
| First contact resolution | Resolved first touch / Total | > X% |

### People Operations

| Metric | Formula | Target |
|--------|---------|--------|
| Time to hire | Offer accepted - Req opened | < X days |
| Offer acceptance rate | Accepted / Extended | > X% |
| Voluntary turnover | Departures / Headcount | < X% |
| eNPS | Promoters - Detractors | > X |

## Operational Review Cadence

### Weekly Review (30-60 min)

- What happened vs plan
- Blockers and escalations
- Next week's priorities

### Monthly Review (60-90 min)

- Month-over-month trends
- Process improvement opportunities
- Resource planning

### Quarterly Review (Half day)

- Progress against OKRs
- Capacity planning next quarter
- Major process changes

## Variance Analysis

When metrics miss target:

### 5 Whys Method

```
Problem: Cycle time increased 50%
Why? → More rework needed
Why? → Requirements unclear
Why? → Specs not reviewed
Why? → No review process
Why? → Never prioritized

Root cause: Missing spec review process
Fix: Implement spec review checklist
```

### Action Response Framework

| Variance | Response |
|----------|----------|
| < 5% | Monitor, no action |
| 5-15% | Investigate, document |
| 15-30% | Action plan required |
| > 30% | Immediate intervention |
