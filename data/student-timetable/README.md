# student-timetable

A student timetable manager supporting:

- A student managing their own schedule (self profile)
- A parent/guardian managing one or more children (child profiles)

Data contract reference: `projects/StudentTimetable/docs/contracts/prd.md`.

## Data layout

All schedule data lives under:

- `schedules/profiles/registry.json`
- `schedules/profiles/<profile_id>/weekly.json`
- `schedules/profiles/<profile_id>/special_events.json`
- `schedules/profiles/<profile_id>/term_calendar.json`

## CLI

Interactive init:

- `node skills/student-timetable/cli.js init`

Query:

- `node skills/student-timetable/cli.js today --profile <id|name|alias>`
- `node skills/student-timetable/cli.js tomorrow --profile <id|name|alias>`
- `node skills/student-timetable/cli.js this_week --profile <id|name|alias>`
- `node skills/student-timetable/cli.js next_week --profile <id|name|alias>`

If you omit `--profile`, the CLI defaults to the self profile ONLY when a self profile exists in `schedules/profiles/registry.json`.

## Profile resolution rules

Matching order:

1. Exact match on `profile_id`
2. Exact match on display name
3. Exact match on an alias

Normalization:

- Case-insensitive
- Trim whitespace
- Collapse internal whitespace runs

Ambiguity handling:

- If multiple profiles match, the tool always asks for clarification.
- The tool never picks a profile based on ordering, recency, or heuristics.

Generic aliases (always require clarification):

- `me`, `myself`, `self`
- `kid`, `child`, `son`, `daughter`, `boy`, `girl`
- `older`, `younger`, `big`, `small`
- `primary`, `secondary`

Reserved words:

- `all`, `everyone`

## Migration

Non-destructive migration from the legacy `kid-schedule` layout:

- Dry run: `node skills/student-timetable/cli.js migrate kid-schedule --dry-run`
- Apply: `node skills/student-timetable/cli.js migrate kid-schedule`

Legacy "zian" single-JSON (heuristic):

- Dry run: `node skills/student-timetable/cli.js migrate legacy-zian --dry-run`
- Apply: `node skills/student-timetable/cli.js migrate legacy-zian`

Migration safety:

- Never deletes old data.
- Does not overwrite destination files if they already exist.
- Creates backups under `schedules/backups/` for any destination files it would overwrite (if present).

## Notes

- Time zone defaults to `Asia/Singapore` in templates.
- Biweekly support uses Monday as week start (per contract).
