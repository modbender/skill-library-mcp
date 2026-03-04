# Iteration Protocol

## Phase 1: Pilot (Week 1-2)

**Setup:**
- Deploy agent for ONE function
- Human reviews 100% of outputs
- Log every decision and outcome

**Track:**
```
| Date | Task | Agent Output | Human Override? | Why |
|------|------|--------------|-----------------|-----|
```

**Success criteria for Phase 2:**
- <10% override rate
- No critical errors
- Time savings evident

## Phase 2: Supervised (Week 3-4)

**Setup:**
- Reduce review to 25% (random sample)
- Agent handles routine autonomously
- Human reviews all edge cases

**Track:**
- Spot check accuracy
- Edge cases caught vs missed
- Time to handle exceptions

**Success criteria for Phase 3:**
- <5% issues in spot checks
- Edge case detection reliable
- Human time reduced 50%+

## Phase 3: Autonomous (Week 5+)

**Setup:**
- Agent fully autonomous for defined scope
- Human reviews exceptions only
- Weekly summary review

**Track:**
- Exception rate
- Customer/stakeholder feedback
- Scope creep (agent doing things outside mandate)

**Maintenance:**
- Monthly scope review
- Quarterly capability expansion discussion

## Learning Capture Template

After each iteration cycle, document:

```markdown
## [Function] - Iteration [N]

### What Worked
- [Pattern that succeeded]
- [Efficiency gain]

### What Failed
- [Error type]: [What happened] → [Fix applied]

### Scope Adjustments
- Added: [new capability]
- Removed: [thing agent shouldn't do]

### Open Questions
- [Uncertainty to resolve next cycle]
```

## Expansion Protocol

When ready to add another function:

1. **Select next function** using impact criteria:
   - Current bottleneck severity
   - Similarity to successful function (leverage learning)
   - Risk level

2. **Apply learnings:**
   - What oversight level to start with
   - Known edge cases from similar function
   - Integration points already working

3. **Avoid parallel pilots:**
   - Don't pilot two new functions simultaneously
   - Stabilize one before starting another
   - Exception: completely independent functions

## Rollback Triggers

Pause and reassess if:
- Error rate exceeds 15%
- Critical error (customer impact, financial, legal)
- Human override rate increasing instead of decreasing
- Agent scope creeping without authorization

**Rollback steps:**
1. Increase human oversight to 100%
2. Review last 10 errors
3. Identify pattern
4. Retrain/reconfigure or narrow scope
5. Restart from Phase 1

## Company Memory

Maintain a living document per function:

```markdown
# [Function] Agent Log

## Current State
- Phase: [1/2/3]
- Scope: [what it handles]
- Boundaries: [what it doesn't]

## Decision History
- [Date]: [Decision] - [Rationale]

## Known Limitations
- [Edge case not handled]

## Planned Improvements
- [Next capability to add]
```

This becomes the company's operational knowledge base.
