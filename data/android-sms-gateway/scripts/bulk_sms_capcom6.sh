#!/usr/bin/env bash
#
# bulk_sms_capcom6.sh - Send SMS to multiple recipients (capcom6/android-sms-gateway)
#
# Usage:
#   ./bulk_sms_capcom6.sh --recipients "+1234567890,+0987654321" --message "Broadcast"
#   ./bulk_sms_capcom6.sh --recipients-file ./contacts.txt --message "Alert"
#

set -euo pipefail

# Defaults
TIMEOUT="${SMS_GATEWAY_TIMEOUT:-30}"
CONFIG_FILE=""
GATEWAY_URL=""
GATEWAY_USER=""
GATEWAY_PASS=""
RECIPIENTS=""
RECIPIENTS_FILE=""
MESSAGE=""
SIM_SLOT=""
DELAY=1  # Delay between messages in seconds
SERVER_MODE="local"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

usage() {
    cat <<EOF
Send SMS to multiple recipients via capcom6/android-sms-gateway

Usage:
  $0 --recipients <numbers> --message <text> [options]
  $0 --recipients-file <file> --message <text> [options]

Options:
  --recipients <nums>    Comma-separated phone numbers (e.g., "+1234567890,+0987654321")
  --recipients-file <f>  File with one number per line
  --message <text>       Message content
  --delay <seconds>      Delay between messages (default: 1)
  --config <file>        Path to config file (JSON)
  --url <gateway-url>    Gateway URL (overrides config/env)
  --user <username>      Basic auth username
  --pass <password>      Basic auth password
  --mode <local|cloud>   Server mode: local or cloud
  --sim <slot>           SIM slot number (1 or 2)
  --dry-run              Show what would be sent
  --verbose              Show detailed output
  --help                 Show this help

Environment variables:
  SMS_GATEWAY_URL        Gateway base URL
  SMS_GATEWAY_USER       Basic auth username
  SMS_GATEWAY_PASS       Basic auth password
  SMS_GATEWAY_TIMEOUT    Request timeout in seconds

Examples:
  $0 --recipients "+1234567890,+0987654321" --message "Meeting reminder"
  $0 --recipients-file ./team-contacts.txt --message "Security alert"
  $0 --mode cloud --recipients "+1234567890" --message "Test" --dry-run

⚠️  Note: capcom6 API supports multiple phone numbers in a single request!
   For bulk sends, consider using the multi-recipient format instead of
   sending individual messages.

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

log_progress() {
    local current=$1
    local total=$2
    local percent=$((current * 100 / total))
    echo -ne "${BLUE}[${current}/${total}] (${percent}%)${NC} "
}

# Parse arguments
DRY_RUN=0
MULTI_RECIPIENT=0  # Use capcom6's multi-recipient feature

while [[ $# -gt 0 ]]; do
    case $1 in
        --recipients)
            RECIPIENTS="$2"
            shift 2
            ;;
        --recipients-file)
            RECIPIENTS_FILE="$2"
            shift 2
            ;;
        --message)
            MESSAGE="$2"
            shift 2
            ;;
        --delay)
            DELAY="$2"
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
        --mode)
            SERVER_MODE="$2"
            shift 2
            ;;
        --sim)
            SIM_SLOT="$2"
            shift 2
            ;;
        --multi)
            MULTI_RECIPIENT=1
            shift
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

# Validate arguments
if [[ -z "$MESSAGE" ]]; then
    log_error "Missing required argument: --message"
    usage
fi

if [[ -z "$RECIPIENTS" && -z "$RECIPIENTS_FILE" ]]; then
    log_error "Must specify --recipients or --recipients-file"
    usage
fi

if [[ -n "$RECIPIENTS" && -n "$RECIPIENTS_FILE" ]]; then
    log_error "Cannot specify both --recipients and --recipients-file"
    usage
fi

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

# Get recipient list
get_recipients() {
    local numbers=()
    
    if [[ -n "$RECIPIENTS_FILE" ]]; then
        if [[ ! -f "$RECIPIENTS_FILE" ]]; then
            log_error "Recipients file not found: $RECIPIENTS_FILE"
            exit 1
        fi
        
        while IFS= read -r line || [[ -n "$line" ]]; do
            # Skip empty lines and comments
            line=$(echo "$line" | sed 's/#.*//' | tr -d '[:space:]')
            if [[ -n "$line" ]]; then
                numbers+=("$line")
            fi
        done < "$RECIPIENTS_FILE"
    else
        # Parse comma-separated list
        IFS=',' read -ra numbers <<< "$RECIPIENTS"
    fi
    
    # Validate and clean numbers
    local valid_numbers=()
    for num in "${numbers[@]}"; do
        # Basic validation: should start with + or contain digits
        if [[ "$num" =~ ^\+?[0-9]+$ ]]; then
            # Ensure starts with +
            if [[ ! "$num" =~ ^\+ ]]; then
                num="+$num"
            fi
            valid_numbers+=("$num")
        else
            log_warn "Invalid number format: $num (skipping)"
        fi
    done
    
    if [[ ${#valid_numbers[@]} -eq 0 ]]; then
        log_error "No valid recipients found"
        exit 1
    fi
    
    printf '%s\n' "${valid_numbers[@]}"
}

# Send SMS to multiple recipients in single request (capcom6 feature!)
send_sms_multi() {
    local -a phones=("$@")
    local url="${GATEWAY_URL}/message"
    
    # Build phone numbers JSON array
    local phones_json=""
    for phone in "${phones[@]}"; do
        if [[ -n "$phones_json" ]]; then
            phones_json="${phones_json},"
        fi
        phones_json="${phones_json}\"${phone}\""
    done
    
    # Build payload for capcom6 multi-recipient
    # Format: {"textMessage": {"text": "..."}, "phoneNumbers": ["+1234", "+5678"]}
    local payload="{\"textMessage\":{\"text\":\"${MESSAGE}\"},\"phoneNumbers\":[${phones_json}]}"
    if [[ -n "$SIM_SLOT" ]]; then
        payload="${payload},\"simSlot\":${SIM_SLOT}"
    fi
    payload="${payload}}"
    
    log_verbose "POST $url"
    log_verbose "Payload: $payload"
    
    if [[ "${DRY_RUN:-0}" == "1" ]]; then
        echo "[DRY RUN] Would send to ${#phones[@]} recipients:"
        for phone in "${phones[@]}"; do
            echo "  - $phone"
        done
        echo "  Message: $MESSAGE"
        return 0
    fi
    
    local response
    local http_code
    
    response=$(curl -s -w "\n%{http_code}" \
        -X POST "$url" \
        -u "${GATEWAY_USER}:${GATEWAY_PASS}" \
        -H "Content-Type: application/json" \
        -d "$payload" \
        --max-time "$TIMEOUT" \
        2>/dev/null) || {
        return 1
    }
    
    http_code=$(echo "$response" | tail -n1)
    
    if [[ "$http_code" == "200" || "$http_code" == "201" || "$http_code" == "202" ]]; then
        return 0
    else
        return 1
    fi
}

# Send single SMS (fallback)
send_single() {
    local to="$1"
    local url="${GATEWAY_URL}/message"
    
    local payload="{\"textMessage\":{\"text\":\"${MESSAGE}\"},\"phoneNumbers\":[\"${to}\"]}"
    if [[ -n "$SIM_SLOT" ]]; then
        payload="${payload},\"simSlot\":${SIM_SLOT}"
    fi
    payload="${payload}}"
    
    local response
    local http_code
    
    response=$(curl -s -w "\n%{http_code}" \
        -X POST "$url" \
        -u "${GATEWAY_USER}:${GATEWAY_PASS}" \
        -H "Content-Type: application/json" \
        -d "$payload" \
        --max-time "$TIMEOUT" \
        2>/dev/null) || {
        return 1
    }
    
    http_code=$(echo "$response" | tail -n1)
    
    if [[ "$http_code" == "200" || "$http_code" == "201" || "$http_code" == "202" ]]; then
        return 0
    else
        return 1
    fi
}

# Main
main() {
    load_config
    
    # Get recipient list
    mapfile -t recipients < <(get_recipients)
    local total=${#recipients[@]}
    
    log_info "Preparing to send to $total recipient(s)"
    log_verbose "Server mode: $SERVER_MODE"
    log_verbose "Multi-recipient mode: $MULTI_RECIPIENT"
    
    if [[ "$DRY_RUN" == "1" ]]; then
        echo ""
        echo "[DRY RUN] Would send to:"
        for num in "${recipients[@]}"; do
            echo "  - $num"
        done
        echo ""
        echo "Message: $MESSAGE"
        echo ""
        log_info "Dry run complete"
        exit 0
    fi
    
    # capcom6 supports multiple recipients in single request!
    if [[ "$MULTI_RECIPIENT" == "1" ]]; then
        log_info "Using multi-recipient mode (single API call)"
        if send_sms_multi "${recipients[@]}"; then
            log_info "✓ Bulk send complete: $total sent"
            exit 0
        else
            log_error "❌ Bulk send failed"
            exit 1
        fi
    fi
    
    # Individual sends (fallback or for better error tracking)
    local sent=0
    local failed=0
    
    echo ""
    for i in "${!recipients[@]}"; do
        local num="${recipients[$i]}"
        local current=$((i + 1))
        
        log_progress "$current" "$total"
        
        if send_single "$num" "$MESSAGE"; then
            echo -e "${GREEN}✓${NC} $num"
            ((sent++))
        else
            echo -e "${RED}✗${NC} $num"
            ((failed++))
        fi
        
        # Delay between messages (except after last)
        if [[ $i -lt $((total - 1)) && "$DELAY" -gt 0 ]]; then
            sleep "$DELAY"
        fi
    done
    
    echo ""
    log_info "Bulk send complete: $sent sent, $failed failed"
    
    if [[ $failed -gt 0 ]]; then
        exit 1
    fi
}

main "$@"
