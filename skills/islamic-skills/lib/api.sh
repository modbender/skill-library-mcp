#!/bin/bash

# API Helper Functions

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/json.sh"

# Perform API Call
# Usage: api_call "url" [max_retries]
api_call() {
    local url="$1"
    local retries="${2:-3}"
    local response
    local http_code
    local count=0
    
    while [ $count -lt $retries ]; do
        # Fetch with curl, capturing HTTP code and content
        # Using -w to get http code at the end
        response=$(curl -sL -w "\n%{http_code}" "$url")
        http_code=$(echo "$response" | tail -n1)
        content=$(echo "$response" | sed '$d')
        
        if [ "$http_code" = "200" ]; then
            # Validate JSON if possible
            if [ "$HAS_JQ" = true ]; then
                if echo "$content" | jq . >/dev/null 2>&1; then
                    echo "$content"
                    return 0
                fi
                # Invalid JSON, but 200 OK? Might be issue
            else
                # If pure bash, just return content
                echo "$content"
                return 0
            fi
        fi
        
        # If we are here, it failed
        count=$((count + 1))
        # Exponential backoff? or just simple sleep
        sleep 1
    done
    
    # If failed after retries
    echo "Error: API request failed after $retries attempts. URL: $url HTTP: $http_code" >&2
    if [ ! -z "$content" ]; then
        echo "Response: $content" >&2
    fi
    return 1
}

# URL Encode string
# Usage: url_encode "string"
url_encode() {
    local string="$1"
    if [ "$HAS_JQ" = true ]; then
        jq -rn --arg x "$string" '$x|@uri'
    else
        # Python fallback if available
        if command -v python3 >/dev/null 2>&1; then
             python3 -c "import urllib.parse, sys; print(urllib.parse.quote(sys.argv[1]))" "$string"
        else
            # Pure bash fallback (simple)
            local length="${#string}"
            for (( i = 0; i < length; i++ )); do
                local c="${string:i:1}"
                case $c in
                    [a-zA-Z0-9.~_-]) printf "$c" ;;
                    *) printf '%%%02X' "'$c" ;;
                esac
            done
        fi
    fi
}
