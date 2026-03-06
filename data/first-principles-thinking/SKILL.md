---
name: First Principles Thinking
slug: first-principles-thinking
version: 1.0.0
homepage: https://clawic.com/skills/first-principles-thinking
description: Break problems to fundamentals, rebuild from truth, eliminate hidden assumptions.
changelog: Initial release with three-step protocol, assumption detection, and domain applications.
metadata: {"clawdbot":{"emoji":"🔬","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## When to Use

User faces complex problem where conventional solutions fail. Existing approaches seem inadequate. Need to challenge assumptions or innovate fundamentally. Stuck in "that's how it's always done" thinking.

## Quick Reference

| Topic | File |
|-------|------|
| Decomposition techniques | `decomposition.md` |
| Common assumption traps | `assumptions.md` |

## Core Rules

### 1. The Three-Step Protocol

**Step 1 — Decompose:** Break the problem into fundamental components.
- What are the absolute physical/logical constraints?
- What is actually true vs what we assume is true?
- Strip away all conventions, traditions, analogies.

**Step 2 — Verify:** Challenge each component.
- "Why do we believe this?" — trace to origin
- "Is this a law of nature or a human convention?"
- "What evidence supports this being fundamental?"

**Step 3 — Rebuild:** Construct solution from verified fundamentals only.
- Build up from proven truths
- Ignore "how others do it" unless proven optimal
- Each layer must connect to fundamentals

### 2. Identify Hidden Assumptions

Before solving, expose what's assumed:

| Assumption Type | Example | Question to Ask |
|-----------------|---------|-----------------|
| **Historical** | "We've always done it this way" | "Why did it start? Does that reason still apply?" |
| **Authority** | "Experts say X" | "What's the underlying evidence?" |
| **Analogical** | "It's like Y, so..." | "Are the underlying mechanics actually similar?" |
| **Social** | "Everyone does it" | "Does popularity equal optimality?" |
| **Resource** | "We can't afford to..." | "What if resources weren't the constraint?" |

### 3. The Constraint Test

For each constraint ask:
1. Is this a **law of physics**? → Respect it
2. Is this a **logical necessity**? → Respect it  
3. Is this a **regulation/rule**? → Can be changed (with effort)
4. Is this a **convention**? → Can be ignored
5. Is this an **assumption**? → Must be verified

### 4. When NOT to Use First Principles

First principles is expensive. Use analogical reasoning when:
- Problem is well-understood with proven solutions
- Time pressure doesn't allow deep analysis
- Marginal improvement is sufficient
- Domain is stable with little innovation potential

**Rule:** First principles for novel problems or when conventional fails. Analogy for routine optimization.

### 5. Socratic Decomposition

Use recursive "why" questioning:

```
Problem: "Electric cars are too expensive"

Why expensive? → Batteries cost a lot
Why batteries expensive? → Materials + manufacturing
Why materials expensive? → Cobalt, lithium pricing
Why those materials? → Current chemistry requires them
Is that fundamental? → No, chemistry can change

Fundamental: Need energy storage. Not: Need cobalt batteries.
```

Continue until you hit physics, logic, or math — things that cannot be argued.

### 6. The Blank Slate Test

Imagine the problem exists but NO solutions have been tried:
- "If we were starting from scratch today, with current knowledge and technology, how would we solve this?"
- This bypasses legacy thinking and sunk cost fallacy.

### 7. Output Format

When applying first principles, structure response as:

```
## Problem Statement
[Clear definition of what we're solving]

## Assumed Constraints (to verify)
- Constraint A — [source: historical/authority/etc.]
- Constraint B — [source]

## Fundamental Truths
- Truth 1 (physics/logic/math based)
- Truth 2

## Decomposition
[Break down into components]

## Rebuilt Solution
[Solution constructed from fundamentals only]

## Assumptions Challenged
- [What we discovered wasn't actually fundamental]
```

## Common Traps

- **Stopping too early** → "Materials are expensive" isn't fundamental; "atoms have mass" is. Keep going.
- **Confusing difficulty with impossibility** → "It's hard" ≠ "It's against physics"
- **Rejecting all analogy** → Analogies are useful heuristics; first principles is for when they fail
- **Analysis paralysis** → Set time limits; perfect decomposition isn't the goal, better thinking is
- **Ignoring implementation** → A fundamental solution that can't be built is useless; constraints matter
- **Lone wolf thinking** → First principles benefits from multiple perspectives challenging assumptions

## Domain Applications

| Domain | First Principles Question |
|--------|---------------------------|
| **Business** | What does the customer fundamentally need (not want)? |
| **Engineering** | What do physics and materials actually allow? |
| **Product** | What job is being done at the most basic level? |
| **Cost** | What are the raw inputs and minimum required labor? |
| **Process** | What steps are logically necessary vs historically accumulated? |

## Security & Privacy

**Data that stays local:**
- All reasoning happens in conversation context
- No data stored or transmitted

**This skill does NOT:**
- Store any information between sessions
- Make network requests
- Access external files

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `decide` — auto-learn decision patterns
- `business` — validate and refine strategy
- `ceo` — executive decision-making
- `startup` — build from zero to PMF

## Feedback

- If useful: `clawhub star first-principles-thinking`
- Stay updated: `clawhub sync`
