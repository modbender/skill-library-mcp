# Tags Commands

## Contents

- Scope
- Commands
- Parameter and safety notes

## Scope

Use this file for `ticktick tags ...` operations.

## Commands

```bash
ticktick tags list [--json]
ticktick tags create NAME [--color HEX] [--parent PARENT_TAG] [--json]
ticktick tags update NAME [--color HEX] [--parent PARENT_TAG | --clear-parent] [--json]
ticktick tags rename OLD_NAME NEW_NAME [--json]
ticktick tags merge SOURCE TARGET [--json]
ticktick tags delete NAME [--json]
```

## Parameter and safety notes

- `NAME`, `OLD_NAME`, `NEW_NAME`, `SOURCE`, `TARGET` are tag names.
- `--color` expects hex string (example `#57A8FF`).
- `update` requires at least one of:
  - `--color`
  - `--parent`
  - `--clear-parent`
- Do not combine `--parent` and `--clear-parent`.
- `merge` and `delete` are destructive; confirm intent first.

Use `ticktick tags <action> --help` only as recovery for parameter errors.
