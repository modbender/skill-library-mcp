#!/usr/bin/env bash
#
# send_sms.sh - Send SMS via Android SMS Gateway
#
# Usage:
#   ./send_sms.sh --to "+1234567890" --message "Hello"
#   ./send_sms.sh --config ~/.openclaw/sms-gateway.json --to "+1234567890" --message "Hello"
#
# Environment variables:
#   SMS_GATEWAY_URL   - Gateway base URL (e.g., http://192.168.1.100:8080)
#   SMS_GATEWAY_TOKEN - API authentication token
#   SMS_GATEWAY_TIMEOUT - Request timeout in seconds (default: 30)
#

set -euo pipefail

# Defaults
TIMEOUT="${SMS_GATEWAY_TIMEOUT:-30}"
CONFIG_FILE=""
GATEWAY_URL=""
API_TOKEN=""
TO=""
MESSAGE=""
SIM_SLOT=""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

usage() {
    cat <<EOF
Send SMS via Android SMS Gateway

Usage:
  $0 --to <number> --message <text> [options]
  $0 --config <file> --to <number> --message <text>

Options:
  --to <number>        Recipient phone number (include country code, e.g., +1234567890)
  --message <text>     Message content
  --config <file>      Path to config file (JSON)
  --url <url>          Gateway URL (overrides config/env)
  --token <token>      API token (overrides config/env)
  --sim <slot>         SIM slot number (1 or 2, for dual SIM phones)
  --timeout <seconds>  Request timeout (default: 30)
  --dry-run            Show request without sending
  --verbose            Show detailed output
  --help               Show this help

Environment variables:
  SMS_GATEWAY_URL      Gateway base URL
  SMS_GATEWAY_TOKEN    API authentication token
  SMS_GATEWAY_TIMEOUT  Request timeout in seconds

Examples:
  $0 --to "+1234567890" --message "Hello from OpenClaw"
  $0 --config ~/.openclaw/sms-gateway.json --to "+1234567890" --message "Alert"
  SMS_GATEWAY_URL="http://192.168.1.100:8080" $0 --to "+1234567890" --message "Test"

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
        --token)
            API_TOKEN="$2"
            shift 2
            ;;
        --sim)
            SIM_SLOT="$2"
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
            if [[ -z "$API_TOKEN" ]]; then
                API_TOKEN=$(jq -r '.api_token // empty' "$CONFIG_FILE")
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
    if [[ -z "$API_TOKEN" ]]; then
        API_TOKEN="${SMS_GATEWAY_TOKEN:-}"
    fi
    
    # Validate we have required config
    if [[ -z "$GATEWAY_URL" ]]; then
        log_error "Gateway URL not configured. Set SMS_GATEWAY_URL env var, use --url, or provide --config"
        exit 1
    fi
    
    if [[ -z "$API_TOKEN" ]]; then
        log_error "API token not configured. Set SMS_GATEWAY_TOKEN env var, use --token, or provide --config"
        exit 1
    fi
}

# Send SMS via SMS Gateway API (itsmeichigo/SMSGateway)
send_sms_gateway_api() {
    local to="$1"
    local message="$2"
    local sim_slot="$3"
    
    local url="${GATEWAY_URL}/api/v1/send"
    local auth_header="Authorization: Bearer ${API_TOKEN}"
    
    # Build JSON payload
    local payload="{\"phone\":\"${to}\",\"message\":\"${message}\""
    if [[ -n "$sim_slot" ]]; then
        payload="${payload},\"sim\":${sim_slot}"
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
        return 0
    fi
    
    # Send request
    local response
    local http_code
    
    response=$(curl -s -w "\n%{http_code}" \
        -X POST "$url" \
        -H "$auth_header" \
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
    if [[ "$http_code" == "200" || "$http_code" == "201" ]]; then
        # Parse response for message ID
        local message_id=""
        if command -v jq &> /dev/null; then
            message_id=$(echo "$body" | jq -r '.message_id // .id // "unknown"' 2>/dev/null || echo "unknown")
        fi
        log_info "SMS sent successfully (ID: $message_id)"
        echo "$message_id"
    else
        log_error "Gateway returned HTTP $http_code"
        if command -v jq &> /dev/null; then
            local error_msg=$(echo "$body" | jq -r '.error // .message // "Unknown error"' 2>/dev/null || echo "$body")
            log_error "Error: $error_msg"
        else
            log_error "Response: $body"
        fi
        exit 1
    fi
}

# Main
main() {
    log_verbose "Starting SMS send"
    log_verbose "To: $TO"
    log_verbose "Message length: ${#MESSAGE} chars"
    
    # Load configuration
    load_config
    
    log_verbose "Gateway URL: $GATEWAY_URL"
    log_verbose "Timeout: ${TIMEOUT}s"
    
    # Check message length
    if [[ ${#MESSAGE} -gt 160 ]]; then
        log_warn "Message is ${#MESSAGE} chars - will be split into multiple SMS"
    fi
    
    # Send via SMS Gateway API (primary supported app)
    send_sms_gateway_api "$TO" "$MESSAGE" "$SIM_SLOT"
}

main "$@"
