#!/bin/bash
# Healthcheck: disk, CPU, memory, services
# Defaults for thresholds
DISK_THRESHOLD=80
CPU_LOAD_THRESHOLD=3.0
MEMORY_THRESHOLD=90

echo "=== Disk Usage ==="
DISK_USAGE=$(df -h / | tail -1 | awk '{print $5}' | sed 's/%//')
echo "Used: ${DISK_USAGE}% / 468G"
if (( DISK_USAGE > DISK_THRESHOLD )); then
  echo "Status: ❌ CRITICAL (Disk usage exceeds ${DISK_THRESHOLD}%)"
else
  echo "Status: ✅ OK (Disk usage within limits)"
fi

echo ""
echo "=== CPU Load (1m) ==="
CPU_LOAD=$(uptime | awk -F'load average:' '{print $2}' | cut -d, -f1 | awk '{printf "%.2f\n", $1}')
echo "Load: ${CPU_LOAD}"
if (( $(echo "${CPU_LOAD} > ${CPU_LOAD_THRESHOLD}" | bc -l) )); then
  echo "Status: ❌ CRITICAL (CPU load exceeds ${CPU_LOAD_THRESHOLD})"
else
  echo "Status: ✅ OK (CPU load within limits)"
fi

echo ""
echo "=== Memory ==="
MEM_USED_PERCENT=$(free -h | awk '/^Mem:/ {printf "%.0f\n", $3/$2 * 100}')
echo "Used: ${MEM_USED_PERCENT}%"
if (( MEM_USED_PERCENT > MEMORY_THRESHOLD )); then
  echo "Status: ❌ CRITICAL (Memory usage exceeds ${MEMORY_THRESHOLD}%)"
else
  echo "Status: ✅ OK (Memory usage within limits)"
fi

echo ""
echo "=== Top 5 Processes by CPU ==="
ps aux --sort=-%cpu | head -6 | awk '{printf "%-10s %5s%% CPU  %5s%% MEM  %s\n", $1, $3, $4, $11}'
echo ""

echo "=== Key Services ==="
if pgrep -f "sshd" > /dev/null; then
  echo "sshd: ✅ running"
else
  echo "sshd: ❌ not running or not found"
fi

if pgrep -f "cron" > /dev/null; then
  echo "cron: ✅ running"
else
  echo "cron: ❌ not running or not found"
fi

if pgrep -f "openclaw-gateway" > /dev/null; then
  echo "openclaw: ✅ running"
else
  echo "openclaw: ❌ not running or not found"
fi
