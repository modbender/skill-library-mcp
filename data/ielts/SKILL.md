---
name: IELTS
slug: ielts
version: 1.0.0
description: Prepare for IELTS Academic or General Training with progress tracking, weak area analysis, band score targeting, and immigration pathway guidance.
---

## When to Use

User is preparing for IELTS (International English Language Testing System). Agent becomes a comprehensive study assistant handling diagnostics, practice, scoring, and target planning.

## Quick Reference

| Topic | File |
|-------|------|
| Exam structure and scoring | `exam-config.md` |
| Progress tracking system | `tracking.md` |
| Study methods and practice | `study-methods.md` |
| Score targets by purpose | `targets.md` |
| User type adaptations | `user-types.md` |
| Self-improvement tracking | `feedback.md` |

## Data Storage

User data lives in `~/ielts/`:
```
~/ielts/
├── profile.md       # Goals, target band, exam date, test type
├── sections/        # Per-section progress (listening, reading, writing, speaking)
├── sessions/        # Study session logs
├── mocks/           # Practice test results and analysis
├── essays/          # Writing samples with feedback
└── speaking/        # Speaking recordings and transcripts
```

## Core Capabilities

1. **Diagnostic assessment** — Identify current band level and weak sections
2. **Band gap analysis** — Compare current vs target scores, calculate points needed
3. **Practice generation** — Create fresh tasks for any section (charts, essays, prompts)
4. **Writing evaluation** — Score essays against IELTS criteria (TA, CC, LR, GRA)
5. **Speaking simulation** — Run timed mock interviews with feedback
6. **Progress tracking** — Monitor scores, time spent, improvement trends
7. **Target guidance** — Match scores to university/immigration requirements

## Decision Checklist

Before study planning, gather:
- [ ] Test type: Academic or General Training
- [ ] Exam date and days remaining
- [ ] Target overall band and per-section minimums
- [ ] Purpose (university, immigration, professional registration)
- [ ] User type (first-timer, retaker, professional, student)
- [ ] Current estimated band from diagnostic or prior attempt

## Critical Rules

- **Academic vs GT** — Writing Task 1 differs completely (graph vs letter). Confirm type first.
- **No section below minimum** — Many targets require ALL bands at threshold (e.g., 6.5 each)
- **2-year validity** — Scores expire. Plan retakes if immigration timeline extends.
- **One Skill Retake** — Available within 60 days of original test. Suggest when one section drags overall down.
- **Band descriptors** — Use official criteria for Writing/Speaking feedback, not impressions.
