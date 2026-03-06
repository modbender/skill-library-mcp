---
name: Retention
description: User retention strategy, cohort analysis, churn prevention, and reactivation campaigns
metadata:
  category: product
  skills: ["retention", "churn", "cohorts", "engagement", "lifecycle"]
---

## Core Metrics

| Metric | Formula | Healthy Range |
|--------|---------|---------------|
| Day 1 retention | Users active day 1 / signups | 40-60% |
| Day 7 retention | Users active day 7 / signups | 20-35% |
| Day 30 retention | Users active day 30 / signups | 10-20% |
| Weekly retention | WAU this week / WAU last week | 85-95% |
| Churn rate | Lost customers / start customers | <5%/month |
| NRR (Net Revenue Retention) | (Start MRR + expansion - churn) / Start MRR | >100% |

## Cohort Analysis

Track by signup week, not calendar week:
- **Horizontal axis**: weeks since signup (0, 1, 2, 3...)
- **Vertical axis**: signup cohort (Jan W1, Jan W2...)
- **Cell value**: % of cohort still active

Identify:
- Which cohorts retain better (product changes, marketing source)
- At which week users drop off (week 2 cliff = aha moment too late)
- Seasonal patterns (holiday signups retain worse)

## Churn Signals

Early warning indicators (flag before churn):
- Login frequency drops 50%+ from baseline
- Core feature usage stops
- Support tickets spike then go silent
- Billing page visits without upgrade
- Team member removals
- Data export requests

## Engagement Loops

Retention requires habit formation:

| Loop Type | Trigger | Action | Reward |
|-----------|---------|--------|--------|
| Personal | Email digest | Review updates | Progress visible |
| Social | Notification | Respond to team | Recognition |
| Content | New content alert | Consume | Knowledge gained |
| Progress | Streak reminder | Complete task | Streak maintained |

Design for variable rewards - predictable = boring.

## Lifecycle Stages

| Stage | Timeframe | Goal | Tactics |
|-------|-----------|------|---------|
| Activation | Day 0-3 | Reach aha moment | Onboarding, setup wizard |
| Engagement | Week 1-4 | Build habit | Usage nudges, tips |
| Retention | Month 1+ | Maintain value | Feature discovery, check-ins |
| Expansion | Ongoing | Increase usage | Upsell, team invites |
| Reactivation | After churn | Win back | Campaigns, incentives |

## Reactivation Campaigns

Timing matters:
- **7 days inactive**: Soft nudge ("We miss you")
- **14 days inactive**: Value reminder + what's new
- **30 days inactive**: Incentive offer (discount, extended trial)
- **90 days inactive**: Last chance + feedback ask

Message formula:
```
[Acknowledge absence] + [New value added] + [Easy re-entry CTA]
"Your dashboard is waiting. We added [feature]. One click to resume →"
```

## Feature Stickiness

Measure which features predict retention:
- **Usage correlation**: Users of feature X retain 2x better
- **Time to feature**: Users who reach feature X in day 1 retain 3x
- **Feature breadth**: Users of 3+ features retain 5x vs 1 feature

Double down on sticky features in onboarding.

## Churn Prevention

When churn signal detected:
1. **Immediate**: In-app message acknowledging drop ("Need help?")
2. **Day 3**: Email from founder (personal, not marketing)
3. **Day 7**: Offer call or live support
4. **Before renewal**: Proactive outreach with usage summary

Cancel flow optimization:
- Ask reason (required, 4-5 options)
- Offer pause instead of cancel
- Show what they'll lose (data, history, price lock)
- Easy return policy ("reactivate anytime, data saved 90 days")

## Retention Benchmarks by Model

| Business Model | Good D30 | Good Monthly Churn |
|----------------|----------|-------------------|
| B2C freemium | 10-15% | N/A (free) |
| B2C subscription | 8-12% | 5-7% |
| B2B SMB | 15-25% | 3-5% |
| B2B Enterprise | 25-40% | 1-2% |

## Common Mistakes

- Measuring retention from signup, not activation
- Treating all churned users the same (voluntary vs involuntary)
- Reactivation emails without new value proposition
- Ignoring payment failures as churn (30-40% of churn is involuntary)
- No segmentation in cohort analysis (power users mask problems)
