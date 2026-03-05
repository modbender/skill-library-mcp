#!/usr/bin/env bash
set -euo pipefail

PROMPT=""
SIZE="1280*720"
DURATION=4
MODEL="wan2.6-t2v"
SHOT_TYPE="single"
OUT="./wan_video.mp4"
MAX_WAIT_SEC=1200
INTERVAL_SEC=5
PROMPT_EXTEND=true
AUDIO_URL=""

usage(){
  cat <<'EOF'
Usage:
  generate.sh --prompt "TEXT" [--size 1280*720] [--duration 4]
              [--out /path/to/out.mp4] [--max-wait-sec 1200] [--interval-sec 5]
              [--model wan2.6-t2v] [--shot-type single|multi] [--no-prompt-extend]
              [--audio-url URL]

Env:
  DASHSCOPE_API_KEY (required)

Output:
  TASK_ID: ...
  VIDEO_URL: ...
  MEDIA: /abs/path/to/out.mp4
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help) usage; exit 0;;
    --prompt) PROMPT=${2:-}; shift 2;;
    --size) SIZE=${2:-}; shift 2;;
    --duration) DURATION=${2:-4}; shift 2;;
    --out) OUT=${2:-}; shift 2;;
    --max-wait-sec) MAX_WAIT_SEC=${2:-1200}; shift 2;;
    --interval-sec) INTERVAL_SEC=${2:-5}; shift 2;;
    --model) MODEL=${2:-}; shift 2;;
    --shot-type) SHOT_TYPE=${2:-single}; shift 2;;
    --no-prompt-extend) PROMPT_EXTEND=false; shift 1;;
    --audio-url) AUDIO_URL=${2:-}; shift 2;;
    *) echo "Unknown arg: $1" >&2; usage; exit 2;;
  esac
done

if [[ -z "$PROMPT" ]]; then
  echo "Error: --prompt is required" >&2
  exit 2
fi

BASE_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

# Submit
SUBMIT_OUT=$(bash "$BASE_DIR/scripts/submit.sh" \
  --prompt "$PROMPT" \
  --size "$SIZE" \
  --duration "$DURATION" \
  --model "$MODEL" \
  --shot-type "$SHOT_TYPE" \
  $( [[ "$PROMPT_EXTEND" == "false" ]] && echo "--no-prompt-extend" ) \
  $( [[ -n "$AUDIO_URL" ]] && printf -- "--audio-url %q" "$AUDIO_URL" )
)

echo "$SUBMIT_OUT"
TASK_ID=$(echo "$SUBMIT_OUT" | sed -n 's/^TASK_ID: //p' | tail -n 1)

# Poll
VIDEO_URL=$(bash "$BASE_DIR/scripts/poll.sh" --task-id "$TASK_ID" --max-wait-sec "$MAX_WAIT_SEC" --interval-sec "$INTERVAL_SEC" | sed -n 's/^VIDEO_URL: //p' | tail -n 1)

echo "VIDEO_URL: $VIDEO_URL"

# Download
mkdir -p "$(dirname "$OUT")"
curl -L -k -o "$OUT" "$VIDEO_URL"

FULL=$(python3 -c 'import os,sys; print(os.path.abspath(sys.argv[1]))' "$OUT")
echo "MEDIA: $FULL"
