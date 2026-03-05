---
name: Kanban
slug: kanban
version: 1.0.0
homepage: https://clawic.com/skills/kanban
description: Build multi-project Kanban systems with deterministic board discovery, consistent task processing, and persistent routing memory across sessions.
changelog: Initial release with project routing, board templates, and deterministic Kanban processing rules.
metadata: {"clawdbot":{"emoji":"📋","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## Setup

If `~/kanban/` does not exist or is empty, read `setup.md` silently and initialize only after user confirmation.

## When to Use

Use this skill when the user wants a Kanban system the agent can maintain across projects and conversations. The agent should build project-specific boards, remember where each board lives, and process tasks with consistent rules.

## Architecture

Memory lives in `~/kanban/`. See `memory-template.md` for base files, `board-template.md` for board structure, and `discovery-protocol.md` for project routing.

```
~/kanban/
├── memory.md                  # Global status, integration, defaults
├── index.md                   # Project registry and board location map
├── templates/
│   └── board-template.md      # Canonical board format copy
└── projects/
    └── {project-id}/
        ├── board.md           # Active board for this project
        ├── rules.md           # Project-specific lane and policy definitions
        ├── log.md             # Board write log
        └── archive/
```

Optional project-local mode:

```
{workspace}/.kanban/
├── board.md
├── rules.md
└── log.md
```

## Quick Reference

Use the smallest relevant file for the current task.

| Topic | File |
|-------|------|
| Setup behavior | `setup.md` |
| Memory and registry template | `memory-template.md` |
| Board schema and examples | `board-template.md` |
| Where to find each project board | `discovery-protocol.md` |
| How to process and update cards | `processing-rules.md` |

## Core Rules

### 1. Resolve Project Context Before Reading or Writing
- Run the discovery sequence in `discovery-protocol.md` at the start of each conversation.
- If project scope is ambiguous, ask once before writing.

### 2. Persist Routing So Any Agent Can Continue
- Keep the Kanban index file updated with workspace path, project aliases, and primary board path.
- After each successful write, update `last_used` for the project entry.

### 3. Allow Custom Board Shapes with a Stable Core Schema
- Users can rename lanes or add custom columns per project in the project rules file.
- Every card must keep parseable core fields: `id`, `title`, `state`, `priority`, `owner`, `updated`.

### 4. Process Cards Deterministically
- Follow the exact decision order in `processing-rules.md` for prioritization and movement.
- Never skip blockers, dependencies, or explicit WIP limits.

### 5. Keep Writes Atomic and Logged
- Update the board file and append one line to the project log in the same operation cycle.
- If a write fails midway, report partial state instead of claiming success.

### 6. Keep Project Boards Isolated
- Never move or edit cards across different project boards without explicit user intent.
- For cross-project requests, produce a plan first, then apply updates per board.

### 7. Preserve Continuity Across Conversations
- On first message of a new conversation, resolve board location and load current state before proposing work.
- If no board exists, initialize from `board-template.md`, register it in the index file, and continue.

## Common Traps

- Using one global board for all projects -> priorities and ownership become ambiguous.
- Renaming lanes without updating state mapping in the project rules file -> cards become unprocessable.
- Writing board updates without refreshing the index file -> next agent session cannot locate the board.
- Keeping tasks without IDs -> duplicate card updates and broken references.
- Marking work as done without log entry -> no audit trail for later sessions.

## Security & Privacy

**Data that stays local:**
- Board files and project registry in `~/kanban/` or `{workspace}/.kanban/`.

**Data that leaves your machine:**
- None by default.

**This skill does NOT:**
- Make undeclared network requests.
- Modify files outside the selected Kanban scope.
- Invent board history when logs are missing.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `workflow` - operational workflow design and execution loops
- `projects` - project organization and cross-project governance
- `delegate` - owner assignment and task handoff protocols
- `daily-planner` - daily planning and task sequencing

## Feedback

- If useful: `clawhub star kanban`
- Stay updated: `clawhub sync`
