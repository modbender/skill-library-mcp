# Security and Privacy Rules

These rules are mandatory for both script mode and compatibility mode.

## Scope Control

1. Operate only under `working_directory`.
2. Do not read, move, or write files outside `working_directory`.
3. Do not follow symlinks when scanning report files.

## Data Minimization

1. Read only report files matching:
- `YYYY-MM-DD-<TICKER>-analysis.md`
- `YYYY-MM-DD-<TICKER>-analysis-vN.md`
2. Parse only required metadata fields.
3. Cap historical reads:
- script mode default: 5 files
- compatibility mode: 3 files

## Script Safety

1. Scripts are local-file utilities only; no network calls.
2. Migration is explicit and non-destructive:
- move only user-confirmed files
- skip when target already exists
3. If a safety check fails, return `blocked` with reason.
