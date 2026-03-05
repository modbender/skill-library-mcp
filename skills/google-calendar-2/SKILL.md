---
name: google-calendar
description: Manages Google Calendar — creates, updates, and queries events, scheduling, and availability. Use when the user mentions calendar, meetings, appointments, agenda, or Google Calendar.
---

# Google Calendar

## First-Time Setup

1. Check if `~/.config/google-calendar-skill/client.json` exists (if exists, move on to step 2 without asking, if not, point them to SETUP.md in the source repo).
2. Run `bun run auth.ts login` — this opens the browser. The user signs into their Google account.
3. After login succeeds, the script prints the authenticated email. Show it to the user.
4. Ask the user what this account is for (e.g. "work", "personal") and optionally its **purpose** (e.g. "Work meetings", "Personal"). Then run:
   ```bash
   bun run auth.ts label <chosen-name> [purpose]
   ```
   If they didn't give a purpose, guess based on what they said about the account and update **config.json** (see Account config below): set `accounts.<label>.purpose`.
5. Ask if they want to connect another Google account. If yes, repeat from step 2.
6. After each `label` (if purpose wasn't passed), ensure config.json has the account's purpose.
7. List their calendars so they can see what's available (runs for all accounts; output is labeled):
   ```bash
   bun run calendar.ts calendars
   ```

## Working Directory

All commands must run from this skill's `scripts/` directory. Determine the path relative to this SKILL.md file:

```bash
cd "$(dirname "<path-to-this-SKILL.md>")/scripts"
```

For the default install location:

```bash
cd ~/.openclaw/skills/google-calendar/scripts
```

## Auth Commands

Run from `scripts/`. Tokens auto-refresh on expiry. All auth commands accept `--account <alias>` (defaults to `default`).

| Command                                      | Description                                                                               |
| -------------------------------------------- | ----------------------------------------------------------------------------------------- |
| `bun run auth.ts login`                      | Start OAuth flow (opens browser)                                                          |
| `bun run auth.ts status`                     | Check authentication status                                                               |
| `bun run auth.ts accounts`                   | List all authenticated accounts with emails                                               |
| `bun run auth.ts label <name> [description]` | Rename an account; optional description → config purpose (defaults to renaming `default`) |
| `bun run auth.ts refresh`                    | Force-refresh the access token                                                            |
| `bun run auth.ts revoke`                     | Revoke tokens and delete local credentials                                                |
| `bun run auth.ts token`                      | Print a valid access token (auto-refreshes)                                               |

## Calendar Commands

Run from `scripts/`.

- **list, get, update, delete, calendars, freebusy** — no `--account`. The script runs for **all** connected accounts and labels output (e.g. `── work ──`, `── personal ──`).
- **create, quick** — require `--account <alias>` (or default `default`). Use config.json to pick the right account when creating events.

Shared flag: `--calendar <ID>` (defaults to `primary`). For create/quick only: `--account <alias>`.

| Command                                                              | Description                                     |
| -------------------------------------------------------------------- | ----------------------------------------------- |
| `bun run calendar.ts list [--from DATE] [--to DATE] [--max N]`       | List upcoming events (all accounts, labeled)    |
| `bun run calendar.ts get <eventId>`                                  | Get event details (tries all accounts, labeled) |
| `bun run calendar.ts create --summary "..." [options] --account X`   | Create an event on account X                    |
| `bun run calendar.ts quick "text" --account X`                       | Quick-add on account X                          |
| `bun run calendar.ts update <eventId> [--summary ...] [--start ...] [--attendees ...] [--add-attendees ...] [--remove-attendees ...]` | Update an event (tries all accounts) |
| `bun run calendar.ts delete <eventId>`                               | Delete an event (tries all accounts)            |
| `bun run calendar.ts calendars`                                      | List all calendars (all accounts, labeled)      |
| `bun run calendar.ts freebusy --from DATE --to DATE`                 | Free/busy (all accounts, labeled)               |

### Create flags

Use exactly these flag names — the CLI does not accept aliases:

`--summary` (required, the event title), `--start`, `--end`, `--description`, `--location`, `--attendees` (comma-separated emails), `--all-day`.

Dates accept any JS-parsable format. Omitting `--start` defaults to 1h from now; omitting `--end` defaults to 1h duration.

```bash
# Timed event
bun run calendar.ts create --summary "Standup" --start "2026-02-07T10:00" --end "2026-02-07T10:30"
# All-day event
bun run calendar.ts create --summary "Vacation" --start "2026-03-01" --end "2026-03-05" --all-day
```

### Update flags

`--summary`, `--start`, `--end`, `--description`, `--location` — same as create (only provided fields are changed).

Attendee flags:

- `--attendees "a@b.com,c@d.com"` — **replaces** all attendees with this list
- `--add-attendees "e@f.com,g@h.com"` — **adds** to existing attendees (skips duplicates)
- `--remove-attendees "a@b.com"` — **removes** specific attendees
- `--no-notify` — skip sending email invitations (by default, invites are sent when attendees change)

```bash
# Add attendees to an existing event (sends invites)
bun run calendar.ts update abc123 --add-attendees "alice@example.com,bob@example.com"
# Replace all attendees without sending invites
bun run calendar.ts update abc123 --attendees "carol@example.com" --no-notify
# Remove an attendee
bun run calendar.ts update abc123 --remove-attendees "alice@example.com"
```

## Multiple Accounts

Each `login` saves to the `default` slot. Use `label` to rename it (optionally with a purpose), then login again for the next account:

```bash
bun run auth.ts login
bun run auth.ts label work "Work meetings, standups"
bun run auth.ts login
bun run auth.ts label personal "Personal appointments, family"
```

Use `--account` only for **create** and **quick**; other calendar commands run for all accounts and label output:

```bash
bun run calendar.ts list
bun run calendar.ts create --summary "Dentist" --account personal --start "2026-02-10T09:00"
```

Manage accounts:

- `bun run auth.ts accounts` — list all with emails
- `bun run auth.ts label <new> [description] --account <old>` — rename any account; optional description → config purpose

## Account config (config.json)

The skill keeps account purposes in **config.json** in the same directory as this SKILL.md (the skill root). The `label` command creates/updates this file when you rename an account; pass an optional description as the second argument to set `purpose`, or add/edit it in config.json afterward.

- **Path:** same folder as this SKILL.md, e.g. `$(dirname "<path-to-this-SKILL.md>")/config.json`
- **Format:**
  ```json
  {
  	"accounts": {
  		"work": { "purpose": "Work meetings, standups, sprint reviews" },
  		"personal": { "purpose": "Personal appointments, family events" }
  	}
  }
  ```

**When creating events:** read `config.json` first. Use it to choose `--account` (and optionally which calendar) from the user's intent or the account `purpose`. If the user doesn't specify an account and there's only one in config, use that; if multiple, infer from context or ask.

**When listing or changing events:** run the calendar command once (no `--account`). The script runs for all connected accounts and labels output with each account name.

## Workflow

When handling a user's calendar request:

```
- [ ] 1. cd into scripts/ directory
- [ ] 2. Check auth: bun run auth.ts accounts
- [ ] 3. If no accounts → run First-Time Setup above
- [ ] 4. **Creating events:** read config.json and pick --account; run create/quick with that --account. **Listing or changing events:** run the command with no --account (script iterates all accounts and labels output).
- [ ] 5. Run the appropriate calendar command (--account only for create/quick)
- [ ] 6. If 401 error → bun run auth.ts refresh [--account ...] → retry
- [ ] 7. If refresh fails → bun run auth.ts login [--account ...]
- [ ] 8. Parse and present results to user
```

## Additional Resources

- For event fields, query parameters, recurrence rules, and attendee options, see [references/API.md](references/API.md)
