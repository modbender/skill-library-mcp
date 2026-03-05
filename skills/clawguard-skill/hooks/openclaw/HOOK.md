---
event: gateway:startup
name: clawwall-autostart
description: Auto-starts the ClawWall DLP service when the OpenClaw gateway boots.
---

# ClawWall Auto-Start Hook

This hook runs on `gateway:startup` and ensures the ClawWall DLP service is running
before any agent tool calls are processed.

## Behavior

1. Checks if `clawwall` binary is available on PATH
2. Checks if port 8642 is already in use (skips if service already running)
3. Spawns `clawwall` as a detached background process
4. Writes PID to `~/.config/clawwall/clawwall.pid`
5. Waits for health endpoint to respond before returning
