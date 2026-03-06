#!/usr/bin/env bash
# list-sessions.sh — Scan Codex rollout files and output a session index.
#
# Usage:
#   ./list-sessions.sh <project-name> [--since <days>d]
#
# Codex stores sessions as rollout JSONL files in date-partitioned directories:
#   ~/.codex/sessions/YYYY/MM/DD/rollout-{timestamp}-{threadId}.jsonl
# The session_meta (first line) contains a "cwd" field used for project matching.
#
# Output: JSON array to stdout with session metadata for matching projects.
# Requires: jq, python3

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

CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
SESSIONS_ROOT="$CODEX_HOME/sessions"

if [[ ! -d "$SESSIONS_ROOT" ]]; then
  echo "[]"
  exit 0
fi

CUTOFF=0
if [[ -n "$SINCE_DAYS" ]]; then
  CUTOFF=$(date -v-"${SINCE_DAYS}"d +%s 2>/dev/null || date -d "${SINCE_DAYS} days ago" +%s 2>/dev/null || echo 0)
fi

PROJECT_LOWER=$(echo "$PROJECT" | tr '[:upper:]' '[:lower:]')

RESULTS="[]"

# Walk the date-partitioned directory tree for rollout files
while IFS= read -r rollout; do
  [[ -f "$rollout" ]] || continue

  # Modification time
  if [[ "$(uname)" == "Darwin" ]]; then
    mod_epoch=$(stat -f %m "$rollout")
    mod_iso=$(date -r "$mod_epoch" -u +"%Y-%m-%dT%H:%M:%SZ")
  else
    mod_epoch=$(stat -c %Y "$rollout")
    mod_iso=$(date -d "@$mod_epoch" -u +"%Y-%m-%dT%H:%M:%SZ")
  fi

  # Time filter
  if [[ "$CUTOFF" -gt 0 && "$mod_epoch" -lt "$CUTOFF" ]]; then
    continue
  fi

  # Read first line to get session_meta
  first_line=$(head -1 "$rollout" 2>/dev/null || echo "")
  if [[ -z "$first_line" ]]; then
    continue
  fi

  # Check if it's a session_meta line and extract cwd
  meta_type=$(echo "$first_line" | jq -r '.type // empty' 2>/dev/null)
  if [[ "$meta_type" != "session_meta" ]]; then
    continue
  fi

  cwd=$(echo "$first_line" | jq -r '.payload.cwd // empty' 2>/dev/null)
  if [[ -z "$cwd" ]]; then
    continue
  fi

  # Fuzzy match project name against cwd
  cwd_lower=$(echo "$cwd" | tr '[:upper:]' '[:lower:]')
  if [[ "$cwd_lower" != *"$PROJECT_LOWER"* ]]; then
    continue
  fi

  lines=$(wc -l < "$rollout" | tr -d ' ')

  # Extract first and last user messages
  msgs=$(python3 -c "
import json, sys

filepath = sys.argv[1]
first_msg = ''
last_msg = ''

with open(filepath, 'r') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except Exception:
            continue
        etype = entry.get('type', '')
        payload = entry.get('payload', {})
        if not isinstance(payload, dict):
            continue
        ptype = payload.get('type', '')

        # event_msg / user_message
        if etype == 'event_msg' and ptype == 'user_message':
            text = payload.get('message', '').strip()
            if text:
                if not first_msg:
                    first_msg = text[:200]
                last_msg = text[:200]

        # response_item / message with role=user (fallback)
        elif etype == 'response_item' and ptype == 'message' and payload.get('role') == 'user':
            content = payload.get('content', [])
            if isinstance(content, list):
                parts = [b.get('text', '') for b in content
                         if isinstance(b, dict) and b.get('type') in ('input_text', 'text')]
                text = ' '.join(parts).strip()
                if text:
                    if not first_msg:
                        first_msg = text[:200]
                    last_msg = text[:200]

print(first_msg)
print(last_msg)
" "$rollout" 2>/dev/null) || continue

  first_msg=$(echo "$msgs" | head -1)
  last_msg=$(echo "$msgs" | tail -1)

  RESULTS=$(echo "$RESULTS" | jq \
    --arg file "$rollout" \
    --arg cwd "$cwd" \
    --arg modified "$mod_iso" \
    --argjson lines "$lines" \
    --arg first "$first_msg" \
    --arg last "$last_msg" \
    '. + [{
      file: $file,
      platform: "codex",
      project_slug: $cwd,
      modified: $modified,
      lines: $lines,
      first_user_message: $first,
      last_user_message: $last
    }]')
done < <(find "$SESSIONS_ROOT" -name 'rollout-*.jsonl' -type f 2>/dev/null | sort -r)

echo "$RESULTS" | jq 'sort_by(.modified) | reverse'
