---
name: skill-health-monitor
description: Monitor deployed skills for performance drift, errors, and unexpected behavior changes. Continuous post-deployment health checks with alerting and trend tracking.
user-invocable: true
metadata: {"openclaw": {"emoji": "📊", "os": ["darwin", "linux"], "requires": {"bins": ["python3"]}}}
---

# Skill Health Monitor

Catch skill degradation before it becomes a crisis. Monitors response times, error rates, output drift, and resource usage for deployed skills.

## Why This Exists

Skills work fine during testing, then silently degrade in production. Free models change behavior, APIs add latency, memory leaks accumulate. By the time you notice, your agent has been running on broken skills for hours.

## Commands

### Monitor a skill execution
```bash
python3 {baseDir}/scripts/health_monitor.py check --skill <name> --cmd "python3 path/to/script.py"
```

### View health dashboard
```bash
python3 {baseDir}/scripts/health_monitor.py dashboard
```

### Set alert thresholds
```bash
python3 {baseDir}/scripts/health_monitor.py threshold --skill <name> --max-latency 5000 --max-errors 3
```

### Export health report
```bash
python3 {baseDir}/scripts/health_monitor.py report --json
```

### View trends for a skill
```bash
python3 {baseDir}/scripts/health_monitor.py trend --skill <name> --period 24h
```

## What It Tracks

- **Latency**: Execution time per invocation, p50/p95/p99 percentiles
- **Error rate**: Failed executions, error types, frequency
- **Output drift**: Detects when output format or content changes unexpectedly
- **Resource usage**: Memory and CPU at execution time
- **Uptime**: Availability over time windows (1h, 24h, 7d)

## Alerting

- Console alerts when thresholds are exceeded
- JSON webhook support for external integrations
- Configurable per-skill thresholds

## Data Storage

Health data is stored in `~/.openclaw/health/` as JSON files. One file per skill, rotated daily.
