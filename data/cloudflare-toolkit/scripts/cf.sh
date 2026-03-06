#!/usr/bin/env bash
# cf — Cloudflare API wrapper for OpenClaw
# Usage: cf <command> [args...]
#
# Requires: CLOUDFLARE_API_TOKEN environment variable
#           CLOUDFLARE_ACCOUNT_ID for account-level operations (optional)

set -euo pipefail

CF_API="https://api.cloudflare.com/client/v4"
TOKEN="${CLOUDFLARE_API_TOKEN:?Set CLOUDFLARE_API_TOKEN}"

# --- helpers ---

_curl() {
  curl -sS -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" "$@"
}

_get()    { _curl "$CF_API$1"; }
_post()   { _curl -X POST -d "$2" "$CF_API$1"; }
_put()    { _curl -X PUT -d "$2" "$CF_API$1"; }
_patch()  { _curl -X PATCH -d "$2" "$CF_API$1"; }
_delete() { _curl -X DELETE "$CF_API$1"; }

_jq_check() {
  if ! command -v jq &>/dev/null; then
    cat  # passthrough raw JSON
  else
    jq "$@"
  fi
}

# --- zones ---

cmd_zones_list() {
  local args=""
  [[ "${1:-}" ]] && args="?name=$1"
  _get "/zones$args" | _jq_check '.result[] | {id, name, status, name_servers}'
}

cmd_zone_get() {
  local zone_id="${1:?Usage: cf zone-get <zone_id>}"
  _get "/zones/$zone_id" | _jq_check '.result | {id, name, status, name_servers, plan: .plan.name}'
}

cmd_zone_id() {
  local domain="${1:?Usage: cf zone-id <domain>}"
  _get "/zones?name=$domain" | _jq_check -r '.result[0].id // empty'
}

# --- DNS records ---

cmd_dns_list() {
  local zone_id="${1:?Usage: cf dns-list <zone_id> [type] [name]}"
  local type="${2:-}" name="${3:-}"
  local qs="?per_page=100"
  [[ "$type" ]] && qs+="&type=$type"
  [[ "$name" ]] && qs+="&name=$name"
  _get "/zones/$zone_id/dns_records$qs" | _jq_check '.result[] | {id, type, name, content, proxied, ttl}'
}

cmd_dns_create() {
  local zone_id="${1:?Usage: cf dns-create <zone_id> <type> <name> <content> [proxied] [ttl]}"
  local type="${2:?}" name="${3:?}" content="${4:?}"
  local proxied="${5:-false}" ttl="${6:-1}"
  local data
  data=$(jq -n --arg t "$type" --arg n "$name" --arg c "$content" \
    --argjson p "$proxied" --argjson ttl "$ttl" \
    '{type:$t, name:$n, content:$c, proxied:$p, ttl:$ttl}')
  _post "/zones/$zone_id/dns_records" "$data" | _jq_check '.result | {id, type, name, content, proxied, ttl}'
}

cmd_dns_update() {
  local zone_id="${1:?Usage: cf dns-update <zone_id> <record_id> <type> <name> <content> [proxied] [ttl]}"
  local record_id="${2:?}" type="${3:?}" name="${4:?}" content="${5:?}"
  local proxied="${6:-false}" ttl="${7:-1}"
  local data
  data=$(jq -n --arg t "$type" --arg n "$name" --arg c "$content" \
    --argjson p "$proxied" --argjson ttl "$ttl" \
    '{type:$t, name:$n, content:$c, proxied:$p, ttl:$ttl}')
  _put "/zones/$zone_id/dns_records/$record_id" "$data" | _jq_check '.result | {id, type, name, content, proxied, ttl}'
}

cmd_dns_delete() {
  local zone_id="${1:?Usage: cf dns-delete <zone_id> <record_id>}"
  local record_id="${2:?}"
  _delete "/zones/$zone_id/dns_records/$record_id" | _jq_check '.'
}

cmd_dns_export() {
  local zone_id="${1:?Usage: cf dns-export <zone_id>}"
  _get "/zones/$zone_id/dns_records?per_page=500" | _jq_check '[.result[] | {type, name, content, proxied, ttl, priority}]'
}

cmd_dns_import() {
  local zone_id="${1:?Usage: cf dns-import <zone_id> <file.json>}"
  local file="${2:?}"
  local count=0
  while IFS= read -r rec; do
    _post "/zones/$zone_id/dns_records" "$rec" | _jq_check '.result | {id, type, name, content}' 2>/dev/null
    ((count++))
  done < <(jq -c '.[]' "$file")
  echo "Imported $count records" >&2
}

# --- zone settings ---

cmd_settings_list() {
  local zone_id="${1:?Usage: cf settings-list <zone_id>}"
  _get "/zones/$zone_id/settings" | _jq_check '.result[] | {id, value}'
}

cmd_setting_get() {
  local zone_id="${1:?Usage: cf setting-get <zone_id> <setting_id>}"
  local setting="${2:?}"
  _get "/zones/$zone_id/settings/$setting" | _jq_check '.result | {id, value}'
}

cmd_setting_set() {
  local zone_id="${1:?Usage: cf setting-set <zone_id> <setting_id> <value>}"
  local setting="${2:?}" value="${3:?}"
  local data
  data=$(jq -n --arg v "$value" '{value:$v}')
  _patch "/zones/$zone_id/settings/$setting" "$data" | _jq_check '.result | {id, value}'
}

# --- SSL ---

cmd_ssl_get() {
  local zone_id="${1:?Usage: cf ssl-get <zone_id>}"
  _get "/zones/$zone_id/settings/ssl" | _jq_check '.result | {id, value}'
}

cmd_ssl_set() {
  local zone_id="${1:?Usage: cf ssl-set <zone_id> <off|flexible|full|strict>}"
  local mode="${2:?}"
  cmd_setting_set "$zone_id" "ssl" "$mode"
}

# --- cache ---

cmd_cache_purge() {
  local zone_id="${1:?Usage: cf cache-purge <zone_id> [url1 url2 ...]}"
  shift
  local data
  if [[ $# -eq 0 ]]; then
    data='{"purge_everything":true}'
  else
    data=$(printf '%s\n' "$@" | jq -R . | jq -sc '{files:.}')
  fi
  _post "/zones/$zone_id/purge_cache" "$data" | _jq_check '.result'
}

# --- page rules ---

cmd_pagerules_list() {
  local zone_id="${1:?Usage: cf pagerules-list <zone_id>}"
  _get "/zones/$zone_id/pagerules" | _jq_check '.result[] | {id, status, targets, actions}'
}

# --- firewall rules (WAF custom rules) ---

cmd_firewall_list() {
  local zone_id="${1:?Usage: cf firewall-list <zone_id>}"
  _get "/zones/$zone_id/firewall/rules" | _jq_check '.result[] | {id, description, action, filter: .filter.expression}'
}

# --- tunnels ---

cmd_tunnels_list() {
  local acct="${CLOUDFLARE_ACCOUNT_ID:?Set CLOUDFLARE_ACCOUNT_ID for tunnel ops}"
  _get "/accounts/$acct/cfd_tunnel" | _jq_check '.result[] | {id, name, status, created_at}'
}

cmd_tunnel_get() {
  local acct="${CLOUDFLARE_ACCOUNT_ID:?Set CLOUDFLARE_ACCOUNT_ID}"
  local tunnel_id="${1:?Usage: cf tunnel-get <tunnel_id>}"
  _get "/accounts/$acct/cfd_tunnel/$tunnel_id" | _jq_check '.result'
}

cmd_tunnel_create() {
  local acct="${CLOUDFLARE_ACCOUNT_ID:?Set CLOUDFLARE_ACCOUNT_ID}"
  local name="${1:?Usage: cf tunnel-create <name>}"
  local secret
  secret=$(openssl rand -base64 32)
  local data
  data=$(jq -n --arg n "$name" --arg s "$secret" '{name:$n, tunnel_secret:$s, config_src:"cloudflare"}')
  _post "/accounts/$acct/cfd_tunnel" "$data" | _jq_check '.result | {id, name, status, created_at}'
}

cmd_tunnel_delete() {
  local acct="${CLOUDFLARE_ACCOUNT_ID:?Set CLOUDFLARE_ACCOUNT_ID}"
  local tunnel_id="${1:?Usage: cf tunnel-delete <tunnel_id>}"
  _delete "/accounts/$acct/cfd_tunnel/$tunnel_id" | _jq_check '.'
}

# --- token verify ---

cmd_verify() {
  _get "/user/tokens/verify" | _jq_check '.result'
}

# --- analytics ---

cmd_analytics() {
  local zone_id="${1:?Usage: cf analytics <zone_id> [since]}"
  local since="${2:--1440}"  # default last 24h in minutes
  _get "/zones/$zone_id/analytics/dashboard?since=$since" | _jq_check '.result.totals'
}

# --- help ---

cmd_help() {
  cat <<'EOF'
cf — Cloudflare API wrapper

Zones:
  zones [domain]              List zones (filter by domain)
  zone-get <zone_id>          Zone details
  zone-id <domain>            Get zone ID from domain name

DNS:
  dns-list <z> [type] [name]  List DNS records
  dns-create <z> <type> <name> <content> [proxied] [ttl]
  dns-update <z> <rec_id> <type> <name> <content> [proxied] [ttl]
  dns-delete <z> <rec_id>     Delete a record
  dns-export <z>              Export records as JSON
  dns-import <z> <file.json>  Import records from JSON

SSL & Settings:
  ssl-get <z>                 Current SSL mode
  ssl-set <z> <mode>          Set SSL (off/flexible/full/strict)
  settings-list <z>           All zone settings
  setting-get <z> <key>       Get a setting
  setting-set <z> <key> <val> Update a setting

Cache:
  cache-purge <z> [urls...]   Purge URLs or everything

Tunnels (requires CLOUDFLARE_ACCOUNT_ID):
  tunnels-list                List tunnels
  tunnel-get <id>             Tunnel details
  tunnel-create <name>        Create a tunnel
  tunnel-delete <id>          Delete a tunnel

Other:
  firewall-list <z>           List firewall rules
  pagerules-list <z>          List page rules
  analytics <z> [since_min]   Zone analytics (default: 24h)
  verify                      Verify API token
  help                        This message
EOF
}

# --- dispatch ---

cmd="${1:-help}"
shift 2>/dev/null || true

case "$cmd" in
  help|--help|-h)  cmd_help ;;
  verify)          cmd_verify "$@" ;;
  zones|zones-list) cmd_zones_list "$@" ;;
  zone-get)        cmd_zone_get "$@" ;;
  zone-id)         cmd_zone_id "$@" ;;
  dns-list)        cmd_dns_list "$@" ;;
  dns-create)      cmd_dns_create "$@" ;;
  dns-update)      cmd_dns_update "$@" ;;
  dns-delete)      cmd_dns_delete "$@" ;;
  dns-export)      cmd_dns_export "$@" ;;
  dns-import)      cmd_dns_import "$@" ;;
  settings-list)   cmd_settings_list "$@" ;;
  setting-get)     cmd_setting_get "$@" ;;
  setting-set)     cmd_setting_set "$@" ;;
  ssl-get)         cmd_ssl_get "$@" ;;
  ssl-set)         cmd_ssl_set "$@" ;;
  cache-purge)     cmd_cache_purge "$@" ;;
  pagerules-list)  cmd_pagerules_list "$@" ;;
  firewall-list)   cmd_firewall_list "$@" ;;
  tunnels-list)    cmd_tunnels_list "$@" ;;
  tunnel-get)      cmd_tunnel_get "$@" ;;
  tunnel-create)   cmd_tunnel_create "$@" ;;
  tunnel-delete)   cmd_tunnel_delete "$@" ;;
  analytics)       cmd_analytics "$@" ;;
  *) echo "Unknown command: $cmd (try 'cf help')" >&2; exit 1 ;;
esac
