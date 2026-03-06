#!/bin/bash
# Jina Reader CLI wrapper
# Usage: ./reader.sh [--mode read|search|ground] [--format markdown|html|text|json] [--json] [--nocache] <URL|query>
# 
# Modes:
#   read    - Extract content from URL (default)
#   search  - Search web and get top results with full content
#   ground  - Fact-check a statement
#
# Examples:
#   ./reader.sh "https://example.com"
#   ./reader.sh --mode search "latest AI news"
#   ./reader.sh --mode ground "OpenAI was founded in 2015"

set -e

MODE="read"
FORMAT="markdown"
JSON=false
NOCACHE=""
SELECTOR=""
REMOVE=""
PROXY=""

show_help() {
    cat << EOF
Jina Reader - Extract web content via Jina AI

Usage: $0 [options] <URL or query>

Options:
    --mode MODE     read, search, or ground (default: read)
    --format FMT    markdown, html, text, or screenshot (default: markdown)
    --json          Output raw JSON
    --nocache       Force fresh content
    --selector CSS  Extract specific element
    --remove SEL   Remove elements (comma-separated)
    --proxy CC     Country code for geo-proxy (br, us, etc.)
    -h, --help     Show this help

Examples:
    $0 "https://example.com"
    $0 --mode search "AI trends 2025"
    $0 --mode ground "Tesla is worth more than Toyota"
EOF
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --mode)
            MODE="$2"
            shift 2
            ;;
        --format)
            FORMAT="$2"
            shift 2
            ;;
        --json)
            JSON=true
            shift
            ;;
        --nocache)
            NOCACHE="?nocache=true"
            shift
            ;;
        --selector)
            SELECTOR="&selector=$(echo $2 | sed 's/ /%20/g')"
            shift 2
            ;;
        --remove)
            REMOVE="&remove=$(echo $2 | sed 's/,/%2C/g')"
            shift 2
            ;;
        --proxy)
            PROXY="?country=$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            TARGET="$1"
            shift
            ;;
    esac
done

if [ -z "$TARGET" ]; then
    echo "Error: URL or query required"
    show_help
    exit 1
fi

# Get API key
API_KEY="${JINA_API_KEY:-}"

# Build URL based on mode
if [ "$MODE" = "read" ]; then
    BASE_URL="https://r.jina.ai/url/$TARGET"
elif [ "$MODE" = "search" ]; then
    BASE_URL="https://r.jina.ai/search$PROXY?q=$(echo "$TARGET" | sed 's/ /%20/g')"
elif [ "$MODE" = "ground" ]; then
    BASE_URL="https://r.jina.ai/ground"$PROXY
    # For ground mode, send as POST would be better, but use q param
    TARGET="statement=$(echo "$TARGET" | sed 's/ /%20/g')"
else
    echo "Error: Unknown mode: $MODE"
    exit 1
fi

# Add format if not default
if [ "$FORMAT" != "markdown" ]; then
    BASE_URL="$BASE_URL&format=$FORMAT"
fi

# Add selectors
BASE_URL="$BASE_URL$SELECTOR$REMOVE$NOCACHE"

# Make request
if [ -n "$API_KEY" ]; then
    # Use API key for full features
    curl -s -H "Authorization: Bearer $API_KEY" \
         -H "Accept: application/json" \
         "$BASE_URL" | if [ "$JSON" = true ]; then
             cat
         else
             # Extract content field if JSON
             grep -o '"content":"[^"]*"' | sed 's/"content":"//;s/"$//' || cat
         fi
else
    # Free tier
    curl -s "$BASE_URL"
fi
