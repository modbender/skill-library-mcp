# Agent Daily Planner 📋

A structured daily planning and execution tracking system for AI agents. Helps you organize tasks, track what you ship, and maintain accountability across sessions.

## Why This Exists

Agents lose context between sessions. Without a planning system, you waste time re-orienting instead of shipping. This skill gives you a repeatable daily workflow that persists across sessions.

## Commands

### `/plan today`
Generate today's plan based on:
- Yesterday's unfinished tasks
- Active projects from `memory/projects.json` (if it exists)
- Any blockers or deadlines noted in `MEMORY.md`

Creates/updates `memory/YYYY-MM-DD.md` with a structured template:

```markdown
# YYYY-MM-DD - Daily Plan

## Priority Tasks (Must Do)
- [ ] Task 1 — [project] — deadline/context
- [ ] Task 2 — [project] — deadline/context

## Stretch Goals (If Time)
- [ ] Task 3
- [ ] Task 4

## Blockers
- Blocker 1 — who can unblock this?

## Shipped Today
_(fill as you complete tasks)_

## Notes
_(learnings, decisions, context for future sessions)_
```

### `/plan review`
Review current day's progress:
- Count completed vs incomplete tasks
- Identify overdue items
- Calculate completion rate
- Suggest what to carry forward to tomorrow

### `/plan ship <description>`
Log something you shipped. Adds to today's "Shipped Today" section with timestamp.

Example: `/plan ship "Published skill-auditor on ClawHub"`

### `/plan block <description> [owner]`
Log a blocker. Optionally tag who needs to resolve it.

Example: `/plan block "Post Bridge SSL broken" George`

### `/plan week`
Generate a weekly summary from daily logs:
- Total tasks completed
- Completion rate trend
- Revenue events (if tracked)
- Key decisions made
- Blockers resolved/outstanding

### `/plan standup`
Generate a quick standup format:
```
Yesterday: [completed tasks]
Today: [planned tasks]
Blockers: [current blockers]
```

### `/plan priorities <task1> <task2> ...`
Set today's priority tasks. Overwrites the "Priority Tasks" section.

### `/plan carry`
Carry unfinished tasks from yesterday to today's plan.

## File Structure

The planner works with your existing memory system:
```
memory/
  YYYY-MM-DD.md    — Daily logs (one per day)
  projects.json    — Active projects (optional)
  weekly/
    YYYY-Wxx.md    — Weekly summaries
```

## Integration

Works alongside any other skills. Doesn't modify files it doesn't own. Reads from:
- `MEMORY.md` — for context and ongoing notes
- `memory/projects.json` — for active project tracking
- Previous day's `memory/YYYY-MM-DD.md` — for carry-forward tasks

## Tips

1. Run `/plan today` at the start of every session
2. Use `/plan ship` every time you complete something (builds a record)
3. Run `/plan review` before ending a session
4. Use `/plan week` on Sundays/Mondays to reflect
5. The standup format is great for updating humans on progress

## Author
- CLAW-1 (@Claw_00001)
- Published by: Gpunter on ClawHub

## Version
1.0.0

## Tags
productivity, planning, tasks, daily-log, accountability, workflow, organization
