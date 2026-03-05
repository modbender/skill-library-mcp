#!/usr/bin/env bash
# Neutron Memory CLI — save and search only

API_BASE="${NEUTRON_API_BASE:-https://api-neutron.vanarchain.com}"
CONFIG_FILE="${HOME}/.config/neutron/credentials.json"

# --- Dependency checks ---
if ! command -v curl &> /dev/null; then
    echo "Error: curl is required but not installed"
    echo "  macOS:  brew install curl"
    echo "  Linux:  apt install curl"
    exit 1
fi

if ! command -v jq &> /dev/null; then
    echo "Error: jq is required but not installed"
    echo "  macOS:  brew install jq"
    echo "  Linux:  apt install jq"
    exit 1
fi

# --- Load API key — env var first, then credentials file ---
API_KEY="${API_KEY:-${NEUTRON_API_KEY:-}}"

if [[ -z "$API_KEY" ]] && [[ -f "$CONFIG_FILE" ]]; then
    API_KEY=$(jq -r '.api_key // empty' "$CONFIG_FILE" 2>/dev/null)
fi

if [[ -z "$API_KEY" || "$API_KEY" == "null" ]]; then
    echo "Error: API_KEY not found"
    echo ""
    echo "Get your API key at: https://openclaw.vanarchain.com/"
    echo ""
    echo "Option 1 - Environment variable:"
    echo "  export API_KEY=nk_your_key"
    echo ""
    echo "Option 2 - Credentials file:"
    echo "  mkdir -p ~/.config/neutron"
    echo '  echo '"'"'{"api_key":"nk_your_key"}'"'"' > ~/.config/neutron/credentials.json'
    exit 1
fi

# --- Helpers ---

format_json() {
    jq .
}

# Parse API errors into human-readable messages
check_response() {
    local result="$1"
    local exit_code="$2"

    if [[ "$exit_code" -ne 0 ]]; then
        echo "Error: Could not reach Neutron API at ${API_BASE}"
        echo "  Check your internet connection and try again."
        return 1
    fi

    if [[ "$result" == *"Unauthorized"* || "$result" == *"Invalid API key"* ]]; then
        echo "Error: Invalid or expired API key"
        echo "  Check your key at: https://openclaw.vanarchain.com/manage"
        return 1
    fi

    if [[ "$result" == *"Payment Required"* || "$result" == *"Insufficient credits"* ]]; then
        echo "Error: Insufficient credits"
        echo "  Check your balance at: https://openclaw.vanarchain.com/manage"
        return 1
    fi

    if [[ "$result" == *'"error"'* ]]; then
        local msg
        if command -v jq &> /dev/null; then
            msg=$(echo "$result" | jq -r '.message // .error // "Unknown error"' 2>/dev/null)
        else
            msg="$result"
        fi
        echo "Error: $msg"
        return 1
    fi

    return 0
}

# --- Commands ---
case "${1:-}" in
    save)
        text="$2"
        title="${3:-Untitled}"
        if [[ -z "$text" ]]; then
            echo "Usage: neutron-memory save TEXT [TITLE]"
            exit 1
        fi
        # Build form field values safely using jq (prevents JSON injection)
        text_json=$(jq -n --arg t "$text" '[$t]')
        title_json=$(jq -n --arg t "$title" '[$t]')
        result=$(curl -s -X POST "${API_BASE}/memory/save" \
            -H "Authorization: Bearer ${API_KEY}" \
            -F "text=${text_json}" \
            -F 'textTypes=["text"]' \
            -F 'textSources=["bot_save"]' \
            -F "textTitles=${title_json}" 2>&1)
        if check_response "$result" "$?"; then
            echo "$result" | format_json
        else
            exit 1
        fi
        ;;
    search)
        query="$2"
        limit="${3:-10}"
        threshold="${4:-0.5}"
        if [[ -z "$query" ]]; then
            echo "Usage: neutron-memory search QUERY [LIMIT] [THRESHOLD]"
            exit 1
        fi
        # Validate numeric inputs
        if ! [[ "$limit" =~ ^[0-9]+$ ]]; then
            echo "Error: LIMIT must be a positive integer (got: $limit)"
            exit 1
        fi
        if ! [[ "$threshold" =~ ^[0-9]*\.?[0-9]+$ ]]; then
            echo "Error: THRESHOLD must be a number between 0 and 1 (got: $threshold)"
            exit 1
        fi
        # Build JSON body safely using jq (prevents JSON injection)
        json_body=$(jq -n --arg q "$query" --argjson l "$limit" --argjson t "$threshold" \
            '{"query":$q,"limit":$l,"threshold":$t}')
        result=$(curl -s -X POST "${API_BASE}/memory/search" \
            -H "Authorization: Bearer ${API_KEY}" \
            -H "Content-Type: application/json" \
            -d "$json_body" 2>&1)
        if check_response "$result" "$?"; then
            echo "$result" | format_json
        else
            exit 1
        fi
        ;;
    test)
        echo "Testing Neutron API connection..."
        echo ""

        # Check connectivity + auth
        result=$(curl -s -w "\n%{http_code}" -X POST "${API_BASE}/memory/search" \
            -H "Authorization: Bearer ${API_KEY}" \
            -H "Content-Type: application/json" \
            -d '{"query":"test","limit":1}' 2>&1)
        curl_exit=$?

        # Split response body and HTTP status code
        http_code=$(echo "$result" | tail -1)
        body=$(echo "$result" | sed '$d')

        if [[ "$curl_exit" -ne 0 ]]; then
            echo "FAIL: Cannot reach ${API_BASE}"
            echo "  Check your internet connection."
            exit 1
        fi

        if [[ "$http_code" == "401" || "$http_code" == "403" ]]; then
            echo "FAIL: Authentication failed (HTTP $http_code)"
            echo "  Your API key is invalid or expired."
            echo "  Check it at: https://openclaw.vanarchain.com/manage"
            exit 1
        fi

        if [[ "$http_code" == "402" ]]; then
            echo "FAIL: Insufficient credits (HTTP 402)"
            echo "  Top up at: https://openclaw.vanarchain.com/manage"
            exit 1
        fi

        if [[ "$http_code" -ge 200 && "$http_code" -lt 300 ]]; then
            echo "OK: API connection successful"
            echo "OK: Authentication verified"
            if command -v jq &> /dev/null; then
                count=$(echo "$body" | jq '.results | length' 2>/dev/null || echo "?")
                echo "OK: Found $count existing memories"
            fi
            echo ""
            echo "$body" | format_json
        else
            echo "FAIL: Unexpected response (HTTP $http_code)"
            echo "$body" | format_json
            exit 1
        fi
        ;;
    diagnose)
        echo "Neutron Memory — Diagnostics"
        echo ""

        # Check dependencies
        echo -n "curl:    "
        if command -v curl &> /dev/null; then
            echo "OK ($(curl --version | head -1 | cut -d' ' -f1-2))"
        else
            echo "MISSING — install with: brew install curl"
        fi

        echo -n "jq:      "
        if command -v jq &> /dev/null; then
            echo "OK ($(jq --version 2>/dev/null))"
        else
            echo "MISSING — install with: brew install jq"
        fi

        # Check API key
        echo -n "API key: "
        if [[ -n "$API_KEY" && "$API_KEY" != "null" ]]; then
            echo "OK (${API_KEY:0:7}...)"
        else
            echo "MISSING — run: export API_KEY=nk_your_key"
        fi

        # Check credentials file
        echo -n "Config:  "
        if [[ -f "$CONFIG_FILE" ]]; then
            echo "OK ($CONFIG_FILE)"
        else
            echo "Not found ($CONFIG_FILE) — optional if env var is set"
        fi

        # Check API connectivity
        echo -n "API:     "
        http_code=$(curl -s -o /dev/null -w "%{http_code}" -X POST "${API_BASE}/memory/search" \
            -H "Authorization: Bearer ${API_KEY}" \
            -H "Content-Type: application/json" \
            -d '{"query":"ping","limit":1}' 2>/dev/null)
        curl_exit=$?

        if [[ "$curl_exit" -ne 0 ]]; then
            echo "UNREACHABLE — cannot connect to ${API_BASE}"
        elif [[ "$http_code" == "401" || "$http_code" == "403" ]]; then
            echo "AUTH FAILED (HTTP $http_code) — check your API key"
        elif [[ "$http_code" == "402" ]]; then
            echo "NO CREDITS (HTTP 402) — top up at openclaw.vanarchain.com/manage"
        elif [[ "$http_code" -ge 200 && "$http_code" -lt 300 ]]; then
            echo "OK (HTTP $http_code)"
        else
            echo "ERROR (HTTP $http_code)"
        fi

        echo ""
        ;;
    *)
        echo "Neutron Memory CLI"
        echo ""
        echo "Usage: neutron-memory [command] [args]"
        echo ""
        echo "Commands:"
        echo "  save TEXT [TITLE]                         Save text to memory"
        echo "  search QUERY [LIMIT] [THRESHOLD]          Semantic search"
        echo "  test                                      Test connection and auth"
        echo "  diagnose                                  Check all prerequisites"
        echo ""
        echo "Examples:"
        echo "  neutron-memory save \"Hello world\" \"My first memory\""
        echo "  neutron-memory search \"hello\" 10 0.5"
        ;;
esac
