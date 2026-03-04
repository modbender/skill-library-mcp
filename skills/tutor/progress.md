# Progress Tracking

## File Formats

### index.md (~/tutor/)
```markdown
# Learners

| Name | Age | Grade | Active Subjects | Last Session |
|------|-----|-------|-----------------|--------------|
| Emma | 9 | 4th | Math, Reading | 2026-02-12 |
| Carlos | 16 | 11th | Physics, SAT Prep | 2026-02-10 |
```

### profile.md (per learner)
```markdown
# Emma

**Age:** 9
**Grade:** 4th grade
**School:** Jefferson Elementary

## Learning Style
- Visual learner — needs diagrams
- Short attention span (~20 min)
- Motivated by games and challenges

## Goals
- Improve multiplication fluency
- Read chapter books independently

## Notes
- Struggles with word problems
- Gets frustrated with fractions
- Loves dinosaurs — use in examples
```

### sessions.jsonl (per learner)
```jsonl
{"date":"2026-02-12","duration":25,"subject":"math","topic":"multiplication 7s and 8s","went_well":"remembered 7x6 and 7x7","needs_work":"8x7 still tricky","engagement":"high"}
{"date":"2026-02-10","duration":20,"subject":"reading","topic":"Charlotte's Web ch 3","went_well":"good comprehension questions","needs_work":"vocabulary - 'injustice'","engagement":"medium"}
```

### progress.json (per learner)
```json
{
  "math": {
    "mastered": ["addition", "subtraction", "mult-1-6"],
    "working_on": ["mult-7-8", "word-problems"],
    "struggling": ["fractions-intro"],
    "last_updated": "2026-02-12"
  },
  "reading": {
    "current_level": "3rd-4th grade",
    "books_completed": ["Magic Tree House #1", "Diary of a Wimpy Kid"],
    "current_book": "Charlotte's Web",
    "vocabulary_log": ["injustice", "humble", "triumph"]
  }
}
```

### subjects/{subject}.md (per subject)
```markdown
# Math — Emma

## Current Unit
Multiplication facts 7-9

## Mastered
- Addition/subtraction fluency
- Multiplication 1-6
- Basic place value

## Working On
- 7s and 8s tables
- Word problems with multiplication

## Patterns
- Forgets 8x7 specifically — tried "56=7x8" memory trick
- Better with visual arrays than rote memorization

## Resources Used
- Times tables songs
- Grid method for multi-digit
```

---

## When to Update

| Event | Update |
|-------|--------|
| Session start | Read profile.md, recent sessions |
| Session end | Append to sessions.jsonl |
| Concept mastered | Update progress.json |
| New struggle identified | Update progress.json, subject file |
| Parent requests report | Generate to reports/ |

---

## Progress Reports

### For Parents (minors)
Generate to `~/tutor/{learner}/reports/{date}-report.md`:

```markdown
# Progress Report — Emma
**Period:** Feb 1-15, 2026
**Sessions:** 6 (2.5 hours total)

## Highlights
- Mastered 7s multiplication table
- Finished Charlotte's Web with strong comprehension
- Growing confidence with word problems

## Areas of Focus
- 8s and 9s multiplication
- Fraction concepts introduction
- Vocabulary building

## Recommendations
- Practice 8s table at home (5 min/day)
- Read together 15 min nightly

## Next Steps
- Complete multiplication unit
- Start fraction manipulatives
```

---

## Pattern Recognition

Track across sessions:
- **Error patterns** — Same mistakes recurring?
- **Energy patterns** — Better mornings vs evenings?
- **Subject avoidance** — Consistently avoiding one area?
- **Breakthroughs** — What approach finally worked?

Use patterns to adjust teaching and inform reports.

---

## Red Flags

Escalate to parent/guardian if:
- Consistent decline over 3+ sessions
- Zero engagement pattern
- Mentions of anxiety, distress
- Signs suggesting learning disability
- Concerning emotional states
