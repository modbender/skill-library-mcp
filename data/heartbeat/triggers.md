# Trigger Types

## Time-Based

Schedule wakes at intervals or specific times.

```
every 30min           # Regular interval
at 09:00, 14:00       # Specific times
weekdays 09:00-18:00  # Time window
```

**Use for:** Routine checks, scheduled summaries, regular syncs.

## Event-Based

Wake when external event occurs.

| Event | Source | Action |
|-------|--------|--------|
| Sub-agent completes | sessions_spawn callback | Review output, continue workflow |
| Webhook fires | External service | Process incoming data |
| File changes | Filesystem watch | React to modifications |
| Message arrives | Channel notification | Triage and respond if needed |

**Use for:** Reactive work, async coordination, external integrations.

## Conditional

Wake only if condition is true at check time.

```
if inbox.unread > 0           # Check email only if new
if calendar.next < 2h         # Alert only if event soon
if deploy.status == "running" # Monitor only active deploys
```

**Use for:** Reducing unnecessary wakes, smart filtering.

## Compound Triggers

Combine multiple conditions.

```
# Wake if urgent OR if it's been 4h since last check
trigger: urgent_flag OR (now - last_wake > 4h)

# Wake during work hours if inbox has unread
trigger: (09:00-18:00) AND inbox.unread > 0
```

## User-Defined Triggers

Phrases that create new triggers:
- "Wake me when X happens" → add event trigger
- "Check Y if Z" → add conditional trigger
- "Stop checking X" → remove trigger
- "Alert me about X" → add with shorter interval

Store in Triggers section of main skill.
