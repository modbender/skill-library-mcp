#!/bin/bash
# WhatsApp -> OpenClaw relay (safe mode)
# Enqueue fast, process with single detached worker.
# Args: name, message, chat_jid, message_id(optional)

set -u

NAME="${1:-Unknown}"
MSG="${2:-}"
JID="${3:-}"
MESSAGE_ID="${4:-}"
SYSTEM_PROMPT="${OC_WA_SYSTEM_PROMPT:-You are a helpful WhatsApp assistant. Be concise and natural.}"

[ -z "$JID" ] && exit 0
[ -z "$MSG" ] && exit 0

DATA_DIR="${OC_WA_AGENT_DATA_DIR:-/tmp/openclaw-wa-agent}"
QUEUE="$DATA_DIR/queue.jsonl"
SEEN_IDS="$DATA_DIR/seen_message_ids.txt"
mkdir -p "$DATA_DIR"
touch "$QUEUE" "$SEEN_IDS"

# Dedupe by message id (if provided)
if [ -n "$MESSAGE_ID" ]; then
  if grep -Fqx "$MESSAGE_ID" "$SEEN_IDS" 2>/dev/null; then
    exit 0
  fi
  echo "$MESSAGE_ID" >> "$SEEN_IDS"
  tail -n 5000 "$SEEN_IDS" > "$SEEN_IDS.tmp" && mv "$SEEN_IDS.tmp" "$SEEN_IDS"
fi

# Append one JSON event to queue.
python3 - "$NAME" "$MSG" "$JID" "$MESSAGE_ID" "$SYSTEM_PROMPT" >> "$QUEUE" <<'PY'
import json,sys,time
name,msg,jid,message_id,system_prompt = sys.argv[1:]
print(json.dumps({
  "ts": int(time.time()),
  "name": name,
  "message": msg,
  "jid": jid,
  "message_id": message_id,
  "system_prompt": system_prompt,
}, ensure_ascii=False))
PY

# Detach worker. It self-locks, so parallel launches are safe.
# Worker path: configurable via OC_WA_WORKER_PATH, or same directory as this script
WORKER_PATH="${OC_WA_WORKER_PATH:-$(dirname "$(realpath "$0")")/wa-notify-worker.sh}"
[ ! -x "$WORKER_PATH" ] && WORKER_PATH="/usr/local/bin/wa-notify-worker.sh"
nohup "$WORKER_PATH" >/dev/null 2>&1 &

exit 0
