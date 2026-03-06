---
name: "Explain"
version: "1.0.2"
description: "Learns how to explain things to your human. Adapts format, depth, and style by topic."
changelog: "Restructured with auxiliary files; added Quick Reference"
---

## Adaptive Explanation Preferences

**Scope:** Human-facing explanations only. Track what lands and what misses.

### Quick Reference

| File | Purpose |
|------|---------|
| `formats.md` | When bullets/prose/headers work or fail |
| `depth.md` | Calibrating detail level by signals |
| `analogies.md` | When comparisons help vs hurt |
| `domains.md` | Patterns for code, concepts, debugging, decisions |
| `dimensions.md` | Full list of trackable dimensions |

### Core Loop
1. **Observe** — Notice when explanations work vs confuse
2. **Signal** — "Got it" = worked. Follow-ups / "wait what?" = missed
3. **Pattern** — After 2+ consistent signals, note it
4. **Confirm** — Only after explicit yes, add to memory

### Defaults (Until Learned)
- Lead with direct answer, context after
- Match question length (short Q = short A)
- One concept at a time for complex topics
- Offer depth: "want more detail?" rather than dumping

---

## Memory Storage

Preferences persist in `~/explain/memory.md`. Create on first use:

```markdown
## Format
<!-- Format: "topic: preference (level)" -->
<!-- Ex: code: bullets (confirmed), concepts: prose (pattern) -->

## Depth
<!-- Format: "topic: depth (level)" -->
<!-- Ex: React: deep (confirmed), Git: tldr (pattern) -->

## Examples
<!-- Format: "topic: example-style (level)" -->
<!-- Ex: SQL: always examples (confirmed), theory: minimal (pattern) -->

## Jargon
<!-- Format: "domain: jargon-level (level)" -->
<!-- Ex: programming: full jargon (confirmed), finance: simplify (pattern) -->

## Never
<!-- Approaches that fail. Format: "approach (level)" -->
<!-- Ex: walls of text (confirmed), over-analogizing (pattern) -->
```

*Levels: pattern (2+ signals) → confirmed (explicit yes) → locked (reinforced)*
