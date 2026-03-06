# Interval Strategies

## By Context

| Context | Base Interval | Adjust When |
|---------|---------------|-------------|
| Active conversation | 5-10 min | User goes quiet → extend |
| Monitoring deploy/task | 10-15 min | Task completes → stop |
| Waiting for email/response | 30-60 min | Response arrives → check |
| Background/idle | 2-4 hours | Nothing pending |
| Night/offline hours | 4-8 hours | User sets DND |

## Adjustment Rules

**Shorten interval when:**
- User mentions urgency ("waiting for X", "need to know when")
- External deadline approaching
- High-value event expected (meeting, deploy, response)

**Extend interval when:**
- Last 3 wakes had no useful action
- User said to reduce frequency
- Night hours or explicit quiet time
- Nothing has changed since last wake

## Hit Rate Tracking

Track per monitor:
```
email: 5/20 useful (25%) → consider extending
calendar: 18/20 useful (90%) → keep current
social: 2/30 useful (7%) → propose reducing or removing
```

**Threshold:** If hit rate < 20% over 10+ wakes, propose reducing frequency.

## Burst vs Steady

- **Burst mode:** Short intervals for limited time (deploy monitoring, urgent wait)
  - Auto-revert to steady after condition clears
  - Set explicit end condition: "until deploy completes", "until 5pm"

- **Steady mode:** Regular intervals for ongoing checks
  - Default state for most monitors
  - Adjust based on observed patterns
