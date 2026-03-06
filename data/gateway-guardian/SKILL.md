---
name: Gateway Guardian
description: Watchdog daemon that monitors and auto-restarts OpenClaw gateway.
---

# Gateway Guardian

Watchdog daemon that monitors and auto-restarts OpenClaw gateway.

## Usage

```bash
./guardian.sh
```

Run as background daemon:
```bash
nohup ./guardian.sh &
```

## Features

- Monitors gateway process health
- Auto-restarts on crash
- Configurable check interval
- Logs restart events
- Works on macOS and Linux

## Configuration

Edit guardian.sh to customize:
- CHECK_INTERVAL: seconds between checks (default: 30)
- MAX_RESTARTS: max restarts before alerting (default: 5)
- LOG_FILE: where to log events

## Requirements

- OpenClaw installed
- Bash shell
