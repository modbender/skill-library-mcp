---
name: TOEFL
slug: toefl
version: 1.0.0
description: Prepare for the TOEFL iBT exam with progress tracking, weak area analysis, score prediction, and university targeting.
---

## When to Use

User is preparing for TOEFL iBT (Test of English as a Foreign Language). Agent becomes a comprehensive study assistant handling scheduling, tracking, practice, score management, and university/immigration planning.

## Quick Reference

| Topic | File |
|-------|------|
| Exam structure and scoring | `exam-config.md` |
| Progress tracking system | `tracking.md` |
| Study methods and practice | `study-methods.md` |
| University and immigration targets | `targets.md` |
| User type adaptations | `user-types.md` |

## Data Storage

User data lives in `~/toefl/`:
```
~/toefl/
├── profile.md       # Goals, target score, test date, target schools
├── sections/        # Per-section progress (reading, listening, speaking, writing)
├── sessions/        # Study session logs
├── practice/        # Practice test results and analysis
├── vocabulary/      # Academic vocabulary tracking
└── feedback.md      # What works, what doesn't
```

## Core Capabilities

1. **Test scheduling** — Find optimal test dates based on application deadlines, track registration
2. **Progress tracking** — Monitor scores, time spent, mastery levels across all sections
3. **Weak area identification** — Analyze errors to find high-ROI question types
4. **Score prediction** — Estimate current level and readiness to test
5. **University research** — Look up TOEFL requirements, MyBest acceptance, waivers
6. **Score sending management** — Track where to send scores, deadlines, costs

## Decision Checklist

Before study planning, gather:
- [ ] Test date and days remaining
- [ ] Target universities/programs (each has different requirements)
- [ ] Current estimated score range
- [ ] User type (student, professional, tutor, retaker)
- [ ] Time available for study per week
- [ ] Previous TOEFL attempts (if any)

## Critical Rules

- **Deadlines first** — Work backwards from application deadline → score delivery → test date
- **Track everything** — Log sessions, scores, errors to `~/toefl/`
- **Adapt to user type** — Students need university research; professionals need immigration info; tutors need multi-student
- **Score is composite** — Each section 0-30, total 0-120; some schools require minimums per section
- **MyBest matters** — Some schools accept best scores across multiple tests; others require single-sitting
