#!/bin/bash
#===============================================================================
# BABY Brain - Web Operations Script
#===============================================================================
# Description: Web fetching, scraping, and browser automation
# Author: Baby
# Version: 1.0.0
#===============================================================================

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

ICON_SUCCESS="✅"
ICON_ERROR="❌"
ICON_INFO="ℹ️"
ICON_WEB="🌐"
ICON_BROWSER="🖥️"
ICON_DATA="📊"

#-------------------------------------------------------------------------------
# Configuration
#-------------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="${HOME}/.baby-brain"
DATA_DIR="${CONFIG_DIR}/web"
mkdir -p "${DATA_DIR}"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "${DATA_DIR}/web.log"
}

#-------------------------------------------------------------------------------
# Help
#-------------------------------------------------------------------------------
show_help() {
    cat << EOF
${CYAN}BABY Brain - Web Operations${NC}

${YELLOW}USAGE:${NC}
    $(basename "$0") [COMMAND] [OPTIONS]

${YELLOW}COMMANDS:${NC}
    ${ICON_WEB} fetch          Fetch URL content
    ${ICON_WEB} api            API requests
    ${ICON_DATA} scrape        Web scraping
    ${ICON_BROWSER} browse     Browser automation
    ${ICON_DATA} extract       Extract data
    ${ICON_WEB} download       Download files
    ${ICON_WEB} screenshot     Take screenshot
    ${ICON_DATA} images        Extract images
    ${ICON_WEB} headers        View HTTP headers
    ${ICON_WEB} test           Test endpoint
    ${ICON_WEB} monitor        Monitor URL changes
    ${ICON_DATA} json         JSON processing

${YELLOW}OPTIONS:${NC}
    -h, --help            Show help
    -u, --url             URL to fetch/scrape
    -o, --output          Output file
    --method              HTTP method (GET, POST, etc.)
    --data                Request body data
    --headers             Custom headers
    --selector            CSS selector
    --user-agent          Custom User-Agent
    --timeout             Timeout in seconds

${YELLOW}EXAMPLES:${NC}
    $(basename "$0") fetch "https://example.com"
    $(basename "$0") scrape "https://..." --selector ".product"
    $(basename "$0") api "https://api..." --method POST --data '{"key":"value"}'
    $(basename "$0") screenshot "https://example.com" -o screenshot.png
    $(basename "$0") download "https://example.com/file.zip"

EOF
}

#-------------------------------------------------------------------------------
# Fetch URL
#-------------------------------------------------------------------------------
cmd_fetch() {
    local url=""
    local output=""
    local headers=false
    local user_agent="BABY-Brain/1.0"
    local timeout=30

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -u|--url) url="$2"; shift 2 ;;
            -o|--output) output="$2"; shift 2 ;;
            --headers|-i) headers=true; shift ;;
            --user-agent) user_agent="$2"; shift 2 ;;
            --timeout) timeout="$2"; shift 2 ;;
            *) shift ;;
        esac
    done

    if [[ -z "$url" ]]; then
        echo -e "${RED}${ICON_ERROR} Missing --url${NC}"
        exit 1
    fi

    echo -e "${CYAN}${ICON_WEB} Fetching: $url${NC}"

    local timestamp=$(date +%Y%m%d_%H%M%S)
    [[ -z "$output" ]] && output="${DATA_DIR}/fetch_${timestamp}"

    if $headers; then
        curl -sI -A "$user_agent" --connect-timeout "$timeout" "$url" > "${output}_headers.txt"
        echo "Headers saved to: ${output}_headers.txt"
    else
        curl -sL -A "$user_agent" --connect-timeout "$timeout" -o "${output}.html" "$url"
        echo -e "${GREEN}${ICON_SUCCESS} Content saved to: ${output}.html${NC}"
        echo "Size: $(wc -c < "${output}.html") bytes"
    fi
}

#-------------------------------------------------------------------------------
# API Request
#-------------------------------------------------------------------------------
cmd_api() {
    local url=""
    local method="GET"
    local data=""
    local headers=""
    local output=""
    local format="json"

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -u|--url) url="$2"; shift 2 ;;
            --method|-m) method="$2"; shift 2 ;;
            --data|-d) data="$2"; shift 2 ;;
            --headers) headers="$2"; shift 2 ;;
            -o|--output) output="$2"; shift 2 ;;
            --format) format="$2"; shift 2 ;;
            *) shift ;;
        esac
    done

    if [[ -z "$url" ]]; then
        echo -e "${RED}${ICON_ERROR} Missing --url${NC}"
        exit 1
    fi

    echo -e "${CYAN}${ICON_WEB} API Request: $method $url${NC}"

    local timestamp=$(date +%Y%m%d_%H%M%S)
    [[ -z "$output" ]] && output="${DATA_DIR}/api_${timestamp}"

    # Build curl command
    local curl_cmd="curl -sL -w \"\n%{http_code}\" -o \"${output}.txt\""

    [[ -n "$headers" ]] && curl_cmd="$curl_cmd -H \"$headers\""
    [[ "$method" != "GET" ]] && curl_cmd="$curl_cmd -X $method"
    [[ -n "$data" ]] && curl_cmd="$curl_cmd -d '$data'"

    curl_cmd="$curl_cmd \"$url\""

    eval "$curl_cmd"

    local status=$(tail -n1 "${output}.txt")
    local body=$(sed '$d' "${output}.txt")

    echo "Status: $status"
    echo "Response:"
    echo "$body" | python3 -m json.tool 2>/dev/null || echo "$body"

    echo -e "${GREEN}${ICON_SUCCESS} Response saved to: ${output}.txt${NC}"
}

#-------------------------------------------------------------------------------
# Web Scraping
#-------------------------------------------------------------------------------
cmd_scrape() {
    local url=""
    local selector=""
    local output=""
    local attr="text"

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -u|--url) url="$2"; shift 2 ;;
            --selector|-s) selector="$2"; shift 2 ;;
            -o|--output) output="$2"; shift 2 ;;
            --attribute|-a) attr="$2"; shift 2 ;;
            *) shift ;;
        esac
    done

    if [[ -z "$url" ]]; then
        echo -e "${RED}${ICON_ERROR} Missing --url${NC}"
        exit 1
    fi

    echo -e "${CYAN}${ICON_DATA} Scraping: $url${NC}"

    local timestamp=$(date +%Y%m%d_%H%M%S)
    [[ -z "$output" ]] && output="${DATA_DIR}/scrape_${timestamp}"

    # Fetch page
    curl -sL "$url" > "${output}.html"
    echo -e "${GREEN}${ICON_SUCCESS} Page saved to: ${output}.html${NC}"

    if [[ -n "$selector" ]]; then
        echo "Extracted data with selector '$selector':"
        if command -v pup &> /dev/null; then
            cat "${output}.html" | pup "$selector" 2>/dev/null || echo "Extraction failed"
        elif command -v grep &> /dev/null; then
            grep -o "$selector" "${output}.html" 2>/dev/null | head -20 || echo "Selector extraction requires pup or similar tool"
        fi
    fi
}

#-------------------------------------------------------------------------------
# Browser Automation
#-------------------------------------------------------------------------------
cmd_browse() {
    local url=""
    local action="navigate"
    local output=""
    local screenshot=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -u|--url) url="$2"; shift 2 ;;
            --action) action="$2"; shift 2 ;;
            -o|--output) output="$2"; shift 2 ;;
            --screenshot|-s) screenshot=true; shift ;;
            *) shift ;;
        esac
    done

    if [[ -z "$url" ]]; then
        echo -e "${RED}${ICON_ERROR} Missing --url${NC}"
        exit 1
    fi

    echo -e "${CYAN}${ICON_BROWSER} Browser Action: $action${NC}"

    [[ -z "$output" ]] && output="${DATA_DIR}/browse_$(date +%Y%m%d_%H%M%S)"

    case "$action" in
        navigate)
            curl -sL -o "${output}.html" "$url"
            echo -e "${GREEN}${ICON_SUCCESS} Page saved to: ${output}.html${NC}"
            ;;
        screenshot)
            if command -v chromium &> /dev/null || command -v google-chrome &> /dev/null; then
                local chrome_cmd=$(command -v chromium || command -v google-chrome)
                $chrome_cmd --headless --disable-gpu --screenshot="${output}.png" --virtual-time-budget=5000 "$url" 2>/dev/null
                echo -e "${GREEN}${ICON_SUCCESS} Screenshot saved to: ${output}.png${NC}"
            else
                echo -e "${RED}${ICON_ERROR} Chrome/Chromium not found${NC}"
            fi
            ;;
        *)
            echo "Unknown action: $action"
            ;;
    esac
}

#-------------------------------------------------------------------------------
# Data Extraction
#-------------------------------------------------------------------------------
cmd_extract() {
    local file=""
    local pattern=""
    local output=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -f|--file) file="$2"; shift 2 ;;
            --pattern|-p) pattern="$2"; shift 2 ;;
            -o|--output) output="$2"; shift 2 ;;
            *) shift ;;
        esac
    done

    if [[ -z "$file" ]]; then
        echo -e "${RED}${ICON_ERROR} Missing --file${NC}"
        exit 1
    fi

    if [[ ! -f "$file" ]]; then
        echo -e "${RED}${ICON_ERROR} File not found: $file${NC}"
        exit 1
    fi

    echo -e "${CYAN}${ICON_DATA} Extracting from: $file${NC}"

    [[ -z "$output" ]] && output="${DATA_DIR}/extract_$(date +%Y%m%d_%H%M%S)"

    if [[ -n "$pattern" ]]; then
        grep -o "$pattern" "$file" > "${output}.txt" 2>/dev/null
        echo -e "${GREEN}${ICON_SUCCESS} Extracted to: ${output}.txt${NC}"
    else
        echo "Usage: --pattern 'regex or text to extract'"
    fi
}

#-------------------------------------------------------------------------------
# Download
#-------------------------------------------------------------------------------
cmd_download() {
    local url=""
    local output=""
    local retries=3

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -u|--url) url="$2"; shift 2 ;;
            -o|--output) output="$2"; shift 2 ;;
            --retries) retries="$2"; shift 2 ;;
            *) shift ;;
        esac
    done

    if [[ -z "$url" ]]; then
        echo -e "${RED}${ICON_ERROR} Missing --url${NC}"
        exit 1
    fi

    echo -e "${CYAN}${ICON_WEB} Downloading: $url${NC}"

    [[ -z "$output" ]] && output=$(basename "$url")

    local attempt=1
    while [[ $attempt -le $retries ]]; do
        echo "Attempt $attempt/$retries..."

        if curl -sL --retry 3 --retry-delay 2 -o "$output" "$url"; then
            echo -e "${GREEN}${ICON_SUCCESS} Downloaded: $output${NC}"
            echo "Size: $(du -h "$output" | cut -f1)"
            return 0
        fi

        ((attempt++))
    done

    echo -e "${RED}${ICON_ERROR} Download failed after $retries attempts${NC}"
}

#-------------------------------------------------------------------------------
# Screenshot
#-------------------------------------------------------------------------------
cmd_screenshot() {
    local url=""
    local output=""
    local full=true

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -u|--url) url="$2"; shift 2 ;;
            -o|--output) output="$2"; shift 2 ;;
            --no-full) full=false; shift ;;
            *) shift ;;
        esac
    done

    if [[ -z "$url" ]]; then
        echo -e "${RED}${ICON_ERROR} Missing --url${NC}"
        exit 1
    fi

    echo -e "${CYAN}${ICON_BROWSER} Taking screenshot: $url${NC}"

    [[ -z "$output" ]] && output="${DATA_DIR}/screenshot_$(date +%Y%m%d_%H%M%S).png"

    if command -v chromium &> /dev/null || command -v google-chrome &> /dev/null; then
        local chrome_cmd=$(command -v chromium || command -v google-chrome)

        if $full; then
            $chrome_cmd --headless --disable-gpu --screenshot="$output" --virtual-time-budget=10000 --full-page-screenshot "$url" 2>/dev/null || {
                $chrome_cmd --headless --disable-gpu --screenshot="$output" --virtual-time-budget=10000 "$url" 2>/dev/null
            }
        else
            $chrome_cmd --headless --disable-gpu --screenshot="$output" --virtual-time-budget=5000 "$url" 2>/dev/null
        fi

        echo -e "${GREEN}${ICON_SUCCESS} Screenshot saved to: $output${NC}"
    else
        echo -e "${RED}${ICON_ERROR} Chrome/Chromium not found${NC}"
        echo "Install chromium: apt install chromium"
    fi
}

#-------------------------------------------------------------------------------
# Extract Images
#-------------------------------------------------------------------------------
cmd_images() {
    local url=""
    local output=""
    local limit=20

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -u|--url) url="$2"; shift 2 ;;
            -o|--output) output="$2"; shift 2 ;;
            --limit) limit="$2"; shift 2 ;;
            *) shift ;;
        esac
    done

    if [[ -z "$url" ]]; then
        echo -e "${RED}${ICON_ERROR} Missing --url${NC}"
        exit 1
    fi

    echo -e "${CYAN}${ICON_DATA} Extracting images from: $url${NC}"

    [[ -z "$output" ]] && output="${DATA_DIR}/images_$(date +%Y%m%d)"

    mkdir -p "$output"

    curl -sL "$url" | grep -o 'src="[^"]*"' | grep -E '\.(jpg|jpeg|png|gif|webp)' | sed 's/src="//;s/"$//' | head -"$limit" | while read -r img_url; do
        [[ "$img_url" == http* ]] || img_url="${url}${img_url}"
        filename=$(basename "$img_url")
        curl -sL -o "${output}/${filename}" "$img_url" 2>/dev/null && echo "Downloaded: $filename" || echo "Failed: $img_url"
    done

    echo -e "${GREEN}${ICON_SUCCESS} Images saved to: $output${NC}"
}

#-------------------------------------------------------------------------------
# View Headers
#-------------------------------------------------------------------------------
cmd_headers() {
    local url=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -u|--url) url="$2"; shift 2 ;;
            *) shift ;;
        esac
    done

    if [[ -z "$url" ]]; then
        echo -e "${RED}${ICON_ERROR} Missing --url${NC}"
        exit 1
    fi

    echo -e "${CYAN}${ICON_WEB} HTTP Headers: $url${NC}"
    echo ""

    curl -sI "$url"
}

#-------------------------------------------------------------------------------
# Test Endpoint
#-------------------------------------------------------------------------------
cmd_test() {
    local url=""
    local method="GET"
    local timeout=10

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -u|--url) url="$2"; shift 2 ;;
            --method) method="$2"; shift 2 ;;
            --timeout) timeout="$2"; shift 2 ;;
            *) shift ;;
        esac
    done

    if [[ -z "$url" ]]; then
        echo -e "${RED}${ICON_ERROR} Missing --url${NC}"
        exit 1
    fi

    echo -e "${CYAN}${ICON_WEB} Testing: $method $url${NC}"
    echo ""

    local start_time=$(date +%s%N)

    local response=$(curl -sL -o /dev/null -w "%{http_code}|%{time_total}|%{size_download}" \
        --connect-timeout "$timeout" -X "$method" "$url" 2>/dev/null)

    local end_time=$(date +%s%N)
    local duration=$(( (end_time - start_time) / 1000000 ))

    local status=$(echo "$response" | cut -d'|' -f1)
    local time_taken=$(echo "$response" | cut -d'|' -f2)
    local size=$(echo "$response" | cut -d'|' -f3)

    echo "Status: $status"
    echo "Response Time: ${time_taken}s"
    echo "Size: ${size} bytes"

    if [[ "$status" == "200" ]]; then
        echo -e "${GREEN}${ICON_SUCCESS} Endpoint is healthy${NC}"
    else
        echo -e "${RED}${ICON_ERROR} Endpoint returned status: $status${NC}"
    fi
}

#-------------------------------------------------------------------------------
# Monitor URL
#-------------------------------------------------------------------------------
cmd_monitor() {
    local url=""
    local interval=60
    local changes_only=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -u|--url) url="$2"; shift 2 ;;
            --interval) interval="$2"; shift 2 ;;
            --changes) changes_only=true; shift ;;
            *) shift ;;
        esac
    done

    if [[ -z "$url" ]]; then
        echo -e "${RED}${ICON_ERROR} Missing --url${NC}"
        exit 1
    fi

    echo -e "${CYAN}${ICON_WEB} Monitoring: $url (every ${interval}s)${NC}"

    local last_hash=""
    local count=1

    while true; do
        local current_content=$(curl -sL "$url" 2>/dev/null)
        local current_hash=$(echo "$current_content" | md5sum | cut -d' ' -f1)

        if [[ "$current_hash" != "$last_hash" ]]; then
            if $changes_only; then
                echo "[$(date '+%H:%M:%S')] Change detected!"
            else
                echo "[$(date '+%H:%M:%S')] Iteration $count - Content changed"
            fi
            echo "  Hash: $current_hash"
            last_hash=$current_hash
        else
            if ! $changes_only; then
                echo "[$(date '+%H:%M:%S')] Iteration $count - No changes"
            fi
        fi

        ((count++))
        sleep "$interval"
    done
}

#-------------------------------------------------------------------------------
# JSON Processing
#-------------------------------------------------------------------------------
cmd_json() {
    local file=""
    local query=""
    local output=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -f|--file) file="$2"; shift 2 ;;
            -q|--query) query="$2"; shift 2 ;;
            -o|--output) output="$2"; shift 2 ;;
            *) shift ;;
        esac
    done

    if [[ -z "$file" ]]; then
        echo -e "${RED}${ICON_ERROR} Missing --file${NC}"
        exit 1
    fi

    echo -e "${CYAN}${ICON_DATA} JSON Processing: $file${NC}"

    [[ -z "$output" ]] && output="${DATA_DIR}/json_$(date +%Y%m%d_%H%M%S)"

    if [[ -f "$file" ]]; then
        if [[ -n "$query" ]]; then
            python3 -c "import json, sys; data=json.load(open('$file')); print(json.dumps($query, indent=2))" > "${output}.txt" 2>/dev/null || {
                python3 -c "import json, sys; data=json.load(open('$file')); print(json.dumps(data.get('$query', 'Not found'), indent=2))" > "${output}.txt"
            }
            echo "Query result saved to: ${output}.txt"
        else
            python3 -m json.tool "$file" > "${output}_formatted.json"
            echo -e "${GREEN}${ICON_SUCCESS} Formatted JSON saved to: ${output}_formatted.json${NC}"
        fi
    else
        echo -e "${RED}${ICON_ERROR} File not found: $file${NC}"
    fi
}

#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------
main() {
    local command="${1:-}"

    if [[ "$command" == "--help" || "$command" == "-h" ]]; then
        show_help
        exit 0
    fi

    if [[ -z "$command" ]]; then
        show_help
        exit 0
    fi

    shift

    case "$command" in
        fetch|get) cmd_fetch "$@" ;;
        api|request) cmd_api "$@" ;;
        scrape|scraping) cmd_scrape "$@" ;;
        browse|browser) cmd_browse "$@" ;;
        extract|extraction) cmd_extract "$@" ;;
        download) cmd_download "$@" ;;
        screenshot) cmd_screenshot "$@" ;;
        images|image-extract) cmd_images "$@" ;;
        headers|http-headers) cmd_headers "$@" ;;
        test|test-endpoint) cmd_test "$@" ;;
        monitor|monitoring) cmd_monitor "$@" ;;
        json|json-process) cmd_json "$@" ;;
        *) echo -e "${RED}Unknown command: $command${NC}"; show_help; exit 1 ;;
    esac
}

main "$@"
