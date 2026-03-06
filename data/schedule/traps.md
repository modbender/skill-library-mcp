# Scheduling Traps

Check before creating any job. Prevent common failures.

## Timezone Hell

| Trap | Fix |
|------|-----|
| ISO without TZ = UTC | Always append zone: `2026-02-15T09:00:00+01:00` |
| "Tomorrow" ambiguous | Confirm exact date: "Tuesday Feb 18" |
| DST shift (March/October) | Jobs at 02:00-03:00 may skip or double |
| User travels | Ask if schedule should follow them or stay fixed |

## Persistence

| Trap | Fix |
|------|-----|
| Stored in memory only | Write to ~/schedule/jobs.json |
| Session reset loses jobs | Always persist to file, never rely on context |
| "I'll remember" | You won't. Save to jobs.json. |

## Confirmation

| Trap | Fix |
|------|-----|
| "Reminder set" | Show WHEN: date, time, timezone |
| "Tomorrow at 9" | Show: "Tuesday Feb 18 at 09:00 (Europe/Madrid)" |
| No ID | Always give ID for cancel/edit |
| Generic message | Include WHAT: "Reminder: call dentist" |

## Execution

| Trap | Fix |
|------|-----|
| Silent failure | Always notify if job fails |
| Duplicate jobs | Check existing before creating |
| Overlapping runs | Use locks for long-running jobs |
| Never ends | Set max retries, notify on repeated failure |

## Recurrence

| Trap | Fix |
|------|-----|
| "Every day" forever | Ask about end date or review period |
| Holiday runs | Ask if holidays should skip |
| Weekend noise | Clarify: include weekends? |

## Before Creating

Checklist:
```
□ Timezone explicit?
□ Exact date/time confirmed?
□ Saved to ~/schedule/jobs.json?
□ Unique ID assigned?
□ Confirmation includes WHAT + WHEN + ID?
```
