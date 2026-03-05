#!/usr/bin/env bash
# Service Watchdog — Lightweight endpoint monitoring for self-hosted infrastructure
# Part of the service-watchdog OpenClaw skill
# License: MIT
set -euo pipefail

VERSION="1.0.0"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="${WATCHDOG_WORKSPACE:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
CONFIG_FILE="${WATCHDOG_CONFIG:-$WORKSPACE/watchdog.json}"
HISTORY_FILE=""  # set from config or default
NOW_UTC=$(date -u '+%Y-%m-%d %H:%M:%S')
NOW_EPOCH=$(date +%s)

# Defaults
DEFAULT_TIMEOUT_MS=5000
DEFAULT_SSL_WARN_DAYS=14
DEFAULT_ALERT_COOLDOWN_MIN=30
DEFAULT_HISTORY_RETENTION_DAYS=30
DEFAULT_HISTORY_FILE="$WORKSPACE/watchdog-history.csv"

# Output modes
MODE="summary"  # summary | report | json | ssl-only | alerts-only
COMPACT=false

# Colors (disabled if not a terminal or piped)
if [[ -t 1 ]]; then
    GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'
    BOLD='\033[1m'; DIM='\033[2m'; RESET='\033[0m'
else
    GREEN=''; RED=''; YELLOW=''; CYAN=''; BOLD=''; DIM=''; RESET=''
fi

# ─── Argument parsing ──────────────────────────────────────────────
usage() {
    cat <<EOF
Service Watchdog v${VERSION} — Lightweight endpoint monitoring

Usage: $(basename "$0") [OPTIONS]

Modes:
  (default)          Summary view — one line per service
  --report           Detailed report with trends and history
  --json             JSON output (machine-readable)
  --ssl-only         Check SSL certificates only
  --alerts-only      Show only services needing attention

Options:
  --config FILE      Config file path (default: \$WORKSPACE/watchdog.json)
  --compact          Minimal output (no decorations)
  --no-history       Skip writing to history file
  -h, --help         Show this help
  -v, --version      Show version

Environment:
  WATCHDOG_CONFIG    Config file path
  WATCHDOG_WORKSPACE Workspace root directory
EOF
}

WRITE_HISTORY=true
while [[ $# -gt 0 ]]; do
    case "$1" in
        --report)      MODE="report"; shift ;;
        --json)        MODE="json"; shift ;;
        --ssl-only)    MODE="ssl-only"; shift ;;
        --alerts-only) MODE="alerts-only"; shift ;;
        --config)      CONFIG_FILE="$2"; shift 2 ;;
        --compact)     COMPACT=true; shift ;;
        --no-history)  WRITE_HISTORY=false; shift ;;
        -h|--help)     usage; exit 0 ;;
        -v|--version)  echo "Service Watchdog v${VERSION}"; exit 0 ;;
        *)             echo "Unknown option: $1"; usage; exit 1 ;;
    esac
done

# ─── Dependency checks ─────────────────────────────────────────────
check_deps() {
    local missing=()
    command -v curl >/dev/null 2>&1 || missing+=("curl")
    command -v jq >/dev/null 2>&1 || missing+=("jq")
    if [[ ${#missing[@]} -gt 0 ]]; then
        echo "Error: Missing required dependencies: ${missing[*]}" >&2
        echo "Install with: apt install ${missing[*]}" >&2
        exit 1
    fi
}
check_deps

# ─── Config loading ────────────────────────────────────────────────
if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "Error: Config file not found: $CONFIG_FILE" >&2
    echo "Create watchdog.json in your workspace. See SKILL.md for format." >&2
    exit 1
fi

# Parse global defaults from config
get_default() {
    local key="$1" fallback="$2"
    jq -r ".defaults.${key} // \"${fallback}\"" "$CONFIG_FILE"
}

DEFAULT_TIMEOUT_MS=$(get_default "timeout_ms" "$DEFAULT_TIMEOUT_MS")
DEFAULT_SSL_WARN_DAYS=$(get_default "ssl_warn_days" "$DEFAULT_SSL_WARN_DAYS")
DEFAULT_ALERT_COOLDOWN_MIN=$(get_default "alert_cooldown_min" "$DEFAULT_ALERT_COOLDOWN_MIN")
DEFAULT_HISTORY_RETENTION_DAYS=$(get_default "history_retention_days" "$DEFAULT_HISTORY_RETENTION_DAYS")
HISTORY_FILE=$(get_default "history_file" "$DEFAULT_HISTORY_FILE")

SERVICE_COUNT=$(jq '.services | length' "$CONFIG_FILE")
if [[ "$SERVICE_COUNT" -eq 0 ]]; then
    echo "Error: No services defined in $CONFIG_FILE" >&2
    exit 1
fi

# ─── History management ────────────────────────────────────────────
init_history() {
    if [[ "$WRITE_HISTORY" == "true" ]] && [[ ! -f "$HISTORY_FILE" ]]; then
        echo "timestamp,name,type,status,response_ms,detail" > "$HISTORY_FILE"
    fi
}

write_history() {
    if [[ "$WRITE_HISTORY" == "true" ]]; then
        local name="$1" type="$2" status="$3" response_ms="$4" detail="$5"
        # CSV-escape fields with commas/quotes
        detail="${detail//\"/\"\"}"
        echo "${NOW_UTC},\"${name}\",${type},${status},${response_ms},\"${detail}\"" >> "$HISTORY_FILE"
    fi
}

prune_history() {
    if [[ "$WRITE_HISTORY" == "true" ]] && [[ -f "$HISTORY_FILE" ]]; then
        local cutoff_epoch=$((NOW_EPOCH - DEFAULT_HISTORY_RETENTION_DAYS * 86400))
        local cutoff_date
        cutoff_date=$(date -u -d "@${cutoff_epoch}" '+%Y-%m-%d' 2>/dev/null || date -u -r "${cutoff_epoch}" '+%Y-%m-%d' 2>/dev/null || echo "")
        if [[ -n "$cutoff_date" ]]; then
            local tmp="${HISTORY_FILE}.tmp"
            head -1 "$HISTORY_FILE" > "$tmp"
            awk -F',' -v cutoff="$cutoff_date" 'NR>1 && $1 >= cutoff' "$HISTORY_FILE" >> "$tmp"
            mv "$tmp" "$HISTORY_FILE"
        fi
    fi
}

# ─── Check functions ───────────────────────────────────────────────

# Returns: status (ok|warn|fail), response_ms, detail
check_http() {
    local url="$1" expect_status="${2:-200}" timeout_ms="${3:-$DEFAULT_TIMEOUT_MS}"
    local method="${4:-GET}" expect_body="${5:-}" ssl_warn_days="${6:-$DEFAULT_SSL_WARN_DAYS}"
    local timeout_s=$(( timeout_ms / 1000 ))
    [[ "$timeout_s" -lt 1 ]] && timeout_s=1

    local start_ms end_ms elapsed_ms http_code body_file header_file
    start_ms=$(date +%s%N 2>/dev/null || echo "0")
    body_file=$(mktemp)
    header_file=$(mktemp)
    trap "rm -f '$body_file' '$header_file'" RETURN

    local curl_args=(-s -S -o "$body_file" -D "$header_file" -w '%{http_code}' \
        --max-time "$timeout_s" --connect-timeout "$timeout_s" \
        -X "$method" -L --insecure)

    http_code=$(curl "${curl_args[@]}" "$url" 2>/dev/null) || {
        end_ms=$(date +%s%N 2>/dev/null || echo "0")
        elapsed_ms=$(( (end_ms - start_ms) / 1000000 ))
        echo "fail|${elapsed_ms}|Connection failed (timeout or refused)"
        return
    }

    end_ms=$(date +%s%N 2>/dev/null || echo "0")
    if [[ "$start_ms" != "0" ]] && [[ "$end_ms" != "0" ]]; then
        elapsed_ms=$(( (end_ms - start_ms) / 1000000 ))
    else
        elapsed_ms=0
    fi

    # Check status code
    if [[ "$http_code" != "$expect_status" ]]; then
        echo "fail|${elapsed_ms}|HTTP ${http_code} (expected ${expect_status})"
        return
    fi

    # Check body content if specified
    if [[ -n "$expect_body" ]] && ! grep -q "$expect_body" "$body_file" 2>/dev/null; then
        echo "fail|${elapsed_ms}|Body mismatch (expected: ${expect_body})"
        return
    fi

    # Check SSL if HTTPS
    local ssl_detail=""
    if [[ "$url" == https://* ]]; then
        local host_port
        host_port=$(echo "$url" | sed -E 's|https://([^/]+).*|\1|')
        local host="${host_port%%:*}"
        local port="${host_port##*:}"
        [[ "$port" == "$host" ]] && port=443

        local ssl_expiry_days
        ssl_expiry_days=$(get_ssl_days "$host" "$port" 2>/dev/null)
        if [[ -n "$ssl_expiry_days" ]] && [[ "$ssl_expiry_days" =~ ^-?[0-9]+$ ]]; then
            if [[ "$ssl_expiry_days" -lt 0 ]]; then
                echo "fail|${elapsed_ms}|HTTP ${http_code} OK | SSL EXPIRED (${ssl_expiry_days}d ago)"
                return
            elif [[ "$ssl_expiry_days" -le "$ssl_warn_days" ]]; then
                echo "warn|${elapsed_ms}|HTTP ${http_code} OK | SSL expires in ${ssl_expiry_days}d"
                return
            fi
            ssl_detail=" | SSL: ${ssl_expiry_days}d"
        fi
    fi

    echo "ok|${elapsed_ms}|${http_code} OK${ssl_detail}"
}

check_tcp() {
    local host="$1" port="$2" timeout_ms="${3:-$DEFAULT_TIMEOUT_MS}"
    local timeout_s=$(( timeout_ms / 1000 ))
    [[ "$timeout_s" -lt 1 ]] && timeout_s=1

    local start_ms end_ms elapsed_ms
    start_ms=$(date +%s%N 2>/dev/null || echo "0")

    # Try nc first, fall back to /dev/tcp
    local success=false
    if command -v nc >/dev/null 2>&1; then
        if nc -z -w "$timeout_s" "$host" "$port" >/dev/null 2>&1; then
            success=true
        fi
    elif command -v ncat >/dev/null 2>&1; then
        if ncat -z -w "$timeout_s" "$host" "$port" >/dev/null 2>&1; then
            success=true
        fi
    else
        # Bash /dev/tcp fallback
        if timeout "$timeout_s" bash -c "echo >/dev/tcp/${host}/${port}" 2>/dev/null; then
            success=true
        fi
    fi

    end_ms=$(date +%s%N 2>/dev/null || echo "0")
    if [[ "$start_ms" != "0" ]] && [[ "$end_ms" != "0" ]]; then
        elapsed_ms=$(( (end_ms - start_ms) / 1000000 ))
    else
        elapsed_ms=0
    fi

    if [[ "$success" == "true" ]]; then
        echo "ok|${elapsed_ms}|port ${port} open"
    else
        echo "fail|${elapsed_ms}|port ${port} closed/unreachable"
    fi
}

check_dns() {
    local domain="$1" expect_ip="${2:-}" nameserver="${3:-}"
    local timeout_ms="${4:-$DEFAULT_TIMEOUT_MS}"

    local start_ms end_ms elapsed_ms resolved_ip
    start_ms=$(date +%s%N 2>/dev/null || echo "0")

    # Try dig, then nslookup, then host
    if command -v dig >/dev/null 2>&1; then
        local dig_args=(+short +time=3 +tries=1 "$domain" A)
        [[ -n "$nameserver" ]] && dig_args=("@${nameserver}" "${dig_args[@]}")
        resolved_ip=$(dig "${dig_args[@]}" 2>/dev/null | head -1)
    elif command -v nslookup >/dev/null 2>&1; then
        if [[ -n "$nameserver" ]]; then
            resolved_ip=$(nslookup "$domain" "$nameserver" 2>/dev/null | awk '/^Address:/ && !/.*#/ {print $2}' | head -1)
        else
            resolved_ip=$(nslookup "$domain" 2>/dev/null | awk '/^Address:/ && !/.*#/ {print $2}' | head -1)
        fi
    elif command -v host >/dev/null 2>&1; then
        resolved_ip=$(host "$domain" ${nameserver:+"$nameserver"} 2>/dev/null | awk '/has address/ {print $4}' | head -1)
    else
        echo "fail|0|No DNS tool available (dig/nslookup/host)"
        return
    fi

    end_ms=$(date +%s%N 2>/dev/null || echo "0")
    if [[ "$start_ms" != "0" ]] && [[ "$end_ms" != "0" ]]; then
        elapsed_ms=$(( (end_ms - start_ms) / 1000000 ))
    else
        elapsed_ms=0
    fi

    if [[ -z "$resolved_ip" ]]; then
        echo "fail|${elapsed_ms}|DNS resolution failed"
        return
    fi

    if [[ -n "$expect_ip" ]] && [[ "$resolved_ip" != "$expect_ip" ]]; then
        echo "warn|${elapsed_ms}|Resolved to ${resolved_ip} (expected ${expect_ip})"
        return
    fi

    echo "ok|${elapsed_ms}|resolves to ${resolved_ip} ✓"
}

get_ssl_days() {
    local host="$1" port="${2:-443}"
    if ! command -v openssl >/dev/null 2>&1; then
        echo ""
        return
    fi

    local expiry_date
    expiry_date=$(echo | openssl s_client -servername "$host" -connect "${host}:${port}" 2>/dev/null | \
        openssl x509 -noout -enddate 2>/dev/null | sed 's/notAfter=//')

    if [[ -z "$expiry_date" ]]; then
        echo ""
        return
    fi

    local expiry_epoch
    expiry_epoch=$(date -d "$expiry_date" +%s 2>/dev/null || date -j -f "%b %d %T %Y %Z" "$expiry_date" +%s 2>/dev/null || echo "")

    if [[ -z "$expiry_epoch" ]]; then
        echo ""
        return
    fi

    echo $(( (expiry_epoch - NOW_EPOCH) / 86400 ))
}

check_ssl_detail() {
    local host="$1" port="${2:-443}" warn_days="${3:-$DEFAULT_SSL_WARN_DAYS}"
    if ! command -v openssl >/dev/null 2>&1; then
        echo "fail|0|openssl not available"
        return
    fi

    local start_ms end_ms elapsed_ms
    start_ms=$(date +%s%N 2>/dev/null || echo "0")

    local cert_info
    cert_info=$(echo | openssl s_client -servername "$host" -connect "${host}:${port}" 2>/dev/null | \
        openssl x509 -noout -enddate -issuer -subject 2>/dev/null)

    end_ms=$(date +%s%N 2>/dev/null || echo "0")
    if [[ "$start_ms" != "0" ]] && [[ "$end_ms" != "0" ]]; then
        elapsed_ms=$(( (end_ms - start_ms) / 1000000 ))
    else
        elapsed_ms=0
    fi

    if [[ -z "$cert_info" ]]; then
        echo "fail|${elapsed_ms}|SSL connection failed"
        return
    fi

    local expiry_date issuer subject
    expiry_date=$(echo "$cert_info" | sed -n 's/notAfter=//p')
    issuer=$(echo "$cert_info" | sed -n 's/issuer=//p' | sed 's/.*CN = //' | sed 's/,.*//')
    subject=$(echo "$cert_info" | sed -n 's/subject=//p' | sed 's/.*CN = //' | sed 's/,.*//')

    local days
    days=$(get_ssl_days "$host" "$port")

    if [[ -z "$days" ]]; then
        echo "fail|${elapsed_ms}|Cannot parse certificate expiry"
        return
    fi

    if [[ "$days" -lt 0 ]]; then
        echo "fail|${elapsed_ms}|EXPIRED ${days}d ago | CN=${subject} | Issuer=${issuer}"
    elif [[ "$days" -le "$warn_days" ]]; then
        echo "warn|${elapsed_ms}|Expires in ${days}d | CN=${subject} | Issuer=${issuer}"
    else
        echo "ok|${elapsed_ms}|Valid for ${days}d | CN=${subject} | Issuer=${issuer}"
    fi
}

# ─── Service processing ───────────────────────────────────────────

declare -a RESULTS=()
declare -a RESULT_NAMES=()
declare -a RESULT_TYPES=()
declare -a RESULT_STATUSES=()
declare -a RESULT_TIMES=()
declare -a RESULT_DETAILS=()

process_services() {
    local i=0
    while [[ $i -lt $SERVICE_COUNT ]]; do
        local svc
        svc=$(jq -c ".services[$i]" "$CONFIG_FILE")

        local name type
        name=$(echo "$svc" | jq -r '.name')
        type=$(echo "$svc" | jq -r '.type')

        local result=""

        case "$type" in
            http|https)
                local url expect_status timeout_ms method expect_body ssl_warn_days
                url=$(echo "$svc" | jq -r '.url')
                expect_status=$(echo "$svc" | jq -r '.expect_status // 200')
                timeout_ms=$(echo "$svc" | jq -r ".timeout_ms // $DEFAULT_TIMEOUT_MS")
                method=$(echo "$svc" | jq -r '.method // "GET"')
                expect_body=$(echo "$svc" | jq -r '.expect_body // ""')
                ssl_warn_days=$(echo "$svc" | jq -r ".ssl_warn_days // $DEFAULT_SSL_WARN_DAYS")

                if [[ "$MODE" == "ssl-only" ]]; then
                    if [[ "$url" == https://* ]]; then
                        local host_port host port
                        host_port=$(echo "$url" | sed -E 's|https://([^/]+).*|\1|')
                        host="${host_port%%:*}"
                        port="${host_port##*:}"
                        [[ "$port" == "$host" ]] && port=443
                        result=$(check_ssl_detail "$host" "$port" "$ssl_warn_days")
                    else
                        i=$((i + 1)); continue
                    fi
                else
                    result=$(check_http "$url" "$expect_status" "$timeout_ms" "$method" "$expect_body" "$ssl_warn_days")
                fi
                ;;
            tcp)
                if [[ "$MODE" == "ssl-only" ]]; then
                    i=$((i + 1)); continue
                fi
                local host port timeout_ms
                host=$(echo "$svc" | jq -r '.host')
                port=$(echo "$svc" | jq -r '.port')
                timeout_ms=$(echo "$svc" | jq -r ".timeout_ms // $DEFAULT_TIMEOUT_MS")
                result=$(check_tcp "$host" "$port" "$timeout_ms")
                ;;
            dns)
                if [[ "$MODE" == "ssl-only" ]]; then
                    i=$((i + 1)); continue
                fi
                local domain expect_ip nameserver timeout_ms
                domain=$(echo "$svc" | jq -r '.domain')
                expect_ip=$(echo "$svc" | jq -r '.expect_ip // ""')
                nameserver=$(echo "$svc" | jq -r '.nameserver // ""')
                timeout_ms=$(echo "$svc" | jq -r ".timeout_ms // $DEFAULT_TIMEOUT_MS")
                result=$(check_dns "$domain" "$expect_ip" "$nameserver" "$timeout_ms")
                ;;
            *)
                result="fail|0|Unknown service type: ${type}"
                ;;
        esac

        # Parse result
        local status response_ms detail
        IFS='|' read -r status response_ms detail <<< "$result"

        RESULT_NAMES+=("$name")
        RESULT_TYPES+=("$type")
        RESULT_STATUSES+=("$status")
        RESULT_TIMES+=("$response_ms")
        RESULT_DETAILS+=("$detail")

        # Write to history
        write_history "$name" "$type" "$status" "$response_ms" "$detail"

        i=$((i + 1))
    done
}

# ─── Output formatting ─────────────────────────────────────────────

status_icon() {
    case "$1" in
        ok)   echo "🟢" ;;
        warn) echo "🟡" ;;
        fail) echo "🔴" ;;
        *)    echo "⚪" ;;
    esac
}

pad_name() {
    local name="$1" width="${2:-24}"
    printf "%-${width}s" "$name"
}

output_summary() {
    local total=${#RESULT_NAMES[@]}
    local healthy=0 warnings=0 failures=0
    local total_ms=0 count_ms=0
    local max_name_len=0

    # Find longest name for padding
    for name in "${RESULT_NAMES[@]}"; do
        [[ ${#name} -gt $max_name_len ]] && max_name_len=${#name}
    done
    local pad_width=$((max_name_len + 2))

    for ((i=0; i<total; i++)); do
        local icon
        icon=$(status_icon "${RESULT_STATUSES[$i]}")
        local padded_name
        padded_name=$(pad_name "${RESULT_NAMES[$i]}" "$pad_width")
        local ms="${RESULT_TIMES[$i]}"
        local detail="${RESULT_DETAILS[$i]}"

        case "${RESULT_STATUSES[$i]}" in
            ok)   healthy=$((healthy + 1)) ;;
            warn) warnings=$((warnings + 1)) ;;
            fail) failures=$((failures + 1)) ;;
        esac

        if [[ "$ms" =~ ^[0-9]+$ ]] && [[ "$ms" -gt 0 ]]; then
            total_ms=$((total_ms + ms))
            ((count_ms++))
        fi

        if [[ "$MODE" == "alerts-only" ]] && [[ "${RESULT_STATUSES[$i]}" == "ok" ]]; then
            continue
        fi

        if [[ "$COMPACT" == "true" ]]; then
            echo "${icon} ${RESULT_NAMES[$i]} — ${detail} (${ms}ms)"
        else
            echo -e "${icon} ${BOLD}${padded_name}${RESET} — ${detail} (${DIM}${ms}ms${RESET})"
        fi
    done

    # Summary line
    local avg_ms=0
    [[ $count_ms -gt 0 ]] && avg_ms=$((total_ms / count_ms))

    if [[ "$MODE" != "alerts-only" ]] || [[ $failures -gt 0 ]] || [[ $warnings -gt 0 ]]; then
        if [[ "$COMPACT" == "true" ]]; then
            echo "━━━"
            echo "${healthy}/${total} healthy | avg: ${avg_ms}ms | ${NOW_UTC}"
        else
            echo -e "${DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
            local status_color="$GREEN"
            [[ $warnings -gt 0 ]] && status_color="$YELLOW"
            [[ $failures -gt 0 ]] && status_color="$RED"
            echo -e "${status_color}${healthy}/${total} healthy${RESET} | avg response: ${CYAN}${avg_ms}ms${RESET} | checked: ${DIM}${NOW_UTC}${RESET}"
            [[ $warnings -gt 0 ]] && echo -e "${YELLOW}⚠ ${warnings} warning(s)${RESET}"
            [[ $failures -gt 0 ]] && echo -e "${RED}✖ ${failures} failure(s)${RESET}"
        fi
    elif [[ "$MODE" == "alerts-only" ]]; then
        echo "All ${total} services healthy ✓"
    fi
}

output_json() {
    local total=${#RESULT_NAMES[@]}
    echo "{"
    echo "  \"timestamp\": \"${NOW_UTC}\","
    echo "  \"services\": ["
    for ((i=0; i<total; i++)); do
        local comma=","
        [[ $((i + 1)) -eq $total ]] && comma=""
        cat <<JSONENTRY
    {
      "name": "${RESULT_NAMES[$i]}",
      "type": "${RESULT_TYPES[$i]}",
      "status": "${RESULT_STATUSES[$i]}",
      "response_ms": ${RESULT_TIMES[$i]},
      "detail": "${RESULT_DETAILS[$i]//\"/\\\"}"
    }${comma}
JSONENTRY
    done
    echo "  ],"

    # Summary stats
    local healthy=0 warnings=0 failures=0
    for s in "${RESULT_STATUSES[@]}"; do
        case "$s" in ok) healthy=$((healthy + 1));; warn) warnings=$((warnings + 1));; fail) failures=$((failures + 1));; esac
    done
    echo "  \"summary\": {"
    echo "    \"total\": ${total},"
    echo "    \"healthy\": ${healthy},"
    echo "    \"warnings\": ${warnings},"
    echo "    \"failures\": ${failures},"
    echo "    \"status\": \"$([ $failures -gt 0 ] && echo "critical" || ([ $warnings -gt 0 ] && echo "warning" || echo "healthy"))\""
    echo "  }"
    echo "}"
}

output_report() {
    echo -e "${BOLD}Service Watchdog Report${RESET}"
    echo -e "${DIM}Generated: ${NOW_UTC}${RESET}"
    echo ""

    # Current status
    echo -e "${BOLD}Current Status${RESET}"
    echo -e "${DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
    output_summary
    echo ""

    # History analysis (if history file exists)
    if [[ -f "$HISTORY_FILE" ]] && [[ $(wc -l < "$HISTORY_FILE") -gt 1 ]]; then
        echo -e "${BOLD}Trend Analysis (last ${DEFAULT_HISTORY_RETENTION_DAYS} days)${RESET}"
        echo -e "${DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"

        # Per-service stats from history
        local names_seen=()
        for name in "${RESULT_NAMES[@]}"; do
            # Skip if already processed
            local seen=false
            for s in "${names_seen[@]:-}"; do
                [[ "$s" == "$name" ]] && seen=true && break
            done
            [[ "$seen" == "true" ]] && continue
            names_seen+=("$name")

            local total_checks ok_checks avg_ms p95_ms
            total_checks=$(awk -F',' -v name="\"$name\"" '$2==name {count++} END {print count+0}' "$HISTORY_FILE")
            ok_checks=$(awk -F',' -v name="\"$name\"" '$2==name && $4=="ok" {count++} END {print count+0}' "$HISTORY_FILE")
            avg_ms=$(awk -F',' -v name="\"$name\"" '$2==name && $5>0 {sum+=$5; count++} END {if(count>0) printf "%.0f", sum/count; else print "0"}' "$HISTORY_FILE")

            # P95 response time
            p95_ms=$(awk -F',' -v name="\"$name\"" '$2==name && $5>0 {print $5}' "$HISTORY_FILE" | \
                sort -n | awk '{a[NR]=$1} END {idx=int(NR*0.95); if(idx<1)idx=1; print a[idx]}')

            local uptime_pct="100.0"
            if [[ $total_checks -gt 0 ]]; then
                uptime_pct=$(awk "BEGIN {printf \"%.1f\", ($ok_checks/$total_checks)*100}")
            fi

            local uptime_color="$GREEN"
            (( $(awk "BEGIN {print ($uptime_pct < 99.5) ? 1 : 0}") )) && uptime_color="$YELLOW"
            (( $(awk "BEGIN {print ($uptime_pct < 95.0) ? 1 : 0}") )) && uptime_color="$RED"

            echo -e "  ${BOLD}${name}${RESET}: ${uptime_color}${uptime_pct}%${RESET} uptime | avg: ${avg_ms}ms | P95: ${p95_ms:-n/a}ms | ${total_checks} checks"
        done

        # Recent incidents
        local incidents
        incidents=$(awk -F',' 'NR>1 && $4=="fail" {gsub(/"/, "", $2); gsub(/"/, "", $6); print $1 " | " $2 " | " $6}' "$HISTORY_FILE" | tail -5)
        if [[ -n "$incidents" ]]; then
            echo ""
            echo -e "${BOLD}Recent Incidents${RESET}"
            echo -e "${DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
            echo "$incidents" | while IFS='|' read -r ts svc detail; do
                echo -e "  ${RED}✖${RESET} ${DIM}${ts}${RESET} ${BOLD}${svc}${RESET} —${detail}"
            done
        fi
    else
        echo -e "${DIM}No history data yet. Run checks over time to build trends.${RESET}"
    fi
}

# ─── Main ──────────────────────────────────────────────────────────

init_history
process_services

case "$MODE" in
    summary|alerts-only|ssl-only)
        output_summary
        ;;
    json)
        output_json
        ;;
    report)
        output_report
        ;;
esac

# Prune old history entries
prune_history

# Exit code: 2 if any failures, 1 if any warnings, 0 if all ok
has_fail=false
has_warn=false
for s in "${RESULT_STATUSES[@]}"; do
    [[ "$s" == "fail" ]] && has_fail=true
    [[ "$s" == "warn" ]] && has_warn=true
done
[[ "$has_fail" == "true" ]] && exit 2
[[ "$has_warn" == "true" ]] && exit 1
exit 0
