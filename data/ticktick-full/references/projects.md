# Projects Commands

## Contents

- Scope
- Read commands
- Create command
- Update command
- Delete command

## Scope

Use this file for `ticktick projects ...` operations.

## Read commands

```bash
ticktick projects list [--json]
ticktick projects get PROJECT_ID [--json]
ticktick projects data PROJECT_ID [--json]
```

Parameter notes:

- `PROJECT_ID`: project identifier.
- `data`: returns project details plus project tasks and columns.

## Create command

```bash
ticktick projects create NAME \
  [--color HEX] \
  [--kind TASK|NOTE] \
  [--view list|kanban|timeline] \
  [--folder FOLDER_ID] \
  [--json]
```

Parameter notes:

- `NAME`: required project name.
- `--color`: hex color string (example `#F18181`).
- `--kind`: defaults to `TASK`.
- `--view`: defaults to `list`.
- `--folder`: folder/project-group ID.

## Update command

```bash
ticktick projects update PROJECT_ID \
  [--name NEW_NAME] \
  [--color HEX] \
  [--folder FOLDER_ID | --remove-folder] \
  [--json]
```

Validation rules:

- At least one update field is required.
- Do not combine `--folder` with `--remove-folder`.

## Delete command

```bash
ticktick projects delete PROJECT_ID [--json]
```

Use confirmation before running delete operations.

Use `ticktick projects <action> --help` only as recovery for parameter errors.
