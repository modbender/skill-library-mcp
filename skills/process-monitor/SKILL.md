---
name: process-monitor
description: Monitor system processes, identify top CPU/memory consumers, and
  alert on resource thresholds.
---


# Process Monitor

Monitor system processes and resource usage with threshold-based alerts.

## Requirements

- Standard Unix tools: `ps`, `top`, `free`, `uptime` (pre-installed on Linux)
- No API keys needed

## Instructions

1. **Resource summary** — Run and format results:
   ```bash
   uptime                          # Load average
   free -h                         # Memory/swap usage
   nproc                           # CPU count
   df -h / /home 2>/dev/null       # Key disk partitions
   ```

2. **Top processes** — By CPU or memory:
   ```bash
   ps aux --sort=-%mem | head -15  # Top memory consumers
   ps aux --sort=-%cpu | head -15  # Top CPU consumers
   ```

3. **Search processes** — Find by name or PID:
   ```bash
   ps aux | grep -i "[n]ode"      # By name (brackets avoid matching grep itself)
   ps -p 1234 -o pid,user,%cpu,%mem,cmd  # By PID
   ```

4. **Threshold alerts** — Flag processes exceeding limits:
   - Single process CPU > 80% → ⚠️ Warning
   - Single process memory > 50% → ⚠️ Warning
   - System memory > 90% → 🔴 Critical
   - Load average > 2× CPU count → 🔴 Critical

5. **Output format**:
   ```
   ## 📊 Process Report — <hostname> (<timestamp>)

   | Metric        | Value          | Status |
   |---------------|----------------|--------|
   | Load Average  | 1.2 / 0.8 / 0.5 | 🟢   |
   | Memory        | 12.3/16.0 GB (77%) | 🟢 |
   | Swap          | 0.0/4.0 GB    | 🟢     |

   ### Top 5 by Memory
   | PID   | User  | %MEM | %CPU | Command        |
   |-------|-------|------|------|----------------|
   | 1234  | root  | 12.3 | 2.1  | /usr/bin/java  |
   ```

## Edge Cases

- **Zombie processes**: Check with `ps aux | awk '$8 ~ /Z/'` — report count and parent PID.
- **No `top` available**: Fall back to `/proc/loadavg` and `/proc/meminfo`.
- **Docker/container**: `ps` may show host processes. Use `--pid=host` awareness.

## Security

- Read-only commands only — never kill processes without explicit user confirmation.
- Sanitize process names in output (may contain sensitive paths or arguments).
