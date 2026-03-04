---
description: Monitor system processes and report CPU/memory usage, top consumers, and resource alerts.
---

# Process Monitor

Monitor system processes and resource usage.

## Capabilities

- **Top Processes**: Show processes by CPU or memory usage
- **Process Search**: Find specific processes by name or PID
- **Resource Summary**: Overall CPU, memory, swap, load average
- **Alerts**: Identify processes exceeding thresholds

## Usage

Ask the agent to:
- "Show top 10 processes by memory usage"
- "Is there anything using more than 80% CPU?"
- "Find all node processes"
- "Give me a system resource summary"

## How It Works

Uses standard system tools:

```bash
ps aux --sort=-%mem | head -20
top -bn1 | head -20
free -h
uptime
```

## Requirements

- Standard Unix tools (`ps`, `top`, `free`, `uptime`)
- No API keys needed
