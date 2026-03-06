# Command Paths - Apple Calendar

Use this order for deterministic command selection.

## Priority Order

1. `apple-calendar-cli` (preferred, structured CRUD workflow)
2. `icalBuddy` (strong read and search fallback)
3. `shortcuts` (scripted local automation fallback)
4. `osascript` (last-mile fallback)

## Probe Pattern

Run lightweight checks before first operation:

```bash
command -v apple-calendar-cli
command -v icalBuddy
command -v shortcuts
command -v osascript
```

## Selection Rules

- Use the first available path in priority order.
- If only read-only tooling is available, allow reads and block writes with a clear explanation.
- If path changes mid-session, state the new path and re-run read verification.

## Unified Calendar Scope

- All paths should target calendars visible in Calendar.app, including synced Google, Exchange, iCloud, and CalDAV calendars.
- Never claim provider-specific write support without verifying that the target calendar is present in local Calendar.app.

## Write Policy by Path

- `apple-calendar-cli`: create, update, delete after confirmation.
- `icalBuddy`: read and search only unless wrapped by a verified write helper.
- `shortcuts` and `osascript`: allow writes only after pre-read and explicit confirmation.
