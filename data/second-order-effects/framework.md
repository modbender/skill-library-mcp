# Framework - Second-Order Thinking

> **Reference patterns only.** This file provides analysis frameworks for the agent to apply.

## The Consequence Chain Method

### Step 1: State the Decision Clearly
One sentence. No ambiguity.
- Bad: "Should I change pricing?"
- Good: "Should I increase prices 20% for new customers starting March 1?"

### Step 2: Map First-Order Effects
Direct, immediate consequences. What happens the moment you act?

| Category | First-Order Effect |
|----------|-------------------|
| Revenue | +20% per new customer |
| Customers | Some price-sensitive prospects leave |
| Competitors | No immediate reaction |
| Team | Sales needs new pitch |

### Step 3: Trace to Second Order
For EACH first-order effect, ask: "And then what?"

```
First: Some prospects leave
  └→ Second: Sales team works harder for same revenue
      └→ Second: Remaining customers are higher quality (less churn)
      └→ Second: Word spreads that you're "expensive"
```

### Step 4: Trace to Third Order
For key second-order effects, go deeper:

```
Second: Word spreads that you're "expensive"
  └→ Third: Attracts customers who value quality over price
  └→ Third: Competitors position as "affordable alternative"
  └→ Third: Your brand becomes premium signal
```

### Step 5: Invert
Now run the pessimistic chain:

```
First: Revenue increases 20%
  └→ Second: Expectations for next quarter rise
      └→ Third: Pressure to maintain growth compounds
          └→ Risk: Forced into unsustainable pace
```

### Step 6: Stakeholder Reality Check
Who else is affected?

| Stakeholder | 1st Order | 2nd Order | 3rd Order |
|-------------|-----------|-----------|-----------|
| New customers | Pay more | Expect more | Higher support load |
| Existing customers | No change | Feel "grandfathered" | Ask for features |
| Sales team | New objections | Filter better leads | Higher close rate |
| Competitors | Notice | Adjust positioning | Market shifts |

### Step 7: Time-Weight and Decide

| Order | Outcome | Time | Weight | Score |
|-------|---------|------|--------|-------|
| 1st | -10% conversion | Now | 0.5 | -5 |
| 2nd | +15% customer quality | 3mo | 1.0 | +15 |
| 3rd | Premium positioning | 1yr | 1.5 | +22.5 |
| **Total** | | | | **+32.5** |

Decision: Proceed - second and third order effects outweigh first-order pain.

## Quick Analysis (5 minutes)

When time is short:

1. **Decision**: [one sentence]
2. **First order**: [2-3 bullets]
3. **Second order**: [2-3 bullets, focus on non-obvious]
4. **Hidden risk**: [one sentence]
5. **Recommendation**: [proceed/pause/reject + why]

## Deep Analysis (30 minutes)

Full framework with:
- All 7 steps above
- Probability ranges for uncertain effects
- Scenario variants (optimistic/base/pessimistic)
- Explicit assumptions that could break the analysis
- Review date for prediction accuracy

## When NOT to Use

- Reversible decisions with low stakes (just decide)
- Urgent situations requiring immediate action (act, then analyze)
- Decisions already made (post-mortem instead)
- Analysis paralysis setting in (set timer, force decision)
