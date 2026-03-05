#!/usr/bin/env bash
#
# check_status.sh - Check Android SMS Gateway health status
#
# Usage:
#   ./check_status.sh
#   ./check_status.sh --json
#

set -euo pipefail

# Defaults
TIMEOUT="${SMS_GATEWAY_TIMEOUT:-10}"
CONFIG_FILE=""
GATEWAY_URL=""
API_TOKEN=""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

usage() {
    cat <<EOF
Check Android SMS Gateway health status

Usage:
  $0 [options]

Options:
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

Exit codes:
  0 - Gateway is healthy
  1 - Gateway is unreachable or error
  2 - Gateway returned error status

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

# Load configuration
load_config() {
    if [[ -n "$CONFIG_FILE" && -f "$CONFIG_FILE" ]]; then
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

# Check gateway status
check_status() {
    local url="${GATEWAY_URL}/api/v1/status"
    local auth_header="Authorization: Bearer ${API_TOKEN}"
    
    log_verbose "GET $url"
    
    local start_time=$(date +%s%N)
    
    local response
    local http_code
    
    response=$(curl -s -w "\n%{http_code}" \
        -X GET "$url" \
        -H "$auth_header" \
        -H "Accept: application/json" \
        --max-time "$TIMEOUT" \
        2>/dev/null) || {
        log_error "❌ Gateway unreachable at $GATEWAY_URL"
        if [[ "$JSON_OUTPUT" == "1" ]]; then
            echo '{"status":"unreachable","error":"Connection failed"}'
        fi
        exit 1
    }
    
    local end_time=$(date +%s%N)
    local latency=$(( (end_time - start_time) / 1000000 )) # Convert to ms
    
    http_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | sed '$d')
    
    log_verbose "HTTP $http_code (${latency}ms)"
    
    if [[ "$http_code" != "200" ]]; then
        log_error "❌ Gateway returned HTTP $http_code"
        if [[ "$JSON_OUTPUT" == "1" ]]; then
            echo "{\"status\":\"error\",\"http_code\":$http_code}"
        fi
        exit 2
    fi
    
    # Parse response
    local status="unknown"
    local phone_number=""
    local signal_strength=""
    local sms_count=""
    
    if command -v jq &> /dev/null; then
        status=$(echo "$body" | jq -r '.status // .state // "unknown"' 2>/dev/null || echo "unknown")
        phone_number=$(echo "$body" | jq -r '.phone_number // .number // ""' 2>/dev/null || echo "")
        signal_strength=$(echo "$body" | jq -r '.signal_strength // .signal // ""' 2>/dev/null || echo "")
        sms_count=$(echo "$body" | jq -r '.pending_messages // .sms_count // ""' 2>/dev/null || echo "")
    fi
    
    # Output
    if [[ "$JSON_OUTPUT" == "1" ]]; then
        echo "{\"status\":\"$status\",\"latency_ms\":$latency,\"phone_number\":\"$phone_number\",\"signal\":\"$signal_strength\"}"
    else
        echo ""
        echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
        echo -e "${BLUE}║${NC}  🛡️  Android SMS Gateway Status    ${BLUE}║${NC}"
        echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
        echo ""
        
        if [[ "$status" == "online" || "$status" == "running" || "$status" == "ok" ]]; then
            echo -e "  Status:        ${GREEN}● Online${NC}"
        else
            echo -e "  Status:        ${YELLOW}● $status${NC}"
        fi
        
        echo -e "  URL:           $GATEWAY_URL"
        echo -e "  Latency:       ${latency}ms"
        
        if [[ -n "$phone_number" ]]; then
            echo -e "  Phone:         $phone_number"
        fi
        if [[ -n "$signal_strength" ]]; then
            echo -e "  Signal:        $signal_strength"
        fi
        if [[ -n "$sms_count" ]]; then
            echo -e "  Pending SMS:   $sms_count"
        fi
        
        echo ""
        log_info "Gateway is healthy"
    fi
    
    exit 0
}

# Main
main() {
    load_config
    check_status
}

main "$@"
