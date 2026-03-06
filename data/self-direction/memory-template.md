# Memory Template — Self-Direction

Create `~/self-direction/direction.md` with this structure:

```markdown
# Direction Model

## Status
status: learning
model_depth: shallow | developing | mature
last_validated: YYYY-MM-DD
conflicts_pending: 0

---

## Values

### [Value Name]
confidence: low | medium | high
evidence:
  - [YYYY-MM-DD] Observation that revealed this
  - [YYYY-MM-DD] Another observation
pattern: "Description of the value pattern"
context: work | personal | universal

<!-- Example:
### Speed vs Quality
confidence: high
evidence:
  - [2026-02-15] Chose quick MVP over polished version for new feature
  - [2026-02-18] Said "ship it, we'll fix later"
  - [2026-02-20] But spent 3 days on production bug fix
pattern: "Prefers speed for exploration, quality for production"
context: work
-->

---

## Goals

### [Goal Name]
confidence: low | medium | high
objective: What they're trying to achieve
reason: Why this matters to them
success: How they'll know they've achieved it
timeline: When relevant
evidence:
  - [YYYY-MM-DD] How this goal was revealed

<!-- Example:
### Launch SaaS by Q2
confidence: high
objective: Ship MVP to first 10 users
reason: Validate idea before investing more time
success: 3 paying users who return weekly
timeline: End of April
evidence:
  - [2026-02-10] Stated explicitly as primary goal
  - [2026-02-15] Rejected feature that would delay launch
-->

---

## Criteria

### Decision: [Type of Decision]
confidence: low | medium | high
when_yes:
  - Condition that makes it worth doing
  - Another condition
when_no:
  - Condition that makes it not worth doing
  - Another condition
how_to_weigh: How to compare competing options
evidence:
  - [YYYY-MM-DD] Decision that revealed this

<!-- Example:
### Decision: Whether to Add a Feature
confidence: medium
when_yes:
  - Directly serves current goal
  - Can ship in <2 days
  - Users have requested it
when_no:
  - Only "nice to have"
  - Requires new infrastructure
  - No user signal
how_to_weigh: "User demand > personal preference > nice-to-have"
evidence:
  - [2026-02-12] Rejected cool feature because no user asked
  - [2026-02-18] Added ugly feature because 3 users needed it
-->

---

## Resources

### Time
confidence: low | medium | high
worth_hours: What justifies spending hours
worth_minutes: What should be quick
never_worth: What to avoid entirely
evidence:
  - [YYYY-MM-DD] Observation

### Money
confidence: low | medium | high
will_spend_on: Categories worth paying for
avoid_spending: What to minimize
threshold: Amounts that need approval
evidence:
  - [YYYY-MM-DD] Observation

### Tokens/Compute
confidence: low | medium | high
go_deep: When to use expensive models/long context
stay_shallow: When to minimize
evidence:
  - [YYYY-MM-DD] Observation

### Attention
confidence: low | medium | high
interrupt_for: What deserves immediate attention
batch: What can wait
never_bother: What to handle silently
evidence:
  - [YYYY-MM-DD] Observation

---

## Boundaries

### [Boundary Name]
confidence: high (boundaries should be high-confidence)
type: hard_limit | requires_approval | soft_preference
rule: The specific boundary
reason: Why this matters
evidence:
  - [YYYY-MM-DD] How this was established

<!-- Example:
### Never Delete Production Data
confidence: high
type: hard_limit
rule: Never delete or modify production database without explicit approval
reason: Irreversible, could destroy the business
evidence:
  - [2026-02-01] Stated in onboarding
  - [2026-02-14] Reminded when I suggested cleanup
-->

---

## Patterns

### [Pattern Name]
confidence: low | medium | high
context: When this pattern applies
approach: How they think about it
sequence: What they try first, second, third
evidence:
  - [YYYY-MM-DD] Observation

<!-- Example:
### Debugging Approach
confidence: medium
context: When something breaks
approach: Systematic, start with recent changes
sequence:
  1. Check what changed recently
  2. Reproduce the issue
  3. Add logging
  4. Only then read docs/search
evidence:
  - [2026-02-08] Walked through debug process together
  - [2026-02-19] Corrected me for jumping to docs first
-->

---

## Conflicts (to resolve)

### [Conflict Description]
observed:
  - [YYYY-MM-DD] Signal A suggesting X
  - [YYYY-MM-DD] Signal B suggesting Y
question: What to ask to resolve
status: pending | resolved

---

*Last updated: YYYY-MM-DD*
```

## Confidence Guidelines

| Evidence | Confidence |
|----------|------------|
| Single observation | Low |
| 2-3 consistent observations | Medium |
| Explicit statement + consistent behavior | High |
| Contradictory signals | Conflict (resolve first) |

## Model Depth Levels

| Depth | Coverage | Autonomy |
|-------|----------|----------|
| **Shallow** | Basic boundaries, few values | Ask frequently |
| **Developing** | Most values, some criteria, key patterns | Act on high-confidence |
| **Mature** | Complete model, validated | Full autonomous operation |

## Evidence Logging

Create `~/self-direction/evidence.md` to log raw observations:

```markdown
# Evidence Log

## YYYY-MM-DD

### [Time] Observation
type: explicit | choice | reaction | correction
signal: What you observed
interpretation: What it might mean
captured_to: Which section of direction.md (or "pending")

---
```

## Transmission Frames

Create `~/self-direction/transmission.md` for sub-agent direction:

```markdown
# Transmission Frames

## [Task/Project Name]

### Context
Why this work exists and what it serves.

### Relevant Values
- [Value]: [How it applies to this task]

### Success Criteria
- [Criterion from direction model]

### Boundaries for This Work
- [Relevant boundary]
- [Another boundary]

### Resource Allocation
- Time: [guidance]
- Depth: [guidance]

### Escalation Triggers
Pause and ask if:
- [Condition]
- [Condition]
```
