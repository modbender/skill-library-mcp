#!/usr/bin/env bash
set -euo pipefail

TOPIC="CaptainDragonflyBot-TopicTest001"
MESSAGE=""
TITLE=""
PRIORITY=""
TAGS=""
CLICK=""
ACTIONS=""
ATTACH=""
FILENAME=""

usage() {
  cat <<'EOF'
Usage:
  send_ntfy.sh [--topic TOPIC] [--message TEXT] [--title TEXT] [--priority 1-5]
               [--tags a,b,c] [--click URL] [--actions ACTIONS]
               [--attach URL] [--filename NAME]

Notes:
  --actions format follows ntfy header syntax, example:
    "view, Open docs, https://docs.openclaw.ai; http, Trigger, https://example.com/hook"
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --topic) TOPIC="$2"; shift 2 ;;
    --message) MESSAGE="$2"; shift 2 ;;
    --title) TITLE="$2"; shift 2 ;;
    --priority) PRIORITY="$2"; shift 2 ;;
    --tags) TAGS="$2"; shift 2 ;;
    --click) CLICK="$2"; shift 2 ;;
    --actions) ACTIONS="$2"; shift 2 ;;
    --attach) ATTACH="$2"; shift 2 ;;
    --filename) FILENAME="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ -z "$MESSAGE" ]]; then
  NOW_UTC="$(date -u +"%Y-%m-%d %H:%M:%S UTC")"
  MESSAGE="这是一条默认消息，现在是${NOW_UTC}，来自沉舟老爷的小跟班"
fi

CMD=(curl -fsS -d "$MESSAGE")

[[ -n "$TITLE" ]] && CMD+=(-H "Title: $TITLE")
[[ -n "$PRIORITY" ]] && CMD+=(-H "Priority: $PRIORITY")
[[ -n "$TAGS" ]] && CMD+=(-H "Tags: $TAGS")
[[ -n "$CLICK" ]] && CMD+=(-H "Click: $CLICK")
[[ -n "$ACTIONS" ]] && CMD+=(-H "Actions: $ACTIONS")
[[ -n "$ATTACH" ]] && CMD+=(-H "Attach: $ATTACH")
[[ -n "$FILENAME" ]] && CMD+=(-H "Filename: $FILENAME")

CMD+=("https://ntfy.sh/$TOPIC")

"${CMD[@]}"
echo
