#!/usr/bin/env bash
# list-sessions.sh — Scan OpenClaw session transcripts and output a session index.
#
# Usage:
#   ./list-sessions.sh <project-name> [--since <days>d]
#
# Output: JSON array to stdout with session metadata for matching projects.
# Requires: jq

set -euo pipefail

PROJECT="${1:-}"
SINCE_DAYS=""

shift || true
while [[ $# -gt 0 ]]; do
  case "$1" in
    --since) SINCE_DAYS="${2%d}"; shift 2 ;;
    *) echo "Unknown flag: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$PROJECT" ]]; then
  echo "Usage: list-sessions.sh <project-name> [--since Nd]" >&2
  exit 1
fi

if ! command -v jq &>/dev/null; then
  echo "Error: jq is required but not installed." >&2
  exit 1
fi

OC_ROOT="$HOME/.openclaw/agents"
if [[ ! -d "$OC_ROOT" ]]; then
  echo "[]"
  exit 0
fi

CUTOFF=0
if [[ -n "$SINCE_DAYS" ]]; then
  CUTOFF=$(date -v-"${SINCE_DAYS}"d +%s 2>/dev/null || date -d "${SINCE_DAYS} days ago" +%s 2>/dev/null || echo 0)
fi

RESULTS="[]"

extract_messages() {
  local file="$1"

  # First user message
  local first_msg
  first_msg=$(while IFS= read -r line; do
    type=$(echo "$line" | jq -r '.type // empty' 2>/dev/null)
    role=$(echo "$line" | jq -r '.message.role // empty' 2>/dev/null)
    if [[ "$type" == "message" && "$role" == "user" ]]; then
      text=$(echo "$line" | jq -r '
        .message.content |
        if type == "array" then
          [.[] | select(.type == "text") | .text] | join(" ")
        else ""
        end
      ' 2>/dev/null)
      if [[ -n "$text" && "$text" != "null" ]]; then
        echo "$text"
        break
      fi
    fi
  done < "$file")

  # Last user message
  local last_msg
  last_msg=$(tail -100 "$file" | tac | while IFS= read -r line; do
    type=$(echo "$line" | jq -r '.type // empty' 2>/dev/null)
    role=$(echo "$line" | jq -r '.message.role // empty' 2>/dev/null)
    if [[ "$type" == "message" && "$role" == "user" ]]; then
      text=$(echo "$line" | jq -r '
        .message.content |
        if type == "array" then
          [.[] | select(.type == "text") | .text] | join(" ")
        else ""
        end
      ' 2>/dev/null)
      if [[ -n "$text" && "$text" != "null" ]]; then
        echo "$text"
        break
      fi
    fi
  done)

  echo "${first_msg:0:200}"
  echo "${last_msg:0:200}"
}

PROJECT_LOWER=$(echo "$PROJECT" | tr '[:upper:]' '[:lower:]')

for agent_dir in "$OC_ROOT"/*/; do
  [[ -d "$agent_dir/sessions" ]] || continue

  agent_name=$(basename "$agent_dir")

  for jsonl in "$agent_dir"sessions/*.jsonl; do
    [[ -f "$jsonl" ]] || continue

    # Read session header (first line) for cwd
    cwd=$(head -1 "$jsonl" | jq -r '.cwd // empty' 2>/dev/null)
    cwd_lower=$(echo "$cwd" | tr '[:upper:]' '[:lower:]')

    if [[ -z "$cwd" || "$cwd_lower" != *"$PROJECT_LOWER"* ]]; then
      continue
    fi

    # Modification time
    if [[ "$(uname)" == "Darwin" ]]; then
      mod_epoch=$(stat -f %m "$jsonl")
      mod_iso=$(date -r "$mod_epoch" -u +"%Y-%m-%dT%H:%M:%SZ")
    else
      mod_epoch=$(stat -c %Y "$jsonl")
      mod_iso=$(date -d "@$mod_epoch" -u +"%Y-%m-%dT%H:%M:%SZ")
    fi

    # Time filter
    if [[ "$CUTOFF" -gt 0 && "$mod_epoch" -lt "$CUTOFF" ]]; then
      continue
    fi

    lines=$(wc -l < "$jsonl" | tr -d ' ')

    msgs=$(extract_messages "$jsonl")
    first_msg=$(echo "$msgs" | head -1)
    last_msg=$(echo "$msgs" | tail -1)

    RESULTS=$(echo "$RESULTS" | jq \
      --arg file "$jsonl" \
      --arg slug "$agent_name:$cwd" \
      --arg modified "$mod_iso" \
      --argjson lines "$lines" \
      --arg first "$first_msg" \
      --arg last "$last_msg" \
      '. + [{
        file: $file,
        platform: "openclaw",
        project_slug: $slug,
        modified: $modified,
        lines: $lines,
        first_user_message: $first,
        last_user_message: $last
      }]')
  done
done

echo "$RESULTS" | jq 'sort_by(.modified) | reverse'
