#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATES_DIR="${SCRIPT_DIR}/templates"
ENV_FILE="${SCRIPT_DIR}/.env"

DATE_FILTER=""
OUTPUT_FILE=""
VERBOSE=0

EWS_URL=""
EWS_USER=""
EWS_PASS=""
EWS_EMAIL=""

log() {
    if [[ $VERBOSE -eq 1 ]]; then
        echo "[DEBUG] $*" >&2
    fi
}

error() {
    echo "[ERROR] $*" >&2
}

load_env() {
    # Priority: environment vars (from OpenClaw/wrapper) > .env file
    if [[ -n "${EWS_URL:-}" && -n "${EWS_USER:-}" && -n "${EWS_PASS:-}" ]]; then
        log "Using credentials from environment"
        EWS_EMAIL="${EWS_EMAIL:-$EWS_USER}"
        log "EWS URL: $EWS_URL"
        log "EWS User: $EWS_USER"
        return 0
    fi

    # Fallback for standalone usage
    if [[ -f "$ENV_FILE" ]]; then
        source "$ENV_FILE"
        log "Loaded environment from $ENV_FILE"
    else
        error "No credentials found."
        error "  Option 1: Run via ews-calendar-secure.sh (uses keyring)"
        error "  Option 2: Create .env file from .env.example"
        error "  Option 3: Set EWS_URL, EWS_USER, EWS_PASS environment variables"
        exit 1
    fi

    local missing=()
    [[ -z "$EWS_URL" ]] && missing+=("EWS_URL")
    [[ -z "$EWS_USER" ]] && missing+=("EWS_USER")
    [[ -z "$EWS_PASS" ]] && missing+=("EWS_PASS")

    if [[ ${#missing[@]} -gt 0 ]]; then
        error "Missing required environment variables: ${missing[*]}"
        exit 1
    fi

    EWS_EMAIL="${EWS_EMAIL:-$EWS_USER}"
    log "EWS URL: $EWS_URL"
    log "EWS User: $EWS_USER"
}

calculate_date_range() {
    local target_date="$1"
    local start_date end_date

    case "$target_date" in
        today)
            target_date=$(date +%Y-%m-%d)
            ;;
        tomorrow)
            target_date=$(date -v+1d +%Y-%m-%d 2>/dev/null || date -d "+1 day" +%Y-%m-%d 2>/dev/null)
            ;;
    esac

    if ! [[ "$target_date" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
        error "Invalid date format: $target_date (expected YYYY-MM-DD, today, or tomorrow)"
        exit 1
    fi

    start_date="${target_date}T00:00:00Z"
    end_date="${target_date}T23:59:59Z"

    log "Date range: $start_date to $end_date"
    echo "$start_date|$end_date"
}

strip_namespaces() {
    sed 's/<\([a-z]\):/<\1_/g; s/<\/\([a-z]\):/<\/\1_/g'
}

extract_links() {
    local text="$1"
    local url_pattern='https?://[^[:space:]"'\''<>]+'
    echo "$text" | grep -oE "$url_pattern" 2>/dev/null | sort -u || true
}

DEBUG_XML=""
save_debug_xml() {
    if [[ -n "$DEBUG_XML" ]]; then
        echo "$1" > "$DEBUG_XML"
        log "Saved raw XML to $DEBUG_XML"
    fi
}

ews_request() {
    local soap_body="$1"
    local response
    local http_code

    log "Sending EWS request..."

    response=$(curl -s -w "\n%{http_code}" \
        -X POST \
        -H "Content-Type: text/xml; charset=utf-8" \
        --ntlm \
        -u "${EWS_USER}:${EWS_PASS}" \
        --data "$soap_body" \
        "$EWS_URL" 2>&1)

    http_code=$(echo "$response" | tail -n 1)
    response=$(echo "$response" | sed '$d')

    if [[ "$http_code" != "200" ]]; then
        error "HTTP request failed with status: $http_code"
        error "Response: $response"
        return 1
    fi

    if echo "$response" | grep -q "<soap:Fault"; then
        error "SOAP Fault detected"
        local fault_code fault_string
        fault_code=$(echo "$response" | xmllint --xpath "//*[local-name()='faultcode']/text()" - 2>/dev/null || echo "Unknown")
        fault_string=$(echo "$response" | xmllint --xpath "//*[local-name()='faultstring']/text()" - 2>/dev/null || echo "Unknown error")
        error "Fault code: $fault_code"
        error "Fault string: $fault_string"
        return 1
    fi

    echo "$response"
}

parse_find_items() {
    local response="$1"
    local items=()

    log "Parsing FindItem response..."

    save_debug_xml "$response"

    local clean_response
    clean_response=$(echo "$response" | strip_namespaces)

    if ! echo "$clean_response" | grep -q "<t_CalendarItem>"; then
        log "No calendar items found"
        return 0
    fi

    local temp_file
    temp_file=$(mktemp)
    echo "$clean_response" > "$temp_file"

    local item_ids
    item_ids=$(xmllint --xpath "//t_CalendarItem/t_ItemId/@Id" "$temp_file" 2>/dev/null | \
        sed 's/ Id="\([^"]*\)"/\1\n/g' | grep -v '^$' || true)

    if [[ -z "$item_ids" ]]; then
        log "No items found in response"
        rm -f "$temp_file"
        return 0
    fi

    local idx=0
    while IFS= read -r item_id; do
        [[ -z "$item_id" ]] && continue

        local item_xml
        item_xml=$(xmllint --xpath "(//t_CalendarItem)[$((idx+1))]" "$temp_file" 2>/dev/null || true)

        if [[ -n "$item_xml" ]]; then
            local item_temp
            item_temp=$(mktemp)
            echo "$item_xml" > "$item_temp"

            local subject start end location organizer
            subject=$(xmllint --xpath "//t_Subject/text()" "$item_temp" 2>/dev/null || echo "")
            start=$(xmllint --xpath "//t_Start/text()" "$item_temp" 2>/dev/null || echo "")
            end=$(xmllint --xpath "//t_End/text()" "$item_temp" 2>/dev/null || echo "")
            location=$(xmllint --xpath "//t_Location/text()" "$item_temp" 2>/dev/null || echo "")
            organizer=$(xmllint --xpath "//t_Organizer//t_EmailAddress/text()" "$item_temp" 2>/dev/null || echo "")

            rm -f "$item_temp"

            subject=$(echo "$subject" | sed 's/\\/\\\\/g; s/"/\\"/g' | tr -d '\n' | tr -d '\r')
            start=$(echo "$start" | tr -d '\n' | tr -d '\r')
            end=$(echo "$end" | tr -d '\n' | tr -d '\r')
            location=$(echo "$location" | sed 's/\\/\\\\/g; s/"/\\"/g' | tr -d '\n' | tr -d '\r')
            organizer=$(echo "$organizer" | tr -d '\n' | tr -d '\r')

            local delim=$'\x1f'
            echo "${item_id}${delim}${subject}${delim}${start}${delim}${end}${delim}${location}${delim}${organizer}"
            ((idx++)) || true
        fi
    done <<< "$item_ids"

    rm -f "$temp_file"
}

get_item_body() {
    local item_id="$1"
    local soap_body response

    soap_body=$(sed "s|__ITEM_ID__|${item_id}|g" "${TEMPLATES_DIR}/get-item.xml")

    log "Fetching body for item: ${item_id:0:20}..."

    response=$(ews_request "$soap_body") || return 1

    local clean_response body
    clean_response=$(echo "$response" | strip_namespaces)
    body=$(echo "$clean_response" | xmllint --xpath "//t_Body/text()" - 2>/dev/null || echo "")

    body=$(echo "$body" | sed 's/&#13;/ /g; s/&#10;/ /g; s/&amp;/\&/g; s/&lt;/</g; s/&gt;/>/g' | tr -s ' ')

    local links
    links=$(extract_links "$body" | paste -sd ',' -)

    body=$(echo "$body" | sed 's/\\/\\\\/g; s/"/\\"/g' | tr -d '\r' | tr -d '\n')

    echo "${body}|${links}"
}

generate_json() {
    local items=("$@")
    local first=1
    local delim=$'\x1f'

    echo "["
    for item in "${items[@]}"; do
        [[ -z "$item" ]] && continue

        IFS="$delim" read -r item_id subject start end location organizer body_with_links <<< "$item"

        IFS='|' read -r body body_links <<< "$body_with_links"

        local location_links
        location_links=$(extract_links "$location" | paste -sd ',' -)

        local all_links
        if [[ -n "$body_links" && -n "$location_links" ]]; then
            all_links=$(echo "${body_links},${location_links}" | tr ',' '\n' | sort -u | paste -sd ',' -)
        elif [[ -n "$body_links" ]]; then
            all_links="$body_links"
        elif [[ -n "$location_links" ]]; then
            all_links="$location_links"
        else
            all_links=""
        fi

        local links_json="[]"
        if [[ -n "$all_links" ]]; then
            local links_array
            links_array=$(echo "$all_links" | tr ',' '\n' | sed 's/^/"/;s/$/"/' | tr '\n' ',' | sed 's/,$//')
            links_json="[$links_array]"
        fi

        [[ $first -eq 0 ]] && echo ","
        first=0

        cat << EOF
  {
    "subject": "${subject}",
    "start": "${start}",
    "end": "${end}",
    "location": "${location}",
    "organizer": "${organizer}",
    "body": "${body}",
    "links": ${links_json}
  }
EOF
    done
    echo "]"
}

show_help() {
    cat << EOF
EWS Calendar Parser - Extract events from Exchange calendar

Usage: $(basename "$0") [OPTIONS]

Options:
  -d, --date DATE       Filter events by date (YYYY-MM-DD, 'today', or 'tomorrow')
  -o, --output FILE     Write output to file instead of stdout
  -v, --verbose         Enable verbose logging
      --debug-xml FILE  Save raw XML response to file for debugging
  -h, --help            Show this help message

Examples:
  $(basename "$0") --date today
  $(basename "$0") --date 2026-03-03 --output events.json
  $(basename "$0") -d tomorrow -v
  $(basename "$0") --date today --debug-xml response.xml

Configuration:
  Create a .env file with:
    EWS_URL=https://outlook.company.com/EWS/Exchange.asmx
    EWS_USER=DOMAIN\\username
    EWS_PASS=your_password
    EWS_EMAIL=user@company.com  (optional)

EOF
    exit 0
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -d|--date)
                DATE_FILTER="$2"
                shift 2
                ;;
            -o|--output)
                OUTPUT_FILE="$2"
                shift 2
                ;;
            -v|--verbose)
                VERBOSE=1
                shift
                ;;
            --debug-xml)
                DEBUG_XML="$2"
                shift 2
                ;;
            *)
                error "Unknown option: $1"
                show_help
                ;;
        esac
    done

    if [[ -z "$DATE_FILTER" ]]; then
        error "Date filter is required. Use --date YYYY-MM-DD, --date today, or --date tomorrow"
        exit 1
    fi
}

main() {
    parse_args "$@"
    load_env

    local date_range
    date_range=$(calculate_date_range "$DATE_FILTER")
    local start_date end_date
    IFS='|' read -r start_date end_date <<< "$date_range"

    local soap_body
    soap_body=$(sed \
        -e "s|__START_DATE__|${start_date}|g" \
        -e "s|__END_DATE__|${end_date}|g" \
        -e "s|__EMAIL__|${EWS_EMAIL}|g" \
        "${TEMPLATES_DIR}/find-items.xml")

    log "SOAP Request prepared"

    local response
    response=$(ews_request "$soap_body") || exit 1

    local parsed_items
    parsed_items=$(parse_find_items "$response")

    local items=()
    local delim=$'\x1f'
    while IFS= read -r item; do
        [[ -z "$item" ]] && continue

        local item_id
        item_id=$(echo "$item" | cut -d"$delim" -f1)

        local body
        body=$(get_item_body "$item_id") || body=""

        items+=("${item}${delim}${body}")
    done <<< "$parsed_items"

    local json_output
    if [[ ${#items[@]} -gt 0 ]]; then
        json_output=$(generate_json "${items[@]}")
    else
        json_output="[]"
    fi

    if [[ -n "$OUTPUT_FILE" ]]; then
        echo "$json_output" > "$OUTPUT_FILE"
        log "Output written to $OUTPUT_FILE"
    else
        echo "$json_output"
    fi

    log "Done. Found ${#items[@]} events."
}

main "$@"
