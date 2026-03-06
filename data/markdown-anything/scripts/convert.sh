#!/usr/bin/env bash
# SECURITY MANIFEST:
# Environment variables accessed: MDA_API_TOKEN, MDA_ENHANCED_AI, MDA_INCLUDE_METADATA, MDA_OPTIMIZE_TOKENS
# External endpoints called: https://markdownanything.com/api/v1/convert (only)
# Local files read: the file path passed as $1
# Local files written: none

set -euo pipefail

FILE_PATH="${1:?Usage: convert.sh <file-path>}"

if [ ! -f "$FILE_PATH" ]; then
    echo "Error: File not found: $FILE_PATH" >&2
    exit 1
fi

CURL_ARGS=(
    --silent --fail --show-error
    -X POST
    -H "Authorization: Bearer ${MDA_API_TOKEN:?MDA_API_TOKEN is not set}"
    -F "file=@${FILE_PATH}"
)

if [ "${MDA_ENHANCED_AI:-false}" = "true" ]; then
    CURL_ARGS+=(-F "use_enhanced_ai=true")
fi

if [ "${MDA_INCLUDE_METADATA:-false}" = "true" ]; then
    CURL_ARGS+=(-F "include_metadata=true")
fi

if [ "${MDA_OPTIMIZE_TOKENS:-false}" = "true" ]; then
    CURL_ARGS+=(-F "optimize_tokens=true")
fi

RESPONSE=$(curl "${CURL_ARGS[@]}" "https://markdownanything.com/api/v1/convert")

SUCCESS=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('success', False))" 2>/dev/null || echo "False")

if [ "$SUCCESS" = "True" ]; then
    echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['markdown'])"
else
    ERROR=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('error', 'Unknown error'))" 2>/dev/null || echo "$RESPONSE")
    echo "Conversion failed: $ERROR" >&2
    exit 1
fi
