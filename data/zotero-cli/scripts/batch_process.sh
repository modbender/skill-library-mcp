#!/usr/bin/env bash
#
# Batch processing script for zotero-cli
#
# Usage:
#   ./batch_process.sh queries.txt
#   ./batch_process.sh queries.txt --output results.txt
#

set -euo pipefail

# Default values
OUTPUT_FILE=""
QUERIES_FILE=""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print usage
usage() {
    echo "Usage: $0 <queries_file> [--output <output_file>]"
    echo ""
    echo "Arguments:"
    echo "  queries-file    Text file with one query per line"
    echo "  --output        Output file (default: stdout)"
    echo ""
    echo "Example:"
    echo "  $0 queries.txt --output results.txt"
    exit 1
}

# Check if zotcli is available
check_zotcli() {
    if ! command -v zotcli &> /dev/null; then
        echo -e "${RED}Error: zotcli not found${NC}"
        echo "Please install zotero-cli first:"
        echo "  pipx install zotero-cli  # or:"
        echo "  pip install --user zotero-cli"
        exit 1
    fi
}

# Check if queries file exists and is readable
check_queries_file() {
    local file="$1"

    if [[ ! -f "$file" ]]; then
        echo -e "${RED}Error: Queries file '$file' not found${NC}"
        exit 1
    fi

    if [[ ! -r "$file" ]]; then
        echo -e "${RED}Error: Cannot read queries file '$file'${NC}"
        exit 1
    fi
}

# Process queries
process_queries() {
    local queries_file="$1"
    local output_file="$2"
    local line_num=0
    local total_lines=$(wc -l < "$queries_file")

    echo -e "${GREEN}Processing $total_lines queries...${NC}"
    echo ""

    while IFS= read -r query || [[ -n "$query" ]]; do
        # Skip empty lines and comments
        if [[ -z "$query" ]] || [[ "$query" =~ ^[[:space:]]*# ]]; then
            continue
        fi

        ((line_num++))
        echo -e "${YELLOW}[$line_num/$total_lines] Query: $query${NC}"

        if [[ -n "$output_file" ]]; then
            echo "=== Query: $query ===" >> "$output_file"
            zotcli query "$query" >> "$output_file" 2>&1 || true
            echo "" >> "$output_file"
        else
            zotcli query "$query" || true
            echo ""
        fi
    done < "$queries_file"

    echo ""
    echo -e "${GREEN}Done! Processed $line_num queries.${NC}"
}

# Main: Parse arguments
if [[ $# -eq 0 ]]; then
    usage
fi

QUERIES_FILE="$1"
shift

# Parse optional arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --output|-o)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        --help|-h)
            usage
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            usage
            ;;
    esac
done

# Execute
check_zotcli
check_queries_file "$QUERIES_FILE"
process_queries "$QUERIES_FILE" "$OUTPUT_FILE"
