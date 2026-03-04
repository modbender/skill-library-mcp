# iCal Recurrence Rules (RRULE)

Apple Calendar uses standard iCal RRULE format for recurring events.

## Common patterns

| Pattern | RRULE |
|---|---|
| Daily | `FREQ=DAILY;INTERVAL=1` |
| Every weekday | `FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR` |
| Weekly | `FREQ=WEEKLY;INTERVAL=1` |
| Biweekly | `FREQ=WEEKLY;INTERVAL=2` |
| Monthly (same date) | `FREQ=MONTHLY;INTERVAL=1` |
| Monthly (e.g. 2nd Tuesday) | `FREQ=MONTHLY;BYDAY=2TU` |
| Yearly | `FREQ=YEARLY;INTERVAL=1` |

## Limiting recurrence

- End after N occurrences: add `COUNT=10`
- End by date: add `UNTIL=20261231T000000Z`

## Examples

- Every Monday and Wednesday: `FREQ=WEEKLY;BYDAY=MO,WE`
- First Friday of every month: `FREQ=MONTHLY;BYDAY=1FR`
- Every 3 days for 5 times: `FREQ=DAILY;INTERVAL=3;COUNT=5`
