#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
EVOLUTION="node $SCRIPT_DIR/evolution.js"

AGENTS_PATH=""
SOUL_PATH=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --agents) AGENTS_PATH="$2"; shift 2 ;;
    --soul) SOUL_PATH="$2"; shift 2 ;;
    *) echo '{"error":"unknown arg: '"$1"'"}'; exit 1 ;;
  esac
done

# Initialize state if needed
$EVOLUTION init 2>/dev/null || true

added=0

extract_rules() {
  local file="$1"
  local source="$2"
  
  if [[ ! -f "$file" ]]; then
    echo '{"warning":"file not found: '"$file"'"}'
    return
  fi

  # Match patterns like "1. **xxx**" or "1. xxx" (numbered rules)
  grep -nE '^\s*[0-9]+\.\s+' "$file" | while IFS= read -r line; do
    # Extract the rule text, strip markdown bold markers and leading number
    text=$(echo "$line" | sed 's/^[^:]*:\s*//' | sed 's/^\s*[0-9]\+\.\s*//' | sed 's/\*\*//g' | sed 's/\s*$//')
    
    # Skip empty or very short
    [[ ${#text} -lt 4 ]] && continue
    
    # Generate kebab-case id from text
    rule_id=$(echo "$text" | tr '[:upper:]' '[:lower:]' | \
      sed 's/[[:punct:]]//g' | \
      tr -s '[:space:]' '-' | \
      cut -c1-60 | \
      sed 's/^-//;s/-$//')
    
    # Skip if id is empty
    [[ -z "$rule_id" ]] && continue
    
    $EVOLUTION add-rule "$rule_id" "$text" "$source" 2>/dev/null || true
  done
}

if [[ -n "$AGENTS_PATH" ]]; then
  extract_rules "$AGENTS_PATH" "AGENTS.md"
fi

if [[ -n "$SOUL_PATH" ]]; then
  extract_rules "$SOUL_PATH" "SOUL.md"
fi

# Show final stats
$EVOLUTION stats
