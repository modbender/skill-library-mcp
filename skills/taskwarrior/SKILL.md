---
name: taskwarrior
description: >
  Workspace-local task management powered by Taskwarrior. Add, organize,
  and track tasks by project, tags, due dates, and priority with all data
  stored inside the active workspace.

metadata: |
  {
    "openclaw": {
      "requires": {
        "bins": ["task"]
      },
      "install": [
        {
          "kind": "apt",
          "bins": ["task"],
          "packages": ["taskwarrior"]
        },
        {
          "kind": "brew",
          "bins": ["task"],
          "packages": ["task"]
        }
      ]
    }
  }
---
# Taskwarrior (Workspace-Local Tasks) — AgentSkill

## Skill name
taskwarrior

## Purpose
Manage tasks using Taskwarrior as the backend with data stored inside the current workspace. This skill provides a safe, workspace-scoped wrapper for common Taskwarrior operations (add/list/modify/done/projects/tags/due/priority/annotations).

## Runtime requirements (ClawHub)
This skill **requires Taskwarrior to already be available** in the runtime environment (e.g., included in the base image).
- Validation: run `task --version`
- If missing: report the dependency and instruct the environment owner to install system package **taskwarrior** (some distros package it as **task**).

This skill **does not perform system-level installs** (no `apt`, `brew`, `dnf`, etc.).

## Workspace root resolution (portable)
The skill resolves the workspace root at runtime:
1) If set, use the first available of:
   - OPENCLAW_WORKSPACE
   - WORKSPACE
   - PROJECT_DIR
   - REPO_ROOT
2) Otherwise, fallback to the current working directory.

All Taskwarrior data is stored under:
`<workspace>/.openclaw/taskwarrior/`

## Workspace-local Taskwarrior home
- taskrc: `<workspace>/.openclaw/taskwarrior/taskrc`
- data dir: `<workspace>/.openclaw/taskwarrior/.task/`

Every Taskwarrior command MUST run with:
- `TASKRC=<workspace>/.openclaw/taskwarrior/taskrc`
- (optional) `TASKDATA=<workspace>/.openclaw/taskwarrior/.task`

Never write to global `~/.task` or `~/.taskrc` unless the user explicitly asks to use global storage.

## Core workflow
1) **Check dependency**
   - Run: `task --version`
   - If missing: stop and return dependency instructions (see references/clawhub_notes.md).

2) **Initialize workspace storage**
   - Ensure directories exist:
     - `<workspace>/.openclaw/taskwarrior/`
     - `<workspace>/.openclaw/taskwarrior/.task/`
   - Ensure `<workspace>/.openclaw/taskwarrior/taskrc` contains at least:
     - `data.location=<workspace>/.openclaw/taskwarrior/.task`
     - `confirmation=off`
     - `verbose=off`

3) **Execute requested operations**
   - Prefer stable/common commands (see references/taskwarrior_cheatsheet.md).

4) **Verify results**
   - After any mutation, show a focused `task <id> info` or filtered `task <filter> list`.

## Supported operations (useful subset)
- Add tasks: `task add ...`
- List tasks: `task list`, `task <filter> list`
- Modify tasks: `task <id> modify ...`
- Complete tasks: `task <id> done`
- Start/stop: `task <id> start|stop` (if desired)
- Projects/tags: `task projects`, `task tags`, `project:<name>`, `+tag`, `-tag`
- Due/priorities: `due:<date>`, `priority:H|M|L`
- Notes: `task <id> annotate "..."`

## Safety
Follow `references/safe_command_policy.md`.
Highlights:
- No delete/purge unless explicitly requested.
- Avoid broad bulk changes without previewing the matching set.
- No global config writes by default.

## References
- references/workspace_data_layout.md
- references/taskwarrior_cheatsheet.md
- references/safe_command_policy.md
- references/examples.md
- references/clawhub_notes.md
