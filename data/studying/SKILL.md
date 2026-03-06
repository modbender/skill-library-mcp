---
name: "Studying"
version: "1.0.1"
changelog: "Preferences now persist across skill updates"
description: "Auto-learns your study habits for academic success. Adapts techniques, timing, and materials to you."
---

## Auto-Adaptive Study Preferences

This skill auto-evolves. User preferences persist in `~/studying/memory.md`. Create on first use:

```markdown
## Techniques
<!-- Study methods that work. Format: "method: context (level)" -->
<!-- Examples: Active recall for facts (confirmed), Mind maps for concepts (pattern) -->

## Schedule
<!-- When/how they study best. Format: "preference (level)" -->
<!-- Examples: Morning sessions (confirmed), 25min blocks (pattern) -->

## Materials
<!-- Preferred formats. Format: "type: context (level)" -->
<!-- Examples: Video lectures for intro (confirmed), Textbooks for deep (pattern) -->

## Exams
<!-- Exam prep patterns. Format: "pattern (level)" -->
<!-- Examples: Past papers week before (confirmed), Cramming doesn't work (locked) -->

## Never
<!-- Approaches that fail. Format: "approach (level)" -->
<!-- Examples: Rereading (confirmed), Highlighting only (pattern) -->
```

*Empty sections = no preference yet. Observe and fill. Levels: pattern → confirmed → locked*

**Rules:**
- Detect patterns from what study methods work and which don't
- Focused on academic contexts (exams, courses, grades)
- Confirm after 2+ consistent signals
- Check `dimensions.md` for categories, `criteria.md` for format
