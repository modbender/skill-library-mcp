---
name: longrunning-agent
description: "Enables AI agents to work on long-running projects across multiple sessions. Use when starting complex projects, resuming work on existing projects, managing task lists with priorities and dependencies, or tracking progress incrementally."
---

# OpenClaw Long-Running Agent Skill

This skill enables AI agents to work on long-running projects across multiple sessions.

## Purpose

The longrunning-agent skill provides a structured workflow for:
- Tracking progress across sessions
- Managing task lists with priorities and dependencies
- Making incremental, atomic progress on complex projects
- Ensuring continuity when resuming work

## Installation

1. Copy this skill directory to your OpenClaw skills folder
2. Ensure Claude Code CLI is installed and configured
3. Create a project directory with the workflow files

## Usage

### Initialize a New Project

```bash
# Create project directory
mkdir my-project && cd my-project

# Initialize workflow files
claude -p "Initialize this project using the longrunning-agent workflow"
```

### Workflow Files

The skill expects these files in the project directory:

- `CLAUDE.md` - Project instructions and workflow guide
- `task.json` - Task list with priorities and dependencies
- `progress.txt` - Log of work completed
- `init.sh` - Environment setup script (optional)

### Task Format

```json
{
  "tasks": [
    {
      "id": "task-1",
      "description": "Set up project structure",
      "priority": 1,
      "dependencies": [],
      "passes": false
    },
    {
      "id": "task-2",
      "description": "Implement core features",
      "priority": 2,
      "dependencies": ["task-1"],
      "passes": false
    }
  ]
}
```

### Progress Format

```
[2024-01-15 10:30:00] Started session
[2024-01-15 10:35:00] Completed task: Set up project structure
[2024-01-15 10:40:00] Milestone: Core features implemented
```

## Workflow Steps

1. **Read Progress** - Check `progress.txt` for recent work
2. **Select Task** - Find next `passes: false` task with met dependencies
3. **Initialize** - Run `init.sh` if needed
4. **Implement** - Work on one task incrementally
5. **Test** - Run lint, build, and tests
6. **Document** - Update `progress.txt`
7. **Mark Complete** - Set `passes: true` in `task.json`
8. **Commit** - Make atomic git commit

## Best Practices

- Work on ONE task per session
- Make commits after each task completion
- Keep progress.txt concise but informative
- Use dependencies to manage task order
- Test thoroughly before marking passes: true

## Integration with Web UI

This skill integrates with the Agent Workflow Web App:
- Tasks sync with the web database
- Progress entries are captured
- Session output is logged
- Git commits are tracked

## Templates

Templates for workflow files are in the `templates/` directory:
- `CLAUDE.md.tpl` - Project template
- `task.json.tpl` - Task list template
