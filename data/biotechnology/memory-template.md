# Memory Template — Biotechnology

Optional memory structure if the user wants persistent context tracking.

## Template

```markdown
# Biotechnology Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD

## Context
User's background and focus area.
Academic level, professional role, organisms they work with.

## Focus Areas
Specific techniques or topics they frequently discuss.
Examples: CRISPR, protein expression, fermentation, bioinformatics.

## Notes
Preferences inferred from conversations.
Level of detail they prefer, how technical to go.
```

## Status Values

| Value | Meaning |
|-------|---------|
| `ongoing` | Still learning about them |
| `complete` | Know their context well |
| `paused` | User said not now |

## Key Principles

- Detect level from vocabulary and questions
- Update organically as conversations reveal context
- Most users stay ongoing — their needs evolve
