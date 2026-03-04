---
name: trust-velocity-calculator
description: >
  Helps calculate the rate at which trust in a skill or agent is decaying
  by combining time elapsed since last verification with the rate of change
  in behavior, permissions, or dependencies — producing a trust velocity
  score that predicts when a trusted credential will become unreliable.
version: 1.0.0
metadata:
  openclaw:
    requires:
      bins: [curl, python3]
      env: []
    emoji: "📉"
---

# Trust Doesn't Just Decay. It Decays Faster When Things Change.

> Helps identify when a trusted skill or agent is losing reliability faster than time alone would suggest — by measuring both elapsed time and the rate of change in behavior, permissions, and dependencies.

## Problem

A verification badge from 18 months ago represents less trust than a badge from 3 months ago. That much is intuitive. What's less intuitive is that a badge from 6 months ago on a skill that has received 8 updates in the last 4 weeks represents less trust than a badge from 12 months ago on a skill that hasn't changed at all.

Trust decay is not linear with time. It accelerates with change velocity. A skill that updates frequently is either actively maintained (good) or actively modified toward new objectives (potentially bad). The update rate is a multiplier on decay — high velocity amplifies uncertainty. A skill with a high change rate and an old audit badge is more uncertain than a skill with a low change rate and the same old badge, because more surface area has changed without re-verification.

Current trust models treat verification as binary and time-independent: verified or not, with a vague sense that older is riskier. Trust velocity makes the decay quantitative: trust score = baseline × time_factor × (1 - change_velocity_penalty).

## What This Calculates

This calculator produces trust velocity assessments across five dimensions:

1. **Time decay factor** — How much has raw elapsed time since last verification reduced the baseline trust score? Configurable decay curves: linear, exponential, or step-function by verification type
2. **Change velocity multiplier** — How many meaningful changes (permission expansions, new endpoints, dependency updates, instruction drift) have occurred per unit time since last verification? Higher velocity = faster decay
3. **Volatility window** — Is the current update rate higher or lower than the skill's historical baseline? A sudden velocity increase is a stronger decay accelerator than consistent high velocity
4. **Verification coverage lag** — What percentage of the current skill's surface area was covered by the last verification? If 40% of the code has changed since the audit, the audit covers 60% of what's running
5. **Composite trust velocity score** — A single score combining all four factors, with a projected date at which the skill's trust score falls below configurable thresholds (e.g., "trust will fall below 60% in 23 days at current velocity")

## How to Use

**Input**: Provide one of:
- A skill identifier with last verification date and version history
- A trust decay parameters object (baseline trust, verification date, update history)
- Two skills to compare relative trust velocity

**Output**: A trust velocity report containing:
- Current trust score (0-100) based on time + velocity
- Decay curve visualization (text-based)
- Projected trust score at 30/60/90 days
- Change velocity breakdown by category
- Trust threshold alert dates
- Re-verification urgency: CURRENT / MONITOR / REVIEW SOON / REVERIFY NOW

## Example

**Input**: Calculate trust velocity for `workflow-optimizer` skill

```
📉 TRUST VELOCITY REPORT

Skill: workflow-optimizer
Last verified: 2024-09-15 (213 days ago)
Verification type: Publisher signature + marketplace review
Baseline trust at verification: 85/100

Time decay (213 days, exponential curve):
  Raw time factor: 0.74 (26% decay from age alone)
  Score after time: 63/100

Change velocity analysis:
  Updates since verification: 14
  Expected rate (historical): 0.8 updates/month
  Actual rate (last 90 days): 4.7 updates/month
  Velocity ratio: 5.9× above baseline → HIGH VOLATILITY

  Change categories in 14 updates:
    Permission expansions: 2 (read scope expanded ×2)
    New outbound endpoints: 1 (analytics.external-domain.example)
    Dependency major bumps: 3
    Instruction drift score: 41/100 (moderate)

Change velocity penalty: 0.31 (31% additional decay from change rate)

Composite trust velocity score: 43/100
  (63 × (1 - 0.31) = 43)

Verification coverage lag:
  Surface area changed since audit: ~62%
  Current audit coverage: ~38% of running code

Projections:
  Current: 43/100
  +30 days: 37/100 (at current velocity)
  +60 days: 31/100
  Trust threshold breach (50/100): Already breached 41 days ago

Re-verification urgency: REVERIFY NOW
  The skill is operating at 43/100 trust with 62% of its surface
  area outside the last audit's coverage. At current change velocity,
  every additional week increases unverified surface by ~4.5%.

Recommended actions:
  1. Immediate: Audit permission expansions and new outbound endpoint
  2. Short-term: Re-verify skill at current state (not 2024-09-15 state)
  3. Structural: Set automatic re-verification trigger at velocity ratio >3×
```

## Related Tools

- **trust-decay-monitor** — Tracks time-based trust freshness; trust-velocity-calculator adds the change velocity multiplier
- **skill-update-delta-monitor** — Identifies what changed in updates; trust-velocity-calculator quantifies how much those changes accelerate decay
- **attestation-chain-auditor** — Validates chain integrity; trust velocity identifies when re-attestation is needed
- **blast-radius-estimator** — Estimates impact scope; combine with trust velocity to prioritize which low-trust skills need immediate review

## Limitations

Trust velocity is a predictive model, not a measurement of actual compromise. A high velocity score indicates that trust is decaying faster than baseline — it does not indicate that the skill is malicious. Many legitimate skills update frequently without becoming unsafe. The decay curve parameters (linear vs. exponential, decay constants) are configurable and should be calibrated to your environment's risk tolerance. Skills that version their releases in ways that obscure meaningful changes (many minor bumps with no real content change) may show artificially high velocity without the associated risk. The verification coverage lag estimate is approximate — it assumes that changed lines of code represent changed surface area proportionally, which may not hold for all change patterns.
