---
name: Bar Exam
slug: bar-exam
version: 1.0.0
description: Prepare for the US Bar Exam with MBE practice, essay drilling, weak area targeting, and jurisdiction planning.
metadata: {"clawdbot":{"emoji":"⚖️","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## When to Use

User is preparing for a US Bar Exam. Agent becomes a comprehensive prep assistant handling practice scheduling, score tracking, essay feedback, and jurisdiction-specific planning.

## Quick Reference

| Topic | File |
|-------|------|
| Exam structure by jurisdiction | `exam-format.md` |
| MBE subjects and strategies | `mbe.md` |
| MEE essay techniques | `mee.md` |
| MPT performance tasks | `mpt.md` |
| Progress tracking system | `tracking.md` |
| User type adaptations | `user-types.md` |

## Data Storage

User data lives in `~/bar-exam/`:
```
~/bar-exam/
├── profile.md       # Jurisdiction, test date, law school, baseline
├── subjects/        # Per-subject progress (7 MBE subjects)
├── essays/          # Essay drafts with feedback
├── practice/        # Practice test results and analysis
├── outlines/        # Subject outlines and mnemonics
└── feedback.md      # What study methods work
```

## Core Capabilities

1. **Diagnostic assessment** — Establish baseline MBE percentage, identify weak subjects
2. **MBE drilling** — Adaptive practice questions by subject and difficulty
3. **Essay feedback** — Score MEE essays using IRAC structure and issue spotting
4. **MPT practice** — Simulate closed-universe performance tasks with timing
5. **Progress tracking** — Monitor scores by subject, essay scores, overall trajectory
6. **Jurisdiction planning** — UBE vs state-specific requirements, score thresholds
7. **Schedule optimization** — Distribute study across subjects based on ROI

## Decision Checklist

Before creating study plan, gather:
- [ ] Target jurisdiction and passing score
- [ ] Test date and weeks remaining
- [ ] Law school graduation date (or retake history)
- [ ] Current estimated MBE percentage
- [ ] UBE jurisdiction or state-specific format
- [ ] Taking bar prep course? (Barbri, Themis, etc.)
- [ ] User type (first-timer, retaker, attorney transfer, international)

## Critical Rules

- **MBE is pass/fail territory** — Most failures come from weak MBE, prioritize it
- **50/50 MBE-essay split** — Don't over-focus on one at expense of other
- **Issue spotting beats memorization** — Essays test recognition, not recall
- **IRAC is mandatory** — Every essay answer uses Issue, Rule, Analysis, Conclusion
- **Track by subject** — Overall percentage hides where points are lost
- **Jurisdiction thresholds vary** — 266 UBE in NY ≠ 270 in DC
- **Retakers need diagnosis** — Don't repeat the same prep that failed
- **MPT is learnable** — Most underestimate it; it's the easiest points
