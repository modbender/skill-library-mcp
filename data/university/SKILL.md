---
name: University
slug: university
version: 1.0.0
description: Replace or complement traditional university with AI-powered degree programs, adaptive learning, exam preparation, and progress tracking.
metadata: {"clawdbot":{"emoji":"🎓","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## When to Use

User wants to: learn a complete degree/career autodidactically, support their current university studies, prepare for certifications/exams, change careers with structured upskilling, or help someone else study. Agent manages the entire learning lifecycle.

## Quick Reference

| Area | File |
|------|------|
| Degree/career setup | `degrees.md` |
| Content generation | `content.md` |
| Assessment & exams | `assessment.md` |
| Planning & calendar | `planning.md` |
| Progress tracking | `tracking.md` |
| Study formats | `formats.md` |
| Learning preferences | `feedback.md` |

## Workspace Structure

All learning data lives in ~/university/:

```
~/university/
├── degrees/              # One folder per degree/career/certification
│   ├── index.md          # Active degrees list with status
│   └── [degree-name]/    # Per-degree folder
│       ├── curriculum.md # Full curriculum with modules
│       ├── progress.md   # Module completion, mastery levels
│       ├── calendar.md   # Exam dates, deadlines, milestones
│       └── modules/      # Study materials by module
├── resources/            # Uploaded PDFs, slides, recordings
├── exams/               # Test history, practice exams
├── flashcards/          # Spaced repetition card sets
└── config.md            # Study preferences, schedule, goals
```

## Core Operations

**New degree/career:** User says what they want to learn → Generate complete curriculum equivalent to university degree → Map prerequisites → Estimate total time → Create study calendar → Store in degrees/[name]/.

**Daily study:** Check calendar and progress → Generate today's session (reading + exercises + review) → Adapt to available time → Track completion.

**Content processing:** User uploads PDF/audio/video → Extract key concepts → Generate summary → Create flashcards → Add to relevant module.

**Assessment:** Generate practice tests from studied material → Simulate real exam conditions → Correct with explanations → Update mastery tracking → Schedule review for weak areas.

**Progress review:** Show completion %, mastery by topic, time invested → Predict readiness for exams → Alert if falling behind → Suggest plan adjustments.

## Critical Rules

- Never generate exam answers without teaching first — explain WHY
- Track what user knows vs doesn't know — don't assume mastery
- Adapt difficulty progressively — start where user actually is
- Spaced repetition is mandatory — schedule reviews automatically
- Distinguish "studied" from "mastered" — require verification
- Support multiple degrees simultaneously — keep them organized
- Learn user's optimal study patterns — times, formats, duration

## User Modes

| Mode | Focus | Trigger |
|------|-------|---------|
| Autodidact | Full degree replacement | "I want to learn medicine/law/engineering" |
| Student | Complement existing university | "Help me with my classes/exams" |
| Career Change | Upskilling with portfolio | "I want to transition to data science" |
| Exam Prep | Certifications, bar exams, etc. | "Help me pass AWS/PMP/MIR" |
| Tutor | Help someone else learn | "Help my kid with school" |

See `degrees.md` for setup workflows per mode.

## On First Use

1. Ask: What do you want to learn? (degree, skill, certification)
2. Assess: Current knowledge level, available time per week
3. Generate: Curriculum with realistic timeline
4. Configure: Study preferences (formats, schedule, goals)
5. Create: ~/university/ structure
