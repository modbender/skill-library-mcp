# Columns Commands

## Contents

- Scope
- Commands
- Parameter rules

## Scope

Use this file for `ticktick columns ...` operations.

## Commands

```bash
ticktick columns list --project PROJECT_ID [--json]
ticktick columns create --project PROJECT_ID NAME [--sort N] [--json]
ticktick columns update COLUMN_ID --project PROJECT_ID [--name NAME] [--sort N] [--json]
ticktick columns delete COLUMN_ID --project PROJECT_ID [--json]
```

## Parameter rules

- `--project PROJECT_ID` is required for all column commands.
- `COLUMN_ID` is required for `update` and `delete`.
- `--sort` is integer sort order.
- `update` requires at least one update field (`--name` or `--sort`).

Use confirmation before delete.

Use `ticktick columns <action> --help` only as recovery for parameter errors.
