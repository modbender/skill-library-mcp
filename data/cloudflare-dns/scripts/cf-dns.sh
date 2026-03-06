#!/usr/bin/env bash
# Cloudflare DNS Management Script
# Requires: CF_API_TOKEN (and optionally CF_ZONE_ID)

set -euo pipefail

API_BASE="https://api.cloudflare.com/client/v4"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

err() { echo -e "${RED}Error: $1${NC}" >&2; exit 1; }
info() { echo -e "${GREEN}$1${NC}" >&2; }
warn() { echo -e "${YELLOW}$1${NC}" >&2; }

usage() {
    cat <<EOF
Usage: cf-dns.sh <command> [options]

Commands:
  zones                         List all zones
  list <zone_id>                List DNS records (or --domain <domain>)
  get <zone_id> <record_id>     Get specific record
  create <zone_id> [opts]       Create DNS record
  update <zone_id> <id> [opts]  Update DNS record
  delete <zone_id> <record_id>  Delete DNS record
  ddns <zone_id> --name <name>  Update A record to current public IP

Options:
  --domain <domain>     Use domain name instead of zone_id (auto-lookup)
  --type <type>         Record type: A, AAAA, CNAME, TXT, MX, etc.
  --name <name>         Record name (@ for root, or subdomain)
  --content <value>     Record content (IP, hostname, text)
  --ttl <seconds>       TTL in seconds (1 = auto)
  --priority <num>      Priority for MX records
  --proxied             Enable Cloudflare proxy (orange cloud)
  --no-proxied          Disable Cloudflare proxy

Environment:
  CF_API_TOKEN          Cloudflare API token (required)
  CF_ZONE_ID            Default zone ID (optional)

Examples:
  cf-dns.sh zones
  cf-dns.sh list --domain example.com
  cf-dns.sh create abc123 --type A --name www --content 1.2.3.4 --proxied
  cf-dns.sh ddns --domain example.com --name home
EOF
    exit 1
}

# Check for required token
[[ -z "${CF_API_TOKEN:-}" ]] && err "CF_API_TOKEN not set"

cf_api() {
    local method="$1"
    local endpoint="$2"
    shift 2
    local data="${1:-}"
    
    local args=(-s -X "$method" -H "Authorization: Bearer $CF_API_TOKEN" -H "Content-Type: application/json")
    [[ -n "$data" ]] && args+=(-d "$data")
    
    curl "${args[@]}" "${API_BASE}${endpoint}"
}

get_zone_id() {
    local domain="$1"
    local result
    result=$(cf_api GET "/zones?name=$domain")
    local zone_id
    zone_id=$(echo "$result" | jq -r '.result[0].id // empty')
    [[ -z "$zone_id" ]] && err "Zone not found for domain: $domain"
    echo "$zone_id"
}

get_public_ip() {
    curl -s https://api.ipify.org || curl -s https://ifconfig.me || err "Could not get public IP"
}

find_record_id() {
    local zone_id="$1"
    local name="$2"
    local type="${3:-A}"
    local result
    result=$(cf_api GET "/zones/$zone_id/dns_records?type=$type&name=$name")
    echo "$result" | jq -r '.result[0].id // empty'
}

cmd_zones() {
    local result
    result=$(cf_api GET "/zones?per_page=50")
    echo "$result" | jq -r '.result[] | "\(.id)\t\(.name)\t\(.status)"' 2>/dev/null || echo "$result"
}

cmd_list() {
    local zone_id="$1"
    local result
    result=$(cf_api GET "/zones/$zone_id/dns_records?per_page=100")
    echo "$result" | jq -r '.result[] | "\(.type)\t\(.name)\t\(.content)\t\(.proxied)\t\(.id)"' 2>/dev/null || echo "$result"
}

cmd_get() {
    local zone_id="$1"
    local record_id="$2"
    cf_api GET "/zones/$zone_id/dns_records/$record_id" | jq .
}

cmd_create() {
    local zone_id="$1"
    shift
    
    local type="" name="" content="" ttl="1" priority="" proxied="false"
    
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --type) type="$2"; shift 2 ;;
            --name) name="$2"; shift 2 ;;
            --content) content="$2"; shift 2 ;;
            --ttl) ttl="$2"; shift 2 ;;
            --priority) priority="$2"; shift 2 ;;
            --proxied) proxied="true"; shift ;;
            --no-proxied) proxied="false"; shift ;;
            *) shift ;;
        esac
    done
    
    [[ -z "$type" ]] && err "Missing --type"
    [[ -z "$name" ]] && err "Missing --name"
    [[ -z "$content" ]] && err "Missing --content"
    
    local data
    data=$(jq -n \
        --arg type "$type" \
        --arg name "$name" \
        --arg content "$content" \
        --argjson ttl "$ttl" \
        --argjson proxied "$proxied" \
        '{type: $type, name: $name, content: $content, ttl: $ttl, proxied: $proxied}')
    
    # Add priority for MX records
    if [[ -n "$priority" ]]; then
        data=$(echo "$data" | jq --argjson priority "$priority" '. + {priority: $priority}')
    fi
    
    local result
    result=$(cf_api POST "/zones/$zone_id/dns_records" "$data")
    
    if echo "$result" | jq -e '.success' >/dev/null 2>&1; then
        info "Record created successfully"
        echo "$result" | jq '.result | {id, type, name, content, proxied, ttl}'
    else
        echo "$result" | jq .
        exit 1
    fi
}

cmd_update() {
    local zone_id="$1"
    local record_id="$2"
    shift 2
    
    local content="" ttl="" proxied=""
    
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --content) content="$2"; shift 2 ;;
            --ttl) ttl="$2"; shift 2 ;;
            --proxied) proxied="true"; shift ;;
            --no-proxied) proxied="false"; shift ;;
            *) shift ;;
        esac
    done
    
    # Get existing record
    local existing
    existing=$(cf_api GET "/zones/$zone_id/dns_records/$record_id")
    
    # Build update payload
    local data
    data=$(echo "$existing" | jq '.result | {type, name, content, ttl, proxied}')
    
    [[ -n "$content" ]] && data=$(echo "$data" | jq --arg c "$content" '.content = $c')
    [[ -n "$ttl" ]] && data=$(echo "$data" | jq --argjson t "$ttl" '.ttl = $t')
    [[ -n "$proxied" ]] && data=$(echo "$data" | jq --argjson p "$proxied" '.proxied = $p')
    
    local result
    result=$(cf_api PUT "/zones/$zone_id/dns_records/$record_id" "$data")
    
    if echo "$result" | jq -e '.success' >/dev/null 2>&1; then
        info "Record updated successfully"
        echo "$result" | jq '.result | {id, type, name, content, proxied, ttl}'
    else
        echo "$result" | jq .
        exit 1
    fi
}

cmd_delete() {
    local zone_id="$1"
    local record_id="$2"
    
    local result
    result=$(cf_api DELETE "/zones/$zone_id/dns_records/$record_id")
    
    if echo "$result" | jq -e '.success' >/dev/null 2>&1; then
        info "Record deleted successfully"
    else
        echo "$result" | jq .
        exit 1
    fi
}

cmd_ddns() {
    local zone_id="${1:-}"
    shift || true
    
    local name="" domain=""
    
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --name) name="$2"; shift 2 ;;
            --domain) domain="$2"; shift 2 ;;
            *) shift ;;
        esac
    done
    
    [[ -z "$name" ]] && err "Missing --name for DDNS"
    
    # Get zone ID from domain if needed
    if [[ -z "$zone_id" && -n "$domain" ]]; then
        zone_id=$(get_zone_id "$domain")
    elif [[ -z "$zone_id" && -n "${CF_ZONE_ID:-}" ]]; then
        zone_id="$CF_ZONE_ID"
    fi
    [[ -z "$zone_id" ]] && err "No zone_id provided (use --domain or CF_ZONE_ID)"
    
    # Get domain name for full record name
    if [[ -z "$domain" ]]; then
        domain=$(cf_api GET "/zones/$zone_id" | jq -r '.result.name')
    fi
    
    local full_name
    if [[ "$name" == "@" ]]; then
        full_name="$domain"
    else
        full_name="${name}.${domain}"
    fi
    
    # Get current public IP
    local ip
    ip=$(get_public_ip)
    info "Current public IP: $ip"
    
    # Find existing record
    local record_id
    record_id=$(find_record_id "$zone_id" "$full_name" "A")
    
    if [[ -n "$record_id" ]]; then
        # Check if IP changed
        local current_content
        current_content=$(cf_api GET "/zones/$zone_id/dns_records/$record_id" | jq -r '.result.content')
        if [[ "$current_content" == "$ip" ]]; then
            info "IP unchanged ($ip), skipping update"
            exit 0
        fi
        info "Updating existing record $full_name"
        cmd_update "$zone_id" "$record_id" --content "$ip"
    else
        info "Creating new A record for $full_name"
        cmd_create "$zone_id" --type A --name "$name" --content "$ip" --ttl 300
    fi
}

# Parse global options and command
zone_id="${CF_ZONE_ID:-}"
domain=""

[[ $# -eq 0 ]] && usage
command="$1"
shift

# Handle --domain flag before zone_id
args=()
while [[ $# -gt 0 ]]; do
    case "$1" in
        --domain)
            domain="$2"
            zone_id=$(get_zone_id "$domain")
            shift 2
            ;;
        *)
            args+=("$1")
            shift
            ;;
    esac
done
set -- "${args[@]+"${args[@]}"}"

case "$command" in
    zones)
        cmd_zones
        ;;
    list)
        zone_id="${1:-$zone_id}"
        [[ -z "$zone_id" ]] && err "No zone_id provided"
        cmd_list "$zone_id"
        ;;
    get)
        zone_id="${1:-$zone_id}"
        record_id="${2:-}"
        [[ -z "$zone_id" ]] && err "No zone_id provided"
        [[ -z "$record_id" ]] && err "No record_id provided"
        cmd_get "$zone_id" "$record_id"
        ;;
    create)
        zone_id="${1:-$zone_id}"
        [[ -z "$zone_id" ]] && err "No zone_id provided"
        shift || true
        cmd_create "$zone_id" "$@"
        ;;
    update)
        zone_id="${1:-$zone_id}"
        record_id="${2:-}"
        [[ -z "$zone_id" ]] && err "No zone_id provided"
        [[ -z "$record_id" ]] && err "No record_id provided"
        shift 2 || true
        cmd_update "$zone_id" "$record_id" "$@"
        ;;
    delete)
        zone_id="${1:-$zone_id}"
        record_id="${2:-}"
        [[ -z "$zone_id" ]] && err "No zone_id provided"
        [[ -z "$record_id" ]] && err "No record_id provided"
        cmd_delete "$zone_id" "$record_id"
        ;;
    ddns)
        cmd_ddns "$zone_id" --name "${1:-}" "$@"
        ;;
    help|--help|-h)
        usage
        ;;
    *)
        err "Unknown command: $command"
        ;;
esac
