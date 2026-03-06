#!/bin/bash
# Keys Broker - makes authenticated API calls without exposing keys to callers
# Dependencies: curl, jq

set -euo pipefail

# === CONFIGURATION ===
# URL allowlist per service (security: prevents key exfiltration)
declare -A ALLOWED_URLS=(
    ["openai"]="^https://api\.openai\.com/"
    ["anthropic"]="^https://api\.anthropic\.com/"
    ["stripe"]="^https://api\.stripe\.com/"
    ["github"]="^https://api\.github\.com/"
)

# === VALIDATION ===
check_dependencies() {
    command -v curl >/dev/null || { echo '{"ok":false,"error":"curl not found"}'; exit 1; }
    command -v jq >/dev/null || { echo '{"ok":false,"error":"jq not found"}'; exit 1; }
}

check_environment() {
    # Detect unsupported environments
    if [[ -f /.dockerenv ]] || grep -q docker /proc/1/cgroup 2>/dev/null; then
        echo '{"ok":false,"error":"Docker containers not supported - no keychain access"}' >&2
        return 1
    fi
    if grep -qi microsoft /proc/version 2>/dev/null; then
        echo '{"ok":false,"error":"WSL not supported - use Windows Credential Manager"}' >&2
        return 1
    fi
    if [[ "$(uname)" == "Linux" && -z "${DBUS_SESSION_BUS_ADDRESS:-}" ]]; then
        echo '{"ok":false,"error":"No D-Bus session - cannot access keyring (headless?)"}' >&2
        return 1
    fi
}

validate_service() {
    local service="$1"
    [[ "$service" =~ ^[a-z0-9_-]+$ ]] || {
        echo '{"ok":false,"error":"Invalid service name"}'
        return 1
    }
}

validate_method() {
    local method="$1"
    [[ "$method" =~ ^(GET|POST|PUT|PATCH|DELETE|HEAD)$ ]] || {
        echo '{"ok":false,"error":"Invalid HTTP method"}'
        return 1
    }
}

validate_url() {
    local service="$1" url="$2"
    
    # Must be HTTPS
    [[ "$url" =~ ^https:// ]] || {
        echo '{"ok":false,"error":"HTTPS required"}'
        return 1
    }
    
    # Must match service allowlist
    local pattern="${ALLOWED_URLS[$service]:-}"
    if [[ -z "$pattern" ]]; then
        echo '{"ok":false,"error":"Unknown service - add to ALLOWED_URLS"}'
        return 1
    fi
    
    [[ "$url" =~ $pattern ]] || {
        echo '{"ok":false,"error":"URL not allowed for this service"}'
        return 1
    }
}

# === KEY RETRIEVAL ===
get_key() {
    local service="$1"
    case "$(uname)" in
        Darwin)
            # Include -a "$USER" to avoid ambiguity with multiple entries
            security find-generic-password -s "keys:${service}" -a "$USER" -w 2>/dev/null
            ;;
        Linux)
            secret-tool lookup service "keys:${service}" 2>/dev/null
            ;;
        *)
            echo "Unsupported OS" >&2
            return 1
            ;;
    esac
}

# === HTTP REQUEST ===
make_request() {
    local service="$1" method="$2" url="$3" body="$4"
    
    # Validate all inputs
    validate_service "$service" || return
    validate_method "$method" || return
    validate_url "$service" "$url" || return
    
    # Get key (separate local to not mask exit code)
    local key
    key=$(get_key "$service") || {
        echo '{"ok":false,"error":"Key not found"}'
        return 1
    }
    [[ -n "$key" ]] || {
        echo '{"ok":false,"error":"Key is empty"}'
        return 1
    }
    
    # Create temp files with error handling
    local tmp_body tmp_header
    tmp_body=$(mktemp) || {
        echo '{"ok":false,"error":"Failed to create temp file"}'
        return 1
    }
    tmp_header=$(mktemp) || {
        rm -f "$tmp_body"
        echo '{"ok":false,"error":"Failed to create temp file"}'
        return 1
    }
    trap "rm -f '$tmp_body' '$tmp_header'" RETURN
    
    # Build auth header via file (not visible in ps)
    printf 'Authorization: Bearer %s' "$key" > "$tmp_header"
    chmod 600 "$tmp_header"
    
    # Make request with timeout
    local http_code curl_exit
    if [[ -n "$body" && "$body" != "null" ]]; then
        http_code=$(curl -s \
            --connect-timeout 10 \
            --max-time 120 \
            -X "$method" \
            -H @"$tmp_header" \
            -H "Content-Type: application/json" \
            --data-binary @- \
            -o "$tmp_body" \
            -w '%{http_code}' \
            -- "$url" <<< "$body")
        curl_exit=$?
    else
        http_code=$(curl -s \
            --connect-timeout 10 \
            --max-time 120 \
            -X "$method" \
            -H @"$tmp_header" \
            -o "$tmp_body" \
            -w '%{http_code}' \
            -- "$url")
        curl_exit=$?
    fi
    
    # Check curl exit code and http_code validity
    if [[ $curl_exit -ne 0 ]]; then
        echo '{"ok":false,"error":"Request failed","curl_exit":'$curl_exit'}'
        return 1
    fi
    if [[ ! "$http_code" =~ ^[0-9]+$ ]] || [[ "$http_code" == "000" ]]; then
        echo '{"ok":false,"error":"Connection failed"}'
        return 1
    fi
    
    # Read response body
    local response_body
    response_body=$(<"$tmp_body")
    
    # Build output JSON safely with jq
    jq -n \
        --argjson ok true \
        --argjson status "$http_code" \
        --arg body "$response_body" \
        '{ok: $ok, status: $status, body: ($body | try fromjson catch $body)}'
}

# === REQUEST HANDLER ===
handle_request() {
    local req="$1"
    
    # Parse JSON safely
    local action service method url body
    action=$(jq -r '.action // empty' <<< "$req") || {
        echo '{"ok":false,"error":"Invalid JSON"}'
        return 1
    }
    
    case "$action" in
        call)
            service=$(jq -r '.service // empty' <<< "$req")
            method=$(jq -r '.method // "POST"' <<< "$req")
            url=$(jq -r '.url // empty' <<< "$req")
            body=$(jq -c '.body // null' <<< "$req")
            
            [[ -n "$service" && -n "$url" ]] || {
                echo '{"ok":false,"error":"Missing service or url"}'
                return 1
            }
            
            make_request "$service" "$method" "$url" "$body"
            ;;
        ping)
            echo '{"ok":true,"status":"running"}'
            ;;
        services)
            # List configured services (not keys!)
            printf '{"ok":true,"services":[%s]}' \
                "$(printf '"%s",' "${!ALLOWED_URLS[@]}" | sed 's/,$//')"
            ;;
        *)
            echo '{"ok":false,"error":"Unknown action"}'
            ;;
    esac
}

# === MAIN ===
main() {
    check_dependencies
    
    case "${1:-help}" in
        call)
            [[ -n "${2:-}" ]] || {
                echo '{"ok":false,"error":"Usage: keys-broker call <json>"}'
                exit 1
            }
            check_environment || exit 1
            handle_request "$2"
            ;;
        ping)
            echo '{"ok":true,"status":"running"}'
            ;;
        services)
            printf '{"ok":true,"services":[%s]}' \
                "$(printf '"%s",' "${!ALLOWED_URLS[@]}" | sed 's/,$//')"
            ;;
        *)
            cat >&2 << 'EOF'
Usage: keys-broker <command> [args]

Commands:
  call <json>   Make authenticated API call
  ping          Check if broker works
  services      List configured services

JSON format for call:
  {"action":"call","service":"openai","url":"https://api.openai.com/v1/...","method":"POST","body":{...}}
EOF
            exit 1
            ;;
    esac
}

main "$@"
