# Memory Template — NumPy

Create `~/numpy/memory.md` with this structure:

```markdown
# NumPy Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending | done | declined

## Context
<!-- Their numerical computing context -->
<!-- experience: beginner | intermediate | advanced -->
<!-- use_cases: data science, scientific computing, ML, general -->

## Preferences
<!-- Saved from explicit user preferences shared in conversation -->
<!-- default_dtype: float32 | float64 -->
<!-- memory_priority: speed | memory | balanced -->

## Common Patterns
<!-- Patterns the user explicitly shares or asks to save -->

## Notes
<!-- Things the user mentions about their workflow -->

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Learning their preferences | Ask when relevant |
| `complete` | Know their preferences well | Work normally |
| `paused` | User said "not now" | Don't ask, work with what you have |
| `never_ask` | User said stop | Never ask for more context |

## Key Principles

- Update `last` on each significant interaction
- Only save information the user explicitly shares
- Preferences are learned from conversations, not inferred from external files
