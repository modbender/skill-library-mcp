---
name: webuntis
description: Read-only access to Untis/WebUntis student timetables. Use when you need to fetch or summarize a student's current schedule (today/this week/date range), upcoming lessons, rooms, teachers, or substitutions from a WebUntis instance.
---

# WebUntis (Untis) timetable

Use the bundled script to log in and fetch the timetable via JSON-RPC.

## Security / credentials

- **Do not** ask the user to paste passwords into chat.
- Prefer a **dedicated read-only student account** if the school allows it.
- Credentials must be provided via environment variables (or injected securely by the operator).

Single profile:
  - `WEBUNTIS_BASE_URL` (e.g. `https://xyz.webuntis.com`)
  - `WEBUNTIS_SCHOOL` (school name / key used by WebUntis)
  - `WEBUNTIS_USER`
  - `WEBUNTIS_PASS`
  - Optional: `WEBUNTIS_ELEMENT_TYPE` (default `5` = student)
  - Optional: `WEBUNTIS_ELEMENT_ID` (if auto-detect fails)

Multiple profiles (parallel):
  - Set `WEBUNTIS_PROFILE=<name>` or pass `--profile <name>`
  - Provide env vars prefixed by the profile name, e.g. for profile `cdg`:
    - `WEBUNTIS_CDG_BASE_URL`
    - `WEBUNTIS_CDG_SCHOOL`
    - `WEBUNTIS_CDG_USER`
    - `WEBUNTIS_CDG_PASS`
    - optional: `WEBUNTIS_CDG_ELEMENT_TYPE`, `WEBUNTIS_CDG_ELEMENT_ID`

## Quick commands (exec)

Today:

```bash
cd skills/webuntis/scripts
./webuntis.py today

# or pick a profile
./webuntis.py --profile cdg today
```

Range:

```bash
cd skills/webuntis/scripts
./webuntis.py range 2026-02-10 2026-02-14
```

## Troubleshooting

If you get "Could not determine element-id":

1) Run once and capture the error.
2) Add `WEBUNTIS_ELEMENT_ID=<number>` and retry.

If auth fails:

- Verify `WEBUNTIS_BASE_URL` is correct for your school.
- Verify `WEBUNTIS_SCHOOL` matches the school key used by WebUntis.

## Output

The script prints one line per lesson/event:
`YYYY-MM-DD HH:MM-HH:MM · <subject> · Raum <room> · bei <teacher>`
