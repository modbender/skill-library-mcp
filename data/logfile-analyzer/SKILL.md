---
name: logfile-analyzer
description: Parse and analyze application logs — extract error patterns,
  frequency, timelines, and actionable insights.
---


# Log Analyzer

Parse and summarize application logs to find errors, patterns, and anomalies.

**Use when** analyzing log files, debugging errors, or summarizing system events.

## Requirements

- Standard Unix tools: `grep`, `awk`, `sort`, `uniq`
- Optional: `jq` (for JSON logs)
- No API keys needed

## Instructions

1. **Get log source** — common locations:
   ```bash
   # System logs
   /var/log/syslog
   /var/log/auth.log
   journalctl -u <service> --since "1 hour ago" --no-pager

   # Web servers
   /var/log/nginx/error.log
   /var/log/nginx/access.log

   # Docker
   docker logs --since 1h <container> 2>&1

   # Application logs
   # Ask user for path
   ```

2. **Quick analysis** — run these in sequence:
   ```bash
   # File overview
   wc -l logfile
   head -1 logfile && tail -1 logfile   # time range

   # Error counts by level
   grep -ciE '(error|fatal|critical)' logfile
   grep -ciE '(warn|warning)' logfile

   # Top error patterns (deduplicated)
   grep -iE '(error|exception|fatal)' logfile | \
     sed 's/[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}[T ][0-9:.]*//g' | \
     sed 's/\[.*\]//g' | sort | uniq -c | sort -rn | head -20

   # Error timeline (per hour)
   grep -iE '(error|fatal)' logfile | \
     grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}[T ][0-9]{2}' | \
     sort | uniq -c

   # Recent errors with context
   grep -iE '(error|exception|fatal)' logfile | tail -30
   ```

3. **JSON logs** (structured logging):
   ```bash
   cat logfile | jq -r 'select(.level == "error") | .message' | sort | uniq -c | sort -rn
   cat logfile | jq -r 'select(.level == "error") | .timestamp' | head -5  # first errors
   ```

4. **Output format**:
   ```
   📊 Log Analysis — filename.log (42,531 lines)
   Time range: 2025-01-15 00:00 → 2025-01-15 14:30

   ## Summary
   | Level | Count | % |
   |-------|-------|---|
   | ERROR | 67 | 0.16% |
   | WARN | 234 | 0.55% |
   | INFO | 42,230 | 99.3% |

   ## Top Errors
   | Count | Error Pattern |
   |-------|--------------|
   | 42 | Connection refused to db:5432 |
   | 18 | TimeoutError: request exceeded 30s |
   | 7 | OutOfMemoryError: heap space |

   ## Error Timeline
   | Hour | Errors | |
   |------|--------|-|
   | 14:00 | 3 | ▪ |
   | 15:00 | 47 | ▪▪▪▪▪▪▪▪▪▪▪▪▪ ⚠️ Spike |
   | 16:00 | 5 | ▪▪ |

   ## 🔍 Recommendations
   - [ ] Check database connectivity (42 connection refused errors)
   - [ ] Review timeout settings (18 timeouts at 30s)
   - [ ] Increase JVM heap size (7 OOM errors)
   ```

## Edge Cases

- **Large files (>100MB)**: Use `tail -n 10000` or `--since` filtering first. Never read entire file into memory.
- **Non-standard log format**: Ask user about the timestamp and level format, then adapt grep patterns.
- **Binary/compressed logs**: `zgrep` for `.gz` files, `journalctl` for systemd binary logs.
- **Multi-line stack traces**: Use `grep -A 5` to capture context lines after errors.
- **No timestamps**: Fall back to line-number-based analysis.

## Real-time Monitoring

For live monitoring, suggest:
```bash
tail -f logfile | grep --line-buffered -iE '(error|fatal)'
```

## Security Considerations

- Log files may contain sensitive data (IPs, emails, tokens). Redact before sharing analysis.
- Don't pipe log contents to external services.
