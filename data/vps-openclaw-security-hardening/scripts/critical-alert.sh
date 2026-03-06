#!/bin/bash
# Critical Security Alerting for OpenClaw
# Usage: ./critical-alert.sh <severity> <event> <details>
# Or pipe from ausearch: ausearch -ts today -k agent_credentials | ./critical-alert.sh
# Supports: telegram, discord, slack, webhook, email

set -euo pipefail

# Configuration
CONFIG_FILE="$(dirname "$0")/../config/alerting.env"

# Load config if exists
if [[ -f "$CONFIG_FILE" ]]; then
    source "$CONFIG_FILE"
fi

# Default values (fallback)
ALERT_CHANNEL="${ALERT_CHANNEL:-telegram}"
ALERT_LEVEL="${ALERT_LEVEL:-critical}"
TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}"
TELEGRAM_CHAT_ID="${TELEGRAM_CHAT_ID:-}"
DISCORD_WEBHOOK_URL="${DISCORD_WEBHOOK_URL:-}"
SLACK_WEBHOOK_URL="${SLACK_WEBHOOK_URL:-}"
WEBHOOK_URL="${WEBHOOK_URL:-}"
EMAIL_TO="${EMAIL_TO:-}"

# Icons
ICON_CRITICAL="🚨"
ICON_WARNING="⚠️"
ICON_INFO="ℹ️"

log_local() {
    local msg="$1"
    local logfile="/var/log/agent-security-alerts.log"
    echo "[$(date -Iseconds)] $msg" >> "$logfile"
}

send_telegram() {
    local message="$1"
    
    if [[ -z "$TELEGRAM_BOT_TOKEN" || -z "$TELEGRAM_CHAT_ID" ]]; then
        log_local "Telegram not configured"
        return 1
    fi
    
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
        -d "chat_id=${TELEGRAM_CHAT_ID}" \
        -d "parse_mode=Markdown" \
        -d "text=${message}" \
        --max-time 10 \
        > /dev/null 2>&1 || {
        log_local "Failed to send Telegram alert"
        return 1
    }
}

send_discord() {
    local message="$1"
    
    if [[ -z "$DISCORD_WEBHOOK_URL" ]]; then
        log_local "Discord not configured"
        return 1
    fi
    
    curl -s -X POST "$DISCORD_WEBHOOK_URL" \
        -H "Content-Type: application/json" \
        -d "{\"content\": \"$message\"}" \
        --max-time 10 \
        > /dev/null 2>&1 || {
        log_local "Failed to send Discord alert"
        return 1
    }
}

send_slack() {
    local message="$1"
    
    if [[ -z "$SLACK_WEBHOOK_URL" ]]; then
        log_local "Slack not configured"
        return 1
    fi
    
    curl -s -X POST "$SLACK_WEBHOOK_URL" \
        -H "Content-Type: application/json" \
        -d "{\"text\": \"$message\"}" \
        --max-time 10 \
        > /dev/null 2>&1 || {
        log_local "Failed to send Slack alert"
        return 1
    }
}

send_webhook() {
    local message="$1"
    
    if [[ -z "$WEBHOOK_URL" ]]; then
        log_local "Webhook not configured"
        return 1
    fi
    
    local method="${WEBHOOK_METHOD:-POST}"
    
    curl -s -X "$method" "$WEBHOOK_URL" \
        -H "Content-Type: application/json" \
        -d "{\"alert\": \"$message\", \"timestamp\": \"$(date -Iseconds)\"}" \
        --max-time 10 \
        > /dev/null 2>&1 || {
        log_local "Failed to send webhook alert"
        return 1
    }
}

send_email() {
    local message="$1"
    
    if [[ -z "$EMAIL_TO" ]]; then
        log_local "Email not configured"
        return 1
    fi
    
    echo "$message" | mail -s "Security Alert" "$EMAIL_TO" 2>/dev/null || {
        log_local "Failed to send email alert"
        return 1
    }
}

send_alert() {
    local message="$1"
    
    # Always log locally
    echo "$message" >> /var/log/agent-security-alerts.log
    
    # Send via configured channel
    case "$ALERT_CHANNEL" in
        telegram)
            send_telegram "$message"
            ;;
        discord)
            send_discord "$message"
            ;;
        slack)
            send_slack "$message"
            ;;
        webhook)
            send_webhook "$message"
            ;;
        email)
            send_email "$message"
            ;;
        *)
            log_local "Unknown alert channel: $ALERT_CHANNEL"
            ;;
    esac
}

format_alert() {
    local severity="$1"
    local event="$2"
    local details="${3:-}"
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    local icon="$ICON_INFO"
    [[ "$severity" == "WARNING" ]] && icon="$ICON_WARNING"
    [[ "$severity" == "CRITICAL" ]] && icon="$ICON_CRITICAL"
    
    cat << EOF
${icon} SECURITY ALERT: ${severity}

Event: ${event}
Time: ${timestamp}
Host: $(hostname)

${details}

Action Required:
Check logs: ausearch -ts today -k agent_${event// /_} | tail -20

_Agent Security Monitor_
EOF
}

# Main alerting logic
main() {
    # Check if piped input
    if [[ ! -t 0 ]]; then
        # Process piped audit events
        local event_data
        event_data=$(cat)
        
        # Parse audit event (simplified)
        if echo "$event_data" | grep -q "type=PATH.*name=.*\.env"; then
            send_alert "$(format_alert "CRITICAL" "Credential Access" "$(echo "$event_data" | head -5)")"
        elif echo "$event_data" | grep -q "type=PATH.*sshd_config"; then
            send_alert "$(format_alert "CRITICAL" "SSH Config Modified" "$(echo "$event_data" | head -5)")"
        elif echo "$event_data" | grep -q "type=SYSCALL.*setuid"; then
            send_alert "$(format_alert "WARNING" "Privilege Escalation" "$(echo "$event_data" | head -5)")"
        fi
        
        exit 0
    fi
    
    # CLI usage
    if [[ $# -lt 2 ]]; then
        echo "Usage: $0 <severity> <event> [details]"
        echo "   or: ausearch -ts today -k agent_credentials | $0"
        echo ""
        echo "Configure alerting channel in: $CONFIG_FILE"
        echo "Supported channels: telegram, discord, slack, webhook, email"
        exit 1
    fi
    
    local severity="$1"
    local event="$2"
    local details="${3:-No additional details}"
    
    # Filter by configured level
    if [[ "$ALERT_LEVEL" == "critical" && "$severity" != "CRITICAL" ]]; then
        log_local "Filtered: $severity $event (level=$ALERT_LEVEL)"
        exit 0
    fi
    
    local message
    message=$(format_alert "$severity" "$event" "$details")
    
    send_alert "$message"
    log_local "Alert sent via $ALERT_CHANNEL: $severity $event"
}

# Example usage
if [[ "${1:-}" == "--test" ]]; then
    echo "Testing alert system via $ALERT_CHANNEL..."
    format_alert "CRITICAL" "Test Alert" "This is a test of the agent security alerting system."
    exit 0
fi

main "$@"
