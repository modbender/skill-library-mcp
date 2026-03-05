---
description: "Use when the user wants to analyze, parse, or summarize application logs. Extracts error patterns, frequency counts, and actionable insights from log files."
---

# Log Analyzer

Parse and summarize application logs to find errors, patterns, and anomalies.

## What This Does

Analyzes log files to provide:
- Error/warning frequency and distribution
- Top error messages (grouped by pattern)
- Timeline of issues
- Actionable summary

## Instructions

1. **Get the log source**: Ask for log file path, or accept piped input. Common locations:
   - `/var/log/syslog`, `/var/log/nginx/error.log`
   - Application logs, Docker logs (`docker logs <container>`)
   - `journalctl -u <service> --since "1 hour ago"`

2. **Quick analysis commands**:

### Error summary
```bash
# Count errors by level
grep -cE '(ERROR|FATAL|CRITICAL)' logfile
grep -cE '(WARN|WARNING)' logfile

# Top 10 error messages (deduplicated)
grep -iE '(error|exception|fatal)' logfile | \
  sed 's/[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}[T ][0-9:.]*//g' | \
  sed 's/\[.*\]//g' | \
  sort | uniq -c | sort -rn | head -20
```

### Timeline
```bash
# Errors per hour
grep -iE '(error|fatal)' logfile | \
  grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}[T ][0-9]{2}' | \
  sort | uniq -c
```

### Recent errors
```bash
# Last 50 errors with context
grep -iE '(error|exception|fatal)' logfile | tail -50
```

3. **Structured output format**:
```
📊 Log Analysis — <filename> (<line_count> lines)

## Summary
- Total lines: X
- Errors: X | Warnings: X | Info: X
- Time range: <start> → <end>

## Top Errors
| Count | Error Pattern |
|-------|--------------|
| 42    | Connection refused to db:5432 |
| 18    | TimeoutError: request exceeded 30s |

## Error Timeline
| Hour | Errors | Notes |
|------|--------|-------|
| 14:00 | 3 | Normal |
| 15:00 | 47 | ⚠️ Spike |

## Recommendations
- [ ] Check database connectivity (42 connection refused errors)
- [ ] Review timeout settings (18 timeout errors)
```

4. **For large files** (>100MB): Use `tail -n 10000` or time-based filtering first. Don't read the entire file into memory.

5. **JSON logs** (structured logging): Use `jq` for parsing:
   ```bash
   cat logfile | jq -r 'select(.level == "error") | .message' | sort | uniq -c | sort -rn
   ```

## Notes
- No API keys required — uses grep, awk, sort, uniq, jq
- Works with any text-based log format
- For real-time monitoring, suggest `tail -f logfile | grep -i error`
