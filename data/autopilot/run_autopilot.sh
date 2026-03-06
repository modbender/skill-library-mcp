#!/bin/bash
# Autopilot launcher — 启动 watchdog 守护进程
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
exec /bin/bash ~/.autopilot/scripts/watchdog.sh
