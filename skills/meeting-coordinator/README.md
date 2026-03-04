# Meeting Coordinator Skill

This OpenClaw skill turns the agent into an executive scheduling assistant for:

- new meeting scheduling
- rescheduling and cancellation
- availability analysis
- in-person venue lookup
- invite follow-up and day-before confirmation

## Operating Model

This README assumes:

- the OpenClaw agent uses its own Gmail account
- the human shares their Google Calendar with that agent account
- the shared calendar permission is at least "Make changes to events" (write/manage)

The agent sends email as the agent Gmail account and schedules on the human's shared calendar.

## What The Skill Enforces

- explicit human approval before sending any email
- explicit human approval before creating/updating/deleting counterparty-visible calendar events
- no fabricated emails, venues, reservation details, or thread IDs
- timezone-safe communication
- complete tracking in `memory/scheduling/in-progress.md`
- conservative record lifecycle management (no active record deletion)

## Repository Contents

- `SKILL.md`: core operating playbook
- `references/email-templates.md`: outbound email templates and formatting rules
- `scripts/check-availability.py`: checks free slots for a date window
- `scripts/find-venue.py`: searches venue options with `goplaces`

## Prerequisites

1. OpenClaw skill loading enabled in your environment
2. Python 3.10+ (for `zoneinfo` in the scripts)
3. `gog` CLI installed and authenticated to the agent Gmail account
4. `goplaces` CLI installed and authenticated
5. Human calendar shared to the agent Gmail account with write/manage permissions
6. `USER.md` available to the agent
7. `SOUL.md` or `IDENTITY.md` available to the agent

## Declared Runtime + Credentials

This skill declares the following in `SKILL.md` `metadata.openclaw`:

- required binaries: `gog`, `goplaces`, `python3`
- required env vars: `GOG_ACCOUNT`, `GOOGLE_PLACES_API_KEY`
- required config dirs: `$HOME/.config/gog`, `$HOME/.config/goplaces`
- primary credential selector: `GOG_ACCOUNT`
- homepage/source: `https://github.com/voshawn/meeting-coordinator-skill`

Notes:

- `GOG_ACCOUNT` identifies which authenticated Google account `gog` will operate as.
- `gog` OAuth tokens are local credentials; use a dedicated, low-privilege agent account.
- `GOOGLE_PLACES_API_KEY` powers venue lookup through `goplaces`.

## Required Profile Data

`USER.md` should include:

- human full name
- human email
- calendar ID to schedule against (shared calendar ID)
- home timezone (IANA, for backend calculations)
- preferred scheduling windows (days/hours)
- default durations by meeting type
- travel and post-meeting buffer defaults
- transit and venue preferences

`SOUL.md` or `IDENTITY.md` should include:

- assistant tone guidance
- email signature block

## Installation

1. Install the skill folder at:
`$CODEX_HOME/skills/meeting-coordinator`
2. Ensure scripts are executable if needed:

```bash
chmod +x scripts/check-availability.py scripts/find-venue.py
```
3. Verify required CLIs are available:

```bash
gog --help
goplaces --help
```
4. Verify scripts run:

```bash
python3 scripts/check-availability.py --help
python3 scripts/find-venue.py --help
```
5. Confirm the agent can access the human calendar via the configured calendar ID.

## Gmail + Calendar Setup (Agent Account)

1. Sign in `gog` as the agent Gmail account.
2. In Google Calendar, share the human's calendar with the agent Gmail.
3. Grant at least "Make changes to events".
4. Put that shared calendar ID into `USER.md`.
5. Do not use `primary` unless explicitly intended.

## Preflight Verification (Run Before First Write Action)

```bash
echo "$GOG_ACCOUNT"
gog auth list
test -n "$GOOGLE_PLACES_API_KEY"
gog calendar events "<shared_calendar_id>" --from "<YYYY-MM-DD>T00:00:00" --to "<YYYY-MM-DD>T23:59:59"
```

If any check fails, stop and fix auth/config before scheduling.

## Email Formatting Rules

- send outbound messages using `--body-html`
- always CC the human
- include timezone labels in every time reference
- display times with standard US labels (`ET`, `CT`, `MT`, `PT`)
- if counterparty timezone differs, include both (example: `3:00 PM ET / 12:00 PM PT`)
- for virtual meetings, create the calendar event with `--meet` so Google Meet is generated automatically

## How Scheduling Flows

1. Intake meeting request and constraints
2. Check availability across preferred windows
3. Find venues for in-person meetings
4. Present options to human for approval
5. Create tentative holds for approved options
6. Draft outreach email and wait for approval
7. Send approved outreach and track thread state
8. On acceptance, create final event and related buffers/travel blocks (virtual meetings use `--meet`)
9. Send approved confirmation follow-up
10. Update tracking record with all event IDs and status

## Tracking Lifecycle Policy

- one meeting = one durable entry in `memory/scheduling/in-progress.md`
- entries are updated in place and include `updated_at` + append-only activity log notes
- active entries are never auto-deleted
- entries are moved to archive only when terminal (`completed`, `cancelled`, `closed-no-response`) and 14+ days old since `updated_at`
