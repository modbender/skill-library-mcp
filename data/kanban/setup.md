# Setup - Kanban

Read this when `~/kanban/` does not exist, is empty, or the current project has no registered board.

## Operating Attitude

- Keep the experience lightweight: answer immediate user needs while building structure in parallel.
- Favor continuity: every decision should make the next session easier for any agent.
- Be explicit about scope: project-local board or shared home board.

## Priority Order

### 1. Integration First

In the first natural exchanges, confirm when this system should activate:
- Always when task planning appears
- Only when user explicitly asks for Kanban
- Only for selected projects

Save this behavior in `~/kanban/memory.md`.

### 2. Route Each Project Once

For each project, resolve and store:
- Project id (stable slug)
- Workspace root (if available)
- Preferred board mode: `workspace-local` or `home-shared`
- Primary board path
- Aliases users might use in chat

Write this registry entry in `~/kanban/index.md`.

### 3. Initialize the Board Skeleton

Create board files using `board-template.md`:
- `board.md`
- `rules.md`
- `log.md`

If the user already has a preferred structure, preserve it and only add missing core fields.

### 4. Start with Real Work

Capture the first actionable tasks immediately:
- Add backlog cards
- Assign initial priority and owner
- Move at least one card to ready or in progress if clear

## What You Save Internally

- `memory.md`: integration preference, defaults, and operating notes
- `index.md`: per-project routing table and last-used timestamps
- `projects/{project-id}/` or `{workspace}/.kanban/`: board state and write log

## Guardrails

- Do not claim setup completion if files were not created.
- Do not overwrite existing boards without explicit user approval.
- If routing is unclear, ask one direct question, then continue.
