#!/usr/bin/env bash
set -euo pipefail
BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=bin/persistent-code-terminal-lib.sh
source "$BASE_DIR/persistent-code-terminal-lib.sh"
JSON_MODE=0

while [ "$#" -gt 0 ]; do
  case "$1" in
    --json)
      JSON_MODE=1
      shift
      ;;
    -h|--help)
      echo "Usage: persistent-code-terminal-list.sh [--json]"
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      exit 1
      ;;
  esac
done

require_tmux
SESSIONS_RAW="$(tmux list-sessions -F '#{session_name}|#{?session_attached,1,0}' 2>/dev/null || true)"
FILTERED="$(printf '%s\n' "$SESSIONS_RAW" | awk -F'|' '$1 ~ /-code-session$/ {print $0}')"

if [ "$JSON_MODE" -eq 1 ]; then
  JSON_OUT="["
  FIRST=1
  while IFS='|' read -r session attached; do
    [ -z "$session" ] && continue
    project="${session%-code-session}"
    if [ "$FIRST" -eq 0 ]; then
      JSON_OUT+=", "
    fi
    if [ "$attached" = "1" ]; then
      attached_json="true"
    else
      attached_json="false"
    fi
    JSON_OUT+="{\"project\":\"$(pct_json_escape "$project")\",\"session\":\"$(pct_json_escape "$session")\",\"attached\":${attached_json}}"
    FIRST=0
  done <<EOF_SESS
$FILTERED
EOF_SESS
  JSON_OUT+="]"
  printf '%s\n' "$JSON_OUT"
  exit 0
fi

printf '%s\n' 'PROJECT_NAME | SESSION_NAME | STATUS'
while IFS='|' read -r session attached; do
  [ -z "$session" ] && continue
  project="${session%-code-session}"
  if [ "$attached" = "1" ]; then
    status="attached"
  else
    status="detached"
  fi
  printf '%s | %s | %s\n' "$project" "$session" "$status"
done <<EOF_SESS
$FILTERED
EOF_SESS
