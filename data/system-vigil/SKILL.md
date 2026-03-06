---
name: system-vigil
description: Monitor host system health (Disk, RAM, CPU). Returns structured JSON status for predictive maintenance.
metadata:
  openclaw:
    emoji: "🛡️"
    requires:
      bins:
        - df
        - free
        - uptime
---

# System Vigil

A health monitor for the host machine. It checks vital signs and returns a structured report, allowing agents to detect resource exhaustion before it causes a crash.

## Capabilities

- **Check Health:** Get a JSON report of Disk, Memory, and CPU usage.
- **Predictive Status:** Returns specific flags (`warning`, `critical`) based on thresholds.

## Usage

**User:** "Run a system health check."
**Agent:** `python3 skills/system-vigil/check.py`
**Output:**
```json
{
  "status": "ok",
  "disk": { "used_percent": 45, "free_gb": 120 },
  "memory": { "used_percent": 30, "free_gb": 12 },
  "cpu": { "load_15m": 0.5 }
}
```

## Implementation

A Python script parsing standard Linux utils (`df`, `free`, `uptime`).
