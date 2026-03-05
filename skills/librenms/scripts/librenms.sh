#!/bin/bash
# LibreNMS CLI wrapper for OpenClaw
# Read-only monitoring/infrastructure skill

set -euo pipefail

# Colors for status indicators
GREEN="●"
RED="●"
YELLOW="●"
BLUE="●"

# Load configuration
load_config() {
    # Environment variables take precedence
    if [[ -n "${LIBRENMS_URL:-}" && -n "${LIBRENMS_TOKEN:-}" ]]; then
        API_URL="$LIBRENMS_URL"
        API_TOKEN="$LIBRENMS_TOKEN"
        return 0
    fi
    
    # Fall back to config file
    local config_file="$HOME/.openclaw/credentials/librenms/config.json"
    if [[ ! -f "$config_file" ]]; then
        echo "ERROR: Config file not found at $config_file" >&2
        echo "Create the file with: {\"url\": \"https://librenms.example.com\", \"api_token\": \"your-token\"}" >&2
        echo "Or set LIBRENMS_URL and LIBRENMS_TOKEN environment variables" >&2
        return 1
    fi
    
    if ! command -v jq &>/dev/null; then
        echo "ERROR: jq is required but not installed" >&2
        return 1
    fi
    
    API_URL=$(jq -r '.url' "$config_file")
    API_TOKEN=$(jq -r '.api_token' "$config_file")
    
    if [[ "$API_URL" == "null" || "$API_TOKEN" == "null" ]]; then
        echo "ERROR: Invalid config file. Required keys: url, api_token" >&2
        return 1
    fi
    
    # Remove trailing slash from URL
    API_URL="${API_URL%/}"
}

# Make API call
api_call() {
    local endpoint="$1"
    local url="${API_URL}/api/v0${endpoint}"
    
    local response
    local http_code
    
    response=$(curl -sk -w "\n%{http_code}" \
        -H "X-Auth-Token: $API_TOKEN" \
        -H "Accept: application/json" \
        "$url" 2>&1) || {
        echo "ERROR: Failed to connect to LibreNMS API at $url" >&2
        return 1
    }
    
    http_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | sed '$d')
    
    if [[ "$http_code" != "200" ]]; then
        echo "ERROR: API returned HTTP $http_code" >&2
        echo "$body" | jq -r '.message // .error // "Unknown error"' 2>/dev/null || echo "$body" >&2
        return 1
    fi
    
    echo "$body"
}

# Format uptime
format_uptime() {
    local seconds="$1"
    if [[ -z "$seconds" || "$seconds" == "null" ]]; then
        echo "N/A"
        return
    fi
    
    local days=$((seconds / 86400))
    local hours=$(( (seconds % 86400) / 3600 ))
    local minutes=$(( (seconds % 3600) / 60 ))
    
    if [[ $days -gt 0 ]]; then
        echo "${days}d ${hours}h"
    elif [[ $hours -gt 0 ]]; then
        echo "${hours}h ${minutes}m"
    else
        echo "${minutes}m"
    fi
}

# Format bytes
format_bytes() {
    local bytes="$1"
    if [[ -z "$bytes" || "$bytes" == "null" ]]; then
        echo "N/A"
        return
    fi
    
    if [[ $bytes -gt 1099511627776 ]]; then
        echo "$(echo "scale=2; $bytes / 1099511627776" | bc)TB"
    elif [[ $bytes -gt 1073741824 ]]; then
        echo "$(echo "scale=2; $bytes / 1073741824" | bc)GB"
    elif [[ $bytes -gt 1048576 ]]; then
        echo "$(echo "scale=2; $bytes / 1048576" | bc)MB"
    elif [[ $bytes -gt 1024 ]]; then
        echo "$(echo "scale=2; $bytes / 1024" | bc)KB"
    else
        echo "${bytes}B"
    fi
}

# Command: summary
cmd_summary() {
    echo "=== LibreNMS Summary ==="
    echo
    
    local devices_data
    devices_data=$(api_call "/devices") || return 1
    
    local alerts_data
    alerts_data=$(api_call "/alerts?state=1") || return 1
    
    local total=$(echo "$devices_data" | jq -r '.count // (.devices | length)')
    local up=$(echo "$devices_data" | jq '[.devices[] | select(.status == "1" or .status == 1)] | length')
    local down=$(echo "$devices_data" | jq '[.devices[] | select(.status != "1" and .status != 1)] | length')
    local alerts=$(echo "$alerts_data" | jq -r '.count // (.alerts | length)')
    
    echo "Devices:"
    echo "  Total: $total"
    echo "  Up:    $up $GREEN"
    echo "  Down:  $down $RED"
    echo
    echo "Active Alerts: $alerts"
}

# Command: devices
cmd_devices() {
    local devices_data
    devices_data=$(api_call "/devices") || return 1
    
    echo "=== All Devices ==="
    echo
    printf "%-4s %-25s %-15s %-15s %-12s\n" "STS" "HOSTNAME" "IP" "OS" "UPTIME"
    printf "%-4s %-25s %-15s %-15s %-12s\n" "---" "--------" "--" "--" "------"
    
    echo "$devices_data" | jq -r '.devices[] | 
        [
            (if .status == "1" or .status == 1 then "UP" else "DOWN" end),
            .hostname,
            .ip // "N/A",
            (.os // "unknown"),
            (.uptime // "0")
        ] | @tsv' | while IFS=$'\t' read -r status hostname ip os uptime; do
        
        local status_icon
        if [[ "$status" == "UP" ]]; then
            status_icon="$GREEN"
        else
            status_icon="$RED"
        fi
        
        local uptime_fmt=$(format_uptime "$uptime")
        
        printf "%-4s %-25s %-15s %-15s %-12s\n" \
            "$status_icon" \
            "${hostname:0:25}" \
            "${ip:0:15}" \
            "${os:0:15}" \
            "$uptime_fmt"
    done
}

# Command: down
cmd_down() {
    local devices_data
    devices_data=$(api_call "/devices") || return 1
    
    echo "=== Devices Down ==="
    echo
    
    local down_devices
    down_devices=$(echo "$devices_data" | jq -r '[.devices[] | select(.status != "1" and .status != 1)]')
    
    local count=$(echo "$down_devices" | jq 'length')
    
    if [[ "$count" == "0" ]]; then
        echo "All devices are up! $GREEN"
        return 0
    fi
    
    printf "%-4s %-30s %-20s %-15s\n" "STS" "HOSTNAME" "IP" "LAST SEEN"
    printf "%-4s %-30s %-20s %-15s\n" "---" "--------" "--" "---------"
    
    echo "$down_devices" | jq -r '.[] | 
        [
            .hostname,
            .ip // "N/A",
            (.last_polled // "never")
        ] | @tsv' | while IFS=$'\t' read -r hostname ip last_seen; do
        
        printf "%-4s %-30s %-20s %-15s\n" \
            "$RED" \
            "${hostname:0:30}" \
            "${ip:0:20}" \
            "${last_seen:0:15}"
    done
}

# Command: device <hostname>
cmd_device() {
    local hostname="$1"
    
    local device_data
    device_data=$(api_call "/devices/$hostname") || return 1
    
    echo "=== Device: $hostname ==="
    echo
    
    echo "$device_data" | jq -r '.devices[0] | 
        "Status:       " + (if .status == "1" or .status == 1 then "UP ●" else "DOWN ●" end) + "\n" +
        "IP:           " + (.ip // "N/A") + "\n" +
        "Hardware:     " + (.hardware // "N/A") + "\n" +
        "OS:           " + (.os // "unknown") + " " + (.version // "") + "\n" +
        "Serial:       " + (.serial // "N/A") + "\n" +
        "Location:     " + (.location // "N/A") + "\n" +
        "Uptime:       " + (.uptime | tostring) + "s\n" +
        "Last Polled:  " + (.last_polled // "never") + "\n" +
        "Type:         " + (.type // "N/A") + "\n" +
        "Purpose:      " + (.purpose // "N/A")
    '
}

# Command: health <hostname>
cmd_health() {
    local hostname="$1"
    
    local health_data
    health_data=$(api_call "/devices/$hostname/health") || return 1
    
    echo "=== Health: $hostname ==="
    echo
    
    # Check if we have any health data
    local has_data
    has_data=$(echo "$health_data" | jq '
        (.sensors.temperature // []) + 
        (.sensors.processor // []) + 
        (.sensors.mempool // []) + 
        (.sensors.storage // []) | length')
    
    if [[ "$has_data" == "0" ]]; then
        echo "No health sensor data available for this device."
        return 0
    fi
    
    # Temperature sensors
    local temp_count
    temp_count=$(echo "$health_data" | jq '(.sensors.temperature // []) | length')
    if [[ "$temp_count" != "0" ]]; then
        echo "Temperature Sensors:"
        echo "$health_data" | jq -r '.sensors.temperature[] | 
            "  " + .sensor_descr + ": " + (.sensor_current | tostring) + "°C"'
        echo
    fi
    
    # Processor
    local proc_count
    proc_count=$(echo "$health_data" | jq '(.sensors.processor // []) | length')
    if [[ "$proc_count" != "0" ]]; then
        echo "Processor:"
        echo "$health_data" | jq -r '.sensors.processor[] | 
            "  " + .sensor_descr + ": " + (.sensor_current | tostring) + "%"'
        echo
    fi
    
    # Memory
    local mem_count
    mem_count=$(echo "$health_data" | jq '(.sensors.mempool // []) | length')
    if [[ "$mem_count" != "0" ]]; then
        echo "Memory:"
        echo "$health_data" | jq -r '.sensors.mempool[] | 
            "  " + .mempool_descr + ": " + (.mempool_perc | tostring) + "% used"'
        echo
    fi
    
    # Storage
    local stor_count
    stor_count=$(echo "$health_data" | jq '(.sensors.storage // []) | length')
    if [[ "$stor_count" != "0" ]]; then
        echo "Storage:"
        echo "$health_data" | jq -r '.sensors.storage[] | 
            "  " + .storage_descr + ": " + (.storage_perc | tostring) + "% used (" + 
            (.storage_used | tostring) + "/" + (.storage_size | tostring) + " bytes)"'
        echo
    fi
}

# Command: ports <hostname>
cmd_ports() {
    local hostname="$1"
    
    local ports_data
    ports_data=$(api_call "/devices/$hostname/ports") || return 1
    
    echo "=== Ports: $hostname ==="
    echo
    
    printf "%-20s %-10s %-12s %-12s %-12s\n" "INTERFACE" "STATUS" "SPEED" "IN" "OUT"
    printf "%-20s %-10s %-12s %-12s %-12s\n" "---------" "------" "-----" "--" "---"
    
    echo "$ports_data" | jq -r '.ports[] | 
        [
            .ifName // .ifDescr,
            (if .ifOperStatus == "up" then "UP" else "DOWN" end),
            (.ifSpeed // "0"),
            (.ifInOctets_rate // "0"),
            (.ifOutOctets_rate // "0")
        ] | @tsv' | while IFS=$'\t' read -r iface status speed in_rate out_rate; do
        
        local status_icon
        if [[ "$status" == "UP" ]]; then
            status_icon="$GREEN"
        else
            status_icon="$RED"
        fi
        
        # Format speed
        local speed_fmt
        if [[ "$speed" == "0" || "$speed" == "null" ]]; then
            speed_fmt="N/A"
        else
            speed_fmt=$(format_bytes "$speed")
        fi
        
        local in_fmt=$(format_bytes "$in_rate")
        local out_fmt=$(format_bytes "$out_rate")
        
        printf "%-20s %-10s %-12s %-12s %-12s\n" \
            "${iface:0:20}" \
            "$status_icon" \
            "$speed_fmt" \
            "$in_fmt/s" \
            "$out_fmt/s"
    done
}

# Command: alerts
cmd_alerts() {
    local alerts_data
    alerts_data=$(api_call "/alerts?state=1") || return 1
    
    echo "=== Active Alerts ==="
    echo
    
    local count
    count=$(echo "$alerts_data" | jq -r '.count // (.alerts | length)')
    
    if [[ "$count" == "0" ]]; then
        echo "No active alerts $GREEN"
        return 0
    fi
    
    echo "$alerts_data" | jq -r '.alerts[] | 
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" +
        "Device:    " + (.hostname // .device_id | tostring) + "\n" +
        "Rule:      " + (.rule // "N/A") + "\n" +
        "Severity:  " + (.severity // "unknown") + "\n" +
        "Timestamp: " + (.timestamp // "N/A") + "\n" +
        "State:     " + (.state | tostring)
    '
}

# Main command dispatcher
main() {
    if [[ $# -eq 0 ]]; then
        echo "Usage: librenms <command> [args]"
        echo
        echo "Commands:"
        echo "  summary              Dashboard overview (devices up/down, alerts)"
        echo "  devices              List all devices"
        echo "  down                 Show only devices that are down"
        echo "  device <hostname>    Detailed info for a device"
        echo "  health <hostname>    Health sensors (temp, CPU, memory, disk)"
        echo "  ports <hostname>     Network interfaces and traffic stats"
        echo "  alerts               List active/unresolved alerts"
        echo
        echo "Configuration:"
        echo "  File: ~/.openclaw/credentials/librenms/config.json"
        echo "  Env:  LIBRENMS_URL, LIBRENMS_TOKEN"
        return 1
    fi
    
    # Load config first
    load_config || return 1
    
    local command="$1"
    shift
    
    case "$command" in
        summary)
            cmd_summary "$@"
            ;;
        devices)
            cmd_devices "$@"
            ;;
        down)
            cmd_down "$@"
            ;;
        device)
            if [[ $# -eq 0 ]]; then
                echo "ERROR: device command requires a hostname" >&2
                return 1
            fi
            cmd_device "$@"
            ;;
        health)
            if [[ $# -eq 0 ]]; then
                echo "ERROR: health command requires a hostname" >&2
                return 1
            fi
            cmd_health "$@"
            ;;
        ports)
            if [[ $# -eq 0 ]]; then
                echo "ERROR: ports command requires a hostname" >&2
                return 1
            fi
            cmd_ports "$@"
            ;;
        alerts)
            cmd_alerts "$@"
            ;;
        *)
            echo "ERROR: Unknown command: $command" >&2
            echo "Run 'librenms' without arguments to see usage" >&2
            return 1
            ;;
    esac
}

main "$@"
