#!/bin/bash
# OPNsense Service Control Script
# Start, stop, restart, and check status of OPNsense services

OPNSENSE_HOST="${OPNSENSE_HOST:-192.168.1.1}"
SSH_PORT="${SSH_PORT:-22}"
SSH_USER="${SSH_USER:-root}"

show_help() {
    cat << EOF
OPNsense Service Control

Usage: $0 <service> <action> [options]

Services:
    unbound         DNS Resolver
    suricata        Intrusion Detection/Prevention
    dhcpd           DHCP Server
    dpinger         Gateway Monitoring
    ssh             SSH Server
    webgui          Web Interface (nginx)
    syslogd         System Logging
    cron            Cron Daemon
    all             All services

Actions:
    start           Start service
    stop            Stop service
    restart         Restart service
    status          Check service status
    reload          Reload configuration

Options:
    -h, --host      OPNsense host (default: 192.168.1.1)
    -p, --port      SSH port (default: 22)
    -u, --user      SSH user (default: root)
    --help          Show this help

Examples:
    $0 unbound restart
    $0 suricata status
    $0 dhcpd reload
    $0 all status
EOF
}

# Parse arguments
SERVICE="${1:-}"
ACTION="${2:-}"

if [[ -z "$SERVICE" || -z "$ACTION" ]]; then
    show_help
    exit 1
fi

# Validate action
case "$ACTION" in
    start|stop|restart|status|reload)
        ;;
    *)
        echo "Invalid action: $ACTION"
        show_help
        exit 1
        ;;
esac

# Service name mapping
case "$SERVICE" in
    unbound)
        SERVICE_NAME="unbound"
        ;;
    suricata|ids|ips)
        SERVICE_NAME="suricata"
        ;;
    dhcpd|dhcp)
        SERVICE_NAME="dhcpd"
        ;;
    dpinger)
        SERVICE_NAME="dpinger"
        ;;
    ssh)
        SERVICE_NAME="sshd"
        ;;
    webgui|nginx)
        SERVICE_NAME="nginx"
        ;;
    syslogd|syslog)
        SERVICE_NAME="syslogd"
        ;;
    cron)
        SERVICE_NAME="cron"
        ;;
    all)
        SERVICE_NAME="all"
        ;;
    *)
        echo "Unknown service: $SERVICE"
        show_help
        exit 1
        ;;
esac

# Execute action via SSH
execute_service_cmd() {
    local svc="$1"
    local act="$2"
    
    echo "Executing: $act $svc"
    
    if [[ "$svc" == "all" ]]; then
        ssh -p "$SSH_PORT" "${SSH_USER}@${OPNSENSE_HOST}" "service -e | while read svc; do echo \"=== \$svc ===\"; service \$(basename \$svc) $act 2>&1; done"
    else
        ssh -p "$SSH_PORT" "${SSH_USER}@${OPNSENSE_HOST}" "service $svc $act 2>&1"
    fi
}

# Special handling for status
if [[ "$ACTION" == "status" ]]; then
    echo "Checking status of $SERVICE_NAME..."
    
    if [[ "$SERVICE_NAME" == "all" ]]; then
        ssh -p "$SSH_PORT" "${SSH_USER}@${OPNSENSE_HOST}" "service -e | head -20"
    else
        # Check service status and also show if it's enabled
        ssh -p "$SSH_PORT" "${SSH_USER}@${OPNSENSE_HOST}" "
            echo '=== Service Status ===' && \
            service $SERVICE_NAME status 2>&1 && \
            echo '' && \
            echo '=== Process Info ===' && \
            pgrep -lf $SERVICE_NAME 2>/dev/null || echo 'No running processes' && \
            echo '' && \
            echo '=== Recent Log Entries ===' && \
            tail -5 /var/log/system/latest.log 2>/dev/null | grep -i $SERVICE_NAME || echo 'No recent log entries'
        "
    fi
else
    execute_service_cmd "$SERVICE_NAME" "$ACTION"
fi

echo ""
echo "Done."
