---
name: Events
description: Build a personal event system for tracking concerts, conferences, parties, appointments, and everything in between.
metadata: {"clawdbot":{"emoji":"📅","os":["linux","darwin","win32"]}}
---

## Core Behavior
- User mentions event → offer to track it
- User planning event → help organize details
- User asks what's coming up → surface relevant events
- Create `~/events/` as workspace

## File Structure
```
~/events/
├── upcoming/
│   ├── concerts/
│   ├── conferences/
│   ├── social/
│   └── appointments/
├── hosting/
├── past/
├── annual/
│   └── recurring.md
└── calendar.md
```

## Event Entry
```markdown
# radiohead-may.md
## Event
Radiohead — MSG

## Date & Time
May 15, 2024, 8:00 PM

## Venue
Madison Square Garden, NYC

## Tickets
Section 112, Row 8
Confirmation: TM-789456

## Logistics
Doors 7pm, meeting Jake at 6:30
No large bags allowed
```

## Hosting an Event
```markdown
# hosting/birthday-2024/
├── overview.md    # date, venue, status checklist
├── guests.md      # confirmed, pending, declined
└── details.md     # food, drinks, music, setup
```

Guest tracking:
```markdown
## Confirmed (12)
- Sarah + 1
- Jake

## Pending (5)
- Tom — following up

## Declined (2)
- Amy — out of town
```

## Annual Recurring
```markdown
# recurring.md
## Birthdays
- Mom: March 22
- Dad: July 8

## Annual Events
- Company retreat: September
- Industry conference: March (register early)
```

## Quick Calendar View
```markdown
# calendar.md
## March 2024
- 5: Jake's birthday party
- 12-14: SXSW Austin
- 22: Mom's birthday
```

## Multi-Day Events
```markdown
# sxsw-2024/
├── overview.md    # dates, location, registration, travel
└── schedule.md    # day-by-day sessions and plans
```

## What To Track
- Date, time, location
- Tickets/confirmation numbers
- Logistics (parking, doors, dress code)
- Who you're going with
- RSVPs when hosting

## What To Surface
- "Concert next week — doors at 7pm"
- "Mom's birthday in 5 days"
- "Registration closes tomorrow"
- "15 confirmed for Saturday"

## Progressive Enhancement
- Start: add upcoming events
- Add annual dates (birthdays, holidays)
- Track past events for memories
- Build hosting checklists

## What NOT To Do
- Forget confirmation numbers
- Miss registration deadlines
- Lose track of RSVPs when hosting
- Skip logistics details
