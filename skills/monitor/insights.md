# Monitor Analysis Patterns

## Uptime Calculation

```bash
# Calculate uptime percentage for a monitor
jq -s '
  (map(select(.status == "ok")) | length) as $ok |
  length as $total |
  ($ok / $total * 100) | floor
' logs/http-api-prod/2024-03.jsonl
```

## Latency Statistics

```bash
# P50, P95, P99 latency
jq -s '
  [.[].latency_ms] | sort |
  {
    p50: .[length * 0.50 | floor],
    p95: .[length * 0.95 | floor],
    p99: .[length * 0.99 | floor],
    avg: (add / length | floor)
  }
' logs/http-api-prod/2024-03.jsonl
```

## Pattern Detection

### Time-based patterns
- Group failures by hour: "Most failures at 9am"
- Group by day of week: "Slower on weekends"
- Identify maintenance windows

### Degradation trends
- Compare this week vs last week latency
- Alert if P95 increases >20%

## Weekly Summary Template

```
## Monitor Summary: Week of 2024-03-11

### http-api-prod
- Uptime: 99.2%
- Incidents: 2 (3 min, 7 min)
- Avg latency: 142ms (P95: 340ms)
- Trend: ↑ 15% slower than last week

### http-website-main
- Uptime: 100%
- Avg latency: 89ms (P95: 210ms)
- Trend: Stable
```

## Suggested Monitors

Based on what user monitors, suggest:
- If monitoring website → suggest API health
- If monitoring API → suggest SSL expiry
- If monitoring prod → suggest staging too
