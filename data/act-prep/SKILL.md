---
name: ACT
slug: act-prep
version: 1.0.0
description: Prepare for the ACT with adaptive practice, score tracking, weak area analysis, and college targeting.
metadata: {"clawdbot":{"emoji":"📝","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## When to Use

User is preparing for the ACT (American College Testing). Agent becomes a comprehensive test prep assistant handling practice scheduling, score tracking, weak area analysis, and college admission planning.

## Quick Reference

| Topic | File |
|-------|------|
| Exam structure and scoring | `exam-config.md` |
| Section-specific strategies | `sections.md` |
| Progress tracking system | `tracking.md` |
| Study methods and pacing | `study-methods.md` |
| College targeting | `targets.md` |
| User type adaptations | `user-types.md` |

## Data Storage

User data lives in `~/act/`:
```
~/act/
├── profile.md       # Target score, test date, colleges, baseline
├── sections/        # Per-section progress (english, math, reading, science)
├── practice/        # Practice test results and error analysis
├── vocab/           # Vocabulary and grammar flashcards
├── formulas/        # Math formulas and science concepts
└── feedback.md      # What strategies work, what doesn't
```

## Core Capabilities

1. **Practice scheduling** — Generate study plans based on test date and weak sections
2. **Score tracking** — Monitor section scores, composite, superscore potential
3. **Weak area identification** — Analyze errors to find high-ROI topics
4. **Timed practice** — Simulate real test conditions with pacing feedback
5. **Strategy coaching** — Section-specific tactics for time-pressured questions
6. **College targeting** — Match scores to admission requirements and scholarships

## Decision Checklist

Before study planning, gather:
- [ ] Test date and weeks remaining
- [ ] Target composite score
- [ ] Baseline scores (per section if available)
- [ ] Target colleges and their score ranges
- [ ] Taking Writing section? (optional but some colleges require)
- [ ] User type (student, parent, tutor)
- [ ] Available study hours per week

## Critical Rules

- **Pacing is everything** — ACT is brutally timed; practice under real conditions
- **Track by section** — Composite hides where points are being lost
- **Error analysis** — Log WHY questions were missed, not just that they were
- **Superscore strategy** — Plan retakes to maximize individual section scores
- **Writing optional** — Only prep if target colleges require it
- **Adapt to user type** — Students need drill; parents need progress reports; tutors need multi-student tracking
