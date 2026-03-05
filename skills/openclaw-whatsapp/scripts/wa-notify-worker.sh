#!/bin/bash
# Queue worker for WhatsApp -> OpenClaw auto-replies.
set -u

# Ensure PATH includes node/openclaw binaries
# Override with OC_WA_OPENCLAW_PATH if openclaw is in a non-standard location
if [ -n "${OC_WA_OPENCLAW_PATH:-}" ]; then
  export PATH="$OC_WA_OPENCLAW_PATH:$PATH"
elif [ -d "$HOME/.nvm/versions/node" ]; then
  # Auto-detect nvm node path
  NODE_BIN=$(ls -d "$HOME"/.nvm/versions/node/*/bin 2>/dev/null | tail -1)
  [ -n "$NODE_BIN" ] && export PATH="$NODE_BIN:$PATH"
fi

# Verify openclaw is available
if ! command -v openclaw &>/dev/null; then
  echo "[$(date -Iseconds)] ERROR: openclaw not found in PATH. Set OC_WA_OPENCLAW_PATH." >> "${OC_WA_AGENT_DATA_DIR:-/tmp/openclaw-wa-agent}/worker.log"
  exit 1
fi

DATA_DIR="${OC_WA_AGENT_DATA_DIR:-/tmp/openclaw-wa-agent}"
QUEUE="$DATA_DIR/queue.jsonl"
LOCK="$DATA_DIR/worker.lock"
LOG_FILE="$DATA_DIR/worker.log"
mkdir -p "$DATA_DIR"
touch "$QUEUE" "$LOCK" "$LOG_FILE"

process_one() {
  local line="$1"

  local name msg jid message_id system_prompt
  name=$(python3 -c 'import json,sys; print(json.loads(sys.argv[1]).get("name","Unknown"))' "$line" 2>/dev/null)
  msg=$(python3 -c 'import json,sys; print(json.loads(sys.argv[1]).get("message",""))' "$line" 2>/dev/null)
  jid=$(python3 -c 'import json,sys; print(json.loads(sys.argv[1]).get("jid",""))' "$line" 2>/dev/null)
  message_id=$(python3 -c 'import json,sys; print(json.loads(sys.argv[1]).get("message_id",""))' "$line" 2>/dev/null)
  system_prompt=$(python3 -c 'import json,sys; print(json.loads(sys.argv[1]).get("system_prompt",""))' "$line" 2>/dev/null)

  [ -z "$jid" ] && return 0

  local history
  history=$(curl -s "http://localhost:8555/chats/${jid}/messages?limit=10" | python3 - <<'PY'
import json,sys
try:
    data=json.loads(sys.stdin.read())
except Exception:
    print("")
    raise SystemExit
lines=[]
for m in reversed(data if isinstance(data,list) else []):
    sender="You" if not m.get("from") else "Customer"
    content=(m.get("content") or "").strip().replace("\n"," ")
    if content:
        lines.append(f"{sender}: {content}")
print("\n".join(lines[-10:]))
PY
  )

  local sid
  sid="wa-auto-$(printf '%s' "$jid" | sha1sum | awk '{print $1}' | cut -c1-12)"

  local prompt
  prompt=$(cat <<EOF
$system_prompt

You are replying to a WhatsApp contact.
Contact name: $name
Contact JID: $jid
Message ID: $message_id

Recent conversation (latest 10):
$history

Latest incoming message:
"$msg"

Task:
1) Write a concise, natural reply.
2) Send it by executing exactly:
   openclaw-whatsapp send "$jid" "<your reply>"
3) After sending, stop.
Do not call cron.add. Do not spawn background loops.
EOF
)

  # Hard timeout avoids stuck workers.
  timeout 45s openclaw agent \
    --agent main \
    --session-id "$sid" \
    --message "$prompt" \
    --timeout 35 \
    --json \
    >>"$LOG_FILE" 2>&1 || echo "[$(date -Iseconds)] Agent failed for $jid" >> "$LOG_FILE"
}

# Single worker globally.
exec 9>"$LOCK"
flock -n 9 || exit 0

while true; do
  line=$(head -n 1 "$QUEUE")
  [ -z "$line" ] && break

  tail -n +2 "$QUEUE" > "$QUEUE.tmp" && mv "$QUEUE.tmp" "$QUEUE"
  process_one "$line"
done

exit 0
