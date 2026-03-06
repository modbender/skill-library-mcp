---
name: local-system-info
description: Return system metrics (CPU, RAM, disk, processes) using psutil.
metadata:
  {
    "openclaw":
      {
        "emoji": "🖥️",
        "requires": { "bins": ["python3"], "pip": ["psutil"] },
        "install":
          [
            {
              "id": "psutil",
              "kind": "pip",
              "package": "psutil",
              "label": "Install psutil",
            },
          ],
        "version": "1.1.0",
      },
  }
---

# Local System Info Skill

Monitor local system resources including CPU, memory, disk usage, and running processes.

## Tool API

### system_info
Retrieve system metrics.

- **Parameters:**
  - `action` (string, required): One of `summary`, `cpu`, `memory`, `disk`, `processes`.
  - `limit` (integer, optional): Number of processes to list (default: 20). Only used with `action=processes`.

**Usage:**

```bash
# Get full system summary
uv run --with psutil skills/local-system-info/sysinfo.py summary

# CPU metrics only
uv run --with psutil skills/local-system-info/sysinfo.py cpu

# Memory metrics only
uv run --with psutil skills/local-system-info/sysinfo.py memory

# Disk usage
uv run --with psutil skills/local-system-info/sysinfo.py disk

# List top processes by CPU usage
uv run --with psutil skills/local-system-info/sysinfo.py processes --limit 10
```

## Output Format

### summary
```json
{
  "cpu": {
    "cpu_percent": 15.2,
    "cpu_count": 8,
    "load_avg": [0.5, 0.3, 0.2]
  },
  "memory": {
    "total": 17179869184,
    "available": 8589934592,
    "percent": 50.0,
    "swap_percent": 5.2
  },
  "disk": {
    "total": 500000000000,
    "used": 250000000000,
    "free": 250000000000,
    "percent": 50.0
  }
}
```

### processes
```json
[
  {
    "pid": 1234,
    "name": "python3",
    "username": "user",
    "cpu_percent": 5.2,
    "memory_percent": 2.1
  },
  ...
]
```

## Metrics Explained

- **cpu_percent:** Current CPU utilization (0-100%)
- **cpu_count:** Number of logical CPU cores
- **load_avg:** System load average (1, 5, 15 min) normalized by CPU count
- **memory.total/available:** RAM in bytes
- **memory.percent:** RAM usage percentage
- **disk.percent:** Root filesystem usage percentage
- **processes:** Top N processes sorted by CPU usage

## Requirements

- **psutil:** Cross-platform system monitoring library
- **Python 3.6+:** For f-string support and typing

## Platform Support

Works on Linux, macOS, Windows, and WSL. Some metrics may vary by platform:
- `load_avg`: Not available on Windows
- Process information depth varies by OS
