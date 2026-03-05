#!/bin/bash
# OPNsense API Helper Script
# Usage: ./opnsense-api.sh <command> [options]

# Configuration - adjust these for your environment
OPNSENSE_HOST="${OPNSENSE_HOST:-192.168.1.1}"
OPNSENSE_PORT="${OPNSENSE_PORT:-443}"
OPNSENSE_KEY="${OPNSENSE_KEY:-}"
OPNSENSE_SECRET="${OPNSENSE_SECRET:-}"
OPNSENSE_INSECURE="${OPNSENSE_INSECURE:-false}"

# If keys not set, try to read from environment file
if [[ -z "$OPNSENSE_KEY" && -f ~/.opnsense/credentials ]]; then
    source ~/.opnsense/credentials
fi

# Parse arguments
INSECURE_FLAG=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --insecure|-k)
            OPNSENSE_INSECURE="true"
            shift
            ;;
        *)
            break
            ;;
    esac
done

# Set curl flags based on security preference
if [[ "$OPNSENSE_INSECURE" == "true" ]]; then
    INSECURE_FLAG="-k"
fi

show_help() {
    cat << EOF
OPNsense API Helper

Usage: $0 [options] <command> [args]

Options:
    --insecure, -k      Disable SSL certificate validation (NOT recommended)

Commands:
    get <endpoint>              Make GET request to endpoint
    post <endpoint> [data]      Make POST request with JSON data
    status                      Get system status
    firmware-status             Get firmware status
    interfaces                  List interface configuration
    firewall-stats              Get firewall statistics
    suricata-status             Get Suricata status
    unbound-stats               Get Unbound DNS statistics
    reboot                      Reboot system
    version                     Show OPNsense version
    help                        Show this help

Environment Variables:
    OPNSENSE_HOST       OPNsense IP/hostname (default: 192.168.1.1)
    OPNSENSE_PORT       HTTPS port (default: 443)
    OPNSENSE_KEY        API key
    OPNSENSE_SECRET     API secret
    OPNSENSE_INSECURE   Set to 'true' to disable SSL verification (default: false)

Credentials File:
    Create ~/.opnsense/credentials with:
    OPNSENSE_KEY=your_key
    OPNSENSE_SECRET=your_secret

Security Note:
    By default, SSL certificate validation is ENABLED.
    Use --insecure or set OPNSENSE_INSECURE=true only for development
    or when using self-signed certificates in internal networks.

Examples:
    $0 status
    $0 get /api/core/system/status
    $0 firmware-status
    $0 --insecure get /api/core/system/status
    $0 post /api/core/firmware/update '{"upgrade":true}'
EOF
}

make_request() {
    local method="$1"
    local endpoint="$2"
    local data="${3:-}"
    
    if [[ -z "$OPNSENSE_KEY" || -z "$OPNSENSE_SECRET" ]]; then
        echo "Error: API credentials not configured"
        echo "Set OPNSENSE_KEY and OPNSENSE_SECRET environment variables"
        echo "Or create ~/.opnsense/credentials file"
        exit 1
    fi
    
    local url="https://${OPNSENSE_HOST}:${OPNSENSE_PORT}${endpoint}"
    
    if [[ "$method" == "GET" ]]; then
        curl -s $INSECURE_FLAG -u "${OPNSENSE_KEY}:${OPNSENSE_SECRET}" \
            -H "Accept: application/json" \
            "$url" | jq . 2>/dev/null || curl -s $INSECURE_FLAG -u "${OPNSENSE_KEY}:${OPNSENSE_SECRET}" "$url"
    else
        curl -s $INSECURE_FLAG -u "${OPNSENSE_KEY}:${OPNSENSE_SECRET}" \
            -H "Content-Type: application/json" \
            -H "Accept: application/json" \
            -X POST \
            -d "$data" \
            "$url" | jq . 2>/dev/null || curl -s $INSECURE_FLAG -u "${OPNSENSE_KEY}:${OPNSENSE_SECRET}" -X POST -d "$data" "$url"
    fi
}

case "${1:-}" in
    get)
        make_request "GET" "$2"
        ;;
    post)
        make_request "POST" "$2" "$3"
        ;;
    status)
        make_request "GET" "/api/core/system/status"
        ;;
    firmware-status)
        make_request "GET" "/api/core/firmware/status"
        ;;
    interfaces)
        make_request "GET" "/api/diagnostics/interface/getInterfaceConfig"
        ;;
    firewall-stats)
        make_request "GET" "/api/diagnostics/firewall/pfstatists"
        ;;
    suricata-status)
        make_request "GET" "/api/ids/service/status"
        ;;
    unbound-stats)
        make_request "GET" "/api/unbound/diagnostics/stats"
        ;;
    reboot)
        echo "Rebooting OPNsense..."
        make_request "POST" "/api/core/system/reboot"
        ;;
    version)
        make_request "GET" "/api/core/firmware/status" | grep -o '"version":"[^"]*"' || echo "Version unknown"
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "Unknown command: ${1:-}"
        show_help
        exit 1
        ;;
esac
