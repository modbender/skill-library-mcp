#!/usr/bin/env bash
#
# register_webhook_capcom6.sh - Register webhook for incoming SMS (capcom6/android-sms-gateway)
#
# Usage:
#   ./register_webhook_capcom6.sh --url "https://your-server.com/webhook"
#   ./register_webhook_capcom6.sh --list
#   ./register_webhook_capcom6.sh --delete "webhook-id"
#

set -euo pipefail

# Defaults
TIMEOUT="${SMS_GATEWAY_TIMEOUT:-30}"
CONFIG_FILE=""
GATEWAY_URL=""
GATEWAY_USER=""
GATEWAY_PASS=""
WEBHOOK_URL=""
WEBHOOK_ID=""
WEBHOOK_EVENT="sms:received"
SERVER_MODE="local"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

usage() {
    cat <<EOF
Manage webhooks for capcom6/android-sms-gateway

Usage:
  $0 --url <webhook-url> [options]    Register new webhook
  $0 --list                           List registered webhooks
  $0 --delete <webhook-id>            Delete a webhook

Options:
  --url <url>             Webhook URL to register (for incoming SMS)
  --event <event>         Event type: sms:received, mms:received, message:status (default: sms:received)
  --id <webhook-id>       Webhook ID (for deletion)
  --list                  List all registered webhooks
  --config <file>         Path to config file (JSON)
  --url <gateway-url>     Gateway URL (overrides config/env)
  --user <username>       Basic auth username
  --pass <password>       Basic auth password
  --mode <local|cloud>    Server mode: local or cloud
  --timeout <seconds>     Request timeout (default: 30)
  --verbose               Show detailed output
  --help                  Show this help

Environment variables:
  SMS_GATEWAY_URL         Gateway base URL
  SMS_GATEWAY_USER        Basic auth username
  SMS_GATEWAY_PASS        Basic auth password
  SMS_GATEWAY_TIMEOUT     Request timeout in seconds

Examples:
  # Register webhook for incoming SMS
  $0 --url "https://your-server.com/sms-webhook"
  
  # Register for MMS events
  $0 --url "https://your-server.com/mms-webhook" --event "mms:received"
  
  # List webhooks
  $0 --list
  
  # Delete webhook
  $0 --delete "webhook-123"
  
  # Cloud mode
  $0 --mode cloud --url "https://your-server.com/webhook"

Notes:
  - Webhook URL must be publicly accessible (HTTPS recommended)
  - For testing, use https://webhook.site to get a temporary URL
  - Webhooks are transmitted directly from the device
  - Local and Cloud mode webhooks are independent

EOF
    exit 1
}

log_info() {
    echo -e "${GREEN}[INFO]${NC} $*"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*" >&2
}

log_verbose() {
    if [[ "${VERBOSE:-0}" == "1" ]]; then
        echo -e "${YELLOW}[DEBUG]${NC} $*"
    fi
}

# Parse arguments
ACTION=""
LIST_WEBHOOKS=0

while [[ $# -gt 0 ]]; do
    case $1 in
        --url)
            if [[ -z "$ACTION" ]]; then
                ACTION="register"
            fi
            WEBHOOK_URL="$2"
            shift 2
            ;;
        --event)
            WEBHOOK_EVENT="$2"
            shift 2
            ;;
        --id)
            WEBHOOK_ID="$2"
            shift 2
            ;;
        --delete)
            ACTION="delete"
            WEBHOOK_ID="$2"
            shift 2
            ;;
        --list)
            ACTION="list"
            LIST_WEBHOOKS=1
            shift
            ;;
        --config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        --gateway-url)
            GATEWAY_URL="$2"
            shift 2
            ;;
        --user)
            GATEWAY_USER="$2"
            shift 2
            ;;
        --pass)
            GATEWAY_PASS="$2"
            shift 2
            ;;
        --mode)
            SERVER_MODE="$2"
            shift 2
            ;;
        --timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        --verbose)
            VERBOSE=1
            shift
            ;;
        --help)
            usage
            ;;
        *)
            log_error "Unknown option: $1"
            usage
            ;;
    esac
done

# Load configuration
load_config() {
    if [[ -n "$CONFIG_FILE" && -f "$CONFIG_FILE" ]]; then
        log_verbose "Loading config from: $CONFIG_FILE"
        
        if command -v jq &> /dev/null; then
            if [[ -z "$GATEWAY_URL" ]]; then
                GATEWAY_URL=$(jq -r '.gateway_url // empty' "$CONFIG_FILE")
            fi
            if [[ -z "$GATEWAY_USER" ]]; then
                GATEWAY_USER=$(jq -r '.gateway_user // empty' "$CONFIG_FILE")
            fi
            if [[ -z "$GATEWAY_PASS" ]]; then
                GATEWAY_PASS=$(jq -r '.gateway_pass // empty' "$CONFIG_FILE")
            fi
            if [[ -z "$SERVER_MODE" || "$SERVER_MODE" == "local" ]]; then
                SERVER_MODE=$(jq -r '.server_mode // "local"' "$CONFIG_FILE")
            fi
        fi
    fi
    
    if [[ -z "$GATEWAY_URL" ]]; then
        GATEWAY_URL="${SMS_GATEWAY_URL:-}"
    fi
    if [[ -z "$GATEWAY_USER" ]]; then
        GATEWAY_USER="${SMS_GATEWAY_USER:-}"
    fi
    if [[ -z "$GATEWAY_PASS" ]]; then
        GATEWAY_PASS="${SMS_GATEWAY_PASS:-}"
    fi
    
    # Set default URL based on mode
    if [[ "$SERVER_MODE" == "cloud" ]]; then
        GATEWAY_URL="https://api.sms-gate.app/3rdparty/v1"
        log_verbose "Using cloud server mode"
    fi
    
    if [[ -z "$GATEWAY_URL" ]]; then
        log_error "Gateway URL not configured"
        exit 1
    fi
    if [[ -z "$GATEWAY_USER" ]]; then
        log_error "Username not configured"
        exit 1
    fi
    if [[ -z "$GATEWAY_PASS" ]]; then
        log_error "Password not configured"
        exit 1
    fi
}

# Register webhook
register_webhook() {
    if [[ -z "$WEBHOOK_URL" ]]; then
        log_error "Webhook URL required for registration"
        exit 1
    fi
    
    local url="${GATEWAY_URL}/webhooks"
    local webhook_id="${WEBHOOK_ID:-webhook_$(date +%s)_$$}"
    
    local payload="{\"id\":\"${webhook_id}\",\"url\":\"${WEBHOOK_URL}\",\"event\":\"${WEBHOOK_EVENT}\"}"
    
    log_info "Registering webhook..."
    log_verbose "POST $url"
    log_verbose "Payload: $payload"
    
    local response
    local http_code
    
    response=$(curl -s -w "\n%{http_code}" \
        -X POST "$url" \
        -u "${GATEWAY_USER}:${GATEWAY_PASS}" \
        -H "Content-Type: application/json" \
        -d "$payload" \
        --max-time "$TIMEOUT" \
        2>/dev/null) || {
        log_error "Failed to connect to gateway"
        exit 1
    }
    
    http_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | sed '$d')
    
    log_verbose "HTTP $http_code"
    
    if [[ "$http_code" == "200" || "$http_code" == "201" ]]; then
        log_info "✓ Webhook registered successfully"
        echo ""
        echo "  Webhook ID:  $webhook_id"
        echo "  URL:         $WEBHOOK_URL"
        echo "  Event:       $WEBHOOK_EVENT"
        echo ""
        echo "  Test by sending an SMS to the device."
        echo "  Payload will be POSTed to your webhook URL."
    else
        log_error "Failed to register webhook (HTTP $http_code)"
        log_error "Response: $body"
        exit 1
    fi
}

# List webhooks
list_webhooks() {
    # Note: capcom6 API may not have a list endpoint
    # This is a placeholder - adjust based on actual API
    log_warn "Webhook listing not supported by capcom6 API"
    log_info "Check your device app for registered webhooks"
    exit 0
}

# Delete webhook
delete_webhook() {
    if [[ -z "$WEBHOOK_ID" ]]; then
        log_error "Webhook ID required for deletion"
        exit 1
    fi
    
    local url="${GATEWAY_URL}/webhooks/${WEBHOOK_ID}"
    
    log_info "Deleting webhook: $WEBHOOK_ID"
    log_verbose "DELETE $url"
    
    local response
    local http_code
    
    response=$(curl -s -w "\n%{http_code}" \
        -X DELETE "$url" \
        -u "${GATEWAY_USER}:${GATEWAY_PASS}" \
        --max-time "$TIMEOUT" \
        2>/dev/null) || {
        log_error "Failed to connect to gateway"
        exit 1
    }
    
    http_code=$(echo "$response" | tail -n1)
    
    log_verbose "HTTP $http_code"
    
    if [[ "$http_code" == "200" || "$http_code" == "204" ]]; then
        log_info "✓ Webhook deleted successfully"
    else
        log_error "Failed to delete webhook (HTTP $http_code)"
        exit 1
    fi
}

# Main
main() {
    load_config
    
    if [[ -z "$ACTION" ]]; then
        log_error "No action specified. Use --url, --list, or --delete"
        usage
    fi
    
    case $ACTION in
        register)
            register_webhook
            ;;
        list)
            list_webhooks
            ;;
        delete)
            delete_webhook
            ;;
        *)
            log_error "Unknown action: $ACTION"
            usage
            ;;
    esac
}

main "$@"
