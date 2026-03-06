---
name: Find
description: Locate anything with progressive search expansion, multi-source validation, and iterative refinement until found.
---

## Pattern

```
Need → Clarify → Search → Validate → [Found? Deliver : Expand]
```

Keep searching until found or exhausted. Start narrow, expand progressively. Validate before delivering.

## When to Use

- User needs to find something specific
- Location or source is unknown
- "Find me...", "Where can I get...", "I need to find..."

**Not for:** Things you already know, simple lookups, browsing.

## Setup

Before searching, clarify:

| Element | Why |
|---------|-----|
| What exactly? | Avoid finding wrong thing |
| Success criteria | How will we know it's right? |
| Constraints | Budget, location, time, format |
| Already tried? | Don't repeat failed paths |

If user is vague → ask ONE clarifying question, then start.

## Search Expansion

Start narrow, expand if not found:

```
1. Obvious sources → Direct lookup, known locations
2. Specialized sources → Domain-specific databases, expert communities  
3. Alternative queries → Different words, related concepts
4. Indirect paths → Who would know? What links to this?
5. Ask human → More context, different angle
```

Each expansion: try multiple sources in parallel when possible.

## Validation

Before delivering, verify:
- Is this actually what was asked for?
- Is the source reliable?
- Is it current/valid?
- Any caveats user should know?

If uncertain → say so. "Found X but not 100% sure it's what you need."

## Delivery

```
FOUND: [what]
WHERE: [source]
CONFIDENCE: [high/medium/low]
CAVEATS: [if any]
```

If multiple results: summarize and let user choose.

## Not Found

If exhausted all paths:
1. Report what was tried
2. Closest alternatives found
3. Suggest different approach or more context needed

---

**Related:** For iterating until success criteria are met, see `loop`. For multi-phase workflows, see `cycle`.
