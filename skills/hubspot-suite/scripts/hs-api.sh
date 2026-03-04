#!/bin/bash

# HubSpot Universal API Helper
# Usage: ./hs-api.sh METHOD /endpoint [json_data]

set -euo pipefail

# Configuration
HUBSPOT_BASE_URL="${HUBSPOT_BASE_URL:-https://api.hubapi.com}"
MAX_RETRIES=5
RETRY_DELAY=2

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Help function
show_help() {
    cat << EOF
HubSpot Universal API Helper

Usage: $0 METHOD ENDPOINT [DATA]

Arguments:
  METHOD    HTTP method (GET, POST, PUT, PATCH, DELETE)
  ENDPOINT  API endpoint (e.g., /crm/v3/objects/contacts)
  DATA      JSON data for POST/PUT/PATCH requests (optional)

Examples:
  $0 GET /crm/v3/objects/contacts
  $0 POST /crm/v3/objects/contacts '{"properties": {"email": "test@example.com"}}'
  $0 PATCH /crm/v3/objects/contacts/12345 '{"properties": {"firstname": "John"}}'

Environment Variables:
  HUBSPOT_ACCESS_TOKEN  Your HubSpot access token (required)
  HUBSPOT_BASE_URL      Base API URL (default: https://api.hubapi.com)
  DEBUG                 Set to 1 for verbose output

EOF
}

# Logging functions
log_error() {
    echo -e "${RED}ERROR: $1${NC}" >&2
}

log_warning() {
    echo -e "${YELLOW}WARNING: $1${NC}" >&2
}

log_success() {
    echo -e "${GREEN}SUCCESS: $1${NC}" >&2
}

log_debug() {
    [ "${DEBUG:-0}" = "1" ] && echo -e "DEBUG: $1" >&2
}

# Validate inputs
validate_inputs() {
    if [ -z "${HUBSPOT_ACCESS_TOKEN:-}" ]; then
        log_error "HUBSPOT_ACCESS_TOKEN environment variable is required"
        exit 1
    fi
    
    if [ $# -lt 2 ]; then
        log_error "Missing required arguments"
        show_help
        exit 1
    fi
    
    local method="$1"
    if [[ ! "$method" =~ ^(GET|POST|PUT|PATCH|DELETE)$ ]]; then
        log_error "Invalid HTTP method: $method"
        exit 1
    fi
}

# Check rate limits from headers
check_rate_limits() {
    local headers_file="$1"
    
    local remaining=$(grep -i "x-hubspot-ratelimit-remaining" "$headers_file" 2>/dev/null | cut -d':' -f2 | tr -d ' \r\n' || echo "")
    local daily_remaining=$(grep -i "x-hubspot-ratelimit-daily-remaining" "$headers_file" 2>/dev/null | cut -d':' -f2 | tr -d ' \r\n' || echo "")
    
    if [ -n "$remaining" ] && [ "$remaining" -lt 10 ]; then
        log_warning "Low rate limit: $remaining requests remaining"
    fi
    
    if [ -n "$daily_remaining" ] && [ "$daily_remaining" -lt 1000 ]; then
        log_warning "Low daily limit: $daily_remaining requests remaining"
    fi
    
    log_debug "Rate limits - Remaining: ${remaining:-unknown}, Daily: ${daily_remaining:-unknown}"
}

# Exponential backoff retry function
make_request_with_retry() {
    local method="$1"
    local url="$2"
    local data="$3"
    local headers_file="$4"
    local retry_count=0
    local delay=$RETRY_DELAY
    
    while [ $retry_count -lt $MAX_RETRIES ]; do
        log_debug "Attempt $((retry_count + 1))/$MAX_RETRIES: $method $url"
        
        # Build curl command
        local curl_cmd=(
            "curl"
            "-s"
            "-w" "%{http_code}"
            "-H" "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN"
            "-H" "Content-Type: application/json"
            "-D" "$headers_file"
            "-X" "$method"
        )
        
        # Add data for POST/PUT/PATCH
        if [ -n "$data" ] && [[ "$method" =~ ^(POST|PUT|PATCH)$ ]]; then
            curl_cmd+=("-d" "$data")
        fi
        
        curl_cmd+=("$url")
        
        # Make request
        local response
        response=$("${curl_cmd[@]}" 2>/dev/null)
        local curl_exit_code=$?
        
        if [ $curl_exit_code -ne 0 ]; then
            log_error "Curl failed with exit code $curl_exit_code"
            retry_count=$((retry_count + 1))
            sleep $delay
            delay=$((delay * 2))
            continue
        fi
        
        # Extract HTTP status and body
        local http_code="${response: -3}"
        local body="${response%???}"
        
        log_debug "HTTP Status: $http_code"
        
        case $http_code in
            200|201|202|204)
                log_success "Request successful (HTTP $http_code)"
                check_rate_limits "$headers_file"
                echo "$body"
                return 0
                ;;
            400)
                log_error "Bad Request (HTTP 400)"
                echo "$body" >&2
                return 1
                ;;
            401)
                log_error "Unauthorized (HTTP 401) - Check your access token"
                echo "$body" >&2
                return 1
                ;;
            403)
                log_error "Forbidden (HTTP 403) - Insufficient permissions"
                echo "$body" >&2
                return 1
                ;;
            404)
                log_error "Not Found (HTTP 404)"
                echo "$body" >&2
                return 1
                ;;
            409)
                log_error "Conflict (HTTP 409) - Resource already exists or conflict"
                echo "$body" >&2
                return 1
                ;;
            429)
                log_warning "Rate limited (HTTP 429) - Retrying in ${delay}s"
                retry_count=$((retry_count + 1))
                sleep $delay
                delay=$((delay * 2))
                continue
                ;;
            5*)
                log_warning "Server error (HTTP $http_code) - Retrying in ${delay}s"
                retry_count=$((retry_count + 1))
                sleep $delay
                delay=$((delay * 2))
                continue
                ;;
            *)
                log_error "Unexpected HTTP status: $http_code"
                echo "$body" >&2
                return 1
                ;;
        esac
    done
    
    log_error "Max retries exceeded"
    return 1
}

# Validate JSON data
validate_json() {
    local json_data="$1"
    
    if [ -n "$json_data" ]; then
        if ! echo "$json_data" | jq . >/dev/null 2>&1; then
            log_error "Invalid JSON data provided"
            return 1
        fi
    fi
    
    return 0
}

# Format JSON output
format_output() {
    local raw_output="$1"
    
    if [ -n "$raw_output" ] && echo "$raw_output" | jq . >/dev/null 2>&1; then
        echo "$raw_output" | jq .
    else
        echo "$raw_output"
    fi
}

# Main function
main() {
    # Show help if requested
    if [[ "${1:-}" == "-h" ]] || [[ "${1:-}" == "--help" ]]; then
        show_help
        exit 0
    fi
    
    # Validate inputs
    validate_inputs "$@"
    
    local method="$1"
    local endpoint="$2"
    local data="${3:-}"
    
    # Validate JSON if provided
    if ! validate_json "$data"; then
        exit 1
    fi
    
    # Build full URL
    local url="$HUBSPOT_BASE_URL$endpoint"
    
    # Create temporary file for headers
    local headers_file
    headers_file=$(mktemp)
    
    # Cleanup function
    cleanup() {
        rm -f "$headers_file"
    }
    trap cleanup EXIT
    
    # Make the request
    log_debug "Making request: $method $url"
    if [ -n "$data" ]; then
        log_debug "Data: $data"
    fi
    
    local response
    if response=$(make_request_with_retry "$method" "$url" "$data" "$headers_file"); then
        # Format and output response
        format_output "$response"
        exit 0
    else
        exit 1
    fi
}

# Run main function with all arguments
main "$@"