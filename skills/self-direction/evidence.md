# Evidence Logging — Self-Direction

This file explains how to log raw observations that feed the direction model.

## Why Log Evidence?

The direction model is built from observations. Evidence logging:
- Preserves the raw signal before interpretation
- Allows re-evaluation if your interpretation was wrong
- Shows the basis for each element in the model
- Helps identify patterns across observations

## Evidence Entry Format

```
## YYYY-MM-DD

### [HH:MM] [Brief Title]

**Type:** explicit | choice | reaction | correction | inference
**Context:** What was happening when this occurred
**Raw signal:** Exactly what you observed (quote if verbal)
**Interpretation:** What this might reveal about their direction
**Confidence:** low | medium | high
**Captured to:** direction.md > [section] or "pending analysis"

---
```

## Evidence Types

### Explicit
They stated something directly about their preferences, values, or boundaries.
- "I always want tests before merging"
- "Speed matters more than perfection for MVPs"
- "Never spend more than $50 without asking"

**Confidence:** Usually high (they said it directly)

### Choice
They chose between options, revealing criteria.
- Selected option A over option B
- Allocated time/money/attention to X instead of Y
- Accepted one suggestion, rejected another

**Confidence:** Medium (you're inferring the criteria)

### Reaction
They reacted positively or negatively to something.
- Excited about a result
- Frustrated with an approach
- Relieved when something worked

**Confidence:** Medium (emotional signal, but needs interpretation)

### Correction
They corrected your decision or output.
- "No, that's not the priority"
- "You should have done X instead"
- "This isn't what I meant"

**Confidence:** High (direct feedback on a specific case)

### Inference
You're connecting multiple observations to form a pattern.
- Combining 3 choices that suggest a value
- Noticing a recurring theme across sessions

**Confidence:** Varies (depends on strength of pattern)

## Example Evidence Log

```markdown
## 2026-02-15

### [09:30] Rejected Feature Idea

**Type:** choice
**Context:** Brainstorming features for the MVP
**Raw signal:** "That's cool but nobody asked for it. Let's focus on what users need."
**Interpretation:** User demand > personal interest when prioritizing features
**Confidence:** medium
**Captured to:** direction.md > criteria > feature_decisions

---

### [14:15] Explicit Speed Preference

**Type:** explicit
**Context:** Discussing timeline for landing page
**Raw signal:** "Just ship something. We can make it pretty later."
**Interpretation:** Values speed over polish for early-stage work
**Confidence:** high
**Captured to:** direction.md > values > speed_vs_quality

---

### [16:45] Correction on Communication

**Type:** correction
**Context:** I summarized a long analysis in 3 paragraphs
**Raw signal:** "Too long. Give me bullets. I'll ask if I need details."
**Interpretation:** Prefers concise communication, pull over push
**Confidence:** high
**Captured to:** direction.md > patterns > communication_style

---
```

## From Evidence to Model

When you have enough evidence on a topic:

1. **Review related entries** — Do they tell a consistent story?
2. **Identify the pattern** — What's the underlying value/criterion/boundary?
3. **Assess confidence** — How strong is the evidence?
4. **Capture to model** — Add to appropriate section of direction.md
5. **Link evidence** — Reference the evidence entries in the model

## When to Log

Log evidence when you observe:
- Any explicit statement about preferences
- Any decision between alternatives
- Any correction of your work
- Any strong reaction (positive or negative)
- Any pattern you notice forming

Don't log:
- Routine instructions (just task details)
- Information without direction signal
- Speculation without observation
