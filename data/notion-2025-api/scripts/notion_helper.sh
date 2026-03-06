#!/bin/bash

# Notion 2025 API Helper Script
# Usage: ./notion_helper.sh <command> [options]
#
# SECURITY NOTE: This script constructs JSON via string concatenation.
# Only use with trusted input (your own data and IDs from Notion).
# Do NOT pass unsanitized user input directly to this script.
# Use jq for proper JSON escaping if needed.

set -e
set -u  # Fail on undefined variables

# Verify dependencies
for cmd in curl jq; do
  if ! command -v "$cmd" &> /dev/null; then
    echo "Error: Required command '$cmd' not found. Please install it." >&2
    exit 127
  fi
done

# Check API key exists
if [ ! -f ~/.openclaw/workspace/secrets/notion_api_key.txt ]; then
  echo "Error: Notion API key not found at ~/.openclaw/workspace/secrets/notion_api_key.txt" >&2
  exit 1
fi

NOTION_KEY=$(cat ~/.openclaw/workspace/secrets/notion_api_key.txt)

# Validate API key format
if [[ ! "$NOTION_KEY" =~ ^ntn_ ]]; then
  echo "Error: Invalid API key format (should start with 'ntn_')" >&2
  exit 1
fi
API_VERSION="2025-09-03"
BASE_URL="https://api.notion.com/v1"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
log_success() {
  echo -e "${GREEN}✓ $1${NC}"
}

log_error() {
  echo -e "${RED}✗ $1${NC}" >&2
}

log_warn() {
  echo -e "${YELLOW}⚠ $1${NC}" >&2
}

# Validate input is a UUID-like Notion ID
validate_notion_id() {
  local id=$1
  local id_type=$2
  
  # Notion IDs are 32-character hex strings (with or without hyphens)
  if [[ ! "$id" =~ ^[a-f0-9\-]{32,36}$ ]]; then
    log_error "Invalid $id_type format: '$id' (expected Notion ID)"
    return 1
  fi
  return 0
}

# Validate command exists
validate_command() {
  local cmd=$1
  case "$cmd" in
    query|create|update|get) return 0 ;;
    *) return 1 ;;
  esac
}

# Command: query_database
query_database() {
  local data_source_id=$1
  local filter=${2:-'{}'}  # Optional filter
  
  if [ -z "$data_source_id" ]; then
    log_error "Usage: notion_helper.sh query <data_source_id> [filter_json]"
    exit 1
  fi
  
  if ! validate_notion_id "$data_source_id" "data_source_id"; then
    exit 1
  fi
  
  # Security: Basic validation of filter JSON
  if [ "$filter" != "{}" ] && ! echo "$filter" | jq empty 2>/dev/null; then
    log_error "Invalid JSON in filter: $filter"
    exit 1
  fi
  
  curl -s -X POST "$BASE_URL/data_sources/$data_source_id/query" \
    -H "Authorization: Bearer $NOTION_KEY" \
    -H "Notion-Version: $API_VERSION" \
    -H "Content-Type: application/json" \
    -d "{$filter}"
}

# Command: create_entry
create_entry() {
  local database_id=$1
  local title=$2
  
  if [ -z "$database_id" ] || [ -z "$title" ]; then
    log_error "Usage: notion_helper.sh create <database_id> <title>"
    exit 1
  fi
  
  if ! validate_notion_id "$database_id" "database_id"; then
    exit 1
  fi
  
  # Security: Properly escape title using jq
  local escaped_title=$(echo "$title" | jq -Rs '.')
  
  local response=$(curl -s -X POST "$BASE_URL/pages" \
    -H "Authorization: Bearer $NOTION_KEY" \
    -H "Notion-Version: $API_VERSION" \
    -H "Content-Type: application/json" \
    -d '{
      "parent": {"database_id": "'$database_id'"},
      "properties": {
        "Name": {"title": [{"text": {"content": '"$escaped_title"'}}]}
      }
    }')
  
  local entry_id=$(echo "$response" | jq -r '.id // empty')
  if [ -z "$entry_id" ]; then
    log_error "Failed to create entry: $(echo "$response" | jq -r '.message // "Unknown error"')"
    exit 1
  fi
  
  log_success "Created entry: $entry_id"
  echo "$entry_id"
}

# Command: update_property
update_property() {
  local page_id=$1
  local property=$2
  local value=$3
  
  if [ -z "$page_id" ] || [ -z "$property" ] || [ -z "$value" ]; then
    log_error "Usage: notion_helper.sh update <page_id> <property> <value>"
    exit 1
  fi
  
  if ! validate_notion_id "$page_id" "page_id"; then
    exit 1
  fi
  
  # Security: Validate value is valid JSON
  if ! echo "$value" | jq empty 2>/dev/null; then
    log_error "Invalid JSON in value: $value"
    exit 1
  fi
  
  local response=$(curl -s -X PATCH "$BASE_URL/pages/$page_id" \
    -H "Authorization: Bearer $NOTION_KEY" \
    -H "Notion-Version: $API_VERSION" \
    -H "Content-Type: application/json" \
    -d '{"properties": {'$property': '$value'}}')
  
  # Check for errors
  if echo "$response" | jq -e '.object == "error"' &>/dev/null; then
    log_error "Update failed: $(echo "$response" | jq -r '.message')"
    exit 1
  fi
  
  log_success "Updated $property on $page_id"
}

# Command: get_entry
get_entry() {
  local page_id=$1
  
  if [ -z "$page_id" ]; then
    log_error "Usage: notion_helper.sh get <page_id>"
    exit 1
  fi
  
  if ! validate_notion_id "$page_id" "page_id"; then
    exit 1
  fi
  
  curl -s -X GET "$BASE_URL/pages/$page_id" \
    -H "Authorization: Bearer $NOTION_KEY" \
    -H "Notion-Version: $API_VERSION"
}

# Main dispatcher
main() {
  local command=${1:-}
  
  if [ -z "$command" ]; then
    echo "Usage: notion_helper.sh <command> [options]"
    echo ""
    echo "Commands:"
    echo "  query <data_source_id> [filter]  - Query database entries"
    echo "  create <database_id> <title>     - Create new database entry"
    echo "  update <page_id> <prop> <val>    - Update page property"
    echo "  get <page_id>                    - Get page details"
    echo ""
    echo "SECURITY:"
    echo "  Only use with trusted input (your own data and Notion IDs)"
    echo "  Properly escape untrusted input using jq before passing to this script"
    exit 1
  fi
  
  if ! validate_command "$command"; then
    log_error "Unknown command: $command"
    exit 1
  fi
  
  case "$command" in
    query)
      shift
      query_database "$@"
      ;;
    create)
      shift
      create_entry "$@"
      ;;
    update)
      shift
      update_property "$@"
      ;;
    get)
      shift
      get_entry "$@"
      ;;
  esac
}

main "$@"
