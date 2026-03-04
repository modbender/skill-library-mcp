#!/bin/bash

# Default values
QUERY=""
ENCODING=""

# Parse parameters
if [[ ! "$1" == --* ]] && [ -n "$1" ]; then
    # First argument is positional, treat it as the query
    QUERY="$1"
    shift
fi

# Parse remaining named arguments
while [ "$#" -gt 0 ]; do
    case "$1" in
        --query)
            QUERY="$2"
            shift 2
            ;;
        --encoding)
            ENCODING="$2"
            shift 2
            ;;
        *)
            echo "Unknown parameter: $1"
            echo "Usage: $0 <query> OR $0 --query <query> [--encoding <text|json|markdown>]"
            exit 1
            ;;
    esac
done

# Validate that query is not empty
if [ -z "$QUERY" ]; then
    echo "Error: the 'query' parameter is required and must be in Chinese."
    echo "Usage: $0 <query> OR $0 --query <query> [--encoding <text|json|markdown>]"
    exit 1
fi

# Validate encoding if provided
if [ -n "$ENCODING" ] && [[ ! "$ENCODING" =~ ^(text|json|markdown)$ ]]; then
    echo "Error: 'encoding' must be one of text, json, or markdown."
    exit 1
fi

# Base API URL
API_URL="https://60s.viki.moe/v2/weather"

# Build the curl command array
# We use -G to make a GET request and --data-urlencode to safely encode the Chinese query
CURL_CMD=(curl -s -G "$API_URL" --data-urlencode "query=$QUERY")

# Add the encoding parameter if it was provided
if [ -n "$ENCODING" ]; then
    CURL_CMD+=(--data-urlencode "encoding=$ENCODING")
fi

# Execute the request
"${CURL_CMD[@]}"
echo # Add a newline at the end for better output readability
