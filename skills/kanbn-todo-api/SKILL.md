---
name: kanbn-todo-api
description: Manage personal TODOs in Kan.bn through API-driven operations. Use when you need single-user task management workflows on Kan.bn, including TODO CRUD, moving items between status lists, checklist completion, search, and personal profile updates; exclude multi-user collaboration, invites, integrations/imports, and attachments.
---

# Kan.bn TODO API

Use this skill to run Kan.bn TODO operations via `scripts/kanbn_todo.py`.

## Configure

Set auth before running commands:

- `KANBN_TOKEN` for bearer auth, or
- `KANBN_API_KEY` for API-key auth.

Optional:

- `KANBN_BASE_URL` (defaults to `https://kan.bn/api/v1`)

## Execute Core TODO Workflows

Use `python3 scripts/kanbn_todo.py <command> ...`.

### 1) Discover workspace and board

```bash
python3 scripts/kanbn_todo.py me
python3 scripts/kanbn_todo.py workspaces
python3 scripts/kanbn_todo.py boards --workspace-id <workspacePublicId>
```

### 2) Create TODO and read it back

```bash
python3 scripts/kanbn_todo.py todo-create \
  --list-id <todoListPublicId> \
  --title "Pay electricity bill" \
  --description "Before Friday" \
  --due-date "2026-03-06T09:00:00.000Z"

python3 scripts/kanbn_todo.py todo-get --card-id <cardPublicId>
```

### 3) Update TODO or change status

- Edit fields:

```bash
python3 scripts/kanbn_todo.py todo-update \
  --card-id <cardPublicId> \
  --title "Pay electricity + water bill" \
  --description "Do both tonight"
```

- Change status by moving lists (e.g., TODO -> DOING -> DONE):

```bash
python3 scripts/kanbn_todo.py todo-move \
  --card-id <cardPublicId> \
  --to-list-id <doingListPublicId>
```

### 4) Delete TODO

```bash
python3 scripts/kanbn_todo.py todo-delete --card-id <cardPublicId>
```

## Use Personal-Only Enhancements

- Search tasks in workspace:

```bash
python3 scripts/kanbn_todo.py search --workspace-id <workspacePublicId> --query "bill"
```

- Add personal notes/comments:

```bash
python3 scripts/kanbn_todo.py comment-add --card-id <cardPublicId> --comment "Waiting for invoice"
```

- Track subtasks with checklist:

```bash
python3 scripts/kanbn_todo.py checklist-add --card-id <cardPublicId> --name "Prep"
python3 scripts/kanbn_todo.py checkitem-add --checklist-id <checklistPublicId> --title "Download invoice"
python3 scripts/kanbn_todo.py checkitem-update --item-id <checklistItemPublicId> --completed true
```

## Respect Scope

Use only single-user TODO endpoints in this skill.

Do not run collaboration/invite/import/integration/attachment flows here.

If endpoint details are needed, read `references/api-scope.md`.
