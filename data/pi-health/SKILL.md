---
name: pi-health
description: Raspberry Pi health monitor. Check CPU temperature, throttling status, voltage levels, memory/disk usage, fan RPM, overclock detection, and power issues. Use when monitoring Pi health, diagnosing thermal throttling, checking for under-voltage, or verifying system stability on any Raspberry Pi (Pi 3/4/5, arm64/armhf).
---

# Pi Health

Run the health check script:

```bash
bash scripts/health.sh
```

## What It Checks

| Check | Source | Warning | Critical |
|-------|--------|---------|----------|
| CPU Temperature | thermal_zone0 | >70°C | >80°C |
| Throttling | vcgencmd get_throttled | any flag set | under-voltage |
| Voltages | vcgencmd measure_volts | — | — |
| Memory | free -m | >75% | >90% |
| Disk | df / | >75% | >90% |
| CPU Frequency | cpufreq sysfs | — | — |
| Load Average | /proc/loadavg | >nCPU | >2×nCPU |
| Fan | hwmon sysfs | — | — |
| Overclock | config.txt | detected | — |
| Power | dmesg | — | under-voltage |

## Exit Codes

- `0` — Healthy (all checks passed)
- `1` — Warnings (non-critical issues)
- `2` — Critical (needs immediate attention)

## Requirements

- Raspberry Pi OS (Bookworm or later)
- `vcgencmd` (optional but recommended — comes with `libraspberrypi-bin`)
- `bc` (standard on Pi OS)
- No external dependencies or API keys
