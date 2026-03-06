#!/bin/bash

# Enhanced System Monitor for OpenClaw
# Provides CPU, RAM, Disk usage, Temperature, and Top Processes

get_cpu() {
    top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1"%"}'
}

get_ram() {
    free -h | awk '/^Mem:/ {print $3 "/" $2 " (" $7 " available)"}'
}

get_disk() {
    df -h / | awk 'NR==2 {print $3 "/" $2 " (" $5 " used)"}'
}

get_temp() {
    if command -v sensors > /dev/null && sensors 2>/dev/null | grep -E "Package id 0|Core 0|temp1" > /dev/null; then
        sensors | grep -E "Package id 0|Core 0|temp1" | head -1 | awk '{print $3}'
    elif [ -f /sys/class/thermal/thermal_zone0/temp ]; then
        awk '{printf "%.1f°C\n", $1/1000}' /sys/class/thermal/thermal_zone0/temp
    else
        echo "N/A (Virtual Server)"
    fi
}

get_top_cpu() {
    ps -eo pcpu,comm --sort=-pcpu | head -6 | tail -5 | awk '{print $2 " (" $1 "%)"}'
}

get_top_mem() {
    ps -eo pmem,comm --sort=-pmem | head -6 | tail -5 | awk '{print $2 " (" $1 "%)"}'
}

case "$1" in
    cpu) get_cpu ;;
    ram) get_ram ;;
    disk) get_disk ;;
    temp) get_temp ;;
    top)
        echo "Top CPU Processes:"
        get_top_cpu
        echo ""
        echo "Top Memory Processes:"
        get_top_mem
        ;;
    all|*)
        echo "--- 🖥️  System Overview ---"
        echo "CPU Usage: $(get_cpu)"
        echo "RAM Used:  $(get_ram)"
        echo "Disk (/):  $(get_disk)"
        echo "Temp:      $(get_temp)"
        echo ""
        echo "--- 📈 Load Average ---"
        uptime | awk -F'load average:' '{ print $2 }'
        echo ""
        echo "--- 🔥 Top Processes (CPU) ---"
        get_top_cpu
        ;;
esac
