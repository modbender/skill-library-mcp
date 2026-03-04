#!/bin/bash
# Tavily Search Script for OpenClaw

# Check if API key is set
if [ -z "$TAVILY_API_KEY" ]; then
    echo "Error: TAVILY_API_KEY environment variable is not set."
    echo "Please set your Tavily API key: export TAVILY_API_KEY='your-key-here'"
    exit 1
fi

# Default parameters
QUERY=""
SEARCH_DEPTH="basic"
MAX_RESULTS=5
INCLUDE_ANSWER=false
INCLUDE_IMAGES=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --query)
            QUERY="$2"
            shift 2
            ;;
        --depth)
            SEARCH_DEPTH="$2"
            shift 2
            ;;
        --max-results)
            MAX_RESULTS="$2"
            shift 2
            ;;
        --include-answer)
            INCLUDE_ANSWER=true
            shift
            ;;
        --include-images)
            INCLUDE_IMAGES=true
            shift
            ;;
        --help)
            echo "Tavily Search Script"
            echo "Usage: $0 --query \"search query\" [options]"
            echo ""
            echo "Options:"
            echo "  --query TEXT          Search query (required)"
            echo "  --depth basic|advanced Search depth (default: basic)"
            echo "  --max-results NUM     Max results (1-10, default: 5)"
            echo "  --include-answer      Include AI-generated answer"
            echo "  --include-images      Include image URLs"
            echo "  --help                Show this help"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Check if query is provided
if [ -z "$QUERY" ]; then
    echo "Error: Query is required. Use --query \"your search query\""
    exit 1
fi

# Make API request
curl -s -X POST "https://api.tavily.com/search" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TAVILY_API_KEY" \
  -d "{
    \"query\": \"$QUERY\",
    \"search_depth\": \"$SEARCH_DEPTH\",
    \"max_results\": $MAX_RESULTS,
    \"include_answer\": $INCLUDE_ANSWER,
    \"include_images\": $INCLUDE_IMAGES
  }" | jq .