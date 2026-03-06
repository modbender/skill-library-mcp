#!/bin/bash
# nest-sdm.sh — Nest Smart Device Management CLI
# Controls thermostat, doorbell, and cameras via Google SDM REST API.
#
# Usage:
#   nest-sdm.sh devices                   - List all devices (JSON)
#   nest-sdm.sh structures                - List structures/rooms
#   nest-sdm.sh thermostat                - Thermostat status (human-readable)
#   nest-sdm.sh set-cool <°F>             - Set COOL mode at temp
#   nest-sdm.sh set-heat <°F>             - Set HEAT mode at temp
#   nest-sdm.sh set-range <low°F> <hi°F>  - Set HEATCOOL range
#   nest-sdm.sh set-mode <MODE>           - Set mode (HEAT|COOL|HEATCOOL|OFF)
#   nest-sdm.sh set-eco <MODE>            - Set eco mode (MANUAL_ECO|OFF)
#   nest-sdm.sh fan-on [seconds]          - Turn fan on (default 900s)
#   nest-sdm.sh fan-off                   - Turn fan off
#   nest-sdm.sh doorbell                  - Doorbell info
#   nest-sdm.sh display                   - Kitchen display info
#   nest-sdm.sh api <METHOD> <path> [body] - Raw API call

set -euo pipefail

# --- Config ---
TOKENS_FILE="${NEST_SDM_TOKENS:-${HOME}/.openclaw/workspace/.nest-sdm-tokens.json}"

if [ ! -f "$TOKENS_FILE" ]; then
  echo "Error: Token file not found at $TOKENS_FILE" >&2
  echo "Run the authorization flow first. See SKILL.md for setup." >&2
  exit 1
fi

PROJECT_ID=$(python3 -c "import json; print(json.load(open('${TOKENS_FILE}'))['project_id'])")
CLIENT_ID=$(python3 -c "import json; print(json.load(open('${TOKENS_FILE}'))['client_id'])")
CLIENT_SECRET=$(python3 -c "import json; print(json.load(open('${TOKENS_FILE}'))['client_secret'])")
REFRESH_TOKEN=$(python3 -c "import json; print(json.load(open('${TOKENS_FILE}'))['refresh_token'])")

# --- Auth ---
get_token() {
  local response
  response=$(curl -s -X POST https://oauth2.googleapis.com/token \
    -d "client_id=${CLIENT_ID}" \
    -d "client_secret=${CLIENT_SECRET}" \
    -d "refresh_token=${REFRESH_TOKEN}" \
    -d "grant_type=refresh_token")

  local token
  token=$(echo "$response" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('access_token',''))" 2>/dev/null)

  if [ -z "$token" ]; then
    echo "Error: Failed to get access token. Response:" >&2
    echo "$response" >&2
    echo "" >&2
    echo "The refresh token may have expired (7-day limit in testing mode)." >&2
    echo "Re-run the authorization flow. See SKILL.md." >&2
    exit 1
  fi
  echo "$token"
}

ACCESS_TOKEN=$(get_token)
BASE_URL="https://smartdevicemanagement.googleapis.com/v1/enterprises/${PROJECT_ID}"

# --- API helpers ---
api_get() {
  curl -s -X GET "${BASE_URL}/$1" \
    -H "Authorization: Bearer ${ACCESS_TOKEN}" \
    -H "Content-Type: application/json"
}

api_post() {
  curl -s -X POST "${BASE_URL}/$1" \
    -H "Authorization: Bearer ${ACCESS_TOKEN}" \
    -H "Content-Type: application/json" \
    -d "$2"
}

# --- Temperature conversion ---
f_to_c() { python3 -c "print(round(($1 - 32) * 5/9, 1))"; }
c_to_f() { python3 -c "print(round($1 * 9/5 + 32, 1))"; }

# --- Device ID resolution ---
# Auto-discover device IDs by type, optionally filtered by --name
# Usage: get_device_id <TYPE> [name_filter]
# name_filter matches against customName or room displayName (case-insensitive, substring)
get_device_id() {
  local dtype="$1"
  local name_filter="${2:-}"
  api_get "devices" | python3 -c "
import sys, json
devices = json.load(sys.stdin).get('devices', [])
name_filter = '''${name_filter}'''.strip().lower()
matches = []
for d in devices:
    if d['type'] == 'sdm.devices.types.${dtype}':
        matches.append(d)

if not matches:
    print(f'Error: No ${dtype} device found.', file=sys.stderr)
    sys.exit(1)

if name_filter:
    filtered = []
    for d in matches:
        custom = d.get('traits', {}).get('sdm.devices.traits.Info', {}).get('customName', '').lower()
        room = (d.get('parentRelations', [{}])[0].get('displayName', '') or '').lower()
        if name_filter in custom or name_filter in room:
            filtered.append(d)
    if not filtered:
        avail = []
        for d in matches:
            custom = d.get('traits', {}).get('sdm.devices.traits.Info', {}).get('customName', '')
            room = d.get('parentRelations', [{}])[0].get('displayName', '')
            label = custom or room or '(unnamed)'
            avail.append(label)
        print(f'Error: No ${dtype} matching \"{name_filter}\". Available: {\", \".join(avail)}', file=sys.stderr)
        sys.exit(1)
    matches = filtered

print(matches[0]['name'].split('/')[-1])
"
}

# --- Argument parsing ---
# Extract --name value from arguments, return remaining args
# Sets global DEVICE_NAME variable
DEVICE_NAME=""

parse_name_flag() {
  DEVICE_NAME=""
  local new_args=()
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --name)
        DEVICE_NAME="${2:?Error: --name requires a value}"
        shift 2
        ;;
      --name=*)
        DEVICE_NAME="${1#--name=}"
        shift
        ;;
      *)
        new_args+=("$1")
        shift
        ;;
    esac
  done
  # Return remaining args via global
  REMAINING_ARGS=("${new_args[@]+"${new_args[@]}"}")
}

# --- Commands ---

cmd_devices() {
  api_get "devices" | python3 -c "
import sys, json
devices = json.load(sys.stdin).get('devices', [])
for d in devices:
    dtype = d['type'].split('.')[-1]
    name = d.get('traits', {}).get('sdm.devices.traits.Info', {}).get('customName', '')
    room = d.get('parentRelations', [{}])[0].get('displayName', 'Unknown')
    dev_id = d['name'].split('/')[-1]
    status = d.get('traits', {}).get('sdm.devices.traits.Connectivity', {}).get('status', '?')
    print(f'{dtype:<12} | {room:<15} | {name or \"(unnamed)\":<20} | {status}')
    print(f'             ID: {dev_id[:30]}...')
    print()
"
}

cmd_structures() {
  local data
  data=$(api_get "structures")
  python3 -c "
import json, sys

data = json.loads('''$(echo "$data" | sed "s/'/\\\\'/g")''')
structs = data.get('structures', [])
if not structs:
    print('No structures found.')
    sys.exit(0)

for s in structs:
    sid = s['name'].split('/')[-1]
    info = s.get('traits', {}).get('sdm.structures.traits.Info', {})
    name = info.get('customName', 'Home')
    print(f'=== {name} ===')
    print(f'  ID: {sid[:30]}...')

    rooms = s.get('traits', {}).get('sdm.structures.traits.RoomInfo', {})
    if rooms:
        print(f'  Rooms:')
        for r in rooms:
            print(f'    - {r}')
    print()
"
  # Also show devices grouped by room
  echo "Devices:"
  api_get "devices" | python3 -c "
import json, sys
from collections import defaultdict

devices = json.load(sys.stdin).get('devices', [])
rooms = defaultdict(list)
for d in devices:
    dtype = d['type'].split('.')[-1]
    room = d.get('parentRelations', [{}])[0].get('displayName', 'Unknown')
    name = d.get('traits', {}).get('sdm.devices.traits.Info', {}).get('customName', '')
    conn = d.get('traits', {}).get('sdm.devices.traits.Connectivity', {}).get('status', '?')
    rooms[room].append(f'{dtype}: {name or \"(unnamed)\"} [{conn}]')

for room, devs in sorted(rooms.items()):
    print(f'  {room}:')
    for dev in devs:
        print(f'    - {dev}')
"
}

cmd_auth_status() {
  if [ ! -f "$TOKENS_FILE" ]; then
    echo "Error: Token file not found." >&2
    exit 1
  fi

  python3 -c "
import json, os, time
from datetime import datetime, timedelta

f = '${TOKENS_FILE}'
mtime = os.path.getmtime(f)
with open(f) as fh:
    data = json.load(fh)

now = time.time()
age_s = now - mtime
age_days = age_s / 86400

# Refresh tokens expire after 7 days in testing mode
expiry_days = 7
remaining_s = (expiry_days * 86400) - age_s
remaining_days = remaining_s / 86400

last_modified = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
expires_at = datetime.fromtimestamp(mtime + expiry_days * 86400).strftime('%Y-%m-%d %H:%M:%S')

print('=== Nest SDM Auth Status ===')
print(f'Token file:    {f}')
print(f'Last modified: {last_modified}')
print(f'Token age:     {age_days:.1f} days')
print(f'Expires:       {expires_at} (7-day testing mode)')
print()

if remaining_s <= 0:
    print('⛔ TOKEN EXPIRED — re-auth required!')
    print('   Run the authorization flow. See SKILL.md.')
elif remaining_days <= 1:
    print(f'🔴 CRITICAL: Token expires in {remaining_days:.1f} days ({int(remaining_s/3600)}h)')
    print('   Re-auth soon to avoid disruption.')
elif remaining_days <= 3:
    print(f'🟡 WARNING: Token expires in {remaining_days:.1f} days')
    print('   Consider re-authing proactively.')
else:
    print(f'🟢 OK: {remaining_days:.1f} days remaining')

print()
print(f'Project ID:    {data.get(\"project_id\", \"?\")[:30]}...')
print(f'Client ID:     {data.get(\"client_id\", \"?\")[:30]}...')
print(f'Has refresh:   {\"yes\" if data.get(\"refresh_token\") else \"NO\"}')
"
}

cmd_thermostat() {
  local dev_id
  dev_id=$(get_device_id "THERMOSTAT" "$DEVICE_NAME")
  local data
  data=$(api_get "devices/${dev_id}")

  python3 -c "
import json, sys

d = json.loads('''$(echo "$data" | sed "s/'/\\\\'/g")''')
t = d['traits']

temp_c = t['sdm.devices.traits.Temperature']['ambientTemperatureCelsius']
temp_f = round(temp_c * 9/5 + 32, 1)
humidity = t['sdm.devices.traits.Humidity']['ambientHumidityPercent']
mode = t['sdm.devices.traits.ThermostatMode']['mode']
hvac = t['sdm.devices.traits.ThermostatHvac']['status']
status = t['sdm.devices.traits.Connectivity']['status']
eco = t['sdm.devices.traits.ThermostatEco']['mode']
fan_mode = t['sdm.devices.traits.Fan']['timerMode']
fan_timeout = t['sdm.devices.traits.Fan'].get('timerTimeout', '')
room = d.get('parentRelations', [{}])[0].get('displayName', 'Unknown')

sp = t.get('sdm.devices.traits.ThermostatTemperatureSetpoint', {})
setpoint = ''
if mode == 'COOL' and 'coolCelsius' in sp:
    sf = round(sp['coolCelsius'] * 9/5 + 32, 1)
    setpoint = f'Cool to {sf}°F'
elif mode == 'HEAT' and 'heatCelsius' in sp:
    sf = round(sp['heatCelsius'] * 9/5 + 32, 1)
    setpoint = f'Heat to {sf}°F'
elif mode == 'HEATCOOL':
    lo = round(sp.get('heatCelsius', 0) * 9/5 + 32, 1)
    hi = round(sp.get('coolCelsius', 0) * 9/5 + 32, 1)
    setpoint = f'Range {lo}°F – {hi}°F'

print(f'=== Nest Thermostat ({room}) ===')
print(f'Status:      {status}')
print(f'Temperature: {temp_f}°F ({temp_c}°C)')
print(f'Humidity:    {humidity}%')
print(f'Mode:        {mode}')
print(f'HVAC:        {hvac}')
print(f'Eco:         {eco}')

# Fan with timer remaining
if fan_mode == 'ON' and fan_timeout:
    from datetime import datetime, timezone
    try:
        exp = datetime.fromisoformat(fan_timeout.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        remaining = (exp - now).total_seconds()
        if remaining > 0:
            mins = int(remaining // 60)
            secs = int(remaining % 60)
            print(f'Fan:         ON ({mins}m {secs}s remaining)')
        else:
            print(f'Fan:         ON (timer expired)')
    except:
        print(f'Fan:         {fan_mode}')
else:
    print(f'Fan:         {fan_mode}')
if setpoint:
    print(f'Setpoint:    {setpoint}')
"
}

cmd_set_cool() {
  local temp_f="$1"
  local temp_c
  temp_c=$(f_to_c "$temp_f")
  local dev_id
  dev_id=$(get_device_id "THERMOSTAT" "$DEVICE_NAME")

  api_post "devices/${dev_id}:executeCommand" \
    "{\"command\":\"sdm.devices.commands.ThermostatMode.SetMode\",\"params\":{\"mode\":\"COOL\"}}" > /dev/null

  api_post "devices/${dev_id}:executeCommand" \
    "{\"command\":\"sdm.devices.commands.ThermostatTemperatureSetpoint.SetCool\",\"params\":{\"coolCelsius\":${temp_c}}}" > /dev/null

  echo "✅ Thermostat set to COOL at ${temp_f}°F (${temp_c}°C)"
}

cmd_set_heat() {
  local temp_f="$1"
  local temp_c
  temp_c=$(f_to_c "$temp_f")
  local dev_id
  dev_id=$(get_device_id "THERMOSTAT" "$DEVICE_NAME")

  api_post "devices/${dev_id}:executeCommand" \
    "{\"command\":\"sdm.devices.commands.ThermostatMode.SetMode\",\"params\":{\"mode\":\"HEAT\"}}" > /dev/null

  api_post "devices/${dev_id}:executeCommand" \
    "{\"command\":\"sdm.devices.commands.ThermostatTemperatureSetpoint.SetHeat\",\"params\":{\"heatCelsius\":${temp_c}}}" > /dev/null

  echo "✅ Thermostat set to HEAT at ${temp_f}°F (${temp_c}°C)"
}

cmd_set_range() {
  local lo_f="$1" hi_f="$2"
  local lo_c hi_c
  lo_c=$(f_to_c "$lo_f")
  hi_c=$(f_to_c "$hi_f")
  local dev_id
  dev_id=$(get_device_id "THERMOSTAT" "$DEVICE_NAME")

  api_post "devices/${dev_id}:executeCommand" \
    "{\"command\":\"sdm.devices.commands.ThermostatMode.SetMode\",\"params\":{\"mode\":\"HEATCOOL\"}}" > /dev/null

  api_post "devices/${dev_id}:executeCommand" \
    "{\"command\":\"sdm.devices.commands.ThermostatTemperatureSetpoint.SetRange\",\"params\":{\"heatCelsius\":${lo_c},\"coolCelsius\":${hi_c}}}" > /dev/null

  echo "✅ Thermostat set to HEATCOOL range: ${lo_f}°F – ${hi_f}°F"
}

cmd_set_mode() {
  local mode="$1"
  local dev_id
  dev_id=$(get_device_id "THERMOSTAT" "$DEVICE_NAME")

  api_post "devices/${dev_id}:executeCommand" \
    "{\"command\":\"sdm.devices.commands.ThermostatMode.SetMode\",\"params\":{\"mode\":\"${mode}\"}}" > /dev/null

  echo "✅ Thermostat mode set to ${mode}"
}

cmd_set_eco() {
  local mode="$1"
  local dev_id
  dev_id=$(get_device_id "THERMOSTAT" "$DEVICE_NAME")

  api_post "devices/${dev_id}:executeCommand" \
    "{\"command\":\"sdm.devices.commands.ThermostatEco.SetMode\",\"params\":{\"mode\":\"${mode}\"}}" > /dev/null

  echo "✅ Eco mode set to ${mode}"
}

cmd_fan_on() {
  local duration="${1:-900}"
  local dev_id
  dev_id=$(get_device_id "THERMOSTAT" "$DEVICE_NAME")

  api_post "devices/${dev_id}:executeCommand" \
    "{\"command\":\"sdm.devices.commands.Fan.SetTimer\",\"params\":{\"timerMode\":\"ON\",\"duration\":\"${duration}s\"}}" > /dev/null

  echo "✅ Fan ON for ${duration}s ($(python3 -c "print(${duration}//60)")min)"
}

cmd_fan_off() {
  local dev_id
  dev_id=$(get_device_id "THERMOSTAT" "$DEVICE_NAME")

  api_post "devices/${dev_id}:executeCommand" \
    "{\"command\":\"sdm.devices.commands.Fan.SetTimer\",\"params\":{\"timerMode\":\"OFF\"}}" > /dev/null

  echo "✅ Fan OFF"
}

cmd_camera_info() {
  local dtype="$1" label="$2"
  local dev_id
  dev_id=$(get_device_id "$dtype" "$DEVICE_NAME")
  local data
  data=$(api_get "devices/${dev_id}")

  python3 -c "
import json

d = json.loads('''$(echo "$data" | sed "s/'/\\\\'/g")''')
t = d['traits']
name = t.get('sdm.devices.traits.Info', {}).get('customName', '${label}')
room = d.get('parentRelations', [{}])[0].get('displayName', 'Unknown')

print(f'=== Nest ${label} ({name}) — {room} ===')

ls = t.get('sdm.devices.traits.CameraLiveStream', {})
if ls:
    print(f'Video:      {ls.get(\"videoCodecs\", [])}')
    print(f'Audio:      {ls.get(\"audioCodecs\", [])}')
    print(f'Protocol:   {ls.get(\"supportedProtocols\", [])}')

img = t.get('sdm.devices.traits.CameraImage', {}).get('maxImageResolution', {})
if img:
    print(f'Resolution: {img.get(\"width\",\"?\")}x{img.get(\"height\",\"?\")}')

traits = [k.split('.')[-1] for k in t.keys() if 'Info' not in k]
print(f'Traits:     {\", \".join(traits)}')
"
}

cmd_camera_stream() {
  local dtype="$1" label="$2"
  local dev_id
  dev_id=$(get_device_id "$dtype" "$DEVICE_NAME")

  # Check supported protocols
  local data
  data=$(api_get "devices/${dev_id}")
  local protocols
  protocols=$(echo "$data" | python3 -c "
import json, sys
d = json.load(sys.stdin)
ls = d.get('traits', {}).get('sdm.devices.traits.CameraLiveStream', {})
protos = ls.get('supportedProtocols', [])
print(','.join(protos))
")

  if echo "$protocols" | grep -q "RTSP"; then
    echo "Generating RTSP stream for ${label}..."
    local result
    result=$(api_post "devices/${dev_id}:executeCommand" \
      '{"command":"sdm.devices.commands.CameraLiveStream.GenerateRtspStream","params":{}}')
    python3 -c "
import json
r = json.loads('''$(echo "$result" | sed "s/'/\\\\'/g")''')
res = r.get('results', {})
print('=== RTSP Live Stream ===')
urls = res.get('streamUrls', {})
for k,v in urls.items():
    print(f'{k}: {v}')
print(f'Token:   {res.get(\"streamToken\", \"?\")[:40]}...')
print(f'Expires: {res.get(\"expiresAt\", \"?\")}')
print()
print('Play with: ffplay \"<rtspUrl>\"')
print('Note: Stream expires in 5 minutes. Use extend-stream to renew.')
"
  elif echo "$protocols" | grep -q "WEB_RTC"; then
    echo "Device supports WebRTC only (not RTSP)."
    echo ""
    echo "WebRTC requires an SDP offer/answer exchange."
    echo "Use: nest api POST devices/${dev_id}:executeCommand"
    echo "  with command: sdm.devices.commands.CameraLiveStream.GenerateWebRtcStream"
    echo "  and params: {\"offerSdp\": \"<your SDP offer>\"}"
    echo ""
    echo "Tip: Use a WebRTC client to generate the SDP offer."
  else
    echo "Error: Device does not support live streaming." >&2
    exit 1
  fi
}

cmd_extend_stream() {
  local dtype="$1" token="$2"
  local dev_id
  dev_id=$(get_device_id "$dtype" "$DEVICE_NAME")

  local result
  result=$(api_post "devices/${dev_id}:executeCommand" \
    "{\"command\":\"sdm.devices.commands.CameraLiveStream.ExtendRtspStream\",\"params\":{\"streamExtensionToken\":\"${token}\"}}")

  python3 -c "
import json
r = json.loads('''$(echo "$result" | sed "s/'/\\\\'/g")''')
res = r.get('results', {})
urls = res.get('streamUrls', {})
print('=== Stream Extended ===')
for k,v in urls.items():
    print(f'{k}: {v}')
print(f'New token: {res.get(\"streamExtensionToken\", \"?\")[:40]}...')
print(f'Expires:   {res.get(\"expiresAt\", \"?\")}')
"
}

cmd_stop_stream() {
  local dtype="$1" token="$2"
  local dev_id
  dev_id=$(get_device_id "$dtype" "$DEVICE_NAME")

  api_post "devices/${dev_id}:executeCommand" \
    "{\"command\":\"sdm.devices.commands.CameraLiveStream.StopRtspStream\",\"params\":{\"streamExtensionToken\":\"${token}\"}}" > /dev/null

  echo "✅ Stream stopped."
}

cmd_event_image() {
  local dtype="$1" event_id="$2" output="${3:-/tmp/nest-event.jpg}"
  local dev_id
  dev_id=$(get_device_id "$dtype" "$DEVICE_NAME")

  local result
  result=$(api_post "devices/${dev_id}:executeCommand" \
    "{\"command\":\"sdm.devices.commands.CameraEventImage.GenerateImage\",\"params\":{\"eventId\":\"${event_id}\"}}")

  python3 -c "
import json
r = json.loads('''$(echo "$result" | sed "s/'/\\\\'/g")''')
res = r.get('results', {})
url = res.get('url', '')
token = res.get('token', '')
if url:
    print(f'Image URL: {url}')
    print(f'Token:     {token[:40]}...')
    print(f'Download:  curl -o ${output} -H \"Authorization: Basic {token}\" \"{url}\"')
else:
    err = r.get('error', {})
    print(f'Error: {err.get(\"message\", \"Unknown error\")}')
    print('Note: Event images are only available for ~30s after the event.')
"
}

cmd_api() {
  local method="$1" path="$2" body="${3:-}"
  if [ "$method" = "GET" ]; then
    api_get "$path" | python3 -m json.tool
  elif [ "$method" = "POST" ]; then
    api_post "$path" "$body" | python3 -m json.tool
  else
    echo "Error: Unsupported method $method (use GET or POST)" >&2
    exit 1
  fi
}

# --- Main ---
# Parse --name flag from all args first
parse_name_flag "$@"
set -- "${REMAINING_ARGS[@]+"${REMAINING_ARGS[@]}"}"

case "${1:-help}" in
  devices)        cmd_devices ;;
  structures)     cmd_structures ;;
  thermostat)     cmd_thermostat ;;
  set-cool)       cmd_set_cool "${2:?Usage: nest set-cool <°F>}" ;;
  set-heat)       cmd_set_heat "${2:?Usage: nest set-heat <°F>}" ;;
  set-range)      cmd_set_range "${2:?Usage: nest set-range <low°F> <high°F>}" "${3:?Missing high temp}" ;;
  set-mode)       cmd_set_mode "${2:?Usage: nest set-mode <HEAT|COOL|HEATCOOL|OFF>}" ;;
  set-eco)        cmd_set_eco "${2:?Usage: nest set-eco <MANUAL_ECO|OFF>}" ;;
  fan-on)         cmd_fan_on "${2:-900}" ;;
  fan-off)        cmd_fan_off ;;
  doorbell)       cmd_camera_info "DOORBELL" "Doorbell" ;;
  display)        cmd_camera_info "DISPLAY" "Display" ;;
  stream-doorbell)  cmd_camera_stream "DOORBELL" "Doorbell" ;;
  stream-display)   cmd_camera_stream "DISPLAY" "Display" ;;
  extend-stream)  cmd_extend_stream "${2:?Device type}" "${3:?Stream extension token}" ;;
  stop-stream)    cmd_stop_stream "${2:?Device type}" "${3:?Stream extension token}" ;;
  event-image)    cmd_event_image "${2:?Device type (DOORBELL|DISPLAY)}" "${3:?Event ID}" "${4:-/tmp/nest-event.jpg}" ;;
  auth-status)    cmd_auth_status ;;
  api)            cmd_api "${2:?Method}" "${3:?Path}" "${4:-}" ;;
  help|*)
    cat <<'EOF'
Nest SDM CLI — Control Nest devices via Google SDM API

USAGE:
  nest <command> [args] [--name <filter>]

OPTIONS:
  --name <filter>            Target device by name or room (case-insensitive, substring match)
                             Without --name, defaults to first device of that type

THERMOSTAT:
  thermostat                 Current thermostat status (with fan timer)
  set-cool <°F>              Set COOL mode at temperature
  set-heat <°F>              Set HEAT mode at temperature
  set-range <lo°F> <hi°F>    Set HEATCOOL range
  set-mode <MODE>            HEAT | COOL | HEATCOOL | OFF
  set-eco <MODE>             MANUAL_ECO | OFF
  fan-on [seconds]           Fan on (default: 900s / 15min)
  fan-off                    Fan off

CAMERAS:
  doorbell                   Doorbell camera info
  display                    Kitchen display info
  stream-doorbell            Generate RTSP/WebRTC stream for doorbell
  stream-display             Generate RTSP/WebRTC stream for display
  extend-stream <type> <token>  Extend an active RTSP stream (5min window)
  stop-stream <type> <token>    Stop an active RTSP stream
  event-image <type> <eventId> [output]  Get image from camera event

GENERAL:
  devices                    List all devices
  structures                 List structures, rooms & devices
  auth-status                Check token age & expiry warning
  api <GET|POST> <path> [body]  Raw SDM API call

EXAMPLES:
  nest thermostat                        # Check first thermostat
  nest thermostat --name "Bedroom"       # Check specific thermostat by name/room
  nest set-cool 72 --name "Entryway"     # Cool specific thermostat to 72°F
  nest set-range 68 75                   # Heat/cool range (first thermostat)
  nest doorbell --name "Front"           # Specific doorbell
  nest stream-doorbell                   # Start doorbell camera stream
  nest auth-status                       # Check token expiry
  nest api GET devices                   # Raw device list
EOF
    ;;
esac
