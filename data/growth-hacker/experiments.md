# Experiments Framework — Growth Hacker

## Experiment Document Template

```markdown
## Experiment: [Name]
**Date:** YYYY-MM-DD
**Owner:** [Name]
**Status:** Planning | Running | Analyzing | Completed

### Hypothesis
If we [action], then [metric] will [change] because [reason].

### Metrics
- Primary: [Metric to move]
- Secondary: [Guard rails]
- Sample size needed: [Number]

### Design
- Control: [Current state]
- Variant: [Change being tested]
- Duration: [Days/weeks]
- Audience: [Segment]

### Results
- Control: [Result]
- Variant: [Result]
- Lift: [Percentage]
- Confidence: [Statistical significance]

### Decision
[ ] Ship variant
[ ] Keep control
[ ] Iterate and retest

### Learnings
[What we learned regardless of outcome]
```

## Experiment Prioritization (ICE Score)

| Factor | Scale | Description |
|--------|-------|-------------|
| Impact | 1-10 | How much will this move the needle? |
| Confidence | 1-10 | How sure are we it will work? |
| Ease | 1-10 | How easy is it to implement? |

**ICE Score = (Impact + Confidence + Ease) / 3**

Run experiments with highest ICE first.

## Weekly Experiment Cadence

| Day | Activity |
|-----|----------|
| Monday | Review last week results, plan new experiments |
| Tuesday-Thursday | Run experiments, collect data |
| Friday | Analyze results, document learnings |

## Minimum Viable Experiments

### Landing Page Tests
- Headline variations (5 min to set up)
- CTA button text and color
- Social proof placement
- Pricing display

### Onboarding Tests
- Number of steps
- Required vs optional fields
- Tutorial vs immediate access
- Progress indicators

### Retention Tests
- Email timing and frequency
- Push notification copy
- Re-engagement triggers
- Feature discovery prompts

### Viral Tests
- Share button placement
- Referral incentives
- Social proof displays
- Invite flow friction

## Statistical Significance Quick Guide

| Sample Size | Minimum Lift Detectable |
|-------------|------------------------|
| 100 per variant | ~30% lift |
| 500 per variant | ~15% lift |
| 1,000 per variant | ~10% lift |
| 5,000 per variant | ~5% lift |

**Rule:** If you need to squint to see the difference, you need more data.

## Failed Experiment Value

Every failed experiment teaches you:
1. What your users do NOT want
2. Assumptions that were wrong
3. Segments that behave differently
4. Ideas for new experiments

**Document failures as rigorously as wins.**
