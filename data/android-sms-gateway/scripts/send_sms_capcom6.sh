#!/usr/bin/env bash
#
# send_sms_capcom6.sh - Send SMS via capcom6/android-sms-gateway
#
# Usage:
#   ./send_sms_capcom6.sh --to "+1234567890" --message "Hello"
#   ./send_sms_capcom6.sh --config ~/.openclaw/sms-gateway.json --to "+1234567890" --message "Hello"
#
# Environment variables:
#   SMS_GATEWAY_URL   - Gateway base URL (e.g., http://192.168.1.100:8080)
#   SMS_GATEWAY_USER  - Basic auth username
#   SMS_GATEWAY_PASS  - Basic auth password
#   SMS_GATEWAY_TIMEOUT - Request timeout in seconds (default: 30)
#

set -euo pipefail

# Defaults
TIMEOUT="${SMS_GATEWAY_TIMEOUT:-30}"
CONFIG_FILE=""
GATEWAY_URL=""
GATEWAY_USER=""
GATEWAY_PASS=""
TO=""
MESSAGE=""
SIM_SLOT=""
SERVER_MODE="local"  # local | cloud

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

usage() {
    cat <<EOF
Send SMS via capcom6/android-sms-gateway

Usage:
  $0 --to <number> --message <text> [options]
  $0 --config <file> --to <number> --message <text>

Options:
  --to <number>        Recipient phone number (include country code, e.g., +1234567890)
  --message <text>     Message content
  --config <file>      Path to config file (JSON)
  --url <url>          Gateway URL (overrides config/env)
  --user <username>    Basic auth username (overrides config/env)
  --pass <password>    Basic auth password (overrides config/env)
  --sim <slot>         SIM slot number (1 or 2, for dual SIM phones)
  --mode <local|cloud> Server mode: local (device) or cloud (api.sms-gate.app)
  --timeout <seconds>  Request timeout (default: 30)
  --dry-run            Show request without sending
  --verbose            Show detailed output
  --help               Show this help

Environment variables:
  SMS_GATEWAY_URL      Gateway base URL
  SMS_GATEWAY_USER     Basic auth username
  SMS_GATEWAY_PASS     Basic auth password
  SMS_GATEWAY_TIMEOUT  Request timeout in seconds

Examples:
  # Local server mode
  $0 --to "+1234567890" --message "Hello from OpenClaw"
  
  # Cloud server mode
  $0 --mode cloud --to "+1234567890" --message "Hello"
  
  # With config file
  $0 --config ~/.openclaw/sms-gateway.json --to "+1234567890" --message "Alert"

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
while [[ $# -gt 0 ]]; do
    case $1 in
        --to)
            TO="$2"
            shift 2
            ;;
        --message)
            MESSAGE="$2"
            shift 2
            ;;
        --config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        --url)
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
        --sim)
            SIM_SLOT="$2"
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
        --dry-run)
            DRY_RUN=1
            shift
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

# Validate required arguments
if [[ -z "$TO" ]]; then
    log_error "Missing required argument: --to"
    usage
fi

if [[ -z "$MESSAGE" ]]; then
    log_error "Missing required argument: --message"
    usage
fi

# Load configuration
load_config() {
    # Priority: CLI args > config file > environment variables
    
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
            if [[ -z "$TIMEOUT" ]]; then
                TIMEOUT=$(jq -r '.timeout_seconds // 30' "$CONFIG_FILE")
            fi
        else
            log_warn "jq not found, cannot parse config file. Using env/CLI args only."
        fi
    fi
    
    # Fall back to environment variables
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
    
    # Validate we have required config
    if [[ -z "$GATEWAY_URL" ]]; then
        log_error "Gateway URL not configured. Set SMS_GATEWAY_URL env var, use --url, or provide --config"
        exit 1
    fi
    
    if [[ -z "$GATEWAY_USER" ]]; then
        log_error "Username not configured. Set SMS_GATEWAY_USER env var, use --user, or provide --config"
        exit 1
    fi
    
    if [[ -z "$GATEWAY_PASS" ]]; then
        log_error "Password not configured. Set SMS_GATEWAY_PASS env var, use --pass, or provide --config"
        exit 1
    fi
}

# Send SMS via capcom6/android-sms-gateway API
send_sms() {
    local to="$1"
    local message="$2"
    local sim_slot="$3"
    
    # capcom6 uses /message endpoint (no /api/v1 prefix)
    local url="${GATEWAY_URL}/message"
    
    # Build JSON payload for capcom6 API
    # Format: {"textMessage": {"text": "..."}, "phoneNumbers": ["+1234567890"]}
    local payload="{\"textMessage\":{\"text\":\"${message}\"},\"phoneNumbers\":[\"${to}\"]"
    if [[ -n "$sim_slot" ]]; then
        payload="${payload},\"simSlot\":${sim_slot}"
    fi
    payload="${payload}}"
    
    log_verbose "POST $url"
    log_verbose "Payload: $payload"
    
    if [[ "${DRY_RUN:-0}" == "1" ]]; then
        echo "[DRY RUN] Would send:"
        echo "  URL: $url"
        echo "  To: $to"
        echo "  Message: $message"
        echo "  Payload: $payload"
        echo "  Auth: ${GATEWAY_USER}:****"
        return 0
    fi
    
    # Send request with Basic Auth
    local response
    local http_code
    
    response=$(curl -s -w "\n%{http_code}" \
        -X POST "$url" \
        -u "${GATEWAY_USER}:${GATEWAY_PASS}" \
        -H "Content-Type: application/json" \
        -d "$payload" \
        --max-time "$TIMEOUT" \
        2>/dev/null) || {
        log_error "Failed to connect to gateway at $GATEWAY_URL"
        exit 1
    }
    
    # Extract HTTP code (last line) and body (everything else)
    http_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | sed '$d')
    
    log_verbose "HTTP $http_code"
    log_verbose "Response: $body"
    
    # Check response
    if [[ "$http_code" == "200" || "$http_code" == "201" || "$http_code" == "202" ]]; then
        # Parse response for message ID
        local message_id=""
        local status=""
        if command -v jq &> /dev/null; then
            message_id=$(echo "$body" | jq -r '.id // .messageId // .message_id // "unknown"' 2>/dev/null || echo "unknown")
            status=$(echo "$body" | jq -r '.status // "sent"' 2>/dev/null || echo "sent")
        fi
        log_info "SMS sent successfully (ID: $message_id, Status: $status)"
        echo "$message_id"
    else
        log_error "Gateway returned HTTP $http_code"
        if command -v jq &> /dev/null; then
            local error_msg=$(echo "$body" | jq -r '.error // .message // .errorMessage // "Unknown error"' 2>/dev/null || echo "$body")
            log_error "Error: $error_msg"
        else
            log_error "Response: $body"
        fi
        exit 1
    fi
}

# Main
main() {
    log_verbose "Starting SMS send (capcom6/android-sms-gateway)"
    log_verbose "To: $TO"
    log_verbose "Message length: ${#MESSAGE} chars"
    log_verbose "Server mode: $SERVER_MODE"
    
    # Load configuration
    load_config
    
    log_verbose "Gateway URL: $GATEWAY_URL"
    log_verbose "Timeout: ${TIMEOUT}s"
    
    # Check message length
    if [[ ${#MESSAGE} -gt 160 ]]; then
        log_warn "Message is ${#MESSAGE} chars - will be split into multiple SMS"
    fi
    
    # Send via capcom6 API
    send_sms "$TO" "$MESSAGE" "$SIM_SLOT"
}

main "$@"
