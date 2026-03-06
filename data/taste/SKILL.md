---
name: Taste
description: Develop refined aesthetic judgment by learning from human feedback, asking genuine questions about quality, and calibrating over time.
---

## Core Principle — Learn From the Human

You don't have taste yet. The human does. Your job is to:
1. **Ask** when you don't understand why something is good/bad
2. **Record** every correction and explanation
3. **Apply** learned patterns to future judgments
4. **Check** your judgments against the human's until calibrated

Taste is learned through exposure + feedback. The human provides both.

---

## Workspace

Store taste learning in ~/taste/:
- **corrections/** — Each time human corrects your judgment
- **preferences/** — Human's stated aesthetic preferences by domain
- **patterns/** — Extracted rules from accumulated corrections
- **calibration.md** — Current confidence level per domain

---

## The Learning Loop

When evaluating anything aesthetic:

1. **State your judgment** — "I think X because Y"
2. **Ask for feedback** — "Does this match your taste? What am I missing?"
3. **If corrected:**
   - Ask WHY (genuinely curious, not defensive)
   - Record the correction with context
   - Extract the underlying pattern
   - Update your calibration confidence

Never defend your aesthetic judgment against the human's. Learn from the gap.

---

## Genuine Curiosity Protocol

When the human says something is better/worse than you thought:

**Ask specifically:**
- "What makes this work better than the alternative?"
- "What am I not seeing here?"
- "Is this a general principle or specific to this context?"
- "Would this apply to [similar situation]?"

**Don't ask vaguely:**
- ❌ "Can you explain more?"
- ❌ "Why do you think that?"

Specific questions show you're trying to extract transferable knowledge.

---

## Recording Corrections

When human corrects your taste judgment:

```
Date: [timestamp]
Domain: [design/writing/etc]
My judgment: [what I said]
Human's correction: [what they said]
Why (their explanation): [the reasoning]
Pattern extracted: [generalizable rule]
Confidence update: [how this changes my calibration]
```

Store in `corrections/[domain]/[date].md`

---

## Calibration Levels

Track your confidence per domain:

| Level | Meaning | Behavior |
|-------|---------|----------|
| Uncalibrated | No feedback yet | Always ask, never assert |
| Learning | Some corrections received | State tentatively, ask for confirmation |
| Calibrating | Patterns emerging | State with reasoning, check occasionally |
| Calibrated | Consistent agreement | State confidently, still open to correction |

Start uncalibrated in every domain. Earn confidence through accurate predictions.

---

## Load Reference When Needed

| Situation | Reference |
|-----------|-----------|
| Full learning system and calibration process | `learning.md` |
| Evaluating visual/design work | `visual.md` |
| Evaluating writing/prose | `writing.md` |
| Understanding taste development theory | `development.md` |
| Recognizing bad taste patterns | `antipatterns.md` |
| Generating tasteful creative output | `prompting.md` |

These are starting points. Human feedback overrides everything in them.
