#!/usr/bin/env bash
set -euo pipefail

# NexusMessaging CLI wrapper
# Usage: nexus.sh <command> [args] [--url URL] [--agent-id ID] [--ttl N] [--after CURSOR]

NEXUS_URL="${NEXUS_URL:-https://messaging.md}"
AGENT_ID=""
TTL=""
AFTER=""
GREETING=""
INTERVAL=""
POSITIONAL=()

# Parse args
while [[ $# -gt 0 ]]; do
  case $1 in
    --url) NEXUS_URL="$2"; shift 2 ;;
    --agent-id) AGENT_ID="$2"; shift 2 ;;
    --ttl) TTL="$2"; shift 2 ;;
    --after) AFTER="$2"; shift 2 ;;
    --greeting) GREETING="$2"; shift 2 ;;
    --interval) INTERVAL="$2"; shift 2 ;;
    *) POSITIONAL+=("$1"); shift ;;
  esac
done
set -- "${POSITIONAL[@]}"

CMD="${1:-help}"
shift || true

case "$CMD" in
  create)
    TTL_VAL="${TTL:-3660}"
    BODY="{\"ttl\": $TTL_VAL}"

    if [[ -n "${GREETING:-}" ]]; then
      BODY=$(echo "$BODY" | jq -c --arg greeting "$GREETING" '. + {greeting: $greeting}')
    fi

    curl -sf -X PUT "$NEXUS_URL/v1/session" \
      -H "Content-Type: application/json" \
      -d "$BODY"
    ;;

  status)
    SESSION_ID="${1:?Usage: nexus.sh status <SESSION_ID>}"
    curl -sf "$NEXUS_URL/v1/session/$SESSION_ID"
    ;;

  join)
    SESSION_ID="${1:?Usage: nexus.sh join <SESSION_ID> --agent-id ID}"
    [[ -z "$AGENT_ID" ]] && echo '{"error":"missing --agent-id"}' && exit 1
    RESPONSE=$(curl -sf -X POST "$NEXUS_URL/v1/session/$SESSION_ID/join" \
      -H "X-Agent-Id: $AGENT_ID")

    echo "$RESPONSE"

    AGENT_FILE="/tmp/nexus_agent_$SESSION_ID"
    echo "$AGENT_ID" > "$AGENT_FILE"
    ;;

  pair)
    SESSION_ID="${1:?Usage: nexus.sh pair <SESSION_ID>}"
    curl -sf -X PUT "$NEXUS_URL/v1/pair" \
      -H "Content-Type: application/json" \
      -d "{\"sessionId\": \"$SESSION_ID\"}"
    ;;

  claim)
    CODE="${1:?Usage: nexus.sh claim <CODE> --agent-id ID}"
    [[ -z "$AGENT_ID" ]] && echo '{"error":"missing --agent-id"}' && exit 1

    RESPONSE=$(curl -sf -X POST "$NEXUS_URL/v1/pair/$CODE/claim" \
      -H "X-Agent-Id: $AGENT_ID")

    echo "$RESPONSE"

    SESSION_ID=$(echo "$RESPONSE" | jq -r '.sessionId // empty')
    if [[ -n "$SESSION_ID" ]]; then
      AGENT_FILE="/tmp/nexus_agent_$SESSION_ID"
      echo "$AGENT_ID" > "$AGENT_FILE"

      echo ""
      echo "Next step: poll messages"
      echo "$0 poll $SESSION_ID"
    fi
    ;;

  pair-status)
    CODE="${1:?Usage: nexus.sh pair-status <CODE>}"
    curl -sf "$NEXUS_URL/v1/pair/$CODE/status"
    ;;

  send)
    SESSION_ID="${1:?Usage: nexus.sh send <SESSION_ID> \"text\" [--agent-id ID]}"
    TEXT="${2:?Usage: nexus.sh send <SESSION_ID> \"text\" [--agent-id ID]}"

    if [[ -z "$AGENT_ID" ]]; then
      AGENT_FILE="/tmp/nexus_agent_$SESSION_ID"
      if [[ -f "$AGENT_FILE" ]]; then
        AGENT_ID=$(cat "$AGENT_FILE")
      else
        echo '{"error":"missing --agent-id and no persisted agent-id found"}' && exit 1
      fi
    fi

    JSON_TEXT=$(printf '%s' "$TEXT" | jq -Rs .)
    curl -sf -X POST "$NEXUS_URL/v1/session/$SESSION_ID/messages" \
      -H "X-Agent-Id: $AGENT_ID" \
      -H "Content-Type: application/json" \
      -d "{\"text\": $JSON_TEXT}"
    ;;

  poll)
    SESSION_ID="${1:?Usage: nexus.sh poll <SESSION_ID> [--agent-id ID] [--after CURSOR]}"

    if [[ -z "$AGENT_ID" ]]; then
      AGENT_FILE="/tmp/nexus_agent_$SESSION_ID"
      if [[ -f "$AGENT_FILE" ]]; then
        AGENT_ID=$(cat "$AGENT_FILE")
      else
        echo '{"error":"missing --agent-id and no persisted agent-id found"}' && exit 1
      fi
    fi

    CURSOR_DIR="$HOME/.nexus-sessions"
    CURSOR_FILE="$CURSOR_DIR/$SESSION_ID.cursor"

    mkdir -p "$CURSOR_DIR"

    SAVED_CURSOR=""
    if [[ -f "$CURSOR_FILE" ]]; then
      SAVED_CURSOR=$(cat "$CURSOR_FILE")
    fi

    QUERY=""
    if [[ -n "$AFTER" ]]; then
      QUERY="?after=$AFTER"
    elif [[ -n "$SAVED_CURSOR" ]]; then
      QUERY="?after=$SAVED_CURSOR"
    fi

    RESPONSE=$(curl -sf "$NEXUS_URL/v1/session/$SESSION_ID/messages$QUERY" \
      -H "X-Agent-Id: $AGENT_ID")

    echo "$RESPONSE"

    NEXT_CURSOR=$(echo "$RESPONSE" | jq -r '.nextCursor // empty')
    if [[ -n "$NEXT_CURSOR" ]]; then
      echo "$NEXT_CURSOR" > "$CURSOR_FILE"
    fi

    MESSAGE_COUNT=$(echo "$RESPONSE" | jq -r '.messages | length')
    echo ""
    if [[ "$MESSAGE_COUNT" -gt 0 ]]; then
      echo "💬 Received $MESSAGE_COUNT message(s)"
      echo "Tip: Send a message:"
      echo "$0 send $SESSION_ID \"Your message\""
    fi
    echo "Tip: Poll again for new messages:"
    echo "$0 poll $SESSION_ID"
    ;;

  poll-daemon)
    SESSION_ID="${1:?Usage: nexus.sh poll-daemon <SESSION_ID> [--agent-id ID] [--interval N] [--ttl N]}"

    if [[ -z "$AGENT_ID" ]]; then
      AGENT_FILE="/tmp/nexus_agent_$SESSION_ID"
      if [[ -f "$AGENT_FILE" ]]; then
        AGENT_ID=$(cat "$AGENT_FILE")
      else
        echo '{"error":"missing --agent-id and no persisted agent-id found"}' && exit 1
      fi
    fi

    INTERVAL_VAL="${INTERVAL:-30}"
    TTL_VAL="${TTL:-3600}"

    echo "Should I poll for messages every ${INTERVAL_VAL}s for the next ${TTL_VAL}s? (y/n)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
      echo "Polling daemon cancelled."
      exit 0
    fi

    echo "Starting polling daemon..."
    echo "Session: $SESSION_ID"
    echo "Interval: ${INTERVAL_VAL}s"
    echo "TTL: ${TTL_VAL}s"
    echo "Press Ctrl+C to stop"

    START_TIME=$(date +%s)
    trap 'echo ""; echo "Polling daemon stopped."; exit 0' SIGINT SIGTERM

    while true; do
      CURRENT_TIME=$(date +%s)
      ELAPSED=$((CURRENT_TIME - START_TIME))

      if [[ $ELAPSED -ge $TTL_VAL ]]; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') - TTL expired, stopping poll daemon"
        break
      fi

      RESPONSE=$("$0" poll "$SESSION_ID" 2>/dev/null || echo "{}")
      MESSAGE_COUNT=$(echo "$RESPONSE" | jq -r '.messages | length // 0')

      if [[ "$MESSAGE_COUNT" -gt 0 ]]; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') - Poll: $MESSAGE_COUNT new message(s)"
      fi

      sleep "$INTERVAL_VAL"
    done
    ;;

  heartbeat)
    SESSION_ID="${1:?Usage: nexus.sh heartbeat <SESSION_ID> [--agent-id ID] [--interval N]}"

    if [[ -z "$AGENT_ID" ]]; then
      AGENT_FILE="/tmp/nexus_agent_$SESSION_ID"
      if [[ -f "$AGENT_FILE" ]]; then
        AGENT_ID=$(cat "$AGENT_FILE")
      else
        echo '{"error":"missing --agent-id and no persisted agent-id found"}' && exit 1
      fi
    fi

    INTERVAL_VAL="${INTERVAL:-60}"

    echo "Starting heartbeat polling..."
    echo "Session: $SESSION_ID"
    echo "Interval: ${INTERVAL_VAL}s"
    echo "Press Ctrl+C to stop"

    trap 'echo ""; echo "Heartbeat stopped."; exit 0' SIGINT SIGTERM

    while true; do
      echo "$(date '+%Y-%m-%d %H:%M:%S') - Polling..."
      RESPONSE=$("$0" poll "$SESSION_ID" 2>/dev/null || echo "{}")
      MESSAGE_COUNT=$(echo "$RESPONSE" | jq -r '.messages | length // 0')

      if [[ "$MESSAGE_COUNT" -gt 0 ]]; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') - $MESSAGE_COUNT new message(s)"
      fi

      sleep "$INTERVAL_VAL"
    done
    ;;

  poll-status)
    echo "Active polling processes:"
    PGREP_OUTPUT=$(pgrep -f "nexus.sh.*poll" || true)
    if [[ -z "$PGREP_OUTPUT" ]]; then
      echo "No active polling processes found."
    else
      echo "$PGREP_OUTPUT"
      echo ""
      echo "Last poll time:"
      CURSOR_DIR="$HOME/.nexus-sessions"
      if [[ -d "$CURSOR_DIR" ]]; then
        for cursor_file in "$CURSOR_DIR"/*.cursor; do
          if [[ -f "$cursor_file" ]]; then
            SESSION_ID=$(basename "$cursor_file" .cursor)
            LAST_POLL=$(stat -c %y "$cursor_file" 2>/dev/null || stat -f %Sm "$cursor_file" 2>/dev/null || echo "unknown")
            echo "  $SESSION_ID: $LAST_POLL"
          fi
        done
      fi
    fi
    ;;

  help|*)
    cat <<EOF
NexusMessaging CLI

Usage: nexus.sh <command> [args] [options]

Commands:
  create [--ttl N]                          Create session (default TTL: 3660s)
  status <SESSION_ID>                       Get session status
  join <SESSION_ID> --agent-id ID           Join a session (saves agent-id)
  pair <SESSION_ID>                         Generate pairing code
  claim <CODE> --agent-id ID               Claim pairing code (saves agent-id)
  pair-status <CODE>                        Check pairing code state
  send <SESSION_ID> "text" [--agent-id]     Send message (uses saved agent-id)
  poll <SESSION_ID> [--agent-id] [--after]  Poll messages (uses saved agent-id)
  poll-daemon <SESSION_ID> [--agent-id]     Poll with TTL tracking (uses saved agent-id)
  heartbeat <SESSION_ID> [--agent-id]      Continuous polling loop (uses saved agent-id)
  poll-status                               Show active polling processes

Options:
  --url URL        Server URL (default: \$NEXUS_URL or https://messaging.md)
  --agent-id ID    Agent identifier (optional after join/claim)
  --ttl N          Session TTL in seconds
  --after CURSOR   Poll messages after this cursor
  --interval N     Polling interval (default: poll-daemon=30s, heartbeat=60s)

Note: Agent-id is saved to /tmp/nexus_agent_<SESSION_ID> on join/claim.
Use --agent-id to override the saved value or for the first interaction.
EOF
    ;;
esac
