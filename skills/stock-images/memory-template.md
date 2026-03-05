# Memory Template — Stock Images

Create `~/stock-images/memory.md` if user wants to save preferences:

```markdown
# Stock Images Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: done

## Context
<!-- What you've learned about their image needs -->
<!-- E.g., "Building a SaaS app, needs professional mockups" -->

## Preferences
<!-- Observed preferences, not asked directly -->
<!-- E.g., "Prefers minimal, light backgrounds" -->
<!-- E.g., "Always asks for 1200x800 dimensions" -->

## Saved Images
<!-- URLs they've used and liked -->

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Learning their preferences | Note what they use |
| `complete` | Know their style | Apply preferences automatically |
| `declined` | Doesn't want tracking | Just provide URLs, no memory |

## Most Users

Most users don't need persistent memory. They just need URLs. Only create memory.md if they ask for saved preferences or consistent style guidance.
