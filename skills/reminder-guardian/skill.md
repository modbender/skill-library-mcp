---
name: reminder-guardian
description: Helps you remember things by keeping a list of reminders, creating the scheduled jobs to alert you, and tracking which ones are done.
---

# Reminder Guardian

A very lightweight skill that turns every reminder request into a logged record plus a ready-to-run `openclaw cron add` blueprint. Installers use the CLI to record the reminder, then immediately paste the printed blueprint into `openclaw cron add`, and finally mark the reminder as scheduled so nothing slips through.

## Quick steps anyone can follow

1. **Log the reminder**: `python3 skills/reminder-guardian/scripts/reminder_guard.py add --message "Take meds" --when 2026-02-19T17:00:00 --label "Medication"`
   - Writes a JSON entry under `memory/reminder-log.json` (status `pending`).
   - Prints the cron blueprint that contains the schedule + payload for the reminder.

2. **Create the cron job**: Copy the printed blueprint and run `openclaw cron add` (choose the delivery channel that fits your workflow).

3. **Tell the skill the job exists**: `python3 skills/reminder-guardian/scripts/reminder_guard.py blueprint <id> --mark` sets status to `scheduled` so the log reflects the Cron job is active.

4. **After the reminder fires**: `python3 skills/reminder-guardian/scripts/reminder_guard.py update <id> --status sent` keeps the log accurate. Nothing happens automatically—the CLI merely tracks your intention and status changes.

5. **See the next reminder**: `python3 skills/reminder-guardian/scripts/reminder_guard.py next` prints the next pending entry plus its blueprint, which is handy if you want to re-schedule or re-run a reminder.

## Time helper and consistency

The skill ships with its own `scripts/time_helper.py`. Every command that needs “the current time” calls that helper before printing or logging anything, keeping the workflow aligned with your canonical time source.

## Why this matters

- The log is auditable (`memory/reminder-log.json`, ignored from git).
- The blueprint gives you a human-reviewed cron payload before you schedule anything.
- Anyone who installs this skill follows the same steps, keeping delivery explicit and safe.

Publishing tip: document that the blueprint must be copied into `openclaw cron add`—without that manual step, reminders never run. Once you publish, future installers will read this explanation and understand exactly how the flow works.
