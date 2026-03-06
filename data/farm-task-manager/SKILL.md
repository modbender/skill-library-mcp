---
name: Farm Task Manager
description: "Farm Task Manager helps farmers organize daily, weekly, and
  seasonal chores with task scheduling, priorities, and tracking. Perfect for:"
---

# Farm Task Manager

*Daily, weekly, and seasonal farm chore management with task scheduling and priorities.*

**Author:** IOU (@johstracke)
**Version:** 1.0.0
**Created:** 2026-02-12

---

## About This Skill

Farm Task Manager helps farmers organize daily, weekly, and seasonal chores with task scheduling, priorities, and tracking. Perfect for:

- Small farmers (1-10 acres)
- Hobby farmers and homesteaders
- Farm-to-table operators
- Anyone juggling multiple farm responsibilities

### Why I Built This

I built Farm Task Manager because farm work is overwhelming - there's always something to do (planting, maintenance, harvesting, animal care, equipment repairs). Keeping track in your head means forgetting important tasks, misprioritizing, and wasting time. Now I just type `farm-task add "Fix irrigation" --priority high` and forget about it until it's due.

---

## Features

- **Task Management**: Add tasks with name, description, priority, due date, category, and assignee
- **Task Filtering**: List tasks by status, priority, category, due date, assignee
- **Task Updates**: Update task status (pending, in-progress, completed) and add notes
- **Recurring Tasks**: Create daily, weekly, monthly, or seasonal recurring tasks
- **Search**: Search across all tasks by name, description, or category
- **Export**: Export to markdown or JSON for sharing and backup

---

## Usage

### Add a Task

```bash
farm-task add "Check irrigation system" \
  --priority high \
  --category maintenance \
  --due "2026-03-01" \
  --assignee "John"
```

**Options:**
- `--name`: Task name (required)
- `--description`: Task description
- `--priority`: Task priority (high, medium, low)
- `--status`: Task status (pending, in-progress, completed)
- `--category`: Task category (planting, maintenance, harvesting, equipment, animals, buildings, other)
- `--due`: Due date (YYYY-MM-DD or YYYY-MM-DD HH:MM)
- `--assignee`: Person assigned to task

### List Tasks

```bash
# List all tasks
farm-task list

# Filter by status
farm-task list --status pending

# Filter by priority
farm-task list --priority high

# Filter by category
farm-task list --category planting

# Filter by due date (show overdue first)
farm-task list --sort-due

# Filter by assignee
farm-task list --assignee "John"
```

### Show Task Details

```bash
farm-task show 1
```

Shows task details including:
- Task information
- Status and priority
- Due date
- Notes and history
- Time since creation

### Update Task Status

```bash
# Mark as in-progress
farm-task update 1 --status in-progress

# Mark as complete
farm-task update 1 --status complete

# Add note to task
farm-task update 1 --note "Checked valves, all good"

# Change priority
farm-task update 1 --priority medium
```

### Add Recurring Task

```bash
# Daily task
farm-task recurring "Check chicken water" \
  --frequency daily \
  --priority medium \
  --category animals

# Weekly task
farm-task recurring "Inspect tractor oil" \
  --frequency weekly \
  --priority high \
  --category equipment

# Monthly task
farm-task recurring "Test fire extinguishers" \
  --frequency monthly \
  --priority medium \
  --category buildings

# Seasonal task (March 1st)
farm-task recurring "Winterize irrigation" \
  --frequency seasonal \
  --season "03-01" \
  --priority high \
  --category maintenance
```

### Complete Task

```bash
farm-task complete 1
```

Marks task as complete and logs completion timestamp.

### Delete Task

```bash
farm-task delete 1
```

Removes task from the system.

### Export Tasks

```bash
# Export all to markdown
farm-task export --file tasks.md

# Export filtered to markdown
farm-task export --file planting-tasks.md --category planting

# Export to JSON
farm-task export --file tasks.json --format json

# Export by date range
farm-task export --file march-tasks.md --after "2026-03-01" --before "2026-04-01"
```

---

## Security

✅ **Security-Verified**: This skill uses path validation to prevent unauthorized file access.

All file operations are restricted to safe directories:
- Workspace: `~/.openclaw/workspace/farm-task-manager/`
- Home directory: `~/` (user-controlled)

**Blocked paths:**
- System directories (`/etc`, `/usr`, `/var`, etc.)
- Sensitive dotfiles (`~/.ssh`, `~/.bashrc`, etc.)

No hardcoded secrets. No arbitrary code execution. Input validation on all operations.

---

## Data Storage

Tasks are stored in JSON format at:
- `~/.openclaw/workspace/farm-task-manager/tasks.json`

The directory is automatically created on first use.

---

## Task Categories

| Category | Description |
|----------|-------------|
| planting | Seed starting, transplanting, soil prep |
| maintenance | General farm maintenance, repairs |
| harvesting | Harvest activities, post-harvest work |
| equipment | Equipment maintenance, repairs, storage |
| animals | Animal care, feeding, health checks |
| buildings | Barn, shed, greenhouse maintenance |
| other | Any other farm tasks |

---

## Priority Levels

| Priority | Description |
|-----------|-------------|
| high | Urgent, do ASAP (safety-critical, time-sensitive) |
| medium | Important, do soon (routine tasks with flexibility) |
| low | Nice to have, do when possible (optimization, improvements) |

---

## Examples

### Daily Routine

```bash
# Morning check
farm-task list --sort-due --status pending

# Complete chicken check
farm-task complete 5
farm-task recurring generate 5  # Generate next day's recurring task
```

### Weekly Planning

```bash
# List high priority tasks
farm-task list --priority high

# Export for planning
farm-task export --file weekly-plan.md --after "today" --before "7 days"
```

### Seasonal Work

```bash
# Winter preparation
farm-task recurring "Winterize irrigation" \
  --frequency seasonal \
  --season "11-01" \
  --priority high \
  --category maintenance

# Spring planting
farm-task export --file spring-tasks.md --category planting --after "2026-03-01" --before "2026-06-01"
```

---

## Troubleshooting

### Q: How do I track multiple workers?

**A:** Use the `--assignee` option when adding tasks. Filter by assignee to see each person's tasks:
```bash
farm-task list --assignee "Jane"
```

### Q: Can I change task priority later?

**A:** Yes, use the update command:
```bash
farm-task update 1 --priority high
```

### Q: How do recurring tasks work?

**A:** Recurring tasks are templates. When you complete a recurring task, generate a new instance:
```bash
farm-task recurring generate 1
```
This creates a new task with the same details and updated due date.

### Q: Can I track project-based work?

**A:** Use categories to group related work:
```bash
farm-task add "Build new fence" --category buildings --assignee "John"
farm-task list --category buildings
```

### Q: How do I export for sharing?

**A:** Export to markdown or JSON:
```bash
# Markdown (human-readable)
farm-task export --file farm-plan.md

# JSON (for data interchange)
farm-task export --file farm-tasks.json --format json
```

---

## Version History

- **1.0.0** (2026-02-12): Initial release
  - Task management (add, list, show, update, delete, complete)
  - Task filtering by status, priority, category, due date, assignee
  - Recurring tasks (daily, weekly, monthly, seasonal)
  - Search across all tasks
  - Export to markdown and JSON

---

## Support

For bugs, feature requests, or questions:
- Author: @johstracke on ClawHub
- Check other IOU skills in the Farming Suite (coming soon!)

---

*Farm Task Manager - Organize your farm work, reduce stress, never forget important tasks again.*
