#!/bin/bash
# Health Check — quick system vitals for heartbeat cycles
# Usage: bash health-check.sh
# Output: JSON summary

set -euo pipefail

echo "{"

# Disk usage
DISK_USED=$(df -h / | awk 'NR==2 {print $5}' | tr -d '%')
DISK_AVAIL=$(df -h / | awk 'NR==2 {print $4}')
echo "  \"disk\": {\"usedPercent\": $DISK_USED, \"available\": \"$DISK_AVAIL\"},"

# Memory
if [[ "$(uname)" == "Darwin" ]]; then
    # macOS
    MEM_TOTAL=$(/usr/sbin/sysctl -n hw.memsize | awk '{printf "%.0f", $1/1073741824}')
    MEM_PRESSURE=$(/usr/bin/memory_pressure 2>/dev/null | grep "System-wide" | head -1 | grep -o '[0-9]*%' || echo "unknown")
    VM_STATS=$(/usr/bin/vm_stat | head -10)
    FREE_PAGES=$(echo "$VM_STATS" | grep "Pages free" | awk '{print $3}' | tr -d '.')
    INACTIVE_PAGES=$(echo "$VM_STATS" | grep "Pages inactive" | awk '{print $3}' | tr -d '.')
    FREE_GB=$(echo "$FREE_PAGES $INACTIVE_PAGES" | awk '{printf "%.1f", ($1 + $2) * 16384 / 1073741824}')
    echo "  \"memory\": {\"totalGB\": $MEM_TOTAL, \"freeGB\": \"$FREE_GB\", \"pressure\": \"$MEM_PRESSURE\"},"
else
    # Linux
    MEM_INFO=$(free -g | awk 'NR==2 {printf "{\"totalGB\": %d, \"freeGB\": %d, \"usedGB\": %d}", $2, $7, $3}')
    echo "  \"memory\": $MEM_INFO,"
fi

# CPU load
LOAD=$(uptime | awk -F'load averages?: ' '{print $2}' | awk -F', ' '{printf "%.2f", $1}')
CPU_COUNT=$(/usr/sbin/sysctl -n hw.ncpu 2>/dev/null || nproc 2>/dev/null || echo 1)
echo "  \"cpu\": {\"load1m\": $LOAD, \"cores\": $CPU_COUNT},"

# Ollama status
if curl -s --max-time 2 http://localhost:11434/api/tags > /dev/null 2>&1; then
    MODEL_COUNT=$(curl -s http://localhost:11434/api/tags | python3 -c "import sys,json; print(len(json.load(sys.stdin).get('models',[])))" 2>/dev/null || echo 0)
    LOADED=$(curl -s http://localhost:11434/api/ps | python3 -c "import sys,json; models=json.load(sys.stdin).get('models',[]); print(models[0]['name'] if models else 'none')" 2>/dev/null || echo "unknown")
    echo "  \"ollama\": {\"running\": true, \"models\": $MODEL_COUNT, \"loaded\": \"$LOADED\"},"
else
    echo "  \"ollama\": {\"running\": false},"
fi

# The Reef status
if curl -s --max-time 2 http://localhost:3030/api/health > /dev/null 2>&1; then
    REEF_HEALTH=$(curl -s http://localhost:3030/api/health)
    echo "  \"reef\": {\"running\": true, \"health\": $REEF_HEALTH},"
else
    echo "  \"reef\": {\"running\": false},"
fi

# Git status
cd "$HOME/.openclaw/workspace" 2>/dev/null
DIRTY=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
BRANCH=$(git branch --show-current 2>/dev/null || echo "none")
echo "  \"git\": {\"branch\": \"$BRANCH\", \"uncommitted\": $DIRTY},"

# Uptime
UP=$(uptime | awk -F'up ' '{print $2}' | awk -F',' '{print $1}')
echo "  \"uptime\": \"$UP\","

# Stale processes
BG_COUNT=$(ps aux | grep -c "[n]ode\|[p]ython3\|[o]llama" || echo 0)
echo "  \"backgroundProcesses\": $BG_COUNT,"

# Timestamp
echo "  \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\""

echo "}"
