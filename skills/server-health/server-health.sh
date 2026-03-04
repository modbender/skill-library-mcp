#!/bin/bash

# Server Health Check Script
# Displays system stats, processes, OpenClaw status, and services

set -euo pipefail

MODE="${1:-standard}"  # standard, verbose, json, alerts

# ============================================================================
# Helper Functions
# ============================================================================

get_bar() {
    local percent=$1
    local width=10
    local filled=$((percent * width / 100))
    local empty=$((width - filled))
    
    printf "█%.0s" $(seq 1 $filled)
    printf "░%.0s" $(seq 1 $empty)
}

get_cpu_usage() {
    top -bn1 | grep "Cpu(s)" | awk '{print int($2+0.5)}'
}

get_load_average() {
    uptime | awk -F'load average:' '{print $2}' | sed 's/^ //' | cut -d',' -f1-3 | sed 's/,//g'
}

get_ram_usage() {
    free -g | awk '/^Mem:/ {printf "%.1f %.1f %d", $3, $2, int($3/$2*100)}'
}

get_disk_usage() {
    df -h / | awk 'NR==2 {print $3, $2, int($3/$2*100)}'
}

get_uptime() {
    uptime -p | sed 's/up //'
}

get_top_processes() {
    ps aux --sort=-%cpu | awk 'NR>1 {printf "%-12s %3d%%   %5dMB\n", $11, int($3), int($6/1024)}' | head -3
}

get_openclaw_pid() {
    pgrep -f "openclaw.*gateway" | head -1 || echo ""
}

get_openclaw_uptime() {
    local pid=$1
    if [[ -n "$pid" ]]; then
        ps -p "$pid" -o etime= | xargs
    else
        echo "N/A"
    fi
}

get_openclaw_version() {
    # Get version from package.json instead of CLI (CLI can hang)
    if [[ -f /usr/lib/node_modules/openclaw/package.json ]]; then
        jq -r '.version // "unknown"' /usr/lib/node_modules/openclaw/package.json 2>/dev/null
    else
        echo "unknown"
    fi
}

get_openclaw_config() {
    if [[ -f /root/.openclaw/openclaw.json ]]; then
        local port=$(jq -r '.gateway.port // 18789' /root/.openclaw/openclaw.json 2>/dev/null)
        local model=$(jq -r '.agents.defaults.model.primary // "unknown"' /root/.openclaw/openclaw.json 2>/dev/null)
        local fallbacks=$(jq -r '.agents.defaults.model.fallbacks // [] | map(split("/")[1] // .) | join(" → ")' /root/.openclaw/openclaw.json 2>/dev/null)
        echo "${port} ${model} ${fallbacks}"
    else
        echo "18789 unknown "
    fi
}

get_session_info() {
    # Try to get from openclaw status
    local status_output=$(openclaw status 2>/dev/null || echo "")
    
    if [[ -n "$status_output" ]]; then
        # Extract session count
        local sessions=$(echo "$status_output" | grep -oP 'sessions \K\d+' | head -1 || echo "0")
        
        # Extract heartbeat
        local heartbeat=$(echo "$status_output" | grep -oP 'Heartbeat.*?\K\d+m' | head -1 || echo "N/A")
        
        # Extract last activity
        local last=$(echo "$status_output" | grep -oP 'updated \K.*? ago' | head -1 || echo "unknown")
        
        echo "$sessions $heartbeat $last"
    else
        echo "0 N/A unknown"
    fi
}

get_model_usage() {
    # Get from session status - parse the output
    local status=$(openclaw status 2>/dev/null || echo "")
    
    # Try to extract context and tokens
    local context=$(echo "$status" | grep -oP 'Context:.*?\K\d+k/\d+k \(\d+%\)' | head -1 || echo "N/A")
    local tokens=$(echo "$status" | grep -oP 'Tokens:.*?\K\d+ in / \d+ out' | head -1 || echo "N/A")
    
    echo "$context|$tokens"
}

check_service() {
    local service=$1
    if systemctl is-active --quiet "$service" 2>/dev/null; then
        echo "✅"
    elif pgrep -x "$service" >/dev/null 2>&1; then
        echo "✅"
    else
        echo "❌"
    fi
}

get_docker_containers() {
    if command -v docker &>/dev/null; then
        docker ps -q 2>/dev/null | wc -l
    else
        echo "0"
    fi
}

# ============================================================================
# Output Functions
# ============================================================================

output_standard() {
    echo "🖥️ SERVER HEALTH"
    echo "━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # SYSTEM
    echo "💻 SYSTEM"
    local cpu=$(get_cpu_usage)
    local load=$(get_load_average)
    read -r ram_used ram_total ram_percent <<< $(get_ram_usage)
    read -r disk_used disk_total disk_percent <<< $(get_disk_usage)
    local uptime=$(get_uptime)
    
    echo "CPU: $(get_bar $cpu) ${cpu}% (Load: ${load})"
    echo "RAM: $(get_bar $ram_percent) ${ram_used}GB/${ram_total}GB (${ram_percent}%)"
    echo "DISK: $(get_bar $disk_percent) ${disk_used}/${disk_total} (${disk_percent}%)"
    echo "UP: ⏱️ ${uptime}"
    echo ""
    
    # TOP PROCESSES
    echo "🔄 TOP PROCESSES"
    get_top_processes
    echo ""
    
    # OPENCLAW GATEWAY
    echo "⚡ OPENCLAW GATEWAY"
    local pid=$(get_openclaw_pid)
    if [[ -n "$pid" ]]; then
        local uptime=$(get_openclaw_uptime "$pid")
        local version=$(get_openclaw_version)
        local port model fallbacks
        read -r port model fallbacks <<< "$(get_openclaw_config)"
        
        echo "Status: ✅ Running (PID: ${pid})"
        echo "Uptime: ${uptime} | Port: ${port} | v${version}"
        echo ""
        
        echo "🤖 MODEL CONFIG"
        echo "Primary: ${model}"
        
        # Get usage info - skip if hangs
        local usage="N/A|N/A"
        local context tokens
        IFS='|' read -r context tokens <<< "$usage"
        if [[ "$context" != "N/A" ]]; then
            echo "Context: ${context} | ${tokens}"
        fi
        
        if [[ -n "$fallbacks" && "$fallbacks" != " " ]]; then
            echo "Fallbacks: ${fallbacks}"
        fi
        echo ""
        
        echo "📊 SESSIONS"
        # Simplified - just count session files
        local sessions=$(ls /root/.openclaw/agents/main/sessions/*.json 2>/dev/null | wc -l || echo "0")
        echo "Active: ${sessions}"
    else
        echo "Status: ❌ Not running"
    fi
    echo ""
    
    # SERVICES
    echo "🐳 SERVICES"
    local docker_count=$(get_docker_containers)
    if [[ "$docker_count" -gt 0 ]]; then
        echo "Docker: ✅ ${docker_count} containers"
    else
        echo "Docker: ❌ Not running"
    fi
    
    if systemctl is-active --quiet postgresql 2>/dev/null; then
        echo "PostgreSQL: ✅ Running"
    else
        echo "PostgreSQL: ❌ Not running"
    fi
}

output_json() {
    local cpu=$(get_cpu_usage)
    local load=$(get_load_average)
    read -r ram_used ram_total ram_percent <<< $(get_ram_usage)
    read -r disk_used disk_total disk_percent <<< $(get_disk_usage)
    local uptime=$(get_uptime)
    local pid=$(get_openclaw_pid)
    
    cat <<EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "system": {
    "cpu": {"usage": $cpu, "load": "$load"},
    "ram": {"used": $ram_used, "total": $ram_total, "percent": $ram_percent},
    "disk": {"used": "$disk_used", "total": "$disk_total", "percent": $disk_percent},
    "uptime": "$uptime"
  },
  "openclaw": {
    "running": $(if [[ -n "$pid" ]]; then echo "true"; else echo "false"; fi),
    "pid": $(if [[ -n "$pid" ]]; then echo "$pid"; else echo "null"; fi)
  }
}
EOF
}

output_alerts() {
    local alerts=0
    
    # Check disk
    read -r disk_used disk_total disk_percent <<< $(get_disk_usage)
    if [[ $disk_percent -gt 90 ]]; then
        echo "🔴 DISK CRITICAL: ${disk_percent}% used (>${disk_used}/${disk_total})"
        alerts=$((alerts + 1))
    elif [[ $disk_percent -gt 80 ]]; then
        echo "🟡 DISK WARNING: ${disk_percent}% used (${disk_used}/${disk_total})"
        alerts=$((alerts + 1))
    fi
    
    # Check RAM
    read -r ram_used ram_total ram_percent <<< $(get_ram_usage)
    if [[ $ram_percent -gt 90 ]]; then
        echo "🔴 RAM CRITICAL: ${ram_percent}% used (${ram_used}GB/${ram_total}GB)"
        alerts=$((alerts + 1))
    elif [[ $ram_percent -gt 80 ]]; then
        echo "🟡 RAM WARNING: ${ram_percent}% used (${ram_used}GB/${ram_total}GB)"
        alerts=$((alerts + 1))
    fi
    
    # Check CPU
    local cpu=$(get_cpu_usage)
    if [[ $cpu -gt 90 ]]; then
        echo "🟡 CPU HIGH: ${cpu}%"
        alerts=$((alerts + 1))
    fi
    
    # Check OpenClaw
    local pid=$(get_openclaw_pid)
    if [[ -z "$pid" ]]; then
        echo "🔴 OPENCLAW DOWN: Gateway not running"
        alerts=$((alerts + 1))
    fi
    
    if [[ $alerts -eq 0 ]]; then
        echo "✅ All systems healthy"
    fi
}

# ============================================================================
# Main
# ============================================================================

case "$MODE" in
    --json)
        output_json
        ;;
    --alerts)
        output_alerts
        ;;
    --verbose)
        output_standard
        # TODO: Add verbose extras (temp, network, I/O)
        ;;
    *)
        output_standard
        ;;
esac
