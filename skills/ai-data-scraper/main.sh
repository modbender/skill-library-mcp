#!/bin/bash
# Data Scraper - Main Script

set -e

URL="${1:-}"
API_URL="${2:-}"
FORMAT="${3:-json}"
OUTPUT="./output"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

init() {
    mkdir -p "$OUTPUT"
}

scrape_web() {
    log_info "Scraping web page: $URL"

    # Check dependencies
    if ! command -v curl &> /dev/null; then
        log_error "curl not installed"
        exit 1
    fi

    # Fetch page
    local data=$(curl -sL "$URL" --compressed)

    # Save data
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local output_file="${OUTPUT}/scrape_${timestamp}.${FORMAT}"

    case "$FORMAT" in
        json)
            echo "$data" > "$output_file"
            ;;
        html)
            echo "$data" > "$output_file"
            ;;
        text)
            echo "$data" | sed 's/<[^>]*>//g' > "$output_file"
            ;;
    esac

    log_info "Saved to: $output_file"
    echo "$output_file"
}

scrape_api() {
    log_info "Fetching API data: $API_URL"

    local data=$(curl -sL "$API_URL" --compressed)

    local timestamp=$(date +%Y%m%d_%H%M%S)
    local output_file="${OUTPUT}/api_${timestamp}.${FORMAT}"

    case "$FORMAT" in
        json)
            echo "$data" > "$output_file"
            ;;
    esac

    log_info "Saved to: $output_file"
    echo "$output_file"
}

main() {
    log_info "Data Scraper Started"

    if [ -n "$URL" ]; then
        scrape_web
    elif [ -n "$API_URL" ]; then
        scrape_api
    else
        log_error "Please provide URL or API_URL"
        echo "Usage: $0 --url <URL> [--format json|html|text]"
        echo "       $0 --api <API_URL> [--format json]"
        exit 1
    fi

    log_info "Done!"
}

init
main "$@"
