---
name: icloud-toolkit
description: >
  Unified iCloud integration for Calendar, Email, and Contacts. Use when:
  (1) creating, listing, searching, or deleting calendar events, (2) reading,
  sending, or searching email, (3) looking up, creating, editing, or deleting
  contacts, (4) any task involving iCloud calendar, email, or contacts. Handles
  timezone conversion, iCloud-compatible formatting, and vdirsyncer sync
  automatically.
metadata:
  openclaw:
    emoji: "☁️"
    install: ["brew install vdirsyncer", "brew install khal", "brew install himalaya", "brew install khard"]
    requires:
      bins: ["python3", "himalaya", "khal", "vdirsyncer", "khard"]
---

# iCloud Toolkit

Calendar + Email + Contacts CLI. One script, all iCloud operations.

**Script:** `scripts/icloud.py` | **Config:** `config/config.json`

## Rules

- **Always use the CLI commands below** instead of reading source files, parsing .ics/.vcf files directly, or grepping code. The CLI handles CalDAV discovery, IMAP operations, feed fetching, sync, timezone conversion, and formatting internally.
- **One query first, fan out only if needed.** Start with a single `calendar list --days N` or `calendar search "<keyword>"` — scan the output yourself before running more commands. Do not run multiple searches with different keywords in parallel. Each command triggers a sync cycle, so fewer calls = faster answers.
- **For multi-calendar queries** (e.g., "when are we both free?"), run `calendar list` for each calendar separately, then reason over the combined output.
- **Subscribed calendars are read-only.** You can list and search them, but `calendar create` and `calendar delete` only work on owned calendars.
- **Run `calendar refresh`** if the user mentions subscribing to a new calendar.
- **If a calendar returns no events, report that to the user — don't debug it.** Empty results are valid. The user may not have events, or the calendar may need a `calendar refresh`. Never write scripts to parse data or call APIs as a workaround.
- **Always ask permission** before sending or deleting emails on behalf of the user.
- **Don't re-read this file every turn.** Once you've read SKILL.md in a session, you have the commands — just use them.

## Quick reference

```bash
ICLOUD=~/.openclaw/workspace/skills/icloud-toolkit/scripts/icloud.py

# Calendar
python3 $ICLOUD calendar list                                    # Today
python3 $ICLOUD calendar list --days 7                           # Next 7 days
python3 $ICLOUD calendar list --days 7 --calendar Appointments   # Specific calendar
python3 $ICLOUD calendar search "meeting"                        # Search events
python3 $ICLOUD calendar create <cal> <date> <start> <end> <title> [--location X] [--description X]
python3 $ICLOUD calendar create-allday <cal> <date> <title> [--description X]
python3 $ICLOUD calendar delete <uid>
python3 $ICLOUD calendar sync                                    # Manual sync
python3 $ICLOUD calendar disable <name>                          # Hide from listings
python3 $ICLOUD calendar enable <name>                           # Show in listings
python3 $ICLOUD calendar refresh                                 # Re-discover calendars

# Email
python3 $ICLOUD email list                                       # Latest 10
python3 $ICLOUD email list --count 20 --folder "Sent Messages"   # Sent folder
python3 $ICLOUD email list --unread                              # Unread only
python3 $ICLOUD email read <id> [--folder X]
python3 $ICLOUD email send <to> <subject> <body>
python3 $ICLOUD email reply <id> <body> [--all] [--folder X]
python3 $ICLOUD email search "from Apple" [--folder X]
python3 $ICLOUD email move <folder> <id> [--source X]            # Move (folder first, then id)
python3 $ICLOUD email delete <id> [--folder X]

# Folder
python3 $ICLOUD folder purge <folder>                            # Purge all emails from folder

# Contacts
python3 $ICLOUD contact list [--addressbook X] [--count N]
python3 $ICLOUD contact show <uid>
python3 $ICLOUD contact search "John"
python3 $ICLOUD contact create John Doe --email j@x.com --phone +15551234567
python3 $ICLOUD contact create --fn "Acme Corp" --org "Acme Corp"
python3 $ICLOUD contact edit <uid> --add-email new@x.com
python3 $ICLOUD contact edit <uid> --first Jane --last Smith
python3 $ICLOUD contact delete <uid>
python3 $ICLOUD contact sync
```

## Calendar

Times are local — the CLI converts to UTC automatically using the configured timezone.

```bash
python3 $ICLOUD calendar create Appointments 2026-03-15 14:00 15:30 "Team Meeting" \
  --location "Board Room" --description "Weekly sync"
python3 $ICLOUD calendar create-allday General 2026-03-15 "Company Holiday"
```

Calendar names are configured during setup. To see available calendars, run `calendar list`.

### Multi-calendar queries

For questions spanning multiple calendars (e.g., "when are we both off?", "do I have conflicts?"):

1. Run `calendar list --days N --calendar <name>` for each relevant calendar
2. Parse the text output to identify busy/free days
3. Answer from the combined results

### Disable/enable

Any calendar (owned or subscribed) can be excluded from listings:

```bash
python3 $ICLOUD calendar disable "Garbage Collection"   # Exclude from list/search
python3 $ICLOUD calendar enable "Garbage Collection"    # Include again
```

### Refresh

Run `calendar refresh` to pick up newly subscribed calendars after initial setup.

## Email

iCloud folders: INBOX, Sent Messages, Drafts, Deleted Messages, Junk, Archive

Search uses himalaya query syntax (positional):

```bash
python3 $ICLOUD email search "from Apple"
python3 $ICLOUD email search "subject invoice"
python3 $ICLOUD email search "after 2026-02-01"
python3 $ICLOUD email search "from Apple and after 2026-01-01"
```

Emails are sent from the `account_email` in config — this may differ from the Apple ID used for authentication (e.g., custom domain users).

Reply auto-matches the From address to whichever address received the original email.

## Contacts

```bash
# Full contact creation
python3 $ICLOUD contact create John Doe \
  --email john@work.com --email john@home.com \
  --phone +15551234567 --phone +15559876543 \
  --org "Acme Corp" --title "Engineer" \
  --nickname "Johnny" --birthday 1990-01-15 \
  --note "Met at conference" --category friend \
  --addressbook Work

# Editing preserves all existing data — only specified fields change
python3 $ICLOUD contact edit <uid> --add-email new@x.com     # Add (keeps existing)
python3 $ICLOUD contact edit <uid> --remove-email old@x.com  # Remove specific
python3 $ICLOUD contact edit <uid> --email only@x.com        # Replace all
python3 $ICLOUD contact edit <uid> --add-phone +15559999999
python3 $ICLOUD contact edit <uid> --remove-phone +15551111111
python3 $ICLOUD contact edit <uid> --org "New Corp" --title "Manager"
```

## Email notifications (heartbeat)

`scripts/heartbeat-cron.py` checks for new unread iCloud emails every 5 minutes and sends triage prompts to the agent.

```bash
python3 scripts/heartbeat-cron.py             # Normal run
python3 scripts/heartbeat-cron.py --dry-run   # Preview without agent call
```

State is stored in `state/heartbeat-state.json` (skill-local). Logs go to `~/.openclaw/logs/heartbeat-icloud.log`.

## Notes

- **Sync** is automatic before reads, before+after writes. Manual: `calendar sync` / `contact sync`.
- **Self-test:** `python3 $ICLOUD --test`

## First-time setup

When `config/config.json` is missing, the skill outputs `SETUP_REQUIRED`. Follow this two-step flow.

### Step 1: Configure

Ask the user for their **Apple ID**, **sending address** (same as Apple ID unless custom domain), **display name**, and **timezone** (IANA format, auto-detected if omitted).

The password is managed via `$ICLOUD_APP_PASSWORD`. If not set:
> Go to https://appleid.apple.com → Sign-In and Security → App-Specific Passwords → Generate one for "iCloud Toolkit". Then set it with: `/secret set ICLOUD_APP_PASSWORD`

```bash
# Most users (sending address = Apple ID):
python3 $ICLOUD setup configure --email APPLE_ID --name "USER_NAME" --timezone TIMEZONE

# Custom domain users:
python3 $ICLOUD setup configure --email SENDING_ADDRESS --apple-id APPLE_ID --name "USER_NAME" --timezone TIMEZONE
```

This writes auth, generates vdirsyncer config, runs discovery+sync, and outputs discovered calendars/address books as JSON.

### Step 2: Finalize

Calendars are auto-discovered — the user just picks a default.

```bash
python3 $ICLOUD setup finalize --email SENDING_ADDRESS --apple-id APPLE_ID --name "USER_NAME" --timezone TIMEZONE \
  --default Personal \
  --addressbooks '{"Contacts":"uuid-from-discovery"}' --default-addressbook Contacts
```

When `--calendars` is omitted, the skill auto-discovers all calendars from iCloud, splitting them into owned and subscribed. `--addressbooks` and `--default-addressbook` are optional.

```bash
python3 $ICLOUD setup verify    # Run smoke tests
```
