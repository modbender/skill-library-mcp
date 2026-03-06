#!/bin/bash
# nest-events.sh — Nest SDM Pub/Sub Event Listener & Telegram Forwarder
# Polls Pub/Sub subscription for doorbell presses, motion, person detection,
# and other device events, then forwards alerts to Telegram.
#
# Usage:
#   nest-events.sh listen              - Poll events continuously (daemon mode)
#   nest-events.sh poll                - Poll once, print events, exit
#   nest-events.sh setup-check         - Verify Pub/Sub config is ready
#   nest-events.sh create-topic        - Create Pub/Sub topic (requires cloud-platform scope)
#   nest-events.sh create-subscription - Create pull subscription
#   nest-events.sh grant-permissions   - Grant SDM publisher role to topic
#
# Environment:
#   NEST_SDM_TOKENS   - Path to tokens file (default: ~/.openclaw/workspace/.nest-sdm-tokens.json)
#   NEST_PUBSUB_TOKENS - Path to Pub/Sub tokens file (default: ~/.openclaw/workspace/.nest-pubsub-tokens.json)
#   TELEGRAM_BOT_TOKEN - Bot token for sending alerts
#   TELEGRAM_CHAT_ID   - Chat/user ID to send alerts to
#   POLL_INTERVAL      - Seconds between polls in listen mode (default: 10)
#   GCP_PROJECT        - GCP project ID (default: YOUR_GCP_PROJECT)
#   PUBSUB_TOPIC       - Pub/Sub topic name (default: nest-sdm-events)
#   PUBSUB_SUBSCRIPTION - Subscription name (default: nest-sdm-events-sub)

set -euo pipefail

# --- Defaults ---
TOKENS_FILE="${NEST_SDM_TOKENS:-${HOME}/.openclaw/workspace/.nest-sdm-tokens.json}"
PUBSUB_TOKENS_FILE="${NEST_PUBSUB_TOKENS:-${HOME}/.openclaw/workspace/.nest-pubsub-tokens.json}"
GCP_PROJECT="${GCP_PROJECT:-YOUR_GCP_PROJECT}"
PUBSUB_TOPIC="${PUBSUB_TOPIC:-nest-sdm-events}"
PUBSUB_SUBSCRIPTION="${PUBSUB_SUBSCRIPTION:-nest-sdm-events-sub}"
POLL_INTERVAL="${POLL_INTERVAL:-10}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="${HOME}/.openclaw/workspace/data/nest-events"

mkdir -p "$LOG_DIR"

# --- Load Telegram config from env or .zshenv ---
load_telegram_config() {
  if [ -z "${TELEGRAM_BOT_TOKEN:-}" ] || [ -z "${TELEGRAM_CHAT_ID:-}" ]; then
    # Try loading from zshenv
    if [ -f "$HOME/.zshenv" ]; then
      TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-$(grep -oP 'TELEGRAM_BOT_TOKEN=\K[^ ]+' "$HOME/.zshenv" 2>/dev/null | tr -d '"'"'" || true)}"
      TELEGRAM_CHAT_ID="${TELEGRAM_CHAT_ID:-$(grep -oP 'TELEGRAM_CHAT_ID=\K[^ ]+' "$HOME/.zshenv" 2>/dev/null | tr -d '"'"'" || true)}"
    fi
  fi
}

# --- Pub/Sub Auth ---
# Pub/Sub needs a separate token with cloud-platform or pubsub scope
get_pubsub_token() {
  local tokens_file="$PUBSUB_TOKENS_FILE"

  # Method 1: OAuth tokens file (if available)
  if [ -f "$tokens_file" ]; then
    local client_id client_secret refresh_token
    client_id=$(python3 -c "import json; print(json.load(open('${tokens_file}'))['client_id'])")
    client_secret=$(python3 -c "import json; print(json.load(open('${tokens_file}'))['client_secret'])")
    refresh_token=$(python3 -c "import json; print(json.load(open('${tokens_file}'))['refresh_token'])")

    local response token
    response=$(curl -s -X POST https://oauth2.googleapis.com/token \
      -d "client_id=${client_id}" \
      -d "client_secret=${client_secret}" \
      -d "refresh_token=${refresh_token}" \
      -d "grant_type=refresh_token")

    token=$(echo "$response" | python3 -c "import sys,json; print(json.load(sys.stdin).get('access_token',''))" 2>/dev/null)

    if [ -n "$token" ]; then
      echo "$token"
      return 0
    fi
    echo "Warning: OAuth token refresh failed, trying gcloud fallback..." >&2
  fi

  # Method 2: gcloud CLI fallback
  local GCLOUD="${HOME}/.local/google-cloud-sdk/bin/gcloud"
  if [ -x "$GCLOUD" ]; then
    local token
    token=$("$GCLOUD" auth print-access-token 2>/dev/null)
    if [ -n "$token" ]; then
      echo "$token"
      return 0
    fi
  fi

  echo "Error: No Pub/Sub auth available. Need OAuth tokens or gcloud CLI." >&2
  return 1
}

# --- Telegram Alert ---
send_telegram_alert() {
  local message="$1"
  local parse_mode="${2:-Markdown}"

  if [ -z "${TELEGRAM_BOT_TOKEN:-}" ] || [ -z "${TELEGRAM_CHAT_ID:-}" ]; then
    echo "[$(date)] ALERT (no Telegram): $message"
    return 0
  fi

  curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    -H "Content-Type: application/json" \
    -d "$(python3 -c "
import json, sys
msg = '''${message}'''
print(json.dumps({
    'chat_id': '${TELEGRAM_CHAT_ID}',
    'text': msg,
    'parse_mode': '${parse_mode}',
    'disable_notification': False
}))
")" > /dev/null 2>&1 || echo "[$(date)] Warning: Failed to send Telegram alert" >&2
}

# --- Event Parsing ---
parse_event() {
  local event_data="$1"

  # Decode base64 data field
  local decoded
  decoded=$(echo "$event_data" | python3 -c "
import sys, json, base64
try:
    msg = json.load(sys.stdin)
    data = msg.get('message', {}).get('data', '')
    if data:
        decoded = base64.b64decode(data).decode('utf-8')
        print(decoded)
    else:
        print('{}')
except Exception as e:
    print(json.dumps({'error': str(e)}))
" 2>/dev/null)

  echo "$decoded"
}

format_event_alert() {
  local event_json="$1"

  python3 -c "
import json, sys
from datetime import datetime

try:
    event = json.loads('''${event_json}''')
except:
    sys.exit(0)

# Extract key fields
event_type = ''
device_name = ''
timestamp = event.get('timestamp', '')

# Parse resource traits events
resource_update = event.get('resourceUpdate', {})
traits = resource_update.get('traits', {})
events = resource_update.get('events', {})

# Device ID
resource_name = resource_update.get('name', event.get('resourceGroup', {}).get('name', ''))
# Simplify device name
if 'AVPHwEu' in resource_name:
    device_name = 'Doorbell'
elif 'AVPHwEv' in resource_name:
    device_name = 'Thermostat'
elif 'AVPHwEt' in resource_name:
    device_name = 'Kitchen Display'
else:
    device_name = resource_name.split('/')[-1][:12] if resource_name else 'Unknown'

alerts = []

# --- Doorbell Events ---
if 'sdm.devices.events.DoorbellChime.Chime' in events:
    e = events['sdm.devices.events.DoorbellChime.Chime']
    event_id = e.get('eventId', '')
    alerts.append(('🔔 *DOORBELL*', f'Someone rang the doorbell!', event_id))

# --- Person Detection ---
if 'sdm.devices.events.CameraPerson.Person' in events:
    e = events['sdm.devices.events.CameraPerson.Person']
    event_id = e.get('eventId', '')
    alerts.append(('👤 *Person Detected*', f'Person seen at {device_name}', event_id))

# --- Motion Detection ---
if 'sdm.devices.events.CameraMotion.Motion' in events:
    e = events['sdm.devices.events.CameraMotion.Motion']
    event_id = e.get('eventId', '')
    alerts.append(('🏃 *Motion Detected*', f'Motion at {device_name}', event_id))

# --- Sound Detection ---
if 'sdm.devices.events.CameraSound.Sound' in events:
    e = events['sdm.devices.events.CameraSound.Sound']
    event_id = e.get('eventId', '')
    alerts.append(('🔊 *Sound Detected*', f'Sound at {device_name}', event_id))

# --- Thermostat Events (trait changes) ---
if 'sdm.devices.traits.ThermostatHvac' in traits:
    hvac = traits['sdm.devices.traits.ThermostatHvac']
    status = hvac.get('status', 'unknown')
    emoji = '❄️' if status == 'COOLING' else '🔥' if status == 'HEATING' else '⏹️'
    alerts.append((f'{emoji} *HVAC Status*', f'Thermostat is now {status}', ''))

if 'sdm.devices.traits.ThermostatTemperatureSetpoint' in traits:
    setpoint = traits['sdm.devices.traits.ThermostatTemperatureSetpoint']
    cool = setpoint.get('coolCelsius', '')
    heat = setpoint.get('heatCelsius', '')
    parts = []
    if cool: parts.append(f'Cool: {round(cool * 9/5 + 32)}°F')
    if heat: parts.append(f'Heat: {round(heat * 9/5 + 32)}°F')
    if parts:
        alerts.append(('🌡️ *Setpoint Changed*', ' | '.join(parts), ''))

# --- Temperature Change ---
if 'sdm.devices.traits.Temperature' in traits:
    temp = traits['sdm.devices.traits.Temperature']
    ambient_c = temp.get('ambientTemperatureCelsius', '')
    if ambient_c:
        ambient_f = round(ambient_c * 9/5 + 32, 1)
        # Only alert on significant changes (skip minor fluctuations)
        # This will be handled by dedup logic
        alerts.append(('🌡️ *Temperature*', f'Ambient: {ambient_f}°F', ''))

# Format timestamp
time_str = ''
if timestamp:
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        time_str = dt.strftime('%I:%M %p')
    except:
        time_str = timestamp[:19]

# Output alerts
for title, body, event_id in alerts:
    msg = f'{title}\\n{body}'
    if time_str:
        msg += f'\\n🕐 {time_str}'
    print(msg)
    print('---EVENT_SEPARATOR---')
" 2>/dev/null
}

# --- Pub/Sub Pull ---
pull_events() {
  local token
  token=$(get_pubsub_token) || return 1

  local response
  response=$(curl -s -X POST \
    "https://pubsub.googleapis.com/v1/projects/${GCP_PROJECT}/subscriptions/${PUBSUB_SUBSCRIPTION}:pull" \
    -H "Authorization: Bearer ${token}" \
    -H "Content-Type: application/json" \
    -d '{
      "maxMessages": 20
    }' 2>/dev/null)

  # Check for errors
  local error
  error=$(echo "$response" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('error',{}).get('message',''))" 2>/dev/null)
  if [ -n "$error" ] && [ "$error" != "" ]; then
    echo "Error pulling events: $error" >&2
    return 1
  fi

  # Process each message
  local ack_ids=()
  local messages
  messages=$(echo "$response" | python3 -c "
import sys, json
d = json.load(sys.stdin)
msgs = d.get('receivedMessages', [])
for m in msgs:
    ack_id = m.get('ackId', '')
    data = json.dumps(m)
    print(f'{ack_id}|||{data}')
" 2>/dev/null)

  if [ -z "$messages" ]; then
    return 0  # No messages
  fi

  local count=0
  while IFS= read -r line; do
    local ack_id="${line%%|||*}"
    local msg_data="${line#*|||}"

    # Parse the event
    local decoded
    decoded=$(echo "$msg_data" | parse_event)

    # Format alerts
    local alerts
    alerts=$(format_event_alert "$decoded")

    # Send each alert
    if [ -n "$alerts" ]; then
      while IFS= read -r alert; do
        if [ "$alert" != "---EVENT_SEPARATOR---" ] && [ -n "$alert" ]; then
          send_telegram_alert "$alert"
          echo "[$(date)] Alert sent: $(echo "$alert" | head -1)"
          ((count++)) || true
        fi
      done <<< "$alerts"
    fi

    # Collect ack IDs
    ack_ids+=("\"$ack_id\"")

    # Log raw event
    echo "$decoded" >> "${LOG_DIR}/events-$(date +%Y-%m-%d).jsonl"
  done <<< "$messages"

  # Acknowledge messages
  if [ ${#ack_ids[@]} -gt 0 ]; then
    local ack_json
    ack_json=$(printf '%s,' "${ack_ids[@]}")
    ack_json="[${ack_json%,}]"

    curl -s -X POST \
      "https://pubsub.googleapis.com/v1/projects/${GCP_PROJECT}/subscriptions/${PUBSUB_SUBSCRIPTION}:acknowledge" \
      -H "Authorization: Bearer ${token}" \
      -H "Content-Type: application/json" \
      -d "{\"ackIds\": ${ack_json}}" > /dev/null 2>&1
  fi

  echo "[$(date)] Processed ${count} alerts from ${#ack_ids[@]} messages"
}

# --- Pub/Sub Topic Management ---
create_topic() {
  local token
  token=$(get_pubsub_token) || return 1

  echo "Creating Pub/Sub topic: projects/${GCP_PROJECT}/topics/${PUBSUB_TOPIC}"
  local response
  response=$(curl -s -X PUT \
    "https://pubsub.googleapis.com/v1/projects/${GCP_PROJECT}/topics/${PUBSUB_TOPIC}" \
    -H "Authorization: Bearer ${token}" \
    -H "Content-Type: application/json" \
    -d '{}' 2>/dev/null)

  echo "$response" | python3 -c "
import sys, json
d = json.load(sys.stdin)
if 'error' in d:
    code = d['error'].get('code', '')
    msg = d['error'].get('message', '')
    if code == 409:
        print(f'Topic already exists ✅')
    else:
        print(f'Error ({code}): {msg}')
else:
    print(f'Topic created: {d.get(\"name\", \"\")} ✅')
" 2>/dev/null
}

create_subscription() {
  local token
  token=$(get_pubsub_token) || return 1

  echo "Creating subscription: projects/${GCP_PROJECT}/subscriptions/${PUBSUB_SUBSCRIPTION}"
  local response
  response=$(curl -s -X PUT \
    "https://pubsub.googleapis.com/v1/projects/${GCP_PROJECT}/subscriptions/${PUBSUB_SUBSCRIPTION}" \
    -H "Authorization: Bearer ${token}" \
    -H "Content-Type: application/json" \
    -d "{
      \"topic\": \"projects/${GCP_PROJECT}/topics/${PUBSUB_TOPIC}\",
      \"ackDeadlineSeconds\": 60,
      \"messageRetentionDuration\": \"86400s\",
      \"expirationPolicy\": {
        \"ttl\": \"2678400s\"
      }
    }" 2>/dev/null)

  echo "$response" | python3 -c "
import sys, json
d = json.load(sys.stdin)
if 'error' in d:
    code = d['error'].get('code', '')
    msg = d['error'].get('message', '')
    if code == 409:
        print(f'Subscription already exists ✅')
    else:
        print(f'Error ({code}): {msg}')
else:
    print(f'Subscription created: {d.get(\"name\", \"\")} ✅')
" 2>/dev/null
}

grant_permissions() {
  local token
  token=$(get_pubsub_token) || return 1

  echo "Granting SDM publisher permissions to topic..."
  local topic_path="projects/${GCP_PROJECT}/topics/${PUBSUB_TOPIC}"

  # Get current IAM policy
  local policy
  policy=$(curl -s -X GET \
    "https://pubsub.googleapis.com/v1/${topic_path}:getIamPolicy" \
    -H "Authorization: Bearer ${token}" 2>/dev/null)

  # Add the SDM publisher binding
  local new_policy
  new_policy=$(echo "$policy" | python3 -c "
import sys, json
policy = json.load(sys.stdin)
if 'error' in policy:
    print(json.dumps(policy))
    sys.exit(0)

bindings = policy.get('bindings', [])
# Check if already exists
for b in bindings:
    if b.get('role') == 'roles/pubsub.publisher':
        if 'group:sdm-publisher@googlegroups.com' in b.get('members', []):
            print(json.dumps({'already_set': True}))
            sys.exit(0)
        b['members'].append('group:sdm-publisher@googlegroups.com')
        policy['bindings'] = bindings
        print(json.dumps({'policy': policy}))
        sys.exit(0)

# Add new binding
bindings.append({
    'role': 'roles/pubsub.publisher',
    'members': ['group:sdm-publisher@googlegroups.com']
})
policy['bindings'] = bindings
print(json.dumps({'policy': policy}))
" 2>/dev/null)

  # Check if already set
  local already_set
  already_set=$(echo "$new_policy" | python3 -c "import sys,json; print(json.load(sys.stdin).get('already_set', False))" 2>/dev/null)
  if [ "$already_set" = "True" ]; then
    echo "SDM publisher already has access ✅"
    return 0
  fi

  # Set the new policy
  local set_policy
  set_policy=$(echo "$new_policy" | python3 -c "import sys,json; print(json.dumps(json.load(sys.stdin).get('policy', {})))" 2>/dev/null)

  local result
  result=$(curl -s -X POST \
    "https://pubsub.googleapis.com/v1/${topic_path}:setIamPolicy" \
    -H "Authorization: Bearer ${token}" \
    -H "Content-Type: application/json" \
    -d "{\"policy\": ${set_policy}}" 2>/dev/null)

  echo "$result" | python3 -c "
import sys, json
d = json.load(sys.stdin)
if 'error' in d:
    print(f'Error: {d[\"error\"].get(\"message\", \"\")}')
else:
    print('SDM publisher permissions granted ✅')
" 2>/dev/null
}

setup_check() {
  echo "=== Nest SDM Pub/Sub Setup Check ==="
  echo ""

  # Check tokens
  echo -n "1. Pub/Sub auth: "
  if [ -f "$PUBSUB_TOKENS_FILE" ]; then
    echo "✅ OAuth tokens at $PUBSUB_TOKENS_FILE"
  else
    local GCLOUD="${HOME}/.local/google-cloud-sdk/bin/gcloud"
    if [ -x "$GCLOUD" ] && "$GCLOUD" auth print-access-token &>/dev/null; then
      local gcloud_account
      gcloud_account=$("$GCLOUD" config get-value account 2>/dev/null)
      echo "✅ Using gcloud CLI fallback (${gcloud_account})"
    else
      echo "❌ No auth available. Need OAuth tokens or gcloud CLI."
      echo "   OAuth URL (use your-email@example.com):"
      local client_id
      client_id=$(python3 -c "import json; print(json.load(open('${TOKENS_FILE}'))['client_id'])" 2>/dev/null || echo "UNKNOWN")
      echo "   https://accounts.google.com/o/oauth2/v2/auth?client_id=${client_id}&redirect_uri=https://www.google.com&response_type=code&scope=https://www.googleapis.com/auth/pubsub%20https://www.googleapis.com/auth/cloud-platform&access_type=offline&prompt=consent"
    fi
  fi

  echo -n "2. Telegram config: "
  load_telegram_config
  if [ -n "${TELEGRAM_BOT_TOKEN:-}" ] && [ -n "${TELEGRAM_CHAT_ID:-}" ]; then
    echo "✅ Bot token and chat ID set"
  else
    echo "❌ Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID"
  fi

  echo -n "3. GCP Project: "
  echo "$GCP_PROJECT"

  echo -n "4. Topic: "
  echo "projects/${GCP_PROJECT}/topics/${PUBSUB_TOPIC}"

  echo -n "5. Subscription: "
  echo "projects/${GCP_PROJECT}/subscriptions/${PUBSUB_SUBSCRIPTION}"

  echo ""
  echo "=== Setup Steps ==="
  echo "1. Run OAuth flow (browser, as your-email@example.com) → save tokens"
  echo "2. nest-events.sh create-topic"
  echo "3. nest-events.sh grant-permissions"
  echo "4. nest-events.sh create-subscription"
  echo "5. Enable events in Device Access Console (https://console.nest.google.com/device-access)"
  echo "   → Select project → Enable Pub/Sub → Enter topic: projects/${GCP_PROJECT}/topics/${PUBSUB_TOPIC}"
  echo "6. Trigger device list API call to initiate events"
  echo "7. nest-events.sh listen"
}

# --- Dedup (prevent alert fatigue) ---
DEDUP_FILE="${LOG_DIR}/.dedup-cache"
should_alert() {
  local event_key="$1"
  local now
  now=$(date +%s)
  local cooldown=60  # Don't re-alert same event type within 60s

  if [ -f "$DEDUP_FILE" ]; then
    local last_time
    last_time=$(grep "^${event_key}|" "$DEDUP_FILE" 2>/dev/null | tail -1 | cut -d'|' -f2)
    if [ -n "$last_time" ]; then
      local diff=$((now - last_time))
      if [ "$diff" -lt "$cooldown" ]; then
        return 1  # Skip
      fi
    fi
  fi

  echo "${event_key}|${now}" >> "$DEDUP_FILE"
  # Prune old entries (keep last 100)
  if [ -f "$DEDUP_FILE" ] && [ "$(wc -l < "$DEDUP_FILE")" -gt 100 ]; then
    tail -50 "$DEDUP_FILE" > "${DEDUP_FILE}.tmp"
    mv "${DEDUP_FILE}.tmp" "$DEDUP_FILE"
  fi

  return 0
}

# --- Listen Mode (Daemon) ---
listen_loop() {
  load_telegram_config
  echo "[$(date)] Nest SDM Event Listener started"
  echo "[$(date)] Polling every ${POLL_INTERVAL}s"
  echo "[$(date)] GCP Project: ${GCP_PROJECT}"
  echo "[$(date)] Subscription: ${PUBSUB_SUBSCRIPTION}"
  echo ""

  while true; do
    pull_events 2>&1 || echo "[$(date)] Pull failed, retrying in ${POLL_INTERVAL}s..."
    sleep "$POLL_INTERVAL"
  done
}

# --- Main ---
case "${1:-help}" in
  listen)
    listen_loop
    ;;
  poll)
    load_telegram_config
    pull_events
    ;;
  setup-check|check|status)
    setup_check
    ;;
  create-topic)
    create_topic
    ;;
  create-subscription|create-sub)
    create_subscription
    ;;
  grant-permissions|grant)
    grant_permissions
    ;;
  help|--help|-h)
    echo "Nest SDM Pub/Sub Event Listener"
    echo ""
    echo "Usage: $(basename "$0") <command>"
    echo ""
    echo "Commands:"
    echo "  listen              Poll events continuously (daemon mode)"
    echo "  poll                Poll once, print events, exit"
    echo "  setup-check         Verify Pub/Sub config is ready"
    echo "  create-topic        Create Pub/Sub topic"
    echo "  create-subscription Create pull subscription"
    echo "  grant-permissions   Grant SDM publisher role to topic"
    echo ""
    echo "Environment:"
    echo "  NEST_PUBSUB_TOKENS  Path to Pub/Sub OAuth tokens"
    echo "  TELEGRAM_BOT_TOKEN  Telegram bot token for alerts"
    echo "  TELEGRAM_CHAT_ID    Chat ID to send alerts to"
    echo "  POLL_INTERVAL       Seconds between polls (default: 10)"
    echo "  GCP_PROJECT         GCP project ID (default: YOUR_GCP_PROJECT)"
    ;;
  *)
    echo "Unknown command: $1. Use --help for usage." >&2
    exit 1
    ;;
esac
