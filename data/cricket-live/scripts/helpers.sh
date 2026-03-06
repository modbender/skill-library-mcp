#!/usr/bin/env bash
# Shared helpers for cricket-scores skill

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CACHE_DIR="${CRICKET_CACHE_DIR:-/tmp/cricket-cache}"
BASE_URL="https://api.cricapi.com/v1"

# Get API key from env or config
get_api_key() {
    if [[ -n "${CRICKET_API_KEY:-}" ]]; then
        echo "$CRICKET_API_KEY"
        return 0
    fi
    # Try reading from config
    local config="$SKILL_DIR/config/cricket.yaml"
    if [[ -f "$config" ]]; then
        local key
        key=$(grep '^api_key:' "$config" | sed 's/api_key: *"\{0,1\}\([^"]*\)"\{0,1\}/\1/' | tr -d ' ')
        if [[ -n "$key" ]]; then
            echo "$key"
            return 0
        fi
    fi
    return 1
}

# Check API key exists
require_api_key() {
    local key
    key=$(get_api_key) || true
    if [[ -z "$key" ]]; then
        echo "❌ No API key found!" >&2
        echo "" >&2
        echo "Set your CricketData.org API key:" >&2
        echo "  export CRICKET_API_KEY=\"your-key-here\"" >&2
        echo "" >&2
        echo "Get a free key at: https://cricketdata.org" >&2
        return 1
    fi
    echo "$key"
}

# Cache helper: get cached response or return empty
# Usage: cache_get "cache-name" ttl_seconds
cache_get() {
    local name="$1" ttl="$2"
    local file="$CACHE_DIR/${name}.json"
    mkdir -p "$CACHE_DIR"
    if [[ -f "$file" ]]; then
        local age=$(( $(date +%s) - $(stat -c %Y "$file" 2>/dev/null || stat -f %m "$file" 2>/dev/null) ))
        if (( age < ttl )); then
            cat "$file"
            return 0
        fi
    fi
    return 1
}

# Cache helper: save response
cache_set() {
    local name="$1"
    local file="$CACHE_DIR/${name}.json"
    mkdir -p "$CACHE_DIR"
    cat > "$file"
}

# Make API call with caching
# Usage: api_call "endpoint" "cache-name" ttl_seconds [extra_params]
api_call() {
    local endpoint="$1" cache_name="$2" ttl="$3" extra_params="${4:-}"
    
    # Try cache first
    local cached
    if cached=$(cache_get "$cache_name" "$ttl"); then
        echo "$cached"
        return 0
    fi
    
    local key
    key=$(require_api_key 2>&1) || { echo "$key"; return 1; }
    
    local url="${BASE_URL}/${endpoint}?apikey=${key}"
    if [[ -n "$extra_params" ]]; then
        url="${url}&${extra_params}"
    fi
    
    local response
    response=$(curl -s --max-time 10 "$url")
    
    # Check for API errors
    local status
    status=$(echo "$response" | jq -r '.status // "unknown"' 2>/dev/null)
    
    if [[ "$status" == "failure" ]]; then
        local reason
        reason=$(echo "$response" | jq -r '.reason // "Unknown error"' 2>/dev/null)
        if [[ "$reason" == *"limit"* ]] || [[ "$reason" == *"quota"* ]]; then
            echo "⚠️ API quota exhausted (100 calls/day limit reached)"
            echo "Try again tomorrow or upgrade at cricketdata.org"
            return 2  # Quota exhausted - caller can try fallback
        fi
        echo "❌ API Error: $reason"
        return 1
    fi
    
    # Cache successful response
    echo "$response" | cache_set "$cache_name"
    echo "$response"
    return 0
}

# Convert UTC date string to IST display
to_ist() {
    local utc_date="$1"
    if [[ -z "$utc_date" ]] || [[ "$utc_date" == "null" ]]; then
        echo "TBD"
        return
    fi
    # Try to parse and convert
    local ist
    ist=$(TZ="Asia/Kolkata" date -d "$utc_date" "+%d %b %Y, %I:%M %p IST" 2>/dev/null)
    if [[ -n "$ist" ]]; then
        echo "$ist"
    else
        echo "$utc_date"
    fi
}

# Resolve team alias to canonical name
resolve_team() {
    local input="$1"
    local teams_file="$SKILL_DIR/config/teams.yaml"
    
    # Simple grep-based matching (case insensitive)
    local match
    match=$(grep -i "^    - ${input}$" "$teams_file" 2>/dev/null | head -1)
    if [[ -n "$match" ]]; then
        # Find the parent key (canonical name)
        local line_num
        line_num=$(grep -in "^    - ${input}$" "$teams_file" | head -1 | cut -d: -f1)
        # Walk backwards to find the canonical name
        local canonical
        canonical=$(head -n "$line_num" "$teams_file" | grep -E '^  [A-Z]' | tail -1 | sed 's/: *$//' | tr -d ' ')
        if [[ -n "$canonical" ]]; then
            echo "$canonical"
            return 0
        fi
    fi
    # Return input as-is if no match
    echo "$input"
}

# Format match status with emoji
format_status() {
    local status="$1"
    case "$status" in
        *"won"*|*"Won"*) echo "🏆 $status" ;;
        *"live"*|*"Live"*|*"In Progress"*) echo "🔴 $status" ;;
        *"Draw"*|*"draw"*) echo "🤝 $status" ;;
        *"No Result"*|*"Abandoned"*) echo "🌧️ $status" ;;
        *) echo "📊 $status" ;;
    esac
}

# Team flag emoji (best effort)
team_emoji() {
    local team="$1"
    case "$team" in
        *India*) echo "🇮🇳" ;;
        *Australia*) echo "🇦🇺" ;;
        *England*) echo "🏴󠁧󠁢󠁥󠁮󠁧󠁿" ;;
        *Pakistan*) echo "🇵🇰" ;;
        *"South Africa"*) echo "🇿🇦" ;;
        *"New Zealand"*) echo "🇳🇿" ;;
        *"Sri Lanka"*) echo "🇱🇰" ;;
        *"West Indies"*) echo "🏝️" ;;
        *Bangladesh*) echo "🇧🇩" ;;
        *Afghanistan*) echo "🇦🇫" ;;
        *) echo "🏏" ;;
    esac
}
