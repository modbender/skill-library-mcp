#!/bin/bash
# HeySummon Consumer Watcher — persistent SSE listener via platform API
# Connects to /api/v1/events/stream for real-time event notifications
# Listens on all active request topics automatically (server-side)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
[ -f "$SKILL_DIR/.env" ] && set -a && source "$SKILL_DIR/.env" && set +a

BASE_URL="${HEYSUMMON_BASE_URL:-http://localhost:3445}"
API_KEY="${HEYSUMMON_API_KEY:?ERROR: Set HEYSUMMON_API_KEY}"
REQUESTS_DIR="${HEYSUMMON_REQUESTS_DIR:-$SKILL_DIR/.requests}"
OPENCLAW_PORT="${OPENCLAW_PORT:-18789}"
NOTIFY_MODE="${HEYSUMMON_NOTIFY_MODE:-message}"
NOTIFY_TARGET="${HEYSUMMON_NOTIFY_TARGET:-}"
STREAM_URL="${BASE_URL}/api/v1/events/stream"

if [ "$NOTIFY_MODE" = "message" ] && [ -z "$NOTIFY_TARGET" ]; then
  echo "ERROR: Set HEYSUMMON_NOTIFY_TARGET for message mode" >&2
  exit 1
fi

# Read OpenClaw gateway token
OPENCLAW_TOKEN=$(node -e "try{const p=require('path').join(require('os').homedir(),'.openclaw/openclaw.json');console.log(JSON.parse(require('fs').readFileSync(p,'utf8')).gateway.auth.token)}catch(e){}" 2>/dev/null)

if [ -z "$OPENCLAW_TOKEN" ]; then
  echo "ERROR: Could not read OpenClaw gateway token" >&2
  exit 1
fi

mkdir -p "$REQUESTS_DIR"

# Deduplication
SEEN_FILE="$SKILL_DIR/.seen-events.txt"
touch "$SEEN_FILE"
tail -500 "$SEEN_FILE" > "${SEEN_FILE}.tmp" 2>/dev/null && mv "${SEEN_FILE}.tmp" "$SEEN_FILE"

send_notification() {
  local MSG="$1"
  if [ "$NOTIFY_MODE" = "file" ]; then
    local EVENTS_FILE="${HEYSUMMON_EVENTS_FILE:-$HOME/.heysummon/consumer-events.jsonl}"
    mkdir -p "$(dirname "$EVENTS_FILE")"
    local TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    echo "{\"timestamp\":\"$TIMESTAMP\",\"message\":$(node -e "console.log(JSON.stringify(process.argv[1]))" "$MSG" 2>/dev/null)}" >> "$EVENTS_FILE"
    curl -s -X POST "http://127.0.0.1:${OPENCLAW_PORT}/cron/wake" \
      -H "Authorization: Bearer ${OPENCLAW_TOKEN}" \
      -H "Content-Type: application/json" \
      -d "{\"text\":\"$MSG\",\"mode\":\"now\",\"agentId\":\"secondary\"}" \
      >/dev/null 2>&1
  else
    local PAYLOAD
    PAYLOAD=$(node -e "console.log(JSON.stringify({
      tool:'message',
      args:{action:'send',message:process.argv[1],target:process.argv[2]}
    }))" "$MSG" "$NOTIFY_TARGET" 2>/dev/null)
    curl -s "http://127.0.0.1:${OPENCLAW_PORT}/tools/invoke" \
      -H "Authorization: Bearer ${OPENCLAW_TOKEN}" \
      -H "Content-Type: application/json" \
      -d "$PAYLOAD" \
      >/dev/null 2>&1
  fi
}

# Write PID for submit-request.sh signaling
mkdir -p "$REQUESTS_DIR"
echo $$ > "$REQUESTS_DIR/.watcher.pid"

# On SIGUSR1: kill active curl to force reconnect (picks up new topics server-side)
CURL_PID=""
reconnect() {
  [ -n "$CURL_PID" ] && kill "$CURL_PID" 2>/dev/null
  echo "🔄 SIGUSR1 — reconnecting"
}
trap reconnect USR1

echo "🦞 Platform watcher started (pid $$) — connecting to ${STREAM_URL}"

BACKOFF=5

while true; do
  echo "🔌 Connecting to SSE stream..."
  
  FIFO="/tmp/.heysummon-consumer-sse-$$"
  rm -f "$FIFO"
  mkfifo "$FIFO"
  
  timeout 300 curl -sN --no-buffer -H "x-api-key: ${API_KEY}" "${STREAM_URL}" > "$FIFO" 2>/dev/null &
  CURL_PID=$!
  
  LAST_EVENT_TYPE=""
  while IFS= read -r line; do
    # Skip empty lines and SSE comments
    [[ -z "$line" ]] && continue
    [[ "$line" == :* ]] && continue

    # Track SSE event type, skip error events
    if [[ "$line" == event:* ]]; then
      LAST_EVENT_TYPE="${line#event:}"
      LAST_EVENT_TYPE="${LAST_EVENT_TYPE# }"
      continue
    fi

    if [[ "$line" == data:* ]]; then
      if [[ "$LAST_EVENT_TYPE" == "error" ]]; then
        echo "⚠️ SSE error: ${line:0:100}"
        LAST_EVENT_TYPE=""
        continue
      fi
      LAST_EVENT_TYPE=""
      data="${line#data:}"
      data="${data# }"
      [[ -z "$data" ]] && continue

      # Validate JSON
      if ! echo "$data" | node -e "let d='';process.stdin.on('data',c=>d+=c);process.stdin.on('end',()=>{try{JSON.parse(d);process.exit(0)}catch(e){process.exit(1)}})" 2>/dev/null; then
        echo "⚠️ Skipping non-JSON: ${data:0:80}"
        continue
      fi

      # Look up refCode from active-requests file
      EVENT_REQ_ID=$(echo "$data" | node -e "let d='';process.stdin.on('data',c=>d+=c);process.stdin.on('end',()=>{try{console.log(JSON.parse(d).requestId||'')}catch(e){console.log('')}})" 2>/dev/null)
      FILE_REF=""
      [ -n "$EVENT_REQ_ID" ] && [ -f "$REQUESTS_DIR/$EVENT_REQ_ID" ] && FILE_REF=$(cat "$REQUESTS_DIR/$EVENT_REQ_ID")

      MSG=$(echo "$data" | REF_FROM_FILE="$FILE_REF" node -e "
        let d='';
        process.stdin.on('data',c=>d+=c);
        process.stdin.on('end',()=>{
          try {
            const j=JSON.parse(d);
            const type=j.type||'unknown';
            const ref=j.refCode||process.env.REF_FROM_FILE||j.requestId||'?';
            switch(type) {
              case 'keys_exchanged':
                console.log('🔑 Key exchange voltooid voor '+ref+' — provider is verbonden');
                break;
              case 'new_message':
                if(j.from==='provider') {
                  console.log('📩 Nieuw antwoord van provider voor '+ref);
                } else {
                  console.log('');
                }
                break;
              case 'responded':
                console.log('📩 Provider heeft geantwoord op '+ref);
                break;
              case 'closed':
                console.log('🔒 Conversatie '+ref+' gesloten');
                break;
              default:
                console.log('🦞 HeySummon event ('+type+') voor '+ref);
            }
          } catch(e) {
            console.log('🦞 HeySummon consumer event');
          }
        });
      " 2>/dev/null)

      # For provider messages, fetch the actual response text
      IS_PROVIDER_MSG=$(echo "$data" | node -e "let d='';process.stdin.on('data',c=>d+=c);process.stdin.on('end',()=>{try{const j=JSON.parse(d);console.log(j.type==='new_message'&&j.from==='provider'?'yes':'')}catch(e){console.log('')}})" 2>/dev/null)
      if [ "$IS_PROVIDER_MSG" = "yes" ] && [ -n "$EVENT_REQ_ID" ]; then
        RESPONSE_TEXT=$(curl -s "${BASE_URL}/api/v1/messages/${EVENT_REQ_ID}" \
          -H "x-api-key: ${API_KEY}" 2>/dev/null | \
          node -e "let d='';process.stdin.on('data',c=>d+=c);process.stdin.on('end',()=>{try{const j=JSON.parse(d);const msgs=j.messages||[];const last=msgs.filter(m=>m.from==='provider').pop();if(last&&last.iv==='plaintext'){console.log(Buffer.from(last.ciphertext,'base64').toString())}else{console.log('(encrypted)')}}catch(e){console.log('')}})" 2>/dev/null)
        if [ -n "$RESPONSE_TEXT" ]; then
          MSG="${MSG}\n💬 ${RESPONSE_TEXT}"
        fi
      fi

      if [ -n "$MSG" ]; then
        # Deduplication
        EVENT_TYPE=$(echo "$data" | node -e "let d='';process.stdin.on('data',c=>d+=c);process.stdin.on('end',()=>{try{console.log(JSON.parse(d).type||'?')}catch(e){console.log('?')}})" 2>/dev/null)
        DEDUP_KEY="${EVENT_TYPE}:${EVENT_REQ_ID}"
        if grep -qF "$DEDUP_KEY" "$SEEN_FILE" 2>/dev/null; then
          echo "⏭️ Skip duplicate: $DEDUP_KEY"
        else
          echo "$DEDUP_KEY" >> "$SEEN_FILE"
          send_notification "$MSG"
          echo "📨 Notified: $MSG"
        fi
      fi

      # Remove closed/expired requests
      EVENT_TYPE=$(echo "$data" | node -e "let d='';process.stdin.on('data',c=>d+=c);process.stdin.on('end',()=>{try{console.log(JSON.parse(d).type)}catch(e){}})" 2>/dev/null)
      if [ "$EVENT_TYPE" = "closed" ] && [ -n "$EVENT_REQ_ID" ]; then
        rm -f "$REQUESTS_DIR/$EVENT_REQ_ID"
      fi
    fi
  done < "$FIFO"

  kill "$CURL_PID" 2>/dev/null
  wait "$CURL_PID" 2>/dev/null
  rm -f "$FIFO"

  echo "🔄 Reconnecting in ${BACKOFF}s..."
  sleep "$BACKOFF"
  [ "$BACKOFF" -lt 60 ] && BACKOFF=$((BACKOFF + 5))
done
