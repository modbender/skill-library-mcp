---
name: apple-calendar-pro
description: iCloud Calendar skill via CalDAV (RFC 4791) — works on macOS/Linux, and Windows with env/keyring auth. Supports event CRUD, multi-calendar queries, managed attachments (RFC 8607), and free/busy lookups.
homepage: https://github.com/xushen-ma/apple-calendar-pro
metadata: {"openclaw":{"requires":{"bins":["python3"],"env":["APPLECAL_PASSWORD"]},"primaryEnv":"APPLECAL_PASSWORD"}}
---

# apple-calendar-pro

Advanced Apple Calendar integration using CalDAV (RFC 4791) and Managed Attachments (RFC 8607).

## Primary CLI
`scripts/applecal.py`

## Capabilities
- **Event CRUD**: List, Create, Update, Delete.
- **Multi-Calendar Support**: Query multiple calendars in a single command.
- **True Attachments**: RFC 8607 compatible (works on iPhone/iPad).
- **Free/Busy**: CalDAV scheduling lookup with event-derived fallback.

## Common Commands

### List Events (Combined)
Check multiple calendars at once:
```bash
python3 scripts/applecal.py events list \
  --apple-id your@icloud.com \
  --calendar Family \
  --calendar Work \
  --from "2026-02-26T00:00:00Z" \
  --to "2026-02-26T23:59:59Z"
```

### Create All-Day Event
```bash
python3 scripts/applecal.py events create \
  --apple-id your@icloud.com \
  --calendar Family \
  --summary "Birthday" \
  --start "2026-02-26" \
  --end "2026-02-26" \
  --all-day
```

### Attach a File (iPhone Safe)
```bash
python3 scripts/applecal.py attach add \
  --apple-id your@icloud.com \
  --calendar Family \
  --uid <UID> \
  --file /path/to/document.pdf
```

### Free/Busy Check
```bash
python3 scripts/applecal.py freebusy \
  --apple-id your@icloud.com \
  --calendar Family \
  --from "2026-02-26T00:00:00Z" \
  --to "2026-02-26T23:59:59Z"
```

## Notes
- **Birthdays**: The virtual "Birthdays" calendar is not searchable via CalDAV. Key birthdays should be added as physical recurring events in the **Family** calendar for agent visibility.
- **Auth**: Resolution order is `APPLECAL_PASSWORD` → Python `keyring` (if installed/configured) → macOS Keychain fallback. Run `doctor` to verify connectivity.
- **Event update clearing**: Use `events update --clear-location` / `--clear-description` to explicitly remove optional fields.
- **Attachment safety**: `attach add` blocks sensitive paths/names, allowlists file extensions, and supports optional directory scoping via `APPLECAL_ATTACH_DIR`.
- **Apple ID**: Always pass `--apple-id your@icloud.com` (the iCloud account email, not necessarily your Apple ID login).
