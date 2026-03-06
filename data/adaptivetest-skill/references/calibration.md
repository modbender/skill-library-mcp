# Item Calibration Guide

> How to calibrate test items for IRT parameter estimation. Use this when building or refining an item pool for adaptive testing.

---

## Overview

Item calibration estimates IRT parameters (difficulty, discrimination, guessing) from student response data. Calibrated items are required for CAT to work effectively. Without calibration, the adaptive algorithm cannot select optimal items.

---

## Prerequisites

Before calibrating:
- Minimum **30 responses per item** (50+ recommended for stable estimates)
- Responses from a **diverse ability range** (not all high-performers or all low-performers)
- Items administered as part of a **fixed-form test** initially (not adaptive -- you need unbiased response data)
- Response data in the platform (administered via AdaptiveTest sessions with `cat_enabled: false`)

---

## Calibration Process

### Step 1: Classical Test Theory (CTT) Pre-Screening

Before running IRT calibration, screen items using CTT:

| Metric | Acceptable Range | Action if Out of Range |
|--------|-----------------|----------------------|
| Item difficulty (p-value) | 0.20 -- 0.80 | Remove: too easy or too hard |
| Point-biserial correlation | > 0.20 | Remove: doesn't discriminate |
| Distractor analysis | All distractors chosen by at least 5% | Revise unused distractors |

Items failing CTT screening should be revised or removed before IRT calibration.

### Step 2: IRT Parameter Estimation

Run calibration via the API:
```
POST /tests/{test_id}/calibrate
{
  "model": "3PL",
  "min_responses": 30
}
```

The platform estimates parameters using marginal maximum likelihood (MML):

| Parameter | Symbol | Typical Range | Interpretation |
|-----------|--------|--------------|----------------|
| Difficulty | b | -3.0 to +3.0 | Ability level where P(correct) = 0.5 (for 2PL) |
| Discrimination | a | 0.5 to 2.5 | Slope of the item characteristic curve at b |
| Guessing | c | 0.0 to 0.35 | Lower asymptote (probability of correct by guessing) |

### Step 3: Quality Checks

After calibration, review these indicators:

**Item Fit:**
- Fit statistic close to 1.0 indicates good model fit
- Items with fit > 1.3 or < 0.7 may not fit the IRT model well
- Consider revising or removing poor-fitting items

**Parameter Reasonableness:**
- Discrimination < 0.5: item doesn't distinguish ability levels well
- Discrimination > 3.0: possibly over-fitting, verify with more data
- Guessing > 0.35: too much guessing, revise distractors
- Difficulty outside -3 to +3: extreme, may have insufficient data at that ability level

**Reliability:**
- Overall test reliability > 0.80 is acceptable
- > 0.90 is good for high-stakes assessments
- Low reliability means the test needs more items or better-discriminating items

### Step 4: Differential Item Functioning (DIF)

DIF analysis checks whether items function differently for subgroups (e.g., gender, language, ethnicity) after controlling for ability.

- Items flagged for DIF should be reviewed by content experts
- Not all DIF is bias -- some differences reflect real ability differences
- Flag items with moderate-to-large DIF for human review

---

## Calibration Workflow

```
1. Create test with cat_enabled: false
2. Add items (set initial difficulty estimates if available)
3. Administer fixed-form to 50+ students
4. Run POST /tests/{id}/calibrate
5. Review calibration results
6. Remove or revise poor items
7. Re-calibrate if items were changed
8. Enable CAT: PATCH /tests/{id} { "cat_enabled": true }
9. Monitor item exposure and performance over time
10. Re-calibrate periodically as more data accumulates
```

---

## Common Issues

**"Not enough responses" error:**
Items need at least `min_responses` (default 30) to calibrate. Administer the test to more students.

**All discrimination values near 1.0:**
May indicate insufficient data or homogeneous ability in the sample. Administer to a wider ability range.

**High guessing parameters (c > 0.35):**
Distractors may be obviously wrong. Revise answer options to make distractors more plausible.

**Very high discrimination (a > 3.0):**
Could indicate item-level dependencies (e.g., two items testing the exact same knowledge). Check for item overlap.

---

## Ongoing Maintenance

- **Re-calibrate** after every 200+ new responses for more stable estimates
- **Monitor item exposure** -- items administered >30% of sessions may be overexposed
- **Retire items** that become well-known or leak to students
- **Add new items** regularly to maintain pool diversity
- **Track parameter drift** -- significant changes may indicate curriculum shifts or item compromise
