# Memory Template — AGI

Create `~/agi/memory.md` with this structure:

```markdown
# AGI Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending

## User Style
<!-- How this user prefers to communicate -->
<!-- Concise vs detailed, technical level, emotional awareness -->

## Effective Patterns
<!-- Reasoning approaches that worked well -->
<!-- Transfer learning successes to remember -->

## Notes
<!-- Observations about what helps this user -->
<!-- Calibration notes: when to be more/less certain -->

---
*Updated: YYYY-MM-DD*
```

## reflections.md Template

Create `~/agi/reflections.md`:

```markdown
# Reasoning Reflections

<!-- Log significant learning moments -->

## Template Entry
### YYYY-MM-DD
**Situation:** What happened
**Insight:** What you learned
**Pattern:** Reusable principle

---
```

## limits.md Template

Create `~/agi/limits.md`:

```markdown
# Known Limits

<!-- Topics where you've discovered gaps -->

## Knowledge Gaps
<!-- Things you've been wrong about or don't know -->
- [Topic]: [What you don't know / were wrong about]

## Uncertainty Patterns
<!-- When to be extra cautious -->
- [Domain/topic]: [Why uncertainty is higher here]

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Default | Keep improving |
| `complete` | Has enough context | Rare for AGI — always learning |
| `paused` | User prefers simpler responses | Reduce meta-cognition |
| `never_ask` | User finds it annoying | Be invisible |

## Key Principles

- **Invisible improvement** — user shouldn't notice "AGI working"
- **Calibrated confidence** — update limits.md when wrong
- **Reflection drives growth** — log insights, review periodically
- **No configuration needed** — just think better
