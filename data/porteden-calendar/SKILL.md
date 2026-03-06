---
name: porteden
description: Secured Calendar management - Google Calendar, Microsoft Outlook & Exchange - list, search, create, update, delete, and respond to calendar events across multiple accounts (gog-cli secure alternative).
homepage: https://porteden.com
metadata: {"openclaw":{"emoji":"📅","requires":{"bins":["porteden"],"env":["PE_API_KEY"]},"primaryEnv":"PE_API_KEY","install":[{"id":"brew","kind":"brew","formula":"porteden/tap/porteden","bins":["porteden"],"label":"Install porteden (brew)"},{"id":"go","kind":"go","module":"github.com/porteden/cli/cmd/porteden@latest","bins":["porteden"],"label":"Install porteden (go)"}]}}
---

# porteden

Use `porteden` for calendar management across multiple accounts. **Use `-jc` flags** for AI-optimized output.

If `porteden` is not installed: `brew install porteden/tap/porteden` (or `go install github.com/porteden/cli/cmd/porteden@latest`).

Setup (once)

- **Browser login (recommended):** `porteden auth login` — opens browser, credentials stored in system keyring
- **Direct token:** `porteden auth login --token <key>` — stored in system keyring
- **Verify:** `porteden auth status`
- If `PE_API_KEY` is set in the environment, the CLI uses it automatically (no login needed).

Common commands

- List calendars: `porteden calendar calendars -jc`
- Events today (or --tomorrow, --week): `porteden calendar events --today -jc`
- Events custom range: `porteden calendar events --from 2026-02-01 --to 2026-02-07 -jc`
- All events (auto-pagination): `porteden calendar events --week --all -jc`
- Search events: `porteden calendar events -q "meeting" --today -jc`
- Events by contact: `porteden calendar by-contact "user@example.com" -jc` (or --name "John Smith")
- Get single event: `porteden calendar event <eventId> -jc`
- Create event: `porteden calendar create --calendar <id> --summary "Meeting" --from "..." --to "..." --location "Room A" --attendees "a@b.com,c@d.com"`
- Update event: `porteden calendar update <eventId> --summary "New Title"` (also: --from, --to, --location)
- Update attendees: `porteden calendar update <eventId> --add-attendees "new@example.com"` (or --remove-attendees; add --notify to send notifications)
- Delete event: `porteden calendar delete <eventId>` (add --no-notify to skip attendee notifications)
- Respond to invite: `porteden calendar respond <eventId> accepted` (or: declined, tentative)


Event Status Values

- `confirmed` - Accepted/scheduled
- `tentative` - Maybe attending
- `needsAction` - Requires response from user
- `cancelled` - Event was cancelled

Time Formats

- All times use RFC3339 UTC format: `2026-02-01T10:00:00Z`
- For all-day events, use midnight-to-midnight with `--all-day` flag
- JSON output includes `startUtc`, `endUtc`, `durationMinutes` fields

Notes

- Credentials persist in the system keyring after login. No repeated auth needed.
- Set `PE_PROFILE=work` to avoid repeating `--profile`.
- `-jc` is shorthand for `--json --compact`: filters noise, truncates descriptions, limits attendees, reduces tokens.
- Use `--all` to auto-fetch all pages; check `meta.hasMore` and `meta.totalCount` in JSON output.
- Manual pagination: `--limit 100 --offset 0`, then `--offset 100`, etc.
- `by-contact` supports partial matching: `"@acme.com"` for email domain, `--name "Smith"` for name.
- Confirm before creating, updating, or deleting events.
- "invalid calendar ID": Get IDs with `porteden calendar calendars -jc`.
- Environment variables: `PE_API_KEY`, `PE_PROFILE`, `PE_TIMEZONE`, `PE_FORMAT`, `PE_COLOR`, `PE_VERBOSE`.