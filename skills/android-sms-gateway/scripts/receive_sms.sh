#!/usr/bin/env bash
#
# receive_sms.sh - Fetch received SMS messages from Android SMS Gateway
#
# Usage:
#   ./receive_sms.sh --limit 10
#   ./receive_sms.sh --since "2026-02-22T00:00:00Z"
#

set -euo pipefail

# Defaults
TIMEOUT="${SMS_GATEWAY_TIMEOUT:-30}"
CONFIG_FILE=""
GATEWAY_URL=""
API_TOKEN=""
LIMIT=10
SINCE=""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

usage() {
    cat <<EOF
Fetch received SMS messages from Android SMS Gateway

Usage:
  $0 [options]

Options:
  --limit <n>          Number of messages to fetch (default: 10)
  --since <timestamp>  Fetch messages since ISO 8601 timestamp
  --config <file>      Path to config file (JSON)
  --url <url>          Gateway URL (overrides config/env)
  --token <token>      API token (overrides config/env)
  --json               Output as JSON
  --verbose            Show detailed output
  --help               Show this help

Environment variables:
  SMS_GATEWAY_URL      Gateway base URL
  SMS_GATEWAY_TOKEN    API authentication token
  SMS_GATEWAY_TIMEOUT  Request timeout in seconds

Examples:
  $0 --limit 20
  $0 --since "2026-02-22T08:00:00Z"
  $0 --json --limit 5

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
JSON_OUTPUT=0

while [[ $# -gt 0 ]]; do
    case $1 in
        --limit)
            LIMIT="$2"
            shift 2
            ;;
        --since)
            SINCE="$2"
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
        --json)
            JSON_OUTPUT=1
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

# Load configuration (same as send_sms.sh)
load_config() {
    if [[ -n "$CONFIG_FILE" && -f "$CONFIG_FILE" ]]; then
        log_verbose "Loading config from: $CONFIG_FILE"
        
        if command -v jq &> /dev/null; then
            if [[ -z "$GATEWAY_URL" ]]; then
                GATEWAY_URL=$(jq -r '.gateway_url // empty' "$CONFIG_FILE")
            fi
            if [[ -z "$API_TOKEN" ]]; then
                API_TOKEN=$(jq -r '.api_token // empty' "$CONFIG_FILE")
            fi
        fi
    fi
    
    if [[ -z "$GATEWAY_URL" ]]; then
        GATEWAY_URL="${SMS_GATEWAY_URL:-}"
    fi
    if [[ -z "$API_TOKEN" ]]; then
        API_TOKEN="${SMS_GATEWAY_TOKEN:-}"
    fi
    
    if [[ -z "$GATEWAY_URL" ]]; then
        log_error "Gateway URL not configured"
        exit 1
    fi
    if [[ -z "$API_TOKEN" ]]; then
        log_error "API token not configured"
        exit 1
    fi
}

# Fetch received messages
fetch_messages() {
    local url="${GATEWAY_URL}/api/v1/messages/received"
    local auth_header="Authorization: Bearer ${API_TOKEN}"
    local query_params="limit=${LIMIT}"
    
    if [[ -n "$SINCE" ]]; then
        query_params="${query_params}&since=${SINCE}"
    fi
    
    log_verbose "GET ${url}?${query_params}"
    
    local response
    local http_code
    
    response=$(curl -s -w "\n%{http_code}" \
        -X GET "${url}?${query_params}" \
        -H "$auth_header" \
        -H "Accept: application/json" \
        --max-time "$TIMEOUT" \
        2>/dev/null) || {
        log_error "Failed to connect to gateway"
        exit 1
    }
    
    http_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | sed '$d')
    
    log_verbose "HTTP $http_code"
    
    if [[ "$http_code" != "200" ]]; then
        log_error "Gateway returned HTTP $http_code"
        exit 1
    fi
    
    # Output
    if [[ "$JSON_OUTPUT" == "1" ]]; then
        echo "$body"
    else
        # Pretty print
        if command -v jq &> /dev/null; then
            local messages=$(echo "$body" | jq -r '.messages // .data // []' 2>/dev/null)
            local count=$(echo "$messages" | jq 'length')
            
            if [[ "$count" == "0" ]]; then
                log_info "No messages found"
                return 0
            fi
            
            log_info "Found $count message(s):"
            echo ""
            
            echo "$messages" | jq -r '.[] | "📱 From: \(.from // .sender)\n📅 Time: \(.received_at // .timestamp)\n💬 Message: \(.message // .text)\n---"'
        else
            echo "$body"
        fi
    fi
}

# Main
main() {
    load_config
    fetch_messages
}

main "$@"
