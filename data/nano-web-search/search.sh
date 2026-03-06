#!/bin/bash
# NanoGPT Web Search CLI

set -e

# API endpoint
API_URL="https://nano-gpt.com/api/web"

# Default values
QUERY=""
PROVIDER="linkup"
DEPTH="standard"
OUTPUT_TYPE="searchResults"
FROM_DATE=""
TO_DATE=""
INCLUDE_DOMAINS=""
EXCLUDE_DOMAINS=""
MAX_RESULTS=""
JSON_OUTPUT=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --provider)
            PROVIDER="$2"
            shift 2
            ;;
        --depth)
            DEPTH="$2"
            shift 2
            ;;
        --output-type)
            OUTPUT_TYPE="$2"
            shift 2
            ;;
        --from-date)
            FROM_DATE="$2"
            shift 2
            ;;
        --to-date)
            TO_DATE="$2"
            shift 2
            ;;
        --include-domains)
            INCLUDE_DOMAINS="$2"
            shift 2
            ;;
        --exclude-domains)
            EXCLUDE_DOMAINS="$2"
            shift 2
            ;;
        --max-results)
            MAX_RESULTS="$2"
            shift 2
            ;;
        --json)
            JSON_OUTPUT=true
            shift
            ;;
        -*)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
        *)
            if [ -z "$QUERY" ]; then
                QUERY="$1"
            fi
            shift
            ;;
    esac
done

if [ -z "$QUERY" ]; then
    echo "Usage: search.sh <query> [options]" >&2
    echo "Options:" >&2
    echo "  --provider PROVIDER       Search provider (default: linkup)" >&2
    echo "  --depth DEPTH             Search depth: standard or deep" >&2
    echo "  --output-type TYPE        Output format: searchResults, sourcedAnswer" >&2
    echo "  --from-date DATE          Start date (YYYY-MM-DD)" >&2
    echo "  --to-date DATE            End date (YYYY-MM-DD)" >&2
    echo "  --include-domains DOMAINS Comma-separated domains to include" >&2
    echo "  --exclude-domains DOMAINS Comma-separated domains to exclude" >&2
    echo "  --max-results N           Max results" >&2
    echo "  --json                    Output raw JSON" >&2
    echo "" >&2
    echo "Set NANOGPT_API_KEY environment variable before using." >&2
    exit 1
fi

# Check for API key
if [ -z "$NANOGPT_API_KEY" ]; then
    echo "Error: NANOGPT_API_KEY environment variable not set." >&2
    echo "Get your API key at https://nano-gpt.com" >&2
    exit 1
fi

# Build JSON payload safely using Python to escape all values
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

JSON_PAYLOAD=$(python3 "$SCRIPT_DIR/build_payload.py" \
    --query "$QUERY" \
    --provider "$PROVIDER" \
    --depth "$DEPTH" \
    --output-type "$OUTPUT_TYPE" \
    ${FROM_DATE:+--from-date "$FROM_DATE"} \
    ${TO_DATE:+--to-date "$TO_DATE"} \
    ${INCLUDE_DOMAINS:+--include-domains "$INCLUDE_DOMAINS"} \
    ${EXCLUDE_DOMAINS:+--exclude-domains "$EXCLUDE_DOMAINS"} \
    ${MAX_RESULTS:+--max-results "$MAX_RESULTS"})

# Make request
RESPONSE=$(curl -s -X POST "$API_URL" \
    -H "Content-Type: application/json" \
    -H "x-api-key: $NANOGPT_API_KEY" \
    -d "$JSON_PAYLOAD")

# Output
if [ "$JSON_OUTPUT" = true ]; then
    echo "$RESPONSE"
else
    echo "$RESPONSE" | python3 "$SCRIPT_DIR/format_output.py"
fi
