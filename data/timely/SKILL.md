---
name: timely
description: Manage Apple Reminders from the command line with geofencing support. Use when creating reminders on macOS with optional location-based triggers (arrive/depart), due dates, or time-based alerts. Works with iCloud-synced reminder lists.
metadata:
  openclaw:
    emoji: "⏰"
    os: ["darwin"]
    requires:
      bins: ["timely"]
    install:
      - id: brew
        kind: brew
        formula: halbotley/tap/timely
        bins: ["timely"]
        label: "Install timely (brew)"
---

# timely

A CLI for Apple Reminders with geofencing support. Create location-aware and time-based reminders without UI interaction.

## Why timely?

- **Location triggers** — Remind when arriving at or departing from a place
- **No UI prompts** — Works silently via EventKit
- **iCloud sync** — Reminders appear on all devices

## Installation

```bash
brew tap halbotley/tap
brew install timely
```

First run prompts for Reminders access (System Settings → Privacy → Reminders). One-time only.

## Commands

### List reminder lists

```bash
timely lists
```

### View reminders

```bash
timely show Reminders        # Show all in list
timely show Reminders 10     # Show last 10
```

### Create time-based reminder

```bash
timely add Reminders "Call mom" --due "tomorrow 3pm"
timely add Reminders "Submit report" --due "friday 5pm"
```

### Create location-based reminder (arrive)

```bash
timely add Reminders "Buy milk" \
  --location "Trader Joe's" \
  --address "123 Main St, Santa Barbara, CA" \
  --arrive
```

### Create location-based reminder (depart)

```bash
timely add Reminders "Text wife leaving" \
  --location "Office" \
  --address "456 Work Ave" \
  --depart
```

### Combined (time + location)

```bash
timely add Reminders "Pick up prescription" \
  --due "today" \
  --location "CVS" \
  --address "789 Pharmacy Rd" \
  --arrive
```

## Due Date Formats

Natural language parsing:

- `"today"`, `"tomorrow"`
- `"monday"`, `"next friday"`
- `"tomorrow 3pm"`, `"friday 5pm"`
- `"2025-03-15"`, `"2025-03-15 14:30"`

## Geofencing Notes

- `--location` is the display name (what you see in Reminders)
- `--address` is used for geocoding (must be a real address)
- `--arrive` triggers when entering the location
- `--depart` triggers when leaving the location
- Default geofence radius is ~100 meters

## Shared Lists

For shared iCloud reminder lists, use the exact list name as it appears in the Reminders app. The list syncs across all family members' devices.

## Examples

```bash
# Simple reminder
timely add Reminders "Water plants" --due "saturday 9am"

# Reminder when getting home
timely add Reminders "Take out trash" \
  --location "Home" \
  --address "123 My Street, My City, CA" \
  --arrive

# Reminder when leaving work
timely add Reminders "Pick up kids" \
  --location "Office" \
  --address "456 Work Blvd" \
  --depart
```
