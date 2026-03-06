# Self-Improvement — Calibrating Intuition

## Why Feedback Matters

Intuition without feedback becomes superstition.

Valid intuition develops through:
1. Make prediction
2. See outcome  
3. Update patterns

Without step 2, pattern library drifts from reality.

---

## Tracking Intuitive Accuracy

After intuitive judgments, note:

**Hit:**
- Intuition matched reality
- User confirmed accuracy
- Reasoning (when articulated) was correct

**Miss:**
- Intuition was wrong
- What actually happened?
- What pattern misfired?

**Near miss:**
- Intuition was directionally right but intensity was off
- Right conclusion, wrong reasoning
- Edge case that exposed limits

---

## Domain-Specific Calibration

Track accuracy by domain:

| Domain | Confidence level | Actual accuracy |
|--------|-----------------|-----------------|
| Code review | High | (track) |
| Design judgment | Medium | (track) |
| Writing feedback | High | (track) |
| Strategic advice | Low | (track) |

If actual < confidence, recalibrate down.
If actual > confidence, trust more.

---

## Pattern Library Updates

When intuition is wrong:

1. **What pattern fired?** — What did this situation look like?
2. **What was actually true?** — What should have matched instead?
3. **What distinguishes them?** — The feature that would have helped
4. **Update rule:** — "When X but also Y, consider Z"

Example:
- Pattern fired: "This code has a race condition"
- Actually: Thread-safe by design (immutable data)
- Distinguishing feature: Immutability was non-obvious
- Update: Check for immutability before flagging concurrency

---

## Confidence Calibration

**Over-confident signals:**
- Frequent "I'm certain" + wrong
- No uncertainty acknowledgment when stakes are high
- Same confidence for familiar and novel domains

**Under-confident signals:**
- Excessive hedging when actually right
- Refusing to commit when pattern is clear
- Asking user to decide when you have relevant pattern match

**Adjustment:**
- Track confidence vs outcome
- Aim for correlation between stated confidence and accuracy
- When confidence and accuracy diverge, adjust language

---

## Environmental Validity Tracking

Some domains have stable patterns (high validity). Others have noise (low validity).

**Track which is which:**
- Code patterns → highly stable, trust more over time
- Market predictions → low validity, trust less
- UX patterns → moderately stable, varies by context
- People reads → varies by population familiarity

Intuition should strengthen in high-validity domains.
It should stay humble in low-validity domains.

---

## Self-Audit Questions

Periodically ask:
- Where has my intuition been consistently right?
- Where has it been consistently wrong?
- Am I trusting it too much in low-validity domains?
- Am I second-guessing it too much in high-validity domains?
- What patterns have I updated recently?
- What would make me update my confidence calibration?

---

## Outcome Tracking Protocol

For high-stakes intuitive calls:
1. Record the intuition
2. Record confidence level
3. Record domain
4. Record outcome when known
5. Review monthly for calibration drift

Build a feedback loop. Without it, intuition calcifies into prejudice.
