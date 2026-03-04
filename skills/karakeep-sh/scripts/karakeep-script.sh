#!/usr/bin/env bash
# Karakeep API Helper Scripts
# Usage: source this file or add to PATH

# Set API base URL
KARAKEEP_API_URL="${KARAKEEP_SERVER_URL}/api/v1"

# Check configuration
check_config() {
  if [ -z "$KARAKEEP_SERVER_URL" ]; then
    echo "Error: KARAKEEP_SERVER_URL environment variable not set"
    echo "Set your API address and run:"
    echo "  export KARAKEEP_SERVER_URL=https://your-instance.com"
    return 1
  fi

  if [ -z "$KARAKEEP_API_KEY" ]; then
    echo "Error: KARAKEEP_API_KEY environment variable not set"
    echo "Get your API key from Karakeep settings and run:"
    echo "  export KARAKEEP_API_KEY=your_api_key_here"
    return 1
  fi

  return 0
}

# Create bookmark with note
# Usage: kb-create <type> <content> <title> <note>
kb-create() {
  check_config || return 1

  local type="$1"
  local content="$2"
  local title="$3"
  local note="$4"

  if [ -z "$type" ] || [ -z "$content" ]; then
    echo "Usage: kb-create <type> <content> <title> <note>"
    echo "Types: link, text"
    return 1
  fi

  # Build JSON using jq for proper escaping
  # For link type: use 'url' field
  # For text type: use 'text' field
  local field="url"
  if [ "$type" = "text" ]; then
    field="text"
  fi

  local json=$(echo '{}' | jq \
    --arg t "$type" \
    --arg c "$content" \
    --arg f "$field" \
    '{type: $t} | . + {($f): $c}')

  if [ -n "$title" ]; then
    json=$(echo "$json" | jq --arg t "$title" '. + {title: $t}')
  fi

  if [ -n "$note" ]; then
    json=$(echo "$json" | jq --arg n "$note" '. + {note: $n}')
  fi

  curl -s -X POST "$KARAKEEP_API_URL/bookmarks" \
       -H "Authorization: Bearer $KARAKEEP_API_KEY" \
       -H "Content-Type: application/json" \
       -d "$json" | jq '.'
}

# Update bookmark note
# Usage: kb-update-note <bookmark_id> <note>
kb-update-note() {
  check_config || return 1

  local bookmark_id="$1"
  local note="$2"

  if [ -z "$bookmark_id" ]; then
    echo "Usage: kb-update-note <bookmark_id> <note>"
    return 1
  fi

  # Use jq to properly escape the note content (handles newlines, quotes, etc.)
  local json=$(echo '{}' | jq --arg n "$note" '{note: $n}')

  curl -s -X PATCH "$KARAKEEP_API_URL/bookmarks/$bookmark_id" \
       -H "Authorization: Bearer $KARAKEEP_API_KEY" \
       -H "Content-Type: application/json" \
       -d "$json" | jq '.'
}

# Delete bookmark
# Usage: kb-delete <bookmark_id>
kb-delete() {
  check_config || return 1

  local bookmark_id="$1"

  if [ -z "$bookmark_id" ]; then
    echo "Usage: kb-delete <bookmark_id>"
    return 1
  fi

  curl -s -X DELETE "$KARAKEEP_API_URL/bookmarks/$bookmark_id" \
       -H "Authorization: Bearer $KARAKEEP_API_KEY"
  echo "Deleted bookmark: $bookmark_id"
}

# Get bookmark details
# Usage: kb-get <bookmark_id>
kb-get() {
  check_config || return 1

  local bookmark_id="$1"

  if [ -z "$bookmark_id" ]; then
    echo "Usage: kb-get <bookmark_id>"
    return 1
  fi

  curl -s -X GET "$KARAKEEP_API_URL/bookmarks/$bookmark_id" \
       -H "Authorization: Bearer $KARAKEEP_API_KEY" | jq '.'
}

# List all bookmarks (basic)
# Usage: kb-list [limit]
kb-list() {
  check_config || return 1

  local limit="${1:-20}"

  # Note: This might need adjustment based on actual API endpoint
  curl -s -X GET "$KARAKEEP_API_URL/bookmarks?limit=$limit" \
       -H "Authorization: Bearer $KARAKEEP_API_KEY" | jq '.'
}

# Search bookmarks with powerful qualifiers
# Usage: kb-search <query> [limit] [sortOrder]
# Examples:
#   kb-search "is:fav after:2023-01-01 #important"
#   kb-search "machine learning is:tagged"
#   kb-search "python" 20 "relevance"
kb-search() {
  check_config || return 1

  local query="$1"
  local limit="${2:-20}"
  local sort_order="${3:-relevance}"

  if [ -z "$query" ]; then
    echo "Usage: kb-search <query> [limit] [sortOrder]"
    echo ""
    echo "Qualifiers:"
    echo "  is:fav, is:archived, is:tagged, is:inlist, is:link, is:text, is:media"
    echo "  url:<value>, #<tag>, list:<name>"
    echo "  after:<YYYY-MM-DD>, before:<YYYY-MM-DD>"
    echo ""
    echo "Sort options: relevance (default), asc, desc"
    echo ""
    echo "Examples:"
    echo "  kb-search \"is:fav after:2023-01-01 #important\""
    echo "  kb-search \"machine learning is:tagged\" 50"
    echo "  kb-search \"python\" 100 desc"
    return 1
  fi

  # Remove newlines and encode for URL
  local encoded_query=$(echo "$query" | tr -d '\n' | jq -sRr @uri)
  local url="$KARAKEEP_API_URL/bookmarks/search?q=${encoded_query}&limit=${limit}&sortOrder=${sort_order}"

  curl -s -X GET "$url" \
       -H "Authorization: Bearer $KARAKEEP_API_KEY"
}

# Get bookmark content as markdown
# Usage: kb-content <bookmark_id>
kb-content() {
  check_config || return 1

  local bookmark_id="$1"

  if [ -z "$bookmark_id" ]; then
    echo "Usage: kb-content <bookmark_id>"
    return 1
  fi

  curl -s -X GET "$KARAKEEP_API_URL/bookmarks/$bookmark_id?includeContent=true" \
       -H "Authorization: Bearer $KARAKEEP_API_KEY" | jq -r '.content.htmlContent'
}

# List all lists
# Usage: kb-lists
kb-lists() {
  check_config || return 1

  curl -s -X GET "$KARAKEEP_API_URL/lists" \
       -H "Authorization: Bearer $KARAKEEP_API_KEY" | jq '.'
}

# Create a new list
# Usage: kb-create-list <name> [icon]
kb-create-list() {
  check_config || return 1

  local name="$1"
  local icon="${2:-📁}"

  if [ -z "$name" ]; then
    echo "Usage: kb-create-list <name> [icon]"
    return 1
  fi

  curl -s -X POST "$KARAKEEP_API_URL/lists" \
       -H "Authorization: Bearer $KARAKEEP_API_KEY" \
       -H "Content-Type: application/json" \
       -d "{\"name\":\"$name\",\"icon\":\"$icon\"}" | jq '.'
}

# Add bookmark to list
# Usage: kb-add-to-list <bookmark_id> <list_id>
kb-add-to-list() {
  check_config || return 1

  local bookmark_id="$1"
  local list_id="$2"

  if [ -z "$bookmark_id" ] || [ -z "$list_id" ]; then
    echo "Usage: kb-add-to-list <bookmark_id> <list_id>"
    return 1
  fi

  curl -s -X PUT "$KARAKEEP_API_URL/lists/$list_id/bookmarks/$bookmark_id" \
       -H "Authorization: Bearer $KARAKEEP_API_KEY"
}

# Remove bookmark from list
# Usage: kb-remove-from-list <bookmark_id> <list_id>
kb-remove-from-list() {
  check_config || return 1

  local bookmark_id="$1"
  local list_id="$2"

  if [ -z "$bookmark_id" ] || [ -z "$list_id" ]; then
    echo "Usage: kb-remove-from-list <bookmark_id> <list_id>"
    return 1
  fi

  curl -s -X DELETE "$KARAKEEP_API_URL/lists/$list_id/bookmarks/$bookmark_id" \
       -H "Authorization: Bearer $KARAKEEP_API_KEY"
}

# Attach tags to bookmark
# Usage: kb-attach-tags <bookmark_id> <tag1> [tag2] ...
kb-attach-tags() {
  check_config || return 1

  local bookmark_id="$1"
  shift

  if [ -z "$bookmark_id" ] || [ $# -eq 0 ]; then
    echo "Usage: kb-attach-tags <bookmark_id> <tag1> [tag2] ..."
    return 1
  fi

  local tags=$(printf '%s\n' "$@" | jq -R . | jq -s 'map({tagName: .})')

  curl -s -X POST "$KARAKEEP_API_URL/bookmarks/$bookmark_id/tags" \
       -H "Authorization: Bearer $KARAKEEP_API_KEY" \
       -H "Content-Type: application/json" \
       -d "{\"tags\":$tags}"
}

# Detach tags from bookmark
# Usage: kb-detach-tags <bookmark_id> <tag1> [tag2] ...
kb-detach-tags() {
  check_config || return 1

  local bookmark_id="$1"
  shift

  if [ -z "$bookmark_id" ] || [ $# -eq 0 ]; then
    echo "Usage: kb-detach-tags <bookmark_id> <tag1> [tag2] ..."
    return 1
  fi

  local tags=$(printf '%s\n' "$@" | jq -R . | jq -s 'map({tagName: .})')

  curl -s -X DELETE "$KARAKEEP_API_URL/bookmarks/$bookmark_id/tags" \
       -H "Authorization: Bearer $KARAKEEP_API_KEY" \
       -H "Content-Type: application/json" \
       -d "{\"tags\":$tags}"
}
