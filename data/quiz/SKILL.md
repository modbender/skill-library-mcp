---
name: Quiz
description: Design engaging quizzes with effective questions, scoring logic, and results that drive learning or conversions.
---

## Situation Detection

| Context | Load |
|---------|------|
| Knowledge assessment, exams, certifications | `types.md` → Knowledge section |
| Personality quizzes, "Which X are you?" | `types.md` → Personality section |
| Lead generation, marketing quizzes | `types.md` → Lead-gen section |
| Writing effective questions | `questions.md` |
| Building quiz UI/UX, gamification | `implementation.md` |

---

## Universal Rules

**One concept per question.** Double-barreled questions confuse and measure nothing. "Do you like pizza and exercise?" → Bad.

**Wrong answers must be plausible.** If correct answer is obvious by elimination, you're testing pattern recognition, not knowledge.

**Results must feel personal.** Generic outcomes kill engagement. "You got 7/10" loses to "You're an 80s Movie Expert — you caught references most people miss."

**Progress visibility motivates.** Show question count, progress bar, time remaining. Uncertainty creates anxiety and abandonment.

---

## Quiz Types Quick Reference

| Type | Goal | Typical Length | Results |
|------|------|----------------|---------|
| Knowledge | Assess learning | 10-20 questions | Score + feedback per answer |
| Personality | Engagement, sharing | 5-12 questions | Personality type/category |
| Assessment | Diagnose level/fit | 10-30 questions | Detailed report |
| Lead-gen | Capture email | 5-8 questions | Results gated behind email |
| Trivia | Entertainment | Any | Leaderboard, social share |

---

## Question Design Checklist

- [ ] Clear, unambiguous wording
- [ ] One correct answer (or explicit multi-select instruction)
- [ ] Distractors are plausible, not obviously wrong
- [ ] No "all of the above" or "none of the above" (lazy design)
- [ ] Avoid negatives ("Which is NOT...")
- [ ] Test the concept, not reading comprehension

---

## Scoring Patterns

**Simple percentage:** Correct/total × 100. Best for knowledge tests.

**Weighted scoring:** Some questions worth more. Good for prioritized competencies.

**Branching outcomes:** Answer combinations map to results. Used in personality quizzes.

**Diagnostic rubric:** Score across multiple dimensions. Best for assessments and skill evaluations.

---

## Engagement Boosters

- Immediate feedback after each answer (right/wrong + explanation)
- Visual progress indicator
- Streak rewards ("3 in a row!")
- Time pressure (optional, increases excitement but also anxiety)
- Social sharing of results
- Leaderboards for competitive contexts

---

## Red Flags

- All correct answers in position B/C → Detectable pattern
- Questions testing obscure trivia vs actual learning objectives
- Results that don't connect to actions ("Now what?")
- Too long with no progress indication → Abandonment
- Mobile-unfriendly UI (tiny buttons, horizontal scroll)

---

## When to Load More

| Situation | Reference |
|-----------|-----------|
| Designing for specific quiz type | `types.md` |
| Writing and reviewing questions | `questions.md` |
| Building quiz flow, UI, tools | `implementation.md` |
