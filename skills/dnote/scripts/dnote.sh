#!/usr/bin/env bash
# dnote.sh - Enhanced Dnote CLI wrapper
# Provides convenient shortcuts and JSON export for AI integration

set -euo pipefail

DB_PATH="${DNOTE_DB_PATH:-}"
FORMAT="pretty"
JSON_OUTPUT=false

# Build dnote base command
DNODE_CMD="dnote"
if [[ -n "$DB_PATH" ]]; then
  DNODE_CMD="dnote --dbPath $DB_PATH"
fi

usage() {
  cat <<EOF
Dnote Enhanced CLI

Usage: dnote.sh [OPTIONS] COMMAND [ARGS]

Adding Notes:
  add <book> <content>      Add note to book
  add-stdin <book>          Add from stdin
  quick <content>           Quick add to 'inbox' book

Retrieving:
  view [book]               List books or notes
  get <book> <index>        Get specific note
  find <query>              Full-text search
  recent [n]                Recent notes (default: 10)
  config                    Show config and paths
  books                     List all books
  export [book]             Export as JSON/text

Managing:
  edit <id> [content]       Edit note by ID
  move <id> <book>          Move note to book
  remove <id>               Delete note
  remove-book <book>        Delete book

Sync:
  sync                      Sync with server
  status                    Show status

Options:
  --json                    Output JSON
  --dbPath PATH             Custom database path
  -h, --help                Show help

Examples:
  dnote.sh add cli "git log --oneline"
  echo "content" | dnote.sh add docker
  dnote.sh find "docker compose"
  dnote.sh recent 20
  dnote.sh export cli
EOF
  exit 0
}

die() { echo "Error: $1" >&2; exit 1; }

# Check dnote is installed
check_dnote() {
  if ! command -v dnote &> /dev/null; then
    die "dnote not found. Install: https://www.getdnote.com/docs/cli/installation/"
  fi
}

# Parse global options
parse_opts() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --json) JSON_OUTPUT=true; shift ;;
      --dbPath) DB_PATH="$2"; DNODE_CMD="dnote --dbPath $DB_PATH"; shift 2 ;;
      -h|--help) usage ;;
      *) break ;;
    esac
  done
}

# Add note to book
cmd_add() {
  local book="${1:-}"
  local content="${2:-}"
  [[ -z "$book" ]] && die "Book name required"
  [[ -z "$content" ]] && die "Content required"
  
  $DNODE_CMD add "$book" -c "$content"
}

# Add from stdin
cmd_add_stdin() {
  local book="${1:-}"
  [[ -z "$book" ]] && die "Book name required"
  
  local content
  content=$(cat)
  [[ -z "$content" ]] && die "No content from stdin"
  
  echo "$content" | $DNODE_CMD add "$book"
}

# Quick add to inbox
cmd_quick() {
  local content="$*"
  [[ -z "$content" ]] && die "Content required"
  
  $DNODE_CMD add inbox -c "$content"
}

# List books or view notes
cmd_view() {
  local book="${1:-}"
  
  if [[ -z "$book" ]]; then
    $DNODE_CMD view
  else
    $DNODE_CMD view "$book"
  fi
}

# Get specific note
cmd_get() {
  local book="${1:-}"
  local index="${2:-}"
  [[ -z "$book" ]] && die "Book name required"
  [[ -z "$index" ]] && die "Note index required"
  
  if [[ "$JSON_OUTPUT" == true ]]; then
    # Export and extract specific note
    $DNODE_CMD view "$book" "$index" --content-only 2>/dev/null || die "Note not found"
  else
    $DNODE_CMD view "$book" "$index"
  fi
}

# Find notes
cmd_find() {
  local query="${1:-}"
  local book=""
  
  # Parse options
  while [[ $# -gt 0 ]]; do
    case "$1" in
      -b|--book) book="$2"; shift 2 ;;
      --) shift; break ;;
      -*) shift ;;
      *) query="$1"; shift ;;
    esac
  done
  
  [[ -z "$query" ]] && die "Search query required"
  
  if [[ -n "$book" ]]; then
    $DNODE_CMD find "$query" -b "$book"
  else
    $DNODE_CMD find "$query"
  fi
}

# Recent notes across all books
cmd_recent() {
  local n="${1:-10}"
  
  # Get all notes sorted by time (most recent first)
  # This is a simplified version - dnote doesn't have a native "recent" command
  # We iterate through books and show recent entries
  local books
  books=$($DNODE_CMD view --name-only 2>/dev/null | head -50)
  
  echo "Recent notes (last $n):"
  echo "======================="
  
  local count=0
  while IFS= read -r book && [[ $count -lt $n ]]; do
    [[ -z "$book" ]] && continue
    local notes
    notes=$($DNODE_CMD view "$book" 2>/dev/null | head -5) || continue
    if [[ -n "$notes" ]]; then
      echo ""
      echo "[$book]"
      echo "$notes" | head -$((n - count))
      count=$((count + $(echo "$notes" | wc -l)))
    fi
  done <<< "$books"
}

# List books
cmd_books() {
  $DNODE_CMD view --name-only
}

# Export notes
cmd_export() {
  local book="${1:-}"
  
  if [[ "$JSON_OUTPUT" == true ]]; then
    if [[ -n "$book" ]]; then
      # Export specific book as JSON-like format
      echo "{"
      echo "  \"book\": \"$book\","
      echo "  \"notes\": ["
      $DNODE_CMD view "$book" | while IFS= read -r line; do
        [[ -n "$line" ]] && echo "    \"$(echo "$line" | sed 's/"/\\"/g')\","
      done | sed '$ s/,$//'
      echo "  ]"
      echo "}"
    else
      # Export all
      echo "{"
      echo "  \"books\": ["
      local first=true
      $DNODE_CMD view --name-only | while IFS= read -r b; do
        [[ -z "$b" ]] && continue
        [[ "$first" == true ]] || echo ","
        first=false
        echo "    {"
        echo "      \"name\": \"$b\","
        echo "      \"notes\": ["
        $DNODE_CMD view "$b" | while IFS= read -r line; do
          [[ -n "$line" ]] && echo "        \"$(echo "$line" | sed 's/"/\\"/g')\","
        done | sed '$ s/,$//'
        echo "      ]"
        echo -n "    }"
      done
      echo ""
      echo "  ]"
      echo "}"
    fi
  else
    if [[ -n "$book" ]]; then
      echo "=== $book ==="
      $DNODE_CMD view "$book"
    else
      $DNODE_CMD view
    fi
  fi
}

# Edit note
cmd_edit() {
  local id="${1:-}"
  local content="${2:-}"
  [[ -z "$id" ]] && die "Note ID required"
  
  if [[ -n "$content" ]]; then
    $DNODE_CMD edit "$id" -c "$content"
  else
    $DNODE_CMD edit "$id"
  fi
}

# Move note
cmd_move() {
  local id="${1:-}"
  local book="${2:-}"
  [[ -z "$id" ]] && die "Note ID required"
  [[ -z "$book" ]] && die "Target book required"
  
  $DNODE_CMD edit "$id" -b "$book"
}

# Remove note
cmd_remove() {
  local id="${1:-}"
  [[ -z "$id" ]] && die "Note ID required"
  
  $DNODE_CMD remove "$id" -y
}

# Remove book
cmd_remove_book() {
  local book="${1:-}"
  [[ -z "$book" ]] && die "Book name required"
  
  $DNODE_CMD remove "$book" -y
}

# Sync
cmd_sync() {
  $DNODE_CMD sync
}

# Config info
cmd_config() {
  echo "Dnote Configuration:"
  echo "===================="
  echo "Config file: ~/.config/dnote/dnoterc"
  echo "Database: ~/.local/share/dnote/dnote.db"
  echo ""
  echo "Environment variables:"
  echo "  XDG_CONFIG_HOME - Config directory"
  echo "  XDG_DATA_HOME   - Data directory"
  echo "  DNOTE_DB_PATH   - Override DB path"
  echo ""
  if [[ -f ~/.config/dnote/dnoterc ]]; then
    echo "Current config:"
    cat ~/.config/dnote/dnoterc
  else
    echo "No config file found. Create one at ~/.config/dnote/dnoterc"
  fi
}

# Status
cmd_status() {
  echo "Dnote Status:"
  echo "============="
  echo "Database: ${DB_PATH:-default (~/.local/share/dnote/dnote.db)}"
  echo "Version: $($DNODE_CMD version 2>/dev/null || echo 'unknown')"
  echo ""
  echo "Books:"
  $DNODE_CMD view --name-only | wc -l | xargs echo "  Count:"
  echo ""
  echo "Recent activity:"
  cmd_recent 5
}

# Main
check_dnote

# Parse options before command
parse_opts "$@"

# Get command and shift
cmd="${1:-}"; shift || true

case "$cmd" in
  add)
    cmd_add "$@"
    ;;
  add-stdin)
    cmd_add_stdin "$@"
    ;;
  quick)
    cmd_quick "$@"
    ;;
  view)
    cmd_view "$@"
    ;;
  get)
    cmd_get "$@"
    ;;
  find)
    cmd_find "$@"
    ;;
  recent)
    cmd_recent "$@"
    ;;
  books)
    cmd_books "$@"
    ;;
  export)
    cmd_export "$@"
    ;;
  edit)
    cmd_edit "$@"
    ;;
  move)
    cmd_move "$@"
    ;;
  remove)
    cmd_remove "$@"
    ;;
  remove-book)
    cmd_remove_book "$@"
    ;;
  sync)
    cmd_sync "$@"
    ;;
  status)
    cmd_status "$@"
    ;;
  config)
    cmd_config "$@"
    ;;
  help|--help|-h)
    usage
    ;;
  *)
    die "Unknown command: ${cmd:-(none)}. Run with --help for usage."
    ;;
esac
