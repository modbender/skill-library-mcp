# Habits Commands

## Contents

- Scope
- Read commands
- Create command
- Update command
- Check-in and lifecycle commands
- Parameter notes

## Scope

Use this file for `ticktick habits ...` operations.

Batch check-in is intentionally omitted from this reference.

## Read commands

```bash
ticktick habits list [--json]
ticktick habits get HABIT_ID [--json]
ticktick habits sections [--json]
ticktick habits preferences [--json]
ticktick habits checkins HABIT_ID [HABIT_ID ...] [--after-stamp YYYYMMDD] [--json]
```

## Create command

```bash
ticktick habits create NAME \
  [--type Boolean|Real] \
  [--goal FLOAT] \
  [--step FLOAT] \
  [--unit TEXT] \
  [--icon ICON_KEY] \
  [--color HEX] \
  [--section SECTION_ID] \
  [--repeat RRULE] \
  [--reminders HH:MM,HH:MM] \
  [--target-days N] \
  [--encouragement TEXT] \
  [--json]
```

Defaults:

- `--type Boolean`
- `--goal 1.0`
- `--step 0.0`
- `--unit Count`
- `--icon habit_daily_check_in`
- `--color #97E38B`
- `--repeat RRULE:FREQ=WEEKLY;BYDAY=SU,MO,TU,WE,TH,FR,SA`
- `--target-days 0`
- `--encouragement ""`

## Update command

```bash
ticktick habits update HABIT_ID \
  [--name TEXT] \
  [--goal FLOAT] \
  [--step FLOAT] \
  [--unit TEXT] \
  [--icon ICON_KEY] \
  [--color HEX] \
  [--section SECTION_ID] \
  [--repeat RRULE] \
  [--reminders HH:MM,HH:MM] \
  [--target-days N] \
  [--encouragement TEXT] \
  [--json]
```

Validation rule:

- At least one update field is required.

## Check-in and lifecycle commands

```bash
ticktick habits checkin HABIT_ID [--value FLOAT] [--date YYYY-MM-DD] [--json]
ticktick habits archive HABIT_ID [--json]
ticktick habits unarchive HABIT_ID [--json]
ticktick habits delete HABIT_ID [--json]
```

## Parameter notes

- `HABIT_ID`: habit identifier.
- `--value` default is `1.0`.
- `--date` uses `YYYY-MM-DD`.
- `--after-stamp` uses integer `YYYYMMDD` format.
- `--reminders` is comma-separated `HH:MM` values.

Use confirmation before delete.

Use `ticktick habits <action> --help` only as recovery for parameter errors.
