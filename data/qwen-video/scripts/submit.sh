#!/usr/bin/env bash
set -euo pipefail

API_URL="https://dashscope.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis"
MODEL="wan2.6-t2v"
PROMPT=""
SIZE="1280*720"
DURATION=4
SHOT_TYPE="single"
PROMPT_EXTEND=true
AUDIO_URL=""

usage(){
  cat <<'EOF'
Usage:
  submit.sh --prompt "TEXT" [--size 1280*720] [--duration 4] [--model wan2.6-t2v]
           [--shot-type single|multi] [--no-prompt-extend] [--audio-url URL]

Env:
  DASHSCOPE_API_KEY  (required)

Output:
  Prints JSON response and a parsed line: TASK_ID: <id>
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help) usage; exit 0;;
    --prompt) PROMPT=${2:-}; shift 2;;
    --size) SIZE=${2:-}; shift 2;;
    --duration) DURATION=${2:-4}; shift 2;;
    --model) MODEL=${2:-}; shift 2;;
    --shot-type) SHOT_TYPE=${2:-single}; shift 2;;
    --no-prompt-extend) PROMPT_EXTEND=false; shift 1;;
    --audio-url) AUDIO_URL=${2:-}; shift 2;;
    *) echo "Unknown arg: $1" >&2; usage; exit 2;;
  esac
done

if [[ -z "$PROMPT" ]]; then
  echo "Error: --prompt is required" >&2
  usage >&2
  exit 2
fi

if [[ -z "${DASHSCOPE_API_KEY:-}" ]]; then
  echo "Error: DASHSCOPE_API_KEY is not set" >&2
  exit 2
fi

# Build JSON (avoid jq dependency)
AUDIO_FIELD=""
if [[ -n "$AUDIO_URL" ]]; then
  AUDIO_FIELD=",\"audio_url\":\"$AUDIO_URL\""
fi

DATA="{\"model\":\"$MODEL\",\"input\":{\"prompt\":\"$PROMPT\"$AUDIO_FIELD},\"parameters\":{\"size\":\"$SIZE\",\"prompt_extend\":$PROMPT_EXTEND,\"duration\":$DURATION,\"shot_type\":\"$SHOT_TYPE\"}}"

RESP=$(curl -sS -k --location "$API_URL" \
  -H 'X-DashScope-Async: enable' \
  -H "Authorization: Bearer $DASHSCOPE_API_KEY" \
  -H 'Content-Type: application/json' \
  -d "$DATA")

echo "$RESP"
TASK_ID=$(echo "$RESP" | sed -n 's/.*"task_id"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n 1)
if [[ -n "$TASK_ID" ]]; then
  echo "TASK_ID: $TASK_ID"
else
  echo "Failed to parse task_id" >&2
  exit 1
fi
