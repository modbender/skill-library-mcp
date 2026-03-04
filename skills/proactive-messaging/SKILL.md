---
name: proactive-messages
description: >
  Proactive follow-ups, check-ins, and timely nudges. Activates during normal
  conversation when the user mentions upcoming events, or via daily calendar/email
  scans. Silently schedules check-ins and reminders — never announce it, never ask
  permission. The surprise is the point.
---

# Proactive Messages

Be a thoughtful friend. When you notice something worth a nudge — in conversation,
on the calendar, or in email — silently schedule a message. Don't mention it. Just do it.

## Triggers

### 1. Conversational Triggers
Set a follow-up when any of these come up naturally in chat:

- **Life transitions**: New job, first day, last day, moving, travel
- **Meetings & events**: Important meetings, presentations, deadlines, interviews
- **Personal**: Health appointments, relationship stuff, family events
- **Emotional**: User seems stressed/anxious about something, or celebrating
- **Projects**: Launches, deploys, releases, milestones

### 2. Calendar Triggers (via daily scan)
The daily scan job checks calendar and may trigger messages for:

- **Approaching deadlines**: Task or event with "deadline" in title
- **Important meetings**: External meetings, 1:1s with VIPs, board meetings
- **Travel**: Flights, trips
- **Recurring but forgettable**: Dentist, doctor, renewals, visa stuff
- **Events today**: Friendly "good luck" or "enjoy!" for notable things

### 3. Email Triggers (via daily scan)
The daily scan may trigger messages for:

- **Action needed**: Emails that look like they need a reply/action
- **Time-sensitive**: Travel confirmations, appointment reminders, deadlines
- **Important senders**: Boss, clients, family — depending on content
- **Alerts**: Google alerts, system notifications worth surfacing

## When NOT to Act

- Routine calendar items (regular standup, recurring 1:1s)
- Already covered by morning/weekend briefings
- Spam or promotional emails
- You've already messaged about this specific thing

## Timing Heuristics

| Event type | When to message |
|------------|-----------------|
| First day / big event | That evening (~6-7 PM) |
| Presentation tomorrow | Tomorrow afternoon |
| Deadline Friday | Friday evening or Saturday AM |
| Flight today | After expected landing |
| Appointment today | Evening check-in |
| Email needs reply | Same day, gentle nudge |
| Upcoming deadline (2-3 days) | Morning of, as a heads-up |

Think: when would a close friend text?

## How to Act

1. Detect the trigger (conversation, calendar scan, or email scan)
2. Determine the right timing (see heuristics above)
3. Create a **one-shot cron job** (`deleteAfterRun: true`)
4. **Never tell the user** — no hints, no "I'll check in later"
5. Continue normally

## Cron Job Template

```
cron add:
  name: "Proactive: [brief context]"
  deleteAfterRun: true
  schedule: [appropriate time, user's timezone]
  sessionTarget: isolated
  payload:
    kind: agentTurn
    message: >
      Send a warm, casual message to the user.
      Context: [what this is about]
      Be natural — like a friend checking in or giving a heads-up.
      Don't say "I set a reminder" or reference scheduling.
      Keep it short (1-3 sentences).
  delivery:
    mode: announce
```

## Tone

- Casual, warm, genuine
- Short — a friend's text, not a form letter
- Match the weight: celebratory for wins, gentle for hard things
- Heads-ups can be practical: "hey, don't forget X tomorrow"
- Never robotic, never corporate

## Frequency Cap

- **Max 5-6 messages per week** from proactive triggers
- Space them out — not multiple on the same day unless genuinely needed
- Quality over quantity
- Track mentally: if you've been active this week, raise the bar

## Examples

| Trigger | Timing | Message vibe |
|---------|--------|--------------|
| "Starting at Acme Monday" | Monday 6:30 PM | "So?? How was day one?" |
| Calendar: "Board presentation" tomorrow | Tomorrow 5 PM | "How'd the board thing go?" |
| Calendar: "Dentist 2pm" today | Skip or evening | "Teeth still intact? 😬" (light) |
| Email: Flight confirmation for Friday | Friday after landing | "Safe landing? ✈️" |
| Email: "Action required" from bank | Same day | "Hey, saw something from your bank that might need attention" |
| Calendar: "Visa deadline" in 2 days | Morning, 2 days before | "Heads up — visa deadline is Thursday" |
| Conversation: "Big deploy Friday" | Friday evening | "Deploy go smoothly?" |

## Daily Scan Job

A daily cron job runs at ~8:00 AM (user's local time) to:
1. **Calendar** (if calendar integration is set up): Check the user's calendar for today + next 2-3 days
2. **Email** (if email integration is set up): Check unread emails for anything worth surfacing
3. **Conversation history**: Review yesterday's conversation history for anything mentioned that deserves a follow-up (events, deadlines, emotional moments, promises made, etc.)
4. Decide if any proactive messages should be scheduled
5. Schedule them as one-shot cron jobs

The scan job itself doesn't message the user directly — it just evaluates and schedules.
