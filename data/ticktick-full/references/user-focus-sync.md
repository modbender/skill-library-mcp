# User, Focus, and Sync Commands

## Contents

- Scope
- User commands
- Focus commands
- Sync command
- Parameter notes

## Scope

Use this file for read-only account/profile/analytics/sync operations.

## User commands

```bash
ticktick user profile [--json]
ticktick user status [--json]
ticktick user statistics [--json]
ticktick user preferences [--json]
```

## Focus commands

```bash
ticktick focus heatmap [--from YYYY-MM-DD] [--to YYYY-MM-DD] [--days N] [--json]
ticktick focus by-tag [--from YYYY-MM-DD] [--to YYYY-MM-DD] [--days N] [--json]
```

## Sync command

```bash
ticktick sync [--json]
```

## Parameter notes

- `--from`, `--to`: ISO date (`YYYY-MM-DD`).
- `--days`: lookback when explicit range is not supplied; default is `30`.
- `sync --json`: emits raw full-account sync payload for diagnostics/export-style inspection.

Use `ticktick <group> <action> --help` only as recovery for parameter errors.
