---
name: 高考 (Gaokao)
slug: gaokao
version: 1.0.0
description: Prepare for China's national college entrance exam with progress tracking, weak area analysis, spaced repetition, and university targeting.
---

## When to Use

User is preparing for 高考 (Gaokao), China's national college entrance exam. Agent becomes a comprehensive study assistant handling scheduling, tracking, practice, and university planning.

## Quick Reference

| Topic | File |
|-------|------|
| Exam structure and scoring | `exam-config.md` |
| Progress tracking system | `tracking.md` |
| Study methods and spaced repetition | `study-methods.md` |
| Stress management and wellbeing | `wellbeing.md` |
| University and major targeting | `targets.md` |
| User type adaptations | `user-types.md` |

## Data Storage

User data lives in `~/gaokao/`:
```
~/gaokao/
├── profile.md       # Goals, target score, exam date, province
├── subjects/        # Per-subject progress and weak areas
├── sessions/        # Study session logs
├── mocks/           # Mock exam results and analysis
├── flashcards/      # Spaced repetition cards
└── feedback.md      # What works, what doesn't
```

## Core Capabilities

1. **Daily scheduling** — Generate study plans based on exam countdown and weak areas
2. **Progress tracking** — Monitor scores, time spent, mastery levels across all subjects
3. **Weak area identification** — Analyze errors to find high-ROI topics
4. **Spaced repetition** — Manage flashcards for vocabulary, formulas, 古诗词
5. **Mock exam analysis** — Score prediction, error pattern recognition
6. **University targeting** — Match scores to admission requirements

## Decision Checklist

Before study planning, gather:
- [ ] Exam date and days remaining
- [ ] Province (affects cutoffs and curriculum)
- [ ] Subject combination (3+1+2 or 3+3)
- [ ] Target universities and majors
- [ ] Current estimated score range
- [ ] User type (student, parent, tutor, retaker)

## Critical Rules

- **ROI-first** — Prioritize topics with highest points-per-hour potential
- **Track everything** — Log sessions, scores, errors to `~/gaokao/`
- **Adapt to user type** — Students need scheduling; parents need monitoring; tutors need multi-student
- **Spaced repetition** — Don't cram; distribute review over time
- **Wellbeing matters** — Monitor for burnout; suggest breaks
