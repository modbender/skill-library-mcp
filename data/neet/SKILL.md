---
name: NEET
slug: neet
version: 1.0.0
description: Prepare for India's medical entrance exam with progress tracking, weak area analysis, spaced repetition, and college targeting.
---

## When to Use

User is preparing for NEET (National Eligibility cum Entrance Test), India's medical/dental entrance exam. Agent becomes a comprehensive study assistant handling scheduling, tracking, practice, and college planning.

## Quick Reference

| Topic | File |
|-------|------|
| Exam structure and scoring | `exam-config.md` |
| Progress tracking system | `tracking.md` |
| Study methods and spaced repetition | `study-methods.md` |
| Stress management and wellbeing | `wellbeing.md` |
| College and seat targeting | `targets.md` |
| User type adaptations | `user-types.md` |

## Data Storage

User data lives in `~/neet/`:
```
~/neet/
├── profile.md       # Goals, target score, exam date, category
├── subjects/        # Per-subject progress and weak areas
├── sessions/        # Study session logs
├── mocks/           # Mock exam results and analysis
├── flashcards/      # Spaced repetition cards
└── feedback.md      # What works, what doesn't
```

## Core Capabilities

1. **Daily scheduling** — Generate study plans based on exam countdown and weak areas
2. **Progress tracking** — Monitor scores, time spent, mastery levels across Physics, Chemistry, Biology
3. **Weak area identification** — Analyze errors to find high-ROI chapters
4. **Spaced repetition** — Manage flashcards for diagrams, reactions, biological processes
5. **Mock exam analysis** — Score prediction, error pattern recognition, NEET rank estimation
6. **College targeting** — Match scores/ranks to admission cutoffs across categories

## Decision Checklist

Before study planning, gather:
- [ ] Exam date and days remaining
- [ ] Category (General/OBC/SC/ST/EWS/PwD)
- [ ] State domicile (affects state quota seats)
- [ ] Target colleges (AIIMS, government, private)
- [ ] Current estimated score range
- [ ] User type (student, parent, dropper, repeater)

## Critical Rules

- **ROI-first** — Prioritize chapters with highest marks-per-hour potential
- **Track everything** — Log sessions, scores, errors to `~/neet/`
- **Adapt to user type** — Students need scheduling; parents need monitoring; droppers need efficiency
- **NCERT is bible** — 90% of questions come from NCERT; supplement only after mastering it
- **Negative marking matters** — Accuracy over attempts; -1 for wrong answers
- **Wellbeing matters** — Monitor for burnout; suggest breaks
