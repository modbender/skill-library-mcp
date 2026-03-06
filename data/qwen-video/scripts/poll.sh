#!/usr/bin/env bash
set -euo pipefail

TASK_ID=""
MAX_WAIT_SEC=1200
INTERVAL_SEC=5

usage(){
  cat <<'EOF'
Usage:
  poll.sh --task-id <id> [--max-wait-sec 1200] [--interval-sec 5]

Env:
  DASHSCOPE_API_KEY (required)

Output:
  Prints status lines. On success prints:
    VIDEO_URL: <url>
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help) usage; exit 0;;
    --task-id) TASK_ID=${2:-}; shift 2;;
    --max-wait-sec) MAX_WAIT_SEC=${2:-1200}; shift 2;;
    --interval-sec) INTERVAL_SEC=${2:-5}; shift 2;;
    *) echo "Unknown arg: $1" >&2; usage; exit 2;;
  esac
done

if [[ -z "$TASK_ID" ]]; then
  echo "Error: --task-id is required" >&2
  exit 2
fi

if [[ -z "${DASHSCOPE_API_KEY:-}" ]]; then
  echo "Error: DASHSCOPE_API_KEY is not set" >&2
  exit 2
fi

START=$(date +%s)
while true; do
  RESP=$(curl -sS -k --location "https://dashscope.aliyuncs.com/api/v1/tasks/$TASK_ID" \
    -H "Authorization: Bearer $DASHSCOPE_API_KEY")

  STATUS=$(echo "$RESP" | sed -n 's/.*"task_status"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n 1)
  NOW=$(date +%s)
  ELAPSED=$((NOW-START))

  echo "[${ELAPSED}s] status=${STATUS:-UNKNOWN}"

  if [[ "$STATUS" == "SUCCEEDED" ]]; then
    VIDEO_URL=$(echo "$RESP" | sed -n 's/.*"video_url"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n 1)
    if [[ -n "$VIDEO_URL" ]]; then
      echo "VIDEO_URL: $VIDEO_URL"
      exit 0
    else
      echo "Error: SUCCEEDED but no video_url found" >&2
      echo "$RESP" >&2
      exit 1
    fi
  fi

  if [[ "$STATUS" == "FAILED" ]]; then
    echo "FAILED" >&2
    echo "$RESP" >&2
    exit 1
  fi

  if (( ELAPSED >= MAX_WAIT_SEC )); then
    echo "Timeout after ${MAX_WAIT_SEC}s" >&2
    echo "$RESP" >&2
    exit 1
  fi

  sleep "$INTERVAL_SEC"
done
