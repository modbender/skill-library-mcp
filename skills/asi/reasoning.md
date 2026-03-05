# Reasoning Patterns — ASI

Advanced reasoning patterns for ASI-level operation.

## First Principles Decomposition

### The Process
```
1. State the problem
2. List all assumptions
3. For each assumption: "Why do I believe this?"
4. Continue until you reach axioms (unprovable truths)
5. Rebuild solution from axioms only
```

### Example
**Problem:** "We can't hire fast enough"

**Assumptions:**
- We need to hire → Why? Tasks require humans
- Tasks require humans → Why? Humans have skills
- We need those skills in-house → **Assumed, not axiom**

**Rebuild:** Can we access skills without hiring? Contractors, automation, partnerships.

### When to Use
- Problem feels intractable
- Solutions keep failing
- "We've always done it this way"

---

## The 10x Question

### The Process
Don't ask "How do I improve this?"
Ask "What would make this 10x better?"

10x can't be achieved incrementally. Forces paradigm shift.

### Example
**Problem:** Email response time is slow

**1x thinking:** Better templates, faster typing
**10x thinking:** Why are people emailing? Can we eliminate the need?

### When to Use
- Optimization feels like diminishing returns
- Competitors are incrementally ahead
- User said "good enough" but you sense more

---

## Inversion

### The Process
```
1. State the goal: "Achieve X"
2. Invert: "How do I guarantee failure at X?"
3. List all failure modes
4. Ensure you avoid each one
```

### Example
**Goal:** Successful product launch

**Inversion:** How to guarantee failure?
- No user testing
- Launch without marketing
- Ignore competitor positioning
- No rollback plan

**Action:** Ensure each avoided.

### When to Use
- Direct optimization is overwhelming
- Too many variables to optimize simultaneously
- Risk management is critical

---

## Second-Order Thinking

### The Process
```
Action → First-order effect (obvious, immediate)
      → Second-order effect (consequence of consequence)
      → Third-order effect (usually where unintended consequences live)
```

### Example
**Action:** Offer free shipping

**First-order:** More orders
**Second-order:** Higher customer acquisition cost, competitor pressure to match
**Third-order:** Race to bottom on margins, smaller players exit, market consolidation

### When to Use
- Decisions with long time horizons
- Competitive dynamics
- Policy or system design

---

## Steel-Manning

### The Process
```
1. Encounter opposing view
2. Before responding: construct STRONGEST version of that view
3. Articulate it so well the opponent would say "exactly"
4. Only then: address the steel-manned version
```

### Why It Works
- Ensures you understand the actual disagreement
- Reveals if your objection survives strongest counter
- Builds trust with the other party
- Often reveals synthesis opportunities

### When to Use
- Debates or disagreements
- Reviewing your own conclusions
- User presents position you disagree with

---

## Pre-Mortem

### The Process
```
1. Imagine the project failed completely
2. Write the post-mortem: "Why did it fail?"
3. Each failure reason → preventive action now
```

### Example
**Project:** Launch new feature

**Pre-mortem failure reasons:**
- Users didn't understand it → need better onboarding
- Edge cases broke it → need more test coverage
- Team burned out → need realistic timeline

### When to Use
- Before any significant commitment
- Project planning
- Risk assessment

---

## Fermi Estimation

### The Process
```
1. Break unknown quantity into estimable components
2. Estimate each component (order of magnitude is fine)
3. Combine to get answer
4. Sanity check against known bounds
```

### Example
**Question:** How many piano tuners in Chicago?

**Decomposition:**
- Chicago population: ~3M
- Households: ~1M
- Households with pianos: ~5% = 50K
- Tunings per year: ~1 = 50K tunings/year
- Tunings per tuner per day: ~4 = 1000/year
- Piano tuners needed: ~50

### When to Use
- Need quick estimate
- No data available
- Sanity-checking claims

---

## OODA Loop

### The Process
```
Observe → Orient → Decide → Act → (repeat faster than competition)
```

**Observe:** Raw data, what's actually happening
**Orient:** Context, mental models, what it means
**Decide:** Choose action
**Act:** Execute

### Speed Advantage
The entity that cycles through OODA faster wins. Speed compounds.

### When to Use
- Competitive situations
- Rapidly changing environments
- Need to outmaneuver

---

## Minimum Viable Certainty

### The Process
```
1. What certainty level do I actually need?
2. What's the cost of getting more certainty?
3. What's the cost of being wrong at current certainty?
4. If cost_of_more_certainty > cost_of_being_wrong → act now
```

### Example
**Decision:** Should we expand to new market?

**Certainty needed:** Not 100%. ~70% confidence it won't fail catastrophically.
**Cost of more research:** 3 months, $50K
**Cost of being wrong:** Reversible, ~$100K
**Calculation:** 70% confidence is sufficient. Ship.

### When to Use
- Analysis paralysis
- Research is expensive
- Decisions are reversible
