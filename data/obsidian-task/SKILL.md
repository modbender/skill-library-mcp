---
name: obsidian-task
description: Manage Obsidian tasks via obsidian-cli. List, toggle, create, and update tasks from the terminal.
compatibility: darwin,linux
metadata:
  version: 1.0.1
  requires:
    bins:
      - obsidian
---

# Obsidian Task

Manage tasks in your Obsidian vault using the official Obsidian CLI.

## Dependencies

| Dependency | Required | Description |
|------------|----------|-------------|
| `obsidian` | Yes | Obsidian CLI (registered via Obsidian settings) |
| `Obsidian 1.12+` | Yes | Catalyst license required for CLI access |

### Check Dependencies

```bash
# Check obsidian CLI availability
obsidian version
```

## Prerequisites

- **Obsidian 1.12+** and **Catalyst license** required
- **Settings → General → Command line interface** → Enable
- Follow prompt to register the `obsidian` command
- Restart terminal or `source ~/.zprofile` (macOS)
- **Note:** Obsidian must be running for CLI to work

Test setup: `obsidian version`

## Usage

```bash
/obsidian-task [command] [options]
```

## Commands

| Command | Description |
|---------|-------------|
| (none) | Show help and available commands |

## Options

| Option | Description |
|--------|-------------|
| `--help` | Show help message |

## Examples

```bash
# List tasks
/obsidian-task tasks file=projects/myproject/todo verbose

# Toggle task on line 2
/obsidian-task task file=projects/myproject/todo line=2 toggle

# Mark task as done
/obsidian-task task file=projects/myproject/todo line=2 done

# Mark task as todo (undo completion)
/obsidian-task task file=projects/myproject/todo line=2 todo

# Create new task
/obsidian-task append file=projects/myproject/todo content="- [ ] task name"
```

## Raw CLI Commands

```bash
# List tasks (shows line numbers and status)
obsidian tasks file=<project_slug>/todo verbose

# Sample output:
# projects/<project_slug>/TODO.md
# 2	- [ ] 未完成的任务
# 3	- [x] 已完成的任务

# Update tasks
obsidian task file=<project_slug>/todo line=2 toggle
obsidian task file=<project_slug>/todo line=2 done
obsidian task file=<project_slug>/todo line=2 todo

# Create new task (via append)
obsidian append file=<project_slug>/todo content="- [ ] task name"
```
```