#!/bin/bash
# System Health Monitor - Main Script
# Version: 1.1.1
# Author: ZLMbot 🦞
# SHA256 Hash: (auto-generated on install)

set -euo pipefail

# Configuration - use $HOME instead of hardcoded path
WORKSPACE_DIR="${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}"
SKILL_DIR="$WORKSPACE_DIR/skills/system-health-monitor"
CONFIG_FILE="$SKILL_DIR/config/health-monitor.json"
LOG_FILE="$WORKSPACE_DIR/logs/health-monitor-$(date +%Y%m%d).log"
STATE_FILE="$SKILL_DIR/data/system-state.json"
HASH_FILE="$SKILL_DIR/scripts/.script_hashes"

# Script version for integrity checking
SCRIPT_VERSION="1.1.1"
SCRIPT_HASH="${SCRIPT_HASH:-}"  # Set during installation

# Default configuration
ALERT_THRESHOLD=80
NOTIFY_ON_CRITICAL=true
TELEGRAM_CHANNEL_ID=""

# Verify script integrity
check_integrity() {
    if [[ -f "$HASH_FILE" ]] && [[ -n "$SCRIPT_HASH" ]]; then
        local current_hash=$(sha256sum "$0" | awk '{print $1}')
        if [[ "$current_hash" != "$SCRIPT_HASH" ]]; then
            echo "⚠️  Warning: Script hash mismatch. Expected: $SCRIPT_HASH, Got: $current_hash" >&2
            echo "   This may indicate the script has been modified." >&2
        fi
    fi
}

# Generate script hash for logging
log_script_hash() {
    local hash=$(sha256sum "$0" | awk '{print $1}')
    echo "[Script Hash: SHA256:$hash]" >> "$LOG_FILE"
}

# Load configuration if exists
load_config() {
    if [[ -f "$CONFIG_FILE" ]]; then
        echo "[INFO] Loading configuration from $CONFIG_FILE"
        ALERT_THRESHOLD=$(jq -r '.alert_threshold // 80' "$CONFIG_FILE")
        NOTIFY_ON_CRITICAL=$(jq -r '.notify_on_critical // true' "$CONFIG_FILE")
        TELEGRAM_CHANNEL_ID=$(jq -r '.telegram_channel_id // ""' "$CONFIG_FILE")
    else
        echo "[INFO] Using default configuration"
    fi
}

# Log function
log() {
    local level="$1"
    local message="$2"
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

# Check monitoring service status
check_service() {
    local service_name="$1"
    local service_type="$2"  # service or timer
    
    # Try system-level first (for root services), then user-level
    if [[ "$service_type" == "timer" ]]; then
        if systemctl is-active "$service_name" >/dev/null 2>&1; then
            echo "✅ $service_name (timer: active - system)"
            return 0
        elif systemctl --user is-active "$service_name" >/dev/null 2>&1; then
            echo "✅ $service_name (timer: active - user)"
            return 0
        else
            echo "❌ $service_name (timer: inactive)"
            return 1
        fi
    else
        # For services, check if they are loaded and enabled
        if systemctl is-enabled "$service_name" >/dev/null 2>&1; then
            echo "✅ $service_name (service: enabled - system)"
            return 0
        elif systemctl --user is-enabled "$service_name" >/dev/null 2>&1; then
            echo "✅ $service_name (service: enabled - user)"
            return 0
        else
            echo "❌ $service_name (service: not enabled)"
            return 1
        fi
    fi
}

# Check specific monitoring layer (8-layer system)
check_layer() {
    local layer_num="$1"
    
    case $layer_num in
        1)
            echo "=== Layer 1: SSH Login Monitor ==="
            check_service "ssh-login-monitor.service" "service"
            ;;
        2)
            echo "=== Layer 2: Heartbeat Monitor ==="
            check_service "heartbeat-monitor.timer" "timer"
            check_service "heartbeat-monitor.service" "service"
            ;;
        3)
            echo "=== Layer 3: Outbound Traffic Monitor ==="
            check_service "outbound-traffic-monitor.service" "service"
            ;;
        4)
            echo "=== Layer 4: UFW Firewall ==="
            if command -v ufw >/dev/null 2>&1; then
                if ufw status | grep -q "Status: active"; then
                    echo "✅ UFW Firewall (active)"
                    return 0
                else
                    echo "❌ UFW Firewall (inactive)"
                    return 1
                fi
            else
                echo "⚠️  UFW not installed, checking iptables..."
                if systemctl is-active iptables >/dev/null 2>&1 || systemctl is-active firewalld >/dev/null 2>&1; then
                    echo "✅ Alternative firewall active (iptables/firewalld)"
                    return 0
                else
                    echo "⚠️  No firewall detected (UFW not installed)"
                    return 0
                fi
            fi
            ;;
        5)
            echo "=== Layer 5: Package Integrity Monitor ==="
            check_service "package-integrity-monitor.timer" "timer"
            check_service "package-integrity-monitor.service" "service"
            ;;
        6)
            echo "=== Layer 6: Report Monitor ==="
            check_service "report-monitor.timer" "timer"
            check_service "report-monitor.service" "service"
            ;;
        7)
            echo "=== Layer 7: Cleanup Monitor ==="
            check_service "cleanup-monitor.timer" "timer"
            check_service "cleanup-monitor.service" "service"
            ;;
        8)
            echo "=== Layer 8: Internal Security Monitor ==="
            check_service "internal-security.timer" "timer"
            check_service "internal-security-critical.timer" "timer"
            ;;
        *)
            echo "❌ Invalid layer number: $layer_num (valid: 1-8)"
            return 1
            ;;
    esac
}

# Calculate health score (8-layer system)
calculate_health_score() {
    local total_layers=8
    local healthy_layers=0
    
    for layer in {1..8}; do
        if check_layer "$layer" >/dev/null 2>&1; then
            ((healthy_layers++))
        fi
    done
    
    local score=$(( (healthy_layers * 100) / total_layers ))
    echo "$score"
}

# Get system status summary
get_status_summary() {
    echo "=== System Health Status ==="
    echo "Timestamp: $(date)"
    echo "Script Version: $SCRIPT_VERSION"
    echo ""
    
    # Check OpenClaw Gateway
    echo "OpenClaw Gateway:"
    if command -v openclaw >/dev/null 2>&1; then
        if openclaw gateway status 2>/dev/null | grep -q "running"; then
            echo "✅ Running"
        else
            echo "❌ Not running"
        fi
    else
        echo "⚠️  openclaw command not found"
    fi
    
    echo ""
    echo "Monitoring Layers Status:"
    
    local score=$(calculate_health_score)
    echo "Health Score: $score/100"
    
    if [[ $score -ge 90 ]]; then
        echo "Status: 🟢 Excellent"
    elif [[ $score -ge 70 ]]; then
        echo "Status: 🟡 Good"
    elif [[ $score -ge 50 ]]; then
        echo "Status: 🟠 Fair"
    else
        echo "Status: 🔴 Poor"
    fi
}

# Generate detailed report
generate_report() {
    echo "=== System Health Report ==="
    echo "Generated: $(date)"
    echo "System: $(hostname)"
    echo "Uptime: $(uptime -p 2>/dev/null || uptime)"
    echo "Script Version: $SCRIPT_VERSION"
    echo ""
    
    get_status_summary
    
    echo ""
    echo "=== Detailed Layer Status (8-Layer System) ==="
    for layer in {1..8}; do
        echo ""
        check_layer "$layer"
    done
    
    echo ""
    echo "=== Security Status ==="
    echo "fail2ban Status:"
    if systemctl is-active fail2ban >/dev/null 2>&1; then
        echo "✅ Active"
        # Try to get banned IP count without sudo
        local banned_count=0
        if fail2ban-client status sshd >/dev/null 2>&1; then
            banned_count=$(fail2ban-client status sshd 2>/dev/null | grep "Currently banned" | awk '{print $4}' || echo 0)
        fi
        echo "Currently banned IPs: $banned_count"
    else
        echo "❌ Inactive"
    fi
    
    echo ""
    echo "SSH Security:"
    local ssh_config="/etc/ssh/sshd_config"
    if [[ -r "$ssh_config" ]]; then
        if grep -q "Port 2222" "$ssh_config" 2>/dev/null; then
            echo "✅ SSH Port: 2222 (hardened)"
        else
            echo "⚠️  SSH Port: default (consider hardening)"
        fi
        
        if grep -q "PasswordAuthentication no" "$ssh_config" 2>/dev/null; then
            echo "✅ Password auth: disabled"
        else
            echo "⚠️  Password auth: enabled"
        fi
        
        if grep -q "PermitRootLogin no" "$ssh_config" 2>/dev/null; then
            echo "✅ Root login: disabled"
        else
            echo "⚠️  Root login: enabled"
        fi
    else
        echo "⚠️  Cannot read SSH config (permission denied)"
    fi
    
    echo ""
    echo "=== Resource Usage ==="
    echo "CPU: $(top -bn1 2>/dev/null | grep "Cpu(s)" | awk '{print $2}' || echo "N/A")"
    echo "Memory: $(free -h 2>/dev/null | awk '/^Mem:/ {print $3 "/" $2}' || echo "N/A")"
    echo "Disk: $(df -h / 2>/dev/null | awk 'NR==2 {print $3 "/" $2 " (" $5 ")"}' || echo "N/A")"
}

# Check security status
check_security() {
    echo "=== Security Status Report ==="
    echo "Generated: $(date)"
    echo ""
    
    # UFW status
    echo "Firewall (UFW):"
    if command -v ufw >/dev/null 2>&1; then
        ufw status 2>/dev/null | head -5 || echo "Cannot check UFW status"
    else
        echo "UFW not installed"
    fi
    
    echo ""
    # fail2ban status
    echo "Intrusion Prevention (fail2ban):"
    if systemctl is-active fail2ban >/dev/null 2>&1; then
        echo "✅ Active"
        fail2ban-client status sshd 2>/dev/null | grep -E "(Status|Currently banned|Total banned)" || echo "Cannot get fail2ban details"
    else
        echo "❌ Inactive"
    fi
    
    echo ""
    # SSH security
    echo "SSH Security Configuration:"
    local ssh_config="/etc/ssh/sshd_config"
    if [[ -r "$ssh_config" ]]; then
        grep -E "^(Port|PasswordAuthentication|PermitRootLogin|ChallengeResponseAuthentication)" "$ssh_config" 2>/dev/null | grep -v "^#" || echo "No SSH hardening config found"
    else
        echo "⚠️  Cannot read SSH config (permission denied)"
    fi
    
    echo ""
    # Recent security alerts
    echo "Recent Security Alerts:"
    local sec_log="$WORKSPACE_DIR/logs/security/outbound-connections.log"
    if [[ -r "$sec_log" ]]; then
        tail -5 "$sec_log" 2>/dev/null | sed 's/^/  /' || echo "No recent alerts"
    else
        echo "No security alert logs found"
    fi
}

# Main function
main() {
    # Check integrity on startup
    check_integrity
    
    load_config
    
    # Ensure log directory exists
    mkdir -p "$(dirname "$LOG_FILE")"
    
    local action="${1:-status}"
    
    case "$action" in
        status)
            log "INFO" "Checking system health status"
            log_script_hash
            get_status_summary
            ;;
        
        report)
            log "INFO" "Generating detailed system report"
            log_script_hash
            generate_report
            ;;
        
        layer)
            if [[ -z "${2:-}" ]]; then
                echo "Usage: $0 layer <layer_number>"
                echo "Available layers: 1-8"
                exit 1
            fi
            log "INFO" "Checking monitoring layer $2"
            log_script_hash
            check_layer "$2"
            ;;
        
        security)
            log "INFO" "Checking security status"
            log_script_hash
            check_security
            ;;
        
        logs)
            local log_type="${2:---all}"
            log "INFO" "Viewing logs: $log_type"
            log_script_hash
            
            case "$log_type" in
                --alerts)
                    echo "=== Recent Security Alerts ==="
                    find "$WORKSPACE_DIR/logs/security/" -name "*.log" -type f -readable 2>/dev/null | \
                        xargs tail -n 20 2>/dev/null || echo "No security logs found"
                    ;;
                --monitor)
                    echo "=== Monitoring Logs ==="
                    journalctl --user -u config-monitor -u heartbeat-monitor -n 20 --no-pager 2>/dev/null || echo "Cannot access journalctl"
                    ;;
                --all)
                    echo "=== All Recent Logs ==="
                    find "$WORKSPACE_DIR/logs/" -name "*.log" -type f -readable 2>/dev/null | \
                        xargs tail -n 10 2>/dev/null | head -50 || echo "No logs found"
                    ;;
                *)
                    echo "Unknown log type: $log_type"
                    echo "Available: --alerts, --monitor, --all"
                    ;;
            esac
            ;;
        
        hash)
            # Display script hash for integrity verification
            echo "Script: $0"
            echo "Version: $SCRIPT_VERSION"
            echo "SHA256: $(sha256sum "$0" | awk '{print $1}')"
            echo ""
            echo "To set hash for integrity checking:"
            echo "export SCRIPT_HASH=$(sha256sum "$0" | awk '{print $1}')"
            ;;
        
        help|--help|-h)
            echo "System Health Monitor v$SCRIPT_VERSION"
            echo "Usage: $0 <command>"
            echo ""
            echo "Commands:"
            echo "  status      - Get current health status"
            echo "  report      - Generate detailed system report"
            echo "  layer <N>   - Check specific monitoring layer (1-8)"
            echo "  security    - Get security status report"
            echo "  logs [type] - View monitoring logs (--alerts, --monitor, --all)"
            echo "  hash        - Display script hash for integrity verification"
            echo "  help        - Show this help message"
            echo ""
            echo "Environment Variables:"
            echo "  OPENCLAW_WORKSPACE - Path to OpenClaw workspace (default: ~/.openclaw/workspace)"
            echo "  SCRIPT_HASH        - Expected SHA256 hash for integrity checking"
            ;;
        
        *)
            echo "Unknown command: $action"
            echo "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
