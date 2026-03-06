---
name: metrics-dashboard
description: Track and visualize your agent's operational metrics. Record API calls, task completions, uptime, errors, and custom counters. Generate text-based dashboards and export data for analysis.
user-invocable: true
metadata: {"openclaw": {"emoji": "📊", "os": ["darwin", "linux"], "requires": {"bins": ["python3"]}}}
---

# Metrics Dashboard

Track your agent's operational health. Record events, count things, measure durations, and generate reports.

## Why This Exists

Agents run 24/7 but have no way to answer basic questions: How many tasks did I complete? What's my error rate? How long do API calls take? Which skills do I use most? Without metrics, you're flying blind.

## Commands

### Record a metric
```bash
python3 {baseDir}/scripts/metrics.py record --name api_calls --value 1 --tags '{"provider": "openrouter", "model": "gpt-4"}'
```

### Record a duration
```bash
python3 {baseDir}/scripts/metrics.py timer --name task_duration --seconds 12.5 --tags '{"task": "scan_skill"}'
```

### Increment a counter
```bash
python3 {baseDir}/scripts/metrics.py counter --name posts_published --increment 1
```

### Record an error
```bash
python3 {baseDir}/scripts/metrics.py error --name moltbook_verify_fail --message "Challenge solver returned wrong answer"
```

### View dashboard
```bash
python3 {baseDir}/scripts/metrics.py dashboard
```

### View metrics for today
```bash
python3 {baseDir}/scripts/metrics.py view --period day
```

### View specific metric history
```bash
python3 {baseDir}/scripts/metrics.py view --name api_calls --period week
```

### Export metrics
```bash
python3 {baseDir}/scripts/metrics.py export --format json > metrics.json
python3 {baseDir}/scripts/metrics.py export --format csv > metrics.csv
```

## Dashboard Output

The text-based dashboard shows:
- Uptime since first metric recorded
- Total events today
- Top metrics by count
- Error rate
- Average durations for timed operations
- Custom counter values

## Metric Types

- **counter** — Things you count (posts published, skills scanned, comments made)
- **timer** — Things you measure in seconds (API response time, task duration)
- **event** — Things that happened (errors, deployments, restarts)
- **gauge** — Current values (karma, budget remaining, queue depth)

## Storage

Metrics are stored in `~/.openclaw/metrics/` as daily JSON files. Lightweight, no database required.

## Integration

Works with the compliance audit trail — log metrics events alongside audit entries for full operational visibility.
