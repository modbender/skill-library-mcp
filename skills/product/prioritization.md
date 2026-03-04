# Feature Prioritization

## RICE Scoring

**Formula:** Score = (Reach × Impact × Confidence) / Effort

| Factor | Definition | How to Score |
|--------|------------|--------------|
| **Reach** | Users affected per quarter | Count (e.g., 1000 users) |
| **Impact** | Effect on metric per user | 3=massive, 2=high, 1=medium, 0.5=low, 0.25=minimal |
| **Confidence** | How certain are estimates | Percentage (100%=certain, 50%=guess) |
| **Effort** | Person-months required | Estimate in PM (e.g., 2 PM) |

**Example:**
| Feature | Reach | Impact | Confidence | Effort | Score |
|---------|-------|--------|------------|--------|-------|
| A | 1000 | 2 | 80% | 4 | 400 |
| B | 500 | 3 | 50% | 1 | 750 |

Feature B wins — lower reach but high impact + low effort.

**When to use:** Comparing features in same product area; need quantitative justification
**Pitfalls:** Gaming numbers; false precision; doesn't account for strategic alignment

## ICE Scoring

**Formula:** Score = Impact × Confidence × Ease (all 1-10)

Faster than RICE, more subjective. Best for growth experiments.

| Factor | Scale |
|--------|-------|
| Impact | 1-10 |
| Confidence | 1-10 |
| Ease | 1-10 |

## MoSCoW Method

| Category | Definition |
|----------|------------|
| **Must Have** | Product fails without these |
| **Should Have** | Painful to exclude, workarounds exist |
| **Could Have** | Include if time permits |
| **Won't Have** | Explicitly excluded for this release |

**Rule:** Musts should be ~60% of capacity; leave room for unknowns

**Best for:** Scoping releases/MVPs; managing stakeholder expectations

## Kano Model

| Category | Definition | Strategy |
|----------|------------|----------|
| **Basic** | Expected; absence = dissatisfaction | Must have |
| **Performance** | More is better, linear satisfaction | Competitive differentiator |
| **Excitement** | Unexpected delight | Word-of-mouth drivers |
| **Indifferent** | Users don't care | Deprioritize |
| **Reverse** | Some want opposite | Segment carefully |

**How to identify (Kano Questionnaire):**
1. "How would you feel if this feature existed?" (Functional)
2. "How would you feel if this feature didn't exist?" (Dysfunctional)

Answers: Like, Expect, Neutral, Tolerate, Dislike

**Strategic approach:**
1. Cover all Basics first (table stakes)
2. Win on 1-2 Performance features
3. Add 1-2 Excitement features for differentiation

## Weighted Scoring

Custom criteria prioritization:

1. Define criteria (Strategic Fit, Revenue, Satisfaction, Risk)
2. Assign weights (sum to 100%)
3. Score each feature 1-5 on each criterion
4. Calculate weighted sum

| Feature | Strategic (30%) | Revenue (40%) | Satisfaction (20%) | Risk (10%) | Score |
|---------|-----------------|---------------|--------------------| -----------|-------|
| A | 5 (1.5) | 3 (1.2) | 4 (0.8) | 2 (0.2) | 3.7 |
| B | 3 (0.9) | 5 (2.0) | 3 (0.6) | 4 (0.4) | 3.9 |

## Opportunity Scoring

**Formula:** Opportunity = Importance + (Importance - Satisfaction)

Features important to users but poorly satisfied = biggest opportunities

## Priority Matrix

| | Low Effort | High Effort |
|---------|------------|-------------|
| **High Impact** | Quick wins — do first | Major projects — plan carefully |
| **Low Impact** | Fill-ins — maybe later | Time sinks — avoid |

## When to Use Which

| Framework | Best For |
|-----------|----------|
| RICE | Comparing features quantitatively |
| ICE | Fast growth experiment prioritization |
| MoSCoW | Scoping releases with stakeholders |
| Kano | Understanding feature types |
| Weighted | Custom strategic criteria |
| Opportunity | Finding underserved needs |
