#!/bin/bash

# Default values
QUERY=""
ENCODING=""
DAYS=""

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
        --days)
            DAYS="$2"
            shift 2
            ;;
        *)
            echo "Unknown parameter: $1"
            echo "Usage: $0 <query> OR $0 --query <query> [--encoding <text|json|markdown>] [--days <0-8>]"
            exit 1
            ;;
    esac
done

# Validate that query is not empty
if [ -z "$QUERY" ]; then
    echo "Error: the 'query' parameter is required and must be in Chinese."
    echo "Usage: $0 <query> OR $0 --query <query> [--encoding <text|json|markdown>] [--days <0-8>]"
    exit 1
fi

# Validate encoding if provided
if [ -n "$ENCODING" ] && [[ ! "$ENCODING" =~ ^(text|json|markdown)$ ]]; then
    echo "Error: 'encoding' must be one of text, json, or markdown."
    exit 1
fi

# Validate days if provided
if [ -n "$DAYS" ] && [[ ! "$DAYS" =~ ^[0-8]$ ]]; then
    echo "Error: 'days' must be an integer between 0 and 8."
    exit 1
fi

# Base API URL
API_URL="https://60s.viki.moe/v2/weather/forecast"

# Build the curl command array
# We use -G to make a GET request and --data-urlencode to safely encode the Chinese query
CURL_CMD=(curl -s -G "$API_URL" --data-urlencode "query=$QUERY")

# Add the encoding parameter if it was provided
if [ -n "$ENCODING" ]; then
    CURL_CMD+=(--data-urlencode "encoding=$ENCODING")
fi

# Add the days parameter if it was provided
if [ -n "$DAYS" ]; then
    CURL_CMD+=(--data-urlencode "days=$DAYS")
fi

# Execute the request
"${CURL_CMD[@]}"
echo # Add a newline at the end for better output readability
