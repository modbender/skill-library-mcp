#!/usr/bin/env bash
#
# check_status_capcom6.sh - Check capcom6/android-sms-gateway health status
#
# Usage:
#   ./check_status_capcom6.sh
#   ./check_status_capcom6.sh --json
#

set -euo pipefail

# Defaults
TIMEOUT="${SMS_GATEWAY_TIMEOUT:-10}"
CONFIG_FILE=""
GATEWAY_URL=""
GATEWAY_USER=""
GATEWAY_PASS=""
SERVER_MODE="local"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

usage() {
    cat <<EOF
Check capcom6/android-sms-gateway health status

Usage:
  $0 [options]

Options:
  --config <file>      Path to config file (JSON)
  --url <gateway-url>  Gateway URL (overrides config/env)
  --user <username>    Basic auth username
  --pass <password>    Basic auth password
  --mode <local|cloud> Server mode: local or cloud
  --json               Output as JSON
  --verbose            Show detailed output
  --help               Show this help

Environment variables:
  SMS_GATEWAY_URL      Gateway base URL
  SMS_GATEWAY_USER     Basic auth username
  SMS_GATEWAY_PASS     Basic auth password
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

# Check gateway status
# Note: capcom6 API doesn't have a dedicated /status endpoint
# We'll test connectivity by making a minimal request
check_status() {
    # Try to get device info or test connectivity
    # capcom6 doesn't have a status endpoint, so we test the message endpoint
    local url="${GATEWAY_URL}/message"
    
    log_verbose "Testing connectivity to $url"
    
    local start_time=$(date +%s%N)
    
    # Make a minimal OPTIONS or GET request to test connectivity
    # Since POST requires a body, we'll just test TCP connectivity
    local response
    local http_code
    
    # Test with a HEAD request first (if supported)
    response=$(curl -s -w "\n%{http_code}" \
        -I "$url" \
        -u "${GATEWAY_USER}:${GATEWAY_PASS}" \
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
    
    log_verbose "HTTP $http_code (${latency}ms)"
    
    # 405 Method Not Allowed is OK - means server is up but doesn't support HEAD
    # 401/403 means server is up but auth might be wrong
    # 200/201 means server is fully functional
    if [[ "$http_code" =~ ^(200|201|204|405|401|403)$ ]]; then
        if [[ "$JSON_OUTPUT" == "1" ]]; then
            echo "{\"status\":\"online\",\"latency_ms\":$latency,\"mode\":\"$SERVER_MODE\"}"
        else
            echo ""
            echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
            echo -e "${BLUE}║${NC}  🛡️  Android SMS Gateway Status    ${BLUE}║${NC}"
            echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
            echo ""
            echo -e "  Status:        ${GREEN}● Online${NC}"
            echo -e "  URL:           $GATEWAY_URL"
            echo -e "  Mode:          $SERVER_MODE"
            echo -e "  Latency:       ${latency}ms"
            echo -e "  Auth:          Basic (${GATEWAY_USER})"
            echo ""
            
            if [[ "$http_code" == "401" || "$http_code" == "403" ]]; then
                echo -e "  ${YELLOW}⚠ Auth may be incorrect${NC}"
            fi
            
            log_info "Gateway is reachable"
        fi
        exit 0
    else
        log_error "❌ Gateway returned HTTP $http_code"
        if [[ "$JSON_OUTPUT" == "1" ]]; then
            echo "{\"status\":\"error\",\"http_code\":$http_code,\"latency_ms\":$latency}"
        fi
        exit 2
    fi
}

# Alternative: Check local server status (device must have local server enabled)
check_local_server() {
    local url="${GATEWAY_URL}/"
    
    log_verbose "Checking local server at $url"
    
    local response
    local http_code
    
    response=$(curl -s -w "\n%{http_code}" \
        -X GET "$url" \
        --max-time "$TIMEOUT" \
        2>/dev/null) || {
        log_error "❌ Local server not responding"
        exit 1
    }
    
    http_code=$(echo "$response" | tail -n1)
    
    if [[ "$http_code" == "200" || "$http_code" == "401" ]]; then
        log_info "✓ Local server is running"
        exit 0
    else
        log_error "❌ Local server returned HTTP $http_code"
        exit 1
    fi
}

# Main
main() {
    load_config
    check_status
}

main "$@"
