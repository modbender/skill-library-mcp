---
name: auto-watchdog
description: "Automatic health monitoring and self-healing for OpenClaw agents. Monitors cron jobs, processes, disk usage, and API health. Auto-restarts crashed services and alerts on issues. Set it and forget it."
version: 1.0.0
---

# Auto-Watchdog 🐕

Your OpenClaw setup runs 24/7. But what watches the watchers?

Auto-Watchdog monitors everything and fixes what it can — silently. You only hear about real problems.

## Features

### 1. Cron Health Monitor
Checks all cron jobs every heartbeat:
- `consecutiveErrors > 0` → immediate alert
- Job not running when expected → alert
- Disabled jobs piling up → cleanup recommendation

### 2. Process Guardian
Monitors critical processes by log freshness (not just PID):
- Log file not updated in X minutes → kill + restart
- Works with any Node.js process
- Configurable per-process thresholds

### 3. Disk Monitor
- Log files growing too large → auto-rotate
- Workspace size alerts
- Temp file cleanup

### 4. Gateway Health
- Checks `openclaw gateway status` every heartbeat
- Auto-restart if down (via Task Scheduler or systemd)

### 5. Silent by Default
- Everything OK → no output (HEARTBEAT_OK)
- Issue found → targeted alert to your chat
- No spam. No unnecessary reports.

## Setup

### Add to HEARTBEAT.md:

```markdown
## 🔍 Health Check (silent = good)

### Crons
- `cron list` → check consecutiveErrors > 0 → alert
- Frequent crons not running >2 hours → alert

### Processes
- Check [your process] log freshness < [X] minutes
- If stale → restart and alert

### Gateway
- `openclaw gateway status` → alert if down

### Disk
- Check log sizes > 10MB → rotate
- Check workspace size > 1GB → alert
```

### For Windows (Task Scheduler Guardian):

Create a VBS wrapper for zero-flash execution:

```vbs
' guardian-silent.vbs — zero flash process monitor
Set oShell = CreateObject("WScript.Shell")
oShell.Run "powershell.exe -NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File ""C:\path\to\guardian.ps1""", 0, True
```

Register as Task Scheduler job running every 1-5 minutes.

### For Linux (systemd):

```bash
# /etc/systemd/system/openclaw-watchdog.service
[Service]
ExecStart=/usr/bin/node /path/to/guardian.js
Restart=always
RestartSec=60
```

## Philosophy

> Monitor by **output freshness**, not PID.
> A process can be "alive" but stuck. Check its log timestamp.

> **Fix first, alert second.**
> If you can restart it automatically, do it. Only alert for things that need human intervention.

> **Silent = healthy.**
> No news is good news. Only speak up when something breaks.

## Production-Tested

Built for a 24/7 autonomous trading system with:
- 5 competing AI agents
- 20+ cron jobs
- Strategy researcher running 23h/day
- Zero downtime over weeks of operation
