#!/bin/bash
# HeySummon Provider Watcher — persistent SSE listener via platform proxy
# Connects to /api/v1/events/stream (never directly to Mercure)
# On new event: sends message via OpenClaw /tools/invoke (channel-agnostic)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
[ -f "$SKILL_DIR/.env" ] && set -a && source "$SKILL_DIR/.env" && set +a

BASE_URL="${HEYSUMMON_BASE_URL:-http://localhost:3456}"
API_KEY="${HEYSUMMON_API_KEY:?ERROR: Set HEYSUMMON_API_KEY}"
SEEN_FILE="$HOME/.heysummon-provider/seen-events.txt"
EVENTS_FILE="$HOME/.heysummon-provider/events.jsonl"
OPENCLAW_PORT="${OPENCLAW_PORT:-18789}"
STREAM_URL="${BASE_URL}/api/v1/events/stream"

mkdir -p "$HOME/.heysummon-provider"
touch "$SEEN_FILE"

# Trim seen-events to last 500 on startup
tail -500 "$SEEN_FILE" > "${SEEN_FILE}.tmp" 2>/dev/null && mv "${SEEN_FILE}.tmp" "$SEEN_FILE"

# Read OpenClaw gateway token
OPENCLAW_TOKEN=$(node -e "try{const p=require('path').join(require('os').homedir(),'.openclaw/openclaw.json');console.log(JSON.parse(require('fs').readFileSync(p,'utf8')).gateway.auth.token)}catch(e){}" 2>/dev/null)

if [ -z "$OPENCLAW_TOKEN" ]; then
  echo "ERROR: Could not read OpenClaw gateway token" >&2
  exit 1
fi

echo "🦞 Provider watcher started (pid $$)"
echo "   Stream: ${STREAM_URL}"
echo "   API key: ${API_KEY:0:15}..."

BACKOFF=5
LAST_EVENT_TYPE=""
PENDING_URL="${BASE_URL}/api/v1/events/pending"
ACK_URL="${BASE_URL}/api/v1/events/ack"

# Send ACK for a delivered event
send_ack() {
  local request_id="$1"
  [[ -z "$request_id" ]] && return
  curl -s -X POST "${ACK_URL}/${request_id}" \
    -H "x-api-key: ${API_KEY}" \
    >/dev/null 2>&1
}

# Poll for missed events on (re)connect
poll_pending() {
  echo "🔍 Polling for missed events..."
  local response
  response=$(curl -s -H "x-api-key: ${API_KEY}" "${PENDING_URL}" 2>/dev/null)
  [[ -z "$response" ]] && return

  local count
  count=$(echo "$response" | node -e "let d='';process.stdin.on('data',c=>d+=c);process.stdin.on('end',()=>{try{const j=JSON.parse(d);console.log((j.events||[]).length)}catch(e){console.log(0)}})" 2>/dev/null)
  
  if [[ "$count" -gt 0 ]]; then
    echo "📬 Found ${count} undelivered event(s)"
    echo "$response" | node -e "
      let d='';
      process.stdin.on('data',c=>d+=c);
      process.stdin.on('end',()=>{
        try {
          const j=JSON.parse(d);
          for(const e of (j.events||[])) {
            console.log('data:'+JSON.stringify(e));
          }
        } catch(e){}
      });
    " 2>/dev/null | while IFS= read -r line; do
      process_line "$line"
    done
  else
    echo "✅ No missed events"
  fi
}

process_line() {
  local line="$1"

  # Skip empty lines
  [[ -z "$line" ]] && return

  # Skip SSE comments (lines starting with :)
  [[ "$line" == :* ]] && return

  # Track SSE event type
  if [[ "$line" == event:* ]]; then
    LAST_EVENT_TYPE="${line#event:}"
    LAST_EVENT_TYPE="${LAST_EVENT_TYPE# }"
    return
  fi

  # Only process data: lines
  [[ "$line" != data:* ]] && return

  # Skip error events from SSE proxy
  if [[ "$LAST_EVENT_TYPE" == "error" ]]; then
    echo "⚠️ SSE error: ${line:0:100}"
    LAST_EVENT_TYPE=""
    return
  fi
  LAST_EVENT_TYPE=""

  local data="${line#data:}"
  data="${data# }"
  [[ -z "$data" ]] && return

  # Parse and deduplicate using node
  local result
  result=$(echo "$data" | node -e "
    let d='';
    process.stdin.on('data',c=>d+=c);
    process.stdin.on('end',()=>{
      try {
        const j=JSON.parse(d);
        const type=j.type||'unknown';
        const ref=j.refCode||'?';
        const id=j.requestId||j.id||'';
        const key=type+':'+id;
        const q=j.question||'';
        const from=j.from||'';
        const preview=j.messagePreview||'';
        
        let msg='🦞 HeySummon ['+ref+'] ';
        switch(type) {
          case 'new_request':
            msg+='Nieuw verzoek';
            if(q && !q.includes('==')) msg+='\n📝 '+q;
            break;
          case 'new_message':
            msg+='Nieuw bericht (van '+from+')';
            if(preview) msg+='\n💬 '+preview.slice(0,240);
            break;
          case 'keys_exchanged':
            msg+='Key exchange voltooid';
            break;
          case 'closed':
            msg+='Conversatie gesloten';
            break;
          case 'responded':
            msg+='Provider heeft geantwoord';
            break;
          default:
            msg+='Event: '+type;
        }
        console.log(JSON.stringify({key,msg}));
      } catch(e) {
        console.log('{}');
      }
    });
  " 2>/dev/null)

  [[ -z "$result" || "$result" == "{}" ]] && return

  local dedup_key msg
  dedup_key=$(echo "$result" | node -e "let d='';process.stdin.on('data',c=>d+=c);process.stdin.on('end',()=>{try{console.log(JSON.parse(d).key)}catch(e){}})" 2>/dev/null)
  msg=$(echo "$result" | node -e "let d='';process.stdin.on('data',c=>d+=c);process.stdin.on('end',()=>{try{console.log(JSON.parse(d).msg)}catch(e){}})" 2>/dev/null)

  [[ -z "$msg" ]] && return

  # Deduplication check
  if grep -qF "$dedup_key" "$SEEN_FILE" 2>/dev/null; then
    echo "⏭️ Skip duplicate: $dedup_key"
    return
  fi
  echo "$dedup_key" >> "$SEEN_FILE"
  echo "$data" >> "$EVENTS_FILE"

  # Send notification via OpenClaw
  local NOTIFY_TARGET="${HEYSUMMON_NOTIFY_TARGET:?ERROR: Set HEYSUMMON_NOTIFY_TARGET}"
  local PAYLOAD
  PAYLOAD=$(node -e "console.log(JSON.stringify({
    tool:'message',
    args:{action:'send',message:process.argv[1],target:process.argv[2]}
  }))" "$msg" "$NOTIFY_TARGET" 2>/dev/null)

  curl -s "http://127.0.0.1:${OPENCLAW_PORT}/tools/invoke" \
    -H "Authorization: Bearer ${OPENCLAW_TOKEN}" \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD" \
    >/dev/null 2>&1

  # Send delivery ACK
  local request_id
  request_id=$(echo "$data" | node -e "let d='';process.stdin.on('data',c=>d+=c);process.stdin.on('end',()=>{try{console.log(JSON.parse(d).requestId||'')}catch(e){console.log('')}})" 2>/dev/null)
  send_ack "$request_id"

  echo "📨 Sent: $dedup_key"
  BACKOFF=5
}

while true; do
  echo "🔌 Connecting to SSE stream..."
  
  # Poll for any missed events before connecting to stream
  poll_pending
  
  # Use a temp file + tail approach to avoid pipe subshell issues
  FIFO="/tmp/.heysummon-sse-$$"
  rm -f "$FIFO"
  mkfifo "$FIFO"
  
  # Start curl writing to fifo in background
  curl -sN --no-buffer -H "x-api-key: ${API_KEY}" "${STREAM_URL}" > "$FIFO" 2>/dev/null &
  CURL_PID=$!
  
  # Read from fifo in main shell (not a subshell!)
  while IFS= read -r line; do
    process_line "$line"
  done < "$FIFO"
  
  # Cleanup
  kill "$CURL_PID" 2>/dev/null
  wait "$CURL_PID" 2>/dev/null
  rm -f "$FIFO"

  echo "🔄 Reconnecting in ${BACKOFF}s..."
  sleep "$BACKOFF"
  [ "$BACKOFF" -lt 60 ] && BACKOFF=$((BACKOFF + 5))
done
