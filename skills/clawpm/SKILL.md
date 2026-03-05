---
name: clawpm
description: Multi-project task and research management (JSON-first CLI)
user-invocable: true
metadata: { "openclaw": { "homepage": "https://github.com/malphas-gh/clawpm", "requires": { "bins": ["clawpm"] }, "emoji": "📋", "install": [{ "id": "uv", "kind": "uv", "package": "git+https://github.com/malphas-gh/clawpm", "bins": ["clawpm"], "label": "Install clawpm (uv)" }] } }
---

# ClawPM Skill

Multi-project task management. All commands emit JSON by default; use `-f text` for human-readable output.

## First-Time Setup

```bash
clawpm setup               # Creates ~/clawpm/ with portfolio.toml, projects/, work_log.jsonl
clawpm setup --check       # Verify installation
```

## Creating Projects

Projects are directories with a `.project/` folder. They don't need to be git repos.

### Initialize in any directory

```bash
cd /path/to/my-project
clawpm project init                    # Auto-detects ID/name from directory
clawpm project init --id myproj        # Custom ID
```

### From a git clone (auto-init)

Git repos under `~/clawpm/projects/` auto-initialize on first use:

```bash
git clone git@github.com:user/repo.git ~/clawpm/projects/repo
cd ~/clawpm/projects/repo
clawpm add "First task"    # Auto-initializes .project/, then adds task
```

### Discover untracked repos

```bash
clawpm projects list --all   # Shows tracked + untracked git repos
```

## Quick Start

```bash
# From a project directory (auto-detected):
clawpm status              # See project status
clawpm next                # Get next task
clawpm start 42            # Start task (short ID works)
clawpm done 42             # Mark done

# Or set a project context:
clawpm use my-project
clawpm status              # Now uses my-project
```

## Top-Level Commands (Shortcuts)

| Command | Equivalent | Description |
|---------|------------|-------------|
| `clawpm add "Title"` | `clawpm tasks add -t "Title"` | Quick add a task |
| `clawpm add "Title" -b "desc"` | `clawpm tasks add -t "Title" -b "desc"` | Add with body |
| `clawpm add "Title" --parent 25` | - | Add subtask |
| `clawpm done 42` | `clawpm tasks state 42 done` | Mark task done |
| `clawpm start 42` | `clawpm tasks state 42 progress` | Start working |
| `clawpm block 42` | `clawpm tasks state 42 blocked` | Mark blocked |
| `clawpm next` | `clawpm projects next` | Get next task |
| `clawpm status` | - | Project overview |
| `clawpm context` | - | Full agent context |
| `clawpm use <id>` | - | Set project context |

## Project Auto-Detection

ClawPM automatically detects your project from (in priority order):
1. **Subcommand flag**: `clawpm tasks list --project clawpm`
2. **Global flag**: `clawpm --project clawpm status`
3. **Current directory**: Walks up looking for `.project/settings.toml`
4. **Auto-init**: If in untracked git repo under project_roots, auto-initializes
5. **Context**: Previously set with `clawpm use <project>`

## Short Task IDs

You can use just the numeric part of a task ID:
- `42` → `CLAWP-042` (prefix derived from project ID)
- `CLAWP-042` → `CLAWP-042` (full ID works too)

## Subtasks

```bash
clawpm add "Subtask" --parent 25   # Creates subtask (auto-splits parent if needed)
clawpm tasks split 25              # Manually convert task to parent directory

clawpm done 25             # Fails if subtasks not done
clawpm done 25 --force     # Override and complete anyway
```

Subtasks move with parent on state change (done/blocked moves entire directory).

## Agent Context (Resuming Work)

Get everything needed to resume work in one command:

```bash
clawpm context             # Full context for current project
clawpm context -p myproj   # Specific project
```

Returns JSON with: project info + spec, in-progress/next task, blockers, recent work log, git status, open issues.

## Workflow Example

```bash
clawpm context             # Get full context
clawpm start 42            # Mark in progress (auto-logs)
# ... do work ...
git add . && git commit -m "feat: ..."
clawpm done 42 --note "Completed"       # Auto-logs with files_changed
clawpm log commit                        # Also log the git commits themselves
```

Hit a blocker:
```bash
clawpm block 42 --note "Need API credentials"
```

## Full Command Reference

### Projects
```bash
clawpm projects list [--all]            # List projects (--all includes untracked repos)
clawpm projects next                    # Next task across all projects
clawpm project context [project]        # Full project context
clawpm project init                     # Initialize project in current dir
```

### Tasks
```bash
clawpm tasks                            # List tasks (default: open+progress+blocked)
clawpm tasks list [-s open|done|blocked|progress|all] [--flat]
clawpm tasks show <id>                  # Task details
clawpm tasks add -t "Title" [--priority 3] [--complexity m] [--parent <id>] [-b "body"]
clawpm tasks edit <id> [--title "..."] [--priority N] [--complexity s|m|l|xl] [--body "..."]
clawpm tasks state <id> open|progress|done|blocked [--note "..."] [--force]
clawpm tasks split <id>                 # Convert to parent directory for subtasks
```

### Work Log
```bash
clawpm log add --task <id> --action progress --summary "What I did"
clawpm log tail [--limit 10]            # Recent entries (auto-filtered to current project)
clawpm log tail --all                   # Recent entries across all projects
clawpm log tail --follow                # Live tail (like tail -f)
clawpm log last                         # Most recent entry (auto-filtered to current project)
clawpm log last --all                   # Most recent entry across all projects
clawpm log commit [-n 10]               # Log recent git commits to work log
clawpm log commit --dry-run             # Preview without logging
clawpm log commit --task <id>           # Associate commits with a task
```

Note: State changes (start/done/block) auto-log to work_log with git files_changed.

### Research
```bash
clawpm research list
clawpm research add --type investigation --title "Question"
clawpm research link --id <research_id> --session-key <key>
```

### Issues
```bash
clawpm issues add --type bug --severity high --actual "What happened"
clawpm issues list [--open]             # Open issues only
```

### Admin
```bash
clawpm setup               # Create portfolio (first-time)
clawpm setup --check       # Verify installation
clawpm status              # Project overview
clawpm context             # Full agent context
clawpm doctor              # Health check
clawpm use [project]       # Set/show project context
clawpm use --clear         # Clear context
```

## Work Log Actions

- `start` - Started working (auto-logged on `clawpm start`)
- `progress` - Made progress
- `done` - Completed (auto-logged on `clawpm done`)
- `blocked` - Hit a blocker (auto-logged on `clawpm block`)
- `commit` - Git commit (logged via `clawpm log commit`)
- `pause` - Switching tasks
- `research` - Research note
- `note` - General observation

## Task States & File Locations

| State | File Pattern | Meaning |
|-------|--------------|---------|
| open | `tasks/CLAWP-042.md` | Ready to work |
| progress | `tasks/CLAWP-042.progress.md` | In progress |
| done | `tasks/done/CLAWP-042.md` | Completed |
| blocked | `tasks/blocked/CLAWP-042.md` | Waiting |

## Tips

- **Flag order**: `clawpm [global flags] <command> [command flags]` — e.g. `clawpm -f text tasks list -s open`
- **JSON output**: All commands emit JSON by default; use `-f text` for human-readable
- **One command per call**: Don't chain clawpm commands with `&&` — run each separately
- **Portfolio root**: Default `~/clawpm`
- **Work log**: Append-only at `<portfolio>/work_log.jsonl`

## Troubleshooting

```bash
clawpm doctor              # Check for issues
clawpm setup --check       # Verify installation
clawpm log tail            # See recent activity
```
