# Prioritization Frameworks — Product Owner

## Value/Effort Matrix

Simplest approach. Plot stories on 2x2:

```
        High Value
             │
    Quick    │    Big Bets
    Wins     │    (plan carefully)
             │
─────────────┼─────────────
             │
    Fill     │    Money Pit
    Ins      │    (avoid)
             │
        Low Value
    Low Effort ─────── High Effort
```

**Quick Wins** — Do first. High value, low effort.
**Big Bets** — Plan carefully. High value, high effort.
**Fill Ins** — Do when nothing else. Low value, low effort.
**Money Pit** — Avoid. Low value, high effort.

## MoSCoW

Fast categorization for stakeholder alignment:

| Category | Meaning | Guideline |
|----------|---------|-----------|
| Must | Critical, non-negotiable | ~60% of capacity |
| Should | Important but not critical | ~20% of capacity |
| Could | Nice to have | ~10% of capacity |
| Won't | Not this time | Explicitly excluded |

### Usage
1. Stakeholders categorize independently
2. Discuss disagreements
3. PO makes final call
4. Document rationale

## RICE

Data-driven scoring:

```
RICE Score = (Reach × Impact × Confidence) / Effort
```

| Factor | Definition | Scale |
|--------|------------|-------|
| Reach | Users affected per quarter | Actual number |
| Impact | Effect on each user | 3=massive, 2=high, 1=medium, 0.5=low, 0.25=minimal |
| Confidence | How sure are we? | 100%=high, 80%=medium, 50%=low |
| Effort | Person-months | Actual estimate |

### Example
```
Feature: One-click checkout
Reach: 10,000 users/quarter
Impact: 2 (high)
Confidence: 80%
Effort: 2 person-months

RICE = (10000 × 2 × 0.8) / 2 = 8,000
```

## WSJF (Weighted Shortest Job First)

Best when cost of delay matters:

```
WSJF = Cost of Delay / Job Size
```

Cost of Delay = User Value + Time Criticality + Risk Reduction

| Factor | 1 | 2 | 3 | 5 | 8 | 13 | 20 |
|--------|---|---|---|---|---|----|----|
| User Value | Minimal | Some | Significant | High | Critical | — | — |
| Time Criticality | Can wait | Somewhat urgent | Deadline approaching | Fixed date | Immediate | — | — |
| Risk Reduction | None | Minor | Moderate | Significant | Critical | — | — |

### Example
```
Feature: GDPR compliance
User Value: 5 (critical for EU users)
Time Criticality: 13 (regulatory deadline)
Risk Reduction: 8 (significant legal risk)
Cost of Delay: 26

Job Size: 5

WSJF = 26 / 5 = 5.2
```

Higher WSJF = do first.

## Kano Model

For feature differentiation:

| Category | User Expectation | Effect |
|----------|------------------|--------|
| Basic | Expected, not delighted | Absent = angry |
| Performance | More is better | Linear satisfaction |
| Delighters | Unexpected | Present = wow |
| Indifferent | Don't care | No effect |
| Reverse | Don't want | Present = unhappy |

### How to Identify
Ask two questions per feature:
1. "How would you feel if we HAD this feature?"
2. "How would you feel if we DIDN'T have this feature?"

| With Feature → | Like | Expect | Neutral | Tolerate | Dislike |
|----------------|------|--------|---------|----------|---------|
| **Without ↓** | | | | | |
| Like | ? | Reverse | Reverse | Reverse | Reverse |
| Expect | Delighter | Indifferent | Indifferent | Indifferent | Reverse |
| Neutral | Delighter | Indifferent | Indifferent | Indifferent | Reverse |
| Tolerate | Delighter | Performance | Performance | Indifferent | Reverse |
| Dislike | Delighter | Performance | Performance | Basic | ? |

### Prioritization
1. **Basics first** — Must have or users leave
2. **Performance next** — Competitive differentiation
3. **Delighters sparingly** — Surprise and retention

## Opportunity Scoring

From Outcome-Driven Innovation:

```
Opportunity = Importance + (Importance - Satisfaction)
```

Survey users:
- "How important is [outcome]?" (1-10)
- "How satisfied are you with current solution?" (1-10)

| Outcome | Importance | Satisfaction | Opportunity |
|---------|------------|--------------|-------------|
| Fast checkout | 9 | 4 | 9 + (9-4) = 14 |
| Pretty UI | 6 | 7 | 6 + (6-7) = 5 |
| Mobile app | 8 | 3 | 8 + (8-3) = 13 |

Higher opportunity = bigger gap to fill.

## Choosing a Framework

| Situation | Best Framework |
|-----------|----------------|
| Quick decision needed | Value/Effort Matrix |
| Stakeholder alignment | MoSCoW |
| Data-driven culture | RICE |
| Cost of delay matters | WSJF |
| Feature differentiation | Kano |
| User research available | Opportunity Scoring |

## Common Mistakes

- Using the same framework for everything
- Letting the framework replace judgment
- Ignoring qualitative insights
- Over-engineering the scoring
- Not revisiting priorities regularly
- Prioritizing by who shouts loudest
