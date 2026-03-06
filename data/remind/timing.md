# Timing Defaults

Default lead times by reminder type. Adjust based on learned preferences.

## Standard Lead Times

| Category | Default Lead | Why |
|----------|-------------|-----|
| Meeting/Call | 15 min | Prep time, join link |
| Deadline | 1 day + morning-of | Time to complete |
| Flight/Travel | 3 hours | Airport logistics |
| Birthday/Event | 1 week + day-of | Gift/prep + actual day |
| Bill/Payment | 3 days | Processing time |
| Appointment | 1 hour | Travel buffer |
| Daily habit | Morning | Start of day |
| Weekly recurring | Same time as last | Consistency |

## Adjustment Factors

Modify lead time based on:

| Factor | Adjustment |
|--------|------------|
| High stakes | +50% lead time |
| User often late | +30% buffer |
| Requires prep work | +time for prep |
| User mentioned concern | +1 extra reminder |
| User always on time | Can reduce slightly |
| Simple action | Shorter lead OK |

## Multi-Reminder Patterns

Some events benefit from staged reminders:

```
Important deadline:
  - 1 week before: "Coming up"
  - 1 day before: "Tomorrow"  
  - Morning of: "Today"
  - 1 hour before: "Final reminder"
```

```
Travel:
  - 1 week: Packing list
  - 1 day: Final prep
  - 3 hours: Leave for airport
```

## Time-of-Day Rules

When to deliver (not just how far ahead):

| Reminder Type | Best Delivery Time |
|---------------|-------------------|
| Morning tasks | 7-8 AM |
| Work items | Start of workday |
| Personal | Evening before or morning of |
| Urgent | Immediately when detected |
| Low priority | Batch with others |

## Learning Signals

Adjust defaults when user says:
- "Too early" → Reduce lead time for this category
- "Forgot" / "Missed it" → Increase lead time
- "I knew already" → Maybe skip this category
- "Perfect timing" → Lock current setting

## Override Syntax

User can specify exact timing:

| Phrase | Interpretation |
|--------|----------------|
| "Remind me at 3pm" | Exact time |
| "Remind me in 2 hours" | Relative offset |
| "Remind me tomorrow morning" | Next day, morning slot |
| "Remind me the day before" | 1 day lead |
| "Give me plenty of warning" | Extra buffer |
