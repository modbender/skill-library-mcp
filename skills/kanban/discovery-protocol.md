# Discovery Protocol - Kanban

Run this sequence at the start of each conversation before touching tasks.

## Step 1: Detect Context

Collect available signals:
- current workspace root
- explicit project name in user message
- aliases in user message

## Step 2: Resolve Project Entry

Search `~/kanban/index.md` in this order:
1. exact workspace root match
2. alias match
3. explicit project id match
4. most recent project (`last_used`) with one confirmation question

If no entry matches, initialize a new project entry.

## Step 3: Resolve Board Path

Use `board_mode` from the resolved entry:
- `workspace-local` -> `{workspace}/.kanban/board.md`
- `home-shared` -> `~/kanban/projects/{project-id}/board.md`

If board file is missing, create it from `board-template.md`.

## Step 4: Load and Validate

Validate the board has:
- `Meta`
- `Lanes`
- `Cards` table

If malformed, repair non-destructively:
- keep existing content
- restore missing required sections
- write repair note to `log.md`

## Step 5: Confirm Scope for Multi-Project Requests

If the user request spans multiple projects:
- list candidate projects
- ask which boards should be updated
- apply changes one project at a time

## Step 6: Update Registry

After every successful write:
- update `last_used` in index
- update `last` in memory
- append action to project `log.md`
