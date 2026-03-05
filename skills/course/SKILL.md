---
name: Course
slug: course
version: 1.0.1
changelog: Minor refinements for consistency
description: Create, launch, and manage online or in-person courses with curriculum design, content production, marketing automation, and student engagement.
metadata: {"clawdbot":{"emoji":"📚","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## When to Use

User wants to: create a course to monetize expertise, transform existing materials into online format, launch and sell a course, manage students and track progress, or improve an existing course. Works for online, in-person, or hybrid formats.

NOT for: taking courses as a student (use `university` or `school`), general teaching without course structure, corporate compliance-only training.

## Quick Reference

| Area | File |
|------|------|
| Audience-specific workflows | `by-audience.md` |
| Curriculum & content creation | `content.md` |
| Video, slides, materials | `production.md` |
| Launch, sales, promotion | `marketing.md` |
| Student support & community | `students.md` |
| Metrics & improvement | `analytics.md` |

## Workspace Structure

All course data lives in ~/courses/:

```
~/courses/
├── [course-name]/           # One folder per course
│   ├── curriculum.md        # Modules, lessons, objectives
│   ├── content/             # Raw materials, scripts, notes
│   ├── production/          # Videos, slides, downloads
│   ├── marketing/           # Sales page, emails, promos
│   ├── students.md          # Enrollment, progress tracking
│   └── analytics.md         # Metrics, feedback, improvements
├── templates/               # Reusable templates
└── config.md                # Platforms, integrations, defaults
```

## Core Operations

**New course:** User has expertise/topic → Analyze existing materials → Generate curriculum structure → Estimate production timeline → Create folder structure.

**Transform content:** User provides PDFs, recordings, presentations → Extract key concepts → Restructure into lesson format → Generate scripts/outlines.

**Create module:** Topic + learning objectives → Write lesson script → Design exercises/assessments → Specify supporting materials needed.

**Launch course:** Course content ready → Generate sales page copy → Create email sequences → Configure platform → Set pricing and access rules.

**Manage students:** Track enrollment and progress → Identify at-risk students → Automate reminders → Generate completion certificates.

**Improve course:** Collect feedback → Analyze completion rates → Identify problem areas → Suggest specific improvements.

## Course Creation Phases

| Phase | Agent Does | User Does |
|-------|------------|-----------|
| 1. Validate | Research competition, identify gaps, suggest positioning | Approve direction |
| 2. Structure | Generate curriculum from materials, define modules | Review and adjust |
| 3. Content | Write scripts, create exercises, design assessments | Record/review |
| 4. Production | Edit videos, create slides, generate materials | Quality check |
| 5. Platform | Configure course, set up payments, test flows | Final approval |
| 6. Launch | Write sales copy, create email sequences, schedule promos | Approve messaging |
| 7. Operate | Answer FAQs, track progress, send reminders | Handle escalations |
| 8. Improve | Analyze feedback, suggest updates, create new content | Prioritize changes |

## Critical Rules (ALWAYS Apply)

- **Never skip validation** — Before creating content, understand competition and positioning
- **Transform, don't recreate** — Start from user's existing materials whenever possible
- **Modular design** — Every lesson should be 10-20 minutes max, self-contained
- **Assessment required** — Each module needs evaluation (quiz, exercise, project)
- **Automation first** — Student support should be 80% automated, 20% human
- **Data-driven iteration** — Track completion rates, feedback, and engagement to improve
- **Platform-agnostic** — Advice should work on any platform (Teachable, Thinkific, Kajabi, custom)

## Content Transformation Quick Guide

| Source Material | Transformation |
|----------------|----------------|
| Long recordings | → Transcribe → Split by topic → Clean into scripts |
| PDF notes/slides | → Extract outline → Expand into lessons → Add exercises |
| 1:1 session recordings | → Identify patterns → Group by theme → Create modules |
| Conference talks | → Transcribe → Restructure for course → Add depth |
| Blog posts/articles | → Organize by topic → Fill gaps → Add assessments |

## On First Use

1. Ask what type of course creator they are (expert, educator, creator, corporate, coach)
2. Understand their existing materials (recordings, notes, slides, nothing)
3. Identify target audience and transformation goal
4. Propose curriculum structure based on materials
5. Create ~/courses/[name]/ folder structure
