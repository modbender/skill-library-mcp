#!/bin/bash
#===============================================================================
# BABY Brain - System Administration Script
#===============================================================================
# Description: System diagnostics, health checks, and maintenance
# Author: Baby
# Version: 1.0.0
#===============================================================================

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

ICON_SUCCESS="✅"
ICON_ERROR="❌"
ICON_INFO="ℹ️"
ICON_WARNING="⚠️"
ICON_HEALTH="🏥"
ICON_FIX="🔧"
ICON_MONITOR="📊"

#-------------------------------------------------------------------------------
# Configuration
#-------------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="${HOME}/.baby-brain"
LOG_DIR="${CONFIG_DIR}/logs/system"
mkdir -p "${LOG_DIR}"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "${LOG_DIR}/system.log"
}

#-------------------------------------------------------------------------------
# Help
#-------------------------------------------------------------------------------
show_help() {
    cat << EOF
${CYAN}BABY Brain - System Administration${NC}

${YELLOW}USAGE:${NC}
    $(basename "$0") [COMMAND] [OPTIONS]

${YELLOW}COMMANDS:${NC}
    ${ICON_HEALTH} health         Quick health check
    ${ICON_HEALTH} diag           Full diagnostic
    ${ICON_FIX} fix              Auto-fix issues
    ${ICON_FIX} repair           Repair OpenClaw
    ${ICON_MONITOR} monitor      Real-time monitoring
    ${ICON_HEALTH} status        System status
    ${ICON_MONITOR} cpu          CPU monitoring
    ${ICON_MONITOR} memory       Memory monitoring
    ${ICON_MONITOR} disk         Disk monitoring
    ${ICON_MONITOR} network      Network diagnostics
    ${ICON_FIX} clean           Cleanup temporary files
    ${ICON_FIX} backup          Create backup
    ${ICON_FIX} update          Update system/skills
    ${ICON_INFO} info           System information
    ${ICON_INFO} logs           View logs

${YELLOW}OPTIONS:${NC}
    -h, --help            Show help
    -a, --alert           Alert threshold
    -o, --output          Output file
    --format              Format (text, json)
    --verbose             Verbose output

${YELLOW}EXAMPLES:${NC}
    $(basename "$0") health
    $(basename "$0") diag --verbose
    $(basename "$0") fix
    $(basename "$0") monitor --alert 80
    $(basename "$0") cpu --alert 90

EOF
}

#-------------------------------------------------------------------------------
# Health Check
#-------------------------------------------------------------------------------
cmd_health() {
    echo -e "${CYAN}${ICON_HEALTH} BABY Brain Health Check${NC}"
    echo ""

    # OpenClaw gateway
    echo -e "${YELLOW}[1/6] OpenClaw Gateway:${NC}"
    if curl -s http://localhost:18789/health > /dev/null 2>&1; then
        echo -e "${GREEN}${ICON_SUCCESS} Gateway is healthy${NC}"
    else
        echo -e "${RED}${ICON_ERROR} Gateway not responding${NC}"
    fi

    # CPU
    echo -e "${YELLOW}[2/6] CPU Usage:${NC}"
    local cpu=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    echo -e "${GREEN}CPU: ${cpu}%${NC}"

    # Memory
    echo -e "${YELLOW}[3/6] Memory Usage:${NC}"
    free -h | grep "^Mem:" | awk '{print "Used: " $3 "/" $2}'

    # Disk
    echo -e "${YELLOW}[4/6] Disk Usage:${NC}"
    df -h / | awk 'NR==2 {print "Disk: " $5 " used (" $3 "/" $2 ")"}'

    # Services
    echo -e "${YELLOW}[5/6] Key Services:${NC}"
    systemctl --user is-active --quiet openclaw-gateway && echo -e "${GREEN}OpenClaw: Running${NC}" || echo -e "${RED}OpenClaw: Stopped${NC}"

    # Network
    echo -e "${YELLOW}[6/6] Network:${NC}"
    curl -s --connect-timeout 2 https://api.ipify.org > /dev/null && echo -e "${GREEN}Internet: Connected${NC}" || echo -e "${RED}Internet: Disconnected${NC}"
}

#-------------------------------------------------------------------------------
# Full Diagnostic
#-------------------------------------------------------------------------------
cmd_diag() {
    local verbose=false
    local output=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --verbose|-v) verbose=true; shift ;;
            -o|--output) output="$2"; shift 2 ;;
            *) shift ;;
        esac
    done

    echo -e "${CYAN}${ICON_HEALTH} Full System Diagnostic${NC}"
    echo ""

    local timestamp=$(date +%Y%m%d_%H%M%S)
    [[ -z "$output" ]] && output="${LOG_DIR}/diag_${timestamp}.txt"

    {
        echo "=== BABY Brain Diagnostic Report ==="
        echo "Generated: $(date)"
        echo ""

        echo "## System Information"
        uname -a
        echo ""

        echo "## OpenClaw Status"
        openclaw status 2>/dev/null || echo "OpenClaw command failed"
        echo ""

        echo "## Gateway Health"
        curl -s http://localhost:18789/health || echo "Gateway not responding"
        echo ""

        echo "## Services"
        systemctl --user status openclaw-gateway --no-pager 2>/dev/null | head -20 || echo "systemctl failed"
        echo ""

        echo "## Ports"
        ss -tlnp 2>/dev/null | head -20 || netstat -tlnp 2>/dev/null | head -20 || echo "Port check failed"
        echo ""

        echo "## Recent Logs"
        tail -50 "${LOG_DIR}/system.log" 2>/dev/null || echo "No logs"
        echo ""

        echo "## Disk"
        df -h
        echo ""

        echo "## Memory"
        free -h
        echo ""

        echo "## End of Report"
    } > "$output"

    echo -e "${GREEN}${ICON_SUCCESS} Diagnostic complete${NC}"
    echo "Report saved to: $output"

    if $verbose; then
        cat "$output"
    fi
}

#-------------------------------------------------------------------------------
# Auto-Fix
#-------------------------------------------------------------------------------
cmd_fix() {
    echo -e "${CYAN}${ICON_FIX} Auto-Fix Mode${NC}"
    echo ""

    local fixed=0

    # Check and fix gateway
    echo -e "${YELLOW}[1/4] Checking OpenClaw Gateway...${NC}"
    if ! curl -s http://localhost:18789/health > /dev/null 2>&1; then
        echo "Attempting to restart gateway..."
        openclaw gateway restart 2>/dev/null && {
            echo -e "${GREEN}${ICON_SUCCESS} Gateway restarted${NC}"
            ((fixed++))
        } || echo -e "${RED}${ICON_ERROR} Failed to restart gateway${NC}"
    else
        echo -e "${GREEN}${ICON_SUCCESS} Gateway already running${NC}"
    fi
    ((fixed++))

    # Check disk space
    echo -e "${YELLOW}[2/4] Checking disk space...${NC}"
    local disk_usage=$(df / | awk 'NR==2 {gsub(/%/,""); print $5}')
    if [[ $disk_usage -gt 85 ]]; then
        echo "Disk usage high (${disk_usage}%). Cleaning..."
        bash "${SCRIPT_DIR}/automation.sh" clean --no-logs 2>/dev/null && ((fixed++))
    else
        echo -e "${GREEN}Disk usage OK: ${disk_usage}%${NC}"
    fi
    ((fixed++))

    # Check memory
    echo -e "${YELLOW}[3/4] Checking memory...${NC}"
    local mem_usage=$(free | awk '/^Mem/{printf("%.0f", $3/$2*100)}')
    if [[ $mem_usage -gt 90 ]]; then
        echo "Memory usage high (${mem_usage}%)."
        sync && echo 3 > /proc/sys/vm/drop_caches 2>/dev/null && {
            echo -e "${GREEN}${ICON_SUCCESS} Cache cleared${NC}"
            ((fixed++))
        }
    else
        echo -e "${GREEN}Memory usage OK: ${mem_usage}%${NC}"
    fi
    ((fixed++))

    # Check services
    echo -e "${YELLOW}[4/4] Verifying services...${NC}"
    systemctl --user is-active --quiet openclaw-gateway && {
        echo -e "${GREEN}${ICON_SUCCESS} OpenClaw running${NC}"
        ((fixed++))
    } || {
        echo -e "${RED}${ICON_ERROR} OpenClaw not running${NC}"
    }

    echo ""
    echo -e "${GREEN}${ICON_SUCCESS} Fix complete: $fixed/4 checks passed${NC}"
}

#-------------------------------------------------------------------------------
# Repair OpenClaw
#-------------------------------------------------------------------------------
cmd_repair() {
    echo -e "${CYAN}${ICON_FIX} OpenClaw Repair Mode${NC}"
    echo ""

    echo -e "${YELLOW}[1/3] Diagnosing issues...${NC}"
    openclaw doctor --non-interactive 2>&1 | head -50

    echo ""
    echo -e "${YELLOW}[2/3] Attempting fixes...${NC}"
    openclaw doctor --fix 2>&1 | head -50

    echo ""
    echo -e "${YELLOW}[3/3] Verifying repair...${NC}"
    openclaw status 2>&1 | head -20

    echo -e "${GREEN}${ICON_SUCCESS} Repair attempt complete${NC}"
}

#-------------------------------------------------------------------------------
# Monitoring
#-------------------------------------------------------------------------------
cmd_monitor() {
    local alert_cpu=80
    local alert_mem=90
    local alert_disk=85
    local duration=60

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --cpu) alert_cpu="$2"; shift 2 ;;
            --memory) alert_mem="$2"; shift 2 ;;
            --disk) alert_disk="$2"; shift 2 ;;
            -d|--duration) duration="$2"; shift 2 ;;
            *) shift ;;
        esac
    done

    echo -e "${CYAN}${ICON_MONITOR} System Monitoring (${duration}s)${NC}"
    echo "Alert thresholds - CPU: ${alert_cpu}%, Memory: ${alert_mem}%, Disk: ${alert_disk}%"
    echo ""

    local end_time=$((SECONDS + duration))
    local iteration=1

    while [[ $SECONDS -lt $end_time ]]; do
        echo -e "${YELLOW}[$(date '+%H:%M:%S')] Iteration $iteration${NC}"

        # CPU
        local cpu=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
        if (( $(echo "$cpu > $alert_cpu" | bc -l) )); then
            echo -e "${RED}${ICON_WARNING} CPU HIGH: ${cpu}%${NC}"
        else
            echo -e "${GREEN}CPU: ${cpu}%${NC}"
        fi

        # Memory
        local mem=$(free | awk '/^Mem/{printf("%.0f", $3/$2*100)}')
        if [[ $mem -gt $alert_mem ]]; then
            echo -e "${RED}${ICON_WARNING} Memory HIGH: ${mem}%${NC}"
        else
            echo -e "${GREEN}Memory: ${mem}%${NC}"
        fi

        # Disk
        local disk=$(df / | awk 'NR==2 {gsub(/%/,""); print $5}')
        if [[ $disk -gt $alert_disk ]]; then
            echo -e "${RED}${ICON_WARNING} Disk HIGH: ${disk}%${NC}"
        else
            echo -e "${GREEN}Disk: ${disk}%${NC}"
        fi

        sleep 5
        ((iteration++))
    done

    echo -e "${GREEN}${ICON_SUCCESS} Monitoring complete${NC}"
}

#-------------------------------------------------------------------------------
# CPU Monitor
#-------------------------------------------------------------------------------
cmd_cpu() {
    local alert=80

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -a|--alert) alert="$2"; shift 2 ;;
            *) shift ;;
        esac
    done

    echo -e "${CYAN}${ICON_MONITOR} CPU Monitor (alert at ${alert}%)${NC}"

    while true; do
        local cpu=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
        printf "[%s] CPU: %s%%\r" "$(date '+%H:%M:%S')" "$cpu"

        if (( $(echo "$cpu > $alert" | bc -l) )); then
            echo ""
            echo -e "${RED}${ICON_WARNING} CPU HIGH: ${cpu}%${NC}"
        fi

        sleep 2
    done
}

#-------------------------------------------------------------------------------
# Memory Monitor
#-------------------------------------------------------------------------------
cmd_memory() {
    local alert=90

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -a|--alert) alert="$2"; shift 2 ;;
            *) shift ;;
        esac
    done

    echo -e "${CYAN}${ICON_MONITOR} Memory Monitor (alert at ${alert}%)${NC}"

    while true; do
        local mem=$(free | awk '/^Mem/{printf("%.0f", $3/$2*100)}')
        printf "[%s] Memory: %s%%\r" "$(date '+%H:%M:%S')" "$mem"

        if [[ $mem -gt $alert ]]; then
            echo ""
            echo -e "${RED}${ICON_WARNING} Memory HIGH: ${mem}%${NC}"
        fi

        sleep 2
    done
}

#-------------------------------------------------------------------------------
# Disk Monitor
#-------------------------------------------------------------------------------
cmd_disk() {
    local alert=85

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -a|--alert) alert="$2"; shift 2 ;;
            *) shift ;;
        esac
    done

    echo -e "${CYAN}${ICON_MONITOR} Disk Monitor (alert at ${alert}%)${NC}"

    local disk=$(df / | awk 'NR==2 {gsub(/%/,""); print $5}')
    echo -e "Current disk usage: ${disk}%${NC}"

    while true; do
        local current=$(df / | awk 'NR==2 {gsub(/%/,""); print $5}')
        printf "[%s] Disk: %s%%\r" "$(date '+%H:%M:%S')" "$current"

        if [[ $current -gt $alert ]]; then
            echo ""
            echo -e "${RED}${ICON_WARNING} Disk HIGH: ${current}%${NC}"
        fi

        sleep 10
    done
}

#-------------------------------------------------------------------------------
# Network Diagnostics
#-------------------------------------------------------------------------------
cmd_network() {
    echo -e "${CYAN}${ICON_MONITOR} Network Diagnostics${NC}"
    echo ""

    echo -e "${YELLOW}[1/5] Interface status:${NC}"
    ip link show 2>/dev/null | head -20 || ifconfig 2>/dev/null | head -20 || echo "Failed"

    echo ""
    echo -e "${YELLOW}[2/5] Routing table:${NC}"
    ip route 2>/dev/null | head -10 || route -n 2>/dev/null | head -10 || echo "Failed"

    echo ""
    echo -e "${YELLOW}[3/5] DNS resolution:${NC}"
    nslookup google.com 2>/dev/null | head -10 || echo "DNS check failed"

    echo ""
    echo -e "${YELLOW}[4/5] Connectivity tests:${NC}"
    curl -s --connect-timeout 2 -o /dev/null -w "Google: %{http_code}\n" https://google.com 2>/dev/null || echo "Google: FAILED"
    curl -s --connect-timeout 2 -o /dev/null -w "OpenAI: %{http_code}\n" https://api.openai.com 2>/dev/null || echo "OpenAI: FAILED"

    echo ""
    echo -e "${YELLOW}[5/5] Open ports:${NC}"
    ss -tlnp 2>/dev/null | head -20 || netstat -tlnp 2>/dev/null | head -20 || echo "Failed"
}

#-------------------------------------------------------------------------------
# Cleanup
#-------------------------------------------------------------------------------
cmd_clean() {
    local temp=true
    local logs=true
    local cache=true

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --no-temp) temp=false; shift ;;
            --no-logs) logs=false; shift ;;
            --no-cache) cache=false; shift ;;
            *) shift ;;
        esac
    done

    echo -e "${CYAN}${ICON_FIX} System Cleanup${NC}"
    echo ""

    local freed=0

    $temp && {
        local temp_size=$(du -sm /tmp 2>/dev/null | cut -f1 || echo 0)
        rm -rf /tmp/* 2>/dev/null || true
        echo -e "Cleaned /tmp: ${temp_size}MB freed"
        ((freed+=temp_size))
    }

    $logs && {
        local log_size=$(find "${LOG_DIR}" -name "*.log" -mtime +7 -exec ls -sm {} \; 2>/dev/null | awk '{sum+=$1} END {print sum+0}' || echo 0)
        find "${LOG_DIR}" -name "*.log" -mtime +7 -delete 2>/dev/null || true
        echo -e "Cleaned old logs: ${log_size}MB freed"
        ((freed+=log_size))
    }

    $cache && {
        local cache_size=$(du -sm "${HOME}/.cache" 2>/dev/null | cut -f1 || echo 0)
        rm -rf "${HOME}/.cache"/* 2>/dev/null || true
        echo -e "Cleaned cache: ${cache_size}MB freed"
        ((freed+=cache_size))
    }

    echo ""
    echo -e "${GREEN}${ICON_SUCCESS} Total freed: ${freed}MB${NC}"
}

#-------------------------------------------------------------------------------
# Backup
#-------------------------------------------------------------------------------
cmd_backup() {
    local source="${HOME}/.baby-brain"
    local destination="${HOME}/.baby-brain/backups/$(date +%Y%m%d_%H%M%S)"

    echo -e "${CYAN}${ICON_FIX} Creating Backup${NC}"
    echo "Source: $source"
    echo "Destination: $destination"

    mkdir -p "$(dirname "$destination")"
    mkdir -p "$destination"

    # Backup config
    cp -r "${source}"/* "$destination/" 2>/dev/null || true

    # Compress
    local archive="${HOME}/.baby-brain/backups/backup_$(date +%Y%m%d_%H%M%S).tar.gz"
    tar -czf "$archive" -C "$(dirname "$source")" "$(basename "$source")" 2>/dev/null || true

    echo -e "${GREEN}${ICON_SUCCESS} Backup created: $archive${NC}"
}

#-------------------------------------------------------------------------------
# Update
#-------------------------------------------------------------------------------
cmd_update() {
    echo -e "${CYAN}${ICON_FIX} System Update${NC}"
    echo ""

    echo -e "${YELLOW}[1/2] Checking OpenClaw updates...${NC}"
    openclaw update status 2>&1 | head -20

    echo ""
    echo -e "${YELLOW}[2/2] Updating ClawHub skills...${NC}"
    clawhub update --all 2>&1 | head -20 || echo "ClawHub update failed"

    echo -e "${GREEN}${ICON_SUCCESS} Update check complete${NC}"
}

#-------------------------------------------------------------------------------
# System Info
#-------------------------------------------------------------------------------
cmd_info() {
    echo -e "${CYAN}${ICON_INFO} System Information${NC}"
    echo ""

    echo "## Host"
    hostname
    uname -a
    echo ""

    echo "## Uptime"
    uptime -p 2>/dev/null || uptime
    echo ""

    echo "## Memory"
    free -h
    echo ""

    echo "## Disk"
    df -h
    echo ""

    echo "## CPU"
    lscpu 2>/dev/null | head -10 || cat /proc/cpuinfo | head -10
}

#-------------------------------------------------------------------------------
# View Logs
#-------------------------------------------------------------------------------
cmd_logs() {
    local lines=50
    local file="${LOG_DIR}/system.log"

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -n|--lines) lines="$2"; shift 2 ;;
            -f|--file) file="$2"; shift 2 ;;
            *) shift ;;
        esac
    done

    echo -e "${CYAN}${ICON_INFO} System Logs${NC}"
    echo ""

    if [[ -f "$file" ]]; then
        tail -n "$lines" "$file"
    else
        echo "Log file not found: $file"
    fi
}

#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------
main() {
    local command="${1:-}"

    if [[ "$command" == "--help" || "$command" == "-h" ]]; then
        show_help
        exit 0
    fi

    if [[ -z "$command" ]]; then
        show_help
        exit 0
    fi

    shift

    case "$command" in
        health|check) cmd_health ;;
        diag|diagnostic) cmd_diag "$@" ;;
        fix|repair) cmd_fix ;;
        repair) cmd_repair ;;
        monitor|monitoring) cmd_monitor "$@" ;;
        cpu) cmd_cpu "$@" ;;
        memory|ram) cmd_memory "$@" ;;
        disk|storage) cmd_disk "$@" ;;
        network|network-check) cmd_network ;;
        clean|cleanup) cmd_clean "$@" ;;
        backup) cmd_backup ;;
        update) cmd_update ;;
        info|information) cmd_info ;;
        logs|logview) cmd_logs "$@" ;;
        status) cmd_health ;;
        *) echo -e "${RED}Unknown command: $command${NC}"; show_help; exit 1 ;;
    esac
}

main "$@"
