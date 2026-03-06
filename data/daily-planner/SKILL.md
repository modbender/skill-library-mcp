---
name: Daily Planner
slug: daily-planner
version: 1.0.0
description: Plan, protect, and execute your day with morning briefings, priority management, calendar blocking, and commitment tracking.
metadata: {"clawdbot":{"emoji":"📆","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## Quick Reference

| File | Purpose |
|------|---------|
| `profiles.md` | Configure by user type (exec, freelancer, parent, student, founder) |
| `routines.md` | Morning briefing, evening review, weekly planning |
| `priorities.md` | Top 3 system, urgent vs important matrix |
| `calendar.md` | Time blocking, deep work protection, conflict detection |
| `tracking.md` | Commitment tracking, follow-up reminders |

## Storage

Data stored in `~/planner/`:
- **config** — Profile, energy windows, constraints
- **today** — Current day plan (regenerated daily)
- **commitments** — Open commitments and follow-ups
- **weekly** — Week overview with deadlines
- **archive/** — Past plans for patterns

## What the Agent Does

| User Says | Agent Action |
|-----------|--------------|
| "Plan my day" | Generate time-blocked schedule based on priorities and energy |
| "What's urgent?" | Filter top 3 from calendar/tasks, show deadline proximity |
| "Protect my morning" | Block deep work, defer non-critical, enable DND mode |
| "I promised X to Y" | Log commitment with deadline, set follow-up reminder |
| "Am I overcommitted?" | Analyze week, flag conflicts, suggest cuts |
| "Weekly review" | Summarize done/pending, adjust next week, archive completed |

## Core Loop

**Morning (configurable time):**
1. Pull calendar events, pending tasks, open commitments
2. Apply profile rules (energy windows, constraints)
3. Generate Top 3 priorities (what MUST happen today)
4. Produce briefing: 5 bullets max, critical first

**During day:**
- Track new commitments from conversations
- Alert on deadline proximity (48h, 24h, 2h)
- Batch interruptions, filter by configured urgency

**Evening:**
- What got done, what moved forward
- Commitments made today logged
- Tomorrow's preview

See `routines.md` for full workflow details.

## Priority Rules

- **Top 3 only** — if user lists >3, force ranking
- **Important > Urgent** — deadline pressure ≠ high impact
- **Energy match** — hard tasks to peak hours, admin to low-energy
- **Buffer mandatory** — never 100% scheduled, leave 20% slack

See `priorities.md` for prioritization framework.

## Profile-Based Behavior

The agent adapts to user type. On first use, ask or infer profile:

- **Executive**: Calendar-driven, meeting prep, delegation suggestions
- **Freelancer**: Project-based, deadline tracking, client context
- **Parent**: Family-work balance, coordination, contingency plans  
- **Student**: Academic calendar, exam periods, study sessions
- **Founder**: Multi-area tracking, interruption filtering, deep work protection

See `profiles.md` for profile-specific behaviors.

## Commitment Tracking

Every promise made = logged automatically:
- Extract from conversations: "I'll send you X by Y"
- Add to commitments file with deadline
- Remind before deadline (configurable: 24h, 48h)
- Flag overdue until resolved

See `tracking.md` for commitment workflow.
