# Tasks Commands

## Contents

- Scope
- Project resolution
- Read/query commands
- Create commands
- Update/lifecycle commands
- Move, hierarchy, pin, column
- Parameter rules

## Scope

Use this file for `ticktick tasks ...` workflows.

## Project resolution

When `--project` is omitted:

- Existing-task mutation commands (`update`, `done`, `abandon`, `delete`, `pin`, `unpin`, `column`, `subtask`, `unparent`) resolve project from task ID.
- Create commands (`add`, `quick-add`) resolve in this order:
  1. `--project`
  2. `TICKTICK_CURRENT_PROJECT_ID`
  3. inbox project ID
- Query commands default to all projects unless `--project` is set.

Prefer explicit `--project` for deterministic writes.

## Read/query commands

```bash
ticktick tasks list [--project PROJECT_ID] [--due YYYY-MM-DD] [--json]
ticktick tasks get TASK_ID [--project PROJECT_ID] [--json]
ticktick tasks search QUERY [--project PROJECT_ID] [--json]
ticktick tasks by-tag TAG_NAME [--project PROJECT_ID] [--json]
ticktick tasks by-priority PRIORITY [--project PROJECT_ID] [--json]
ticktick tasks today [--project PROJECT_ID] [--json]
ticktick tasks overdue [--project PROJECT_ID] [--json]
ticktick tasks completed [--days N] [--limit N] [--project PROJECT_ID] [--json]
ticktick tasks abandoned [--days N] [--limit N] [--project PROJECT_ID] [--json]
ticktick tasks deleted [--limit N] [--project PROJECT_ID] [--json]
```

Key parameters:

- `TASK_ID`: task identifier.
- `QUERY`: text search query.
- `TAG_NAME`: tag name (not tag ID).
- `PRIORITY`: `none|low|medium|high|0|1|3|5`.
- `--due` on `list`: local-date filter in `YYYY-MM-DD`.
- `--days`: lookback days (default `7` for completed/abandoned).
- `--limit`: result cap (default `100` where supported).

## Create commands

```bash
ticktick tasks add TITLE \
  [--project PROJECT_ID] \
  [--content TEXT] \
  [--description TEXT] \
  [--kind TEXT|NOTE|CHECKLIST] \
  [--start YYYY-MM-DD|ISO_DATETIME] \
  [--due YYYY-MM-DD|ISO_DATETIME] \
  [--priority none|low|medium|high] \
  [--tags tag1,tag2] \
  [--recurrence RRULE] \
  [--time-zone IANA_TZ] \
  [--all-day|--timed] \
  [--parent PARENT_TASK_ID] \
  [--reminders TRIGGER_1,TRIGGER_2] \
  [--json]

ticktick tasks quick-add TEXT [--project PROJECT_ID] [--json]
```

Parameter notes:

- `TITLE`: required task title.
- `--content`: note/body text.
- `--description`: checklist description field.
- `--kind`: task kind (`TEXT`, `NOTE`, `CHECKLIST`; case-insensitive in CLI input).
- `--start`, `--due`: accept date-only or ISO datetime.
- `--tags`: comma-separated names.
- `--recurrence`: RRULE string.
- `--time-zone`: IANA timezone stored on task.
- `--all-day` / `--timed`: mutually exclusive.
- `--parent`: create task as subtask.
- `--reminders`: comma-separated trigger strings (example `TRIGGER:-PT30M`).

## Update/lifecycle commands

```bash
ticktick tasks update TASK_ID \
  [--project PROJECT_ID] \
  [--title TEXT] \
  [--content TEXT] \
  [--description TEXT] \
  [--kind TEXT|NOTE|CHECKLIST] \
  [--priority none|low|medium|high] \
  [--start YYYY-MM-DD|ISO_DATETIME|--clear-start] \
  [--due YYYY-MM-DD|ISO_DATETIME|--clear-due] \
  [--tags tag1,tag2|--clear-tags] \
  [--recurrence RRULE|--clear-recurrence] \
  [--time-zone IANA_TZ] \
  [--all-day|--timed] \
  [--json]

ticktick tasks done TASK_ID [--project PROJECT_ID] [--json]
ticktick tasks abandon TASK_ID [--project PROJECT_ID] [--json]
ticktick tasks delete TASK_ID [--project PROJECT_ID] [--json]
```

Update validation rules:

- At least one update field is required.
- Invalid combinations:
  - `--start` with `--clear-start`
  - `--due` with `--clear-due`
  - `--tags` with `--clear-tags`
  - `--recurrence` with `--clear-recurrence`

## Move, hierarchy, pin, column

```bash
ticktick tasks move TASK_ID --to-project PROJECT_ID [--from-project PROJECT_ID] [--json]
ticktick tasks subtask TASK_ID --parent PARENT_TASK_ID [--project PROJECT_ID] [--json]
ticktick tasks unparent TASK_ID [--project PROJECT_ID] [--json]
ticktick tasks pin TASK_ID [--project PROJECT_ID] [--json]
ticktick tasks unpin TASK_ID [--project PROJECT_ID] [--json]
ticktick tasks column TASK_ID [--project PROJECT_ID] (--column COLUMN_ID | --clear-column) [--json]
```

Parameter notes:

- `move`: `--to-project` required; `--from-project` optional (auto-resolved from task when omitted).
- `subtask`: `--parent` required.
- `column`: must set one of `--column` or `--clear-column`.

## Parameter rules

- Priority mapping: `none=0`, `low=1`, `medium=3`, `high=5`.
- `TZ` controls local-date interpretation for listing/filtering.
- Date-only values are interpreted as all-day task values.
- Use `--json` for deterministic parsing.

Use `ticktick tasks <action> --help` only when a command fails due parameter mismatch.
