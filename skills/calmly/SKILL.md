---
name: calmly
description: Manage macOS Calendar events from the command line using EventKit. Use when creating, listing, or viewing calendar events on macOS without AppleScript dialogs or UI prompts. Supports all-day events, multi-day events, and timed events. Works with iCloud, local, and CalDAV calendars.
metadata:
  openclaw:
    emoji: "📅"
    os: ["darwin"]
    requires:
      bins: ["calmly"]
    install:
      - id: brew
        kind: brew
        formula: halbotley/tap/calmly
        bins: ["calmly"]
        label: "Install calmly (brew)"
---

# calmly

A calm CLI for macOS Calendar. Manage iCloud and local calendars without dialogs, prompts, or UI interruptions.

## Why calmly?

- **AppleScript hangs** — Calendar scripting often freezes waiting for permissions
- **ICS imports pop dialogs** — Can't automate without user interaction  
- **icalBuddy is read-only** — Can't create events

calmly uses EventKit directly, so it works silently.

## Installation

```bash
brew tap halbotley/tap
brew install calmly
```

First run prompts for Calendar access (System Settings → Privacy → Calendars). One-time only.

## Commands

### List calendars

```bash
calmly list
```

### View upcoming events

```bash
calmly events Work           # Next 30 days
calmly events Family 14      # Next 14 days
```

### Create all-day event

```bash
calmly add Work "Day Off" 2025-03-15
```

### Create multi-day event

```bash
calmly add Family "Vacation" 2025-07-01 2025-07-14
```

### Create timed event

```bash
calmly addtimed Work "Meeting" 2025-03-15 09:00 10:30
calmly addtimed Kids "Swim Practice" 2025-02-03 07:00 08:30
```

## Batch Event Creation

For recurring events, loop in bash:

```bash
# Morning practice every Tuesday/Thursday for 6 weeks
for d in 2025-02-04 2025-02-06 2025-02-11 2025-02-13; do
  calmly addtimed Kids "🏊 AM Practice" "$d" 07:00 08:30
done
```

## Date Verification

Before creating events, verify day/date alignment:

```bash
for d in 3 4 5 6 7; do date -j -f "%Y-%m-%d" "2025-02-0$d" "+%A %B %d"; done
```

## Notes

- Dates use `YYYY-MM-DD` format
- Times use 24-hour `HH:MM` format
- Calendar names are case-insensitive
- Events sync to iCloud automatically
- No delete command yet — delete via Calendar app or iCloud web
