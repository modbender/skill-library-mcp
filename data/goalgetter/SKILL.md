---
name: goalgetter
description: "Tasks and goals management via simple markdown files. Create, track, and complete tasks and goals with streak tracking. Stores data in ~/.openclaw/goalgetter/. Triggers: 'add task', 'new goal', 'task done', 'show tasks', 'goal streak', 'complete task'."
author: DevSef
version: 1.0.0
tags: [tasks, goals, productivity, habits, streaks, markdown]
---

# GoalGetter - Tasks & Goals in Markdown

Simple task and goal tracking using plain markdown files. No external dependencies.

## Data Location

Default: `~/.openclaw/goalgetter/`

Files:
- `tasks.md` - Todo list
- `goals.md` - Goal tracking with streaks
- `done/` - Archive of completed items

## Commands

### Tasks

**Add task:**
```bash
echo "- [ ] $TEXT" >> ~/.openclaw/goalgetter/tasks.md
```

**Complete task:**
```bash
# Read tasks.md, find task, move to done/TIMESTAMP.md, mark complete
```

**List tasks:**
```bash
cat ~/.openclaw/goalgetter/tasks.md
```

### Goals

**Add goal:**
```bash
echo "## $GOAL_NAME" >> ~/.openclaw/goalgetter/goals.md
echo "- streak: 0" >> ~/.openclaw/goalgetter/goals.md
echo "- created: $DATE" >> ~/.openclaw/goalgetter/goals.md
echo "- log:" >> ~/.openclaw/goalgetter/goals.md
```

**Mark goal done:**
```bash
# Read goals.md, increment streak, add date to log
```

**Show streaks:**
```bash
# Read goals.md and display each goal with current streak
```

## File Formats

### tasks.md
```markdown
# Tasks

- [ ] Buy groceries
- [x] Call dentist
- [ ] Finish SAAS research
```

### goals.md
```markdown
# Goals

## Meditation
- streak: 5
- created: 2026-01-15
- log:
  - 2026-01-15
  - 2026-01-16
  - 2026-01-17
  - 2026-01-18
  - 2026-01-19

## Exercise
- streak: 2
- created: 2026-02-01
- log:
  - 2026-02-15
  - 2026-02-16
```

## Usage Examples

| User says | Action |
|-----------|--------|
| "Add task: finish report" | Add to tasks.md |
| "Show my tasks" | Cat tasks.md |
| "Complete task: finish report" | Mark complete, move to done/ |
| "New goal: meditation" | Add to goals.md |
| "Did meditation" | Increment streak, add date |
| "Show goal streaks" | Display all goals with streaks |
| "How's my meditation goal?" | Show streak for that goal |

## Notes

- Always create ~/.openclaw/goalgetter/ if it doesn't exist
- Use ISO dates (YYYY-MM-DD) for consistency
- Use read tool to view current state before modifying
- Use write tool to update files
