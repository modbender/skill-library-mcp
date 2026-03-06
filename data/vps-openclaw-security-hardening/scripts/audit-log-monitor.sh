#!/bin/bash
# Audit Log Monitor - Real-time monitoring of audit logs
# Called by cron every 5 minutes

LOG_FILE="/var/log/audit/audit.log"
ALERT_CONFIG="$(dirname "$0")/../config/alerting.env"

# Check if alerting is configured
if [ -f "$ALERT_CONFIG" ]; then
    source "$ALERT_CONFIG"
fi

# Monitor for critical events in last 5 minutes
CRITICAL_EVENTS=$(ausearch -ts recent -k agent_ -i 2>/dev/null | grep -E "(credential_access|ssh_config|privesc|firewall_disabled)" | head -20)

if [ -n "$CRITICAL_EVENTS" ]; then
    # Send alert if configured
    if [ -f "$(dirname "$0")/critical-alert.sh" ] && [ -n "$TELEGRAM_BOT_TOKEN" ]; then
        echo "$CRITICAL_EVENTS" | "$(dirname "$0")/critical-alert.sh"
    fi
fi

exit 0
