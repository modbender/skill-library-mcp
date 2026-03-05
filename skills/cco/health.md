# Customer Health Scoring

## Health Score Components

### Usage Metrics (40% weight)
- **Login frequency** — Daily/weekly active users vs licenses
- **Feature adoption** — Breadth of product usage
- **Depth of usage** — Power features, advanced workflows
- **Usage trend** — Growing, stable, or declining

### Engagement Metrics (30% weight)
- **Support tickets** — Volume and sentiment (high volume can be good or bad)
- **Response rates** — Email opens, meeting attendance
- **Training completion** — Onboarding and ongoing education
- **Community participation** — Forums, events, user groups

### Relationship Metrics (20% weight)
- **Executive sponsor status** — Active, changed, or departed
- **Champion health** — Main contact engagement level
- **Stakeholder breadth** — Single-threaded vs multi-threaded
- **NPS/CSAT scores** — Survey feedback

### Business Metrics (10% weight)
- **Contract value trend** — Expanding or contracting
- **Payment history** — On-time, late, disputes
- **Company health** — Growth signals, funding, news

## Scoring Models

### Simple Scoring (Early Stage)
```
Health = (Usage Score + Engagement Score + Relationship Score) / 3

Green: 70-100 — Healthy, expansion opportunity
Yellow: 40-69 — At risk, needs attention
Red: 0-39 — Critical, immediate intervention
```

### Weighted Scoring (Mature)
```
Health = (Usage × 0.4) + (Engagement × 0.3) + (Relationship × 0.2) + (Business × 0.1)
```

Adjust weights based on what actually predicts churn in your data.

## Early Warning Signals

### Immediate Action Required
- Executive sponsor departed
- Usage dropped >50% in 30 days
- Support escalation to leadership
- Competitor mentioned in calls
- Renewal pushed or questioned

### Monitor Closely
- Champion role changed
- Usage declined 3 consecutive weeks
- Training sessions declined
- Meeting no-shows increased
- Feature requests stopped

### Positive Signals
- New use cases emerging
- Additional teams onboarding
- Executive engagement increasing
- Reference or case study interest
- Proactive expansion questions

## Health Score Cadence

| Segment | Calculation Frequency | Review Cadence |
|---------|----------------------|----------------|
| Enterprise | Real-time | Weekly |
| Mid-market | Daily | Bi-weekly |
| SMB | Weekly | Monthly |

## Building Your First Health Score

1. **Start simple** — Usage + engagement + relationship
2. **Validate against outcomes** — Does low score predict churn?
3. **Iterate quarterly** — Add/remove signals based on data
4. **Automate alerts** — Don't rely on manual review
5. **Trust but verify** — Health scores lie sometimes; investigate anomalies

## Common Health Score Mistakes

- Too many inputs — Keep it under 10 signals
- All signals equal weight — Some predict churn better
- No validation — Score doesn't correlate with outcomes
- Static thresholds — Different for different segments
- Ignoring trends — Current score matters less than direction
