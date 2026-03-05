#!/bin/bash
# Synology Surveillance Station CLI Helper
# Interagiert mit der Surveillance Station Web API

SYNO_HOST="${SYNOLOGY_HOST:-192.168.1.100}"
SYNO_PORT="${SYNOLOGY_PORT:-5000}"
SYNO_USER="${SYNOLOGY_USER:-admin}"
SYNO_PASS="${SYNOLOGY_PASS:-}"
SYNO_HTTPS="${SYNOLOGY_HTTPS:-false}"

COOKIE_FILE="/tmp/syno_session_$$.cookie"
BASE_URL="http${SYNO_HTTPS:+s}://${SYNO_HOST}:${SYNO_PORT}"

# Cleanup beim Beenden
trap 'rm -f "$COOKIE_FILE"' EXIT

# Hilfe anzeigen
show_help() {
    cat << EOF
Usage: $0 <command> [args...]

Commands:
  login                      - Login und Session erstellen
  logout                     - Session beenden
  cameras                    - Liste aller Kameras anzeigen
  snapshot <camera-id>       - Snapshot einer Kamera abrufen
  record <camera-id> [start|stop] - Aufnahme starten/stoppen
  events [limit]             - Letzte Ereignisse anzeigen (default: 10)
  stream <camera-id>         - Live-Stream URL anzeigen
  ptz <camera-id> <direction>  - PTZ Bewegung (left|right|up|down|zoomin|zoomout)
  preset <camera-id> <num>    - PTZ Voreinstellung anfahren

Environment Variables:
  SYNOLOGY_HOST   - NAS IP/Hostname (default: 192.168.1.100)
  SYNOLOGY_PORT   - NAS Port (default: 5000, HTTPS: 5001)
  SYNOLOGY_USER   - Username (default: admin)
  SYNOLOGY_PASS   - Passwort
  SYNOLOGY_HTTPS  - HTTPS verwenden (default: false)

Examples:
  $0 cameras
  $0 snapshot 1
  $0 record 1 start
  $0 events 20
  $0 ptz 1 left
EOF
}

# API Request mit Session-Handling
api_request() {
    local endpoint=$1
    local params=$2
    
    curl -s -b "$COOKIE_FILE" -c "$COOKIE_FILE" \
        "${BASE_URL}/webapi/${endpoint}?${params}"
}

# Einloggen
syno_login() {
    if [[ -z "$SYNO_PASS" ]]; then
        echo "Error: SYNOLOGY_PASS nicht gesetzt"
        exit 1
    fi
    
    local response=$(curl -s -c "$COOKIE_FILE" \
        "${BASE_URL}/webapi/auth.cgi?api=SYNO.API.Auth&method=login&version=3&account=${SYNO_USER}&passwd=${SYNO_PASS}&session=SurveillanceStation&format=cookie")
    
    if echo "$response" | grep -q '"success":true'; then
        echo "Login erfolgreich"
        return 0
    else
        echo "Login fehlgeschlagen: $response"
        return 1
    fi
}

# Ausloggen
syno_logout() {
    api_request "auth.cgi" "api=SYNO.API.Auth&method=logout&version=1&session=SurveillanceStation"
    echo "Logout durchgeführt"
}

# Kameraliste abrufen
syno_cameras() {
    api_request "entry.cgi" "api=SYNO.SurveillanceStation.Camera&method=List&version=1&_=$(date +%s)" | jq -r '.data.cameras[] | "ID: \(.id), Name: \(.name), Status: \(.status)"' 2>/dev/null || echo "Fehler beim Abrufen der Kameras"
}

# Snapshot erstellen
syno_snapshot() {
    local camera_id=$1
    if [[ -z "$camera_id" ]]; then
        echo "Usage: $0 snapshot <camera-id>"
        exit 1
    fi
    
    local timestamp=$(date +%s)
    local output="syno_snapshot_${camera_id}_${timestamp}.jpg"
    
    curl -s -b "$COOKIE_FILE" \
        "${BASE_URL}/webapi/entry.cgi?api=SYNO.SurveillanceStation.Camera&method=GetSnapshot&version=1&cameraId=${camera_id}&_=${timestamp}" \
        -o "$output"
    
    if [[ -f "$output" && -s "$output" ]]; then
        echo "Snapshot gespeichert: $output"
    else
        rm -f "$output"
        echo "Fehler beim Erstellen des Snapshots"
    fi
}

# Aufnahme steuern
syno_record() {
    local camera_id=$1
    local action=$2
    
    if [[ -z "$camera_id" || -z "$action" ]]; then
        echo "Usage: $0 record <camera-id> [start|stop]"
        exit 1
    fi
    
    local method=""
    case "$action" in
        start) method="Record" ;;
        stop) method="Stop" ;;
        *) echo "Ungültige Aktion: $action (start|stop)"; exit 1 ;;
    esac
    
    api_request "entry.cgi" "api=SYNO.SurveillanceStation.Recording&method=${method}&version=1&cameraId=${camera_id}"
}

# Ereignisse abrufen
syno_events() {
    local limit=${1:-10}
    api_request "entry.cgi" "api=SYNO.SurveillanceStation.Event&method=List&version=1&limit=${limit}" | jq -r '.data.events[] | "\(.timestamp): \(.camera_name) - \(.reason)"' 2>/dev/null || echo "Keine Ereignisse gefunden"
}

# Stream URL anzeigen
syno_stream() {
    local camera_id=$1
    if [[ -z "$camera_id" ]]; then
        echo "Usage: $0 stream <camera-id>"
        exit 1
    fi
    
    echo "Live-Stream URL:"
    echo "${BASE_URL}/webapi/entry.cgi?api=SYNO.SurveillanceStation.Streaming&method=LiveStream&version=1&cameraId=${camera_id}&format=mjpeg"
}

# PTZ Steuerung
syno_ptz() {
    local camera_id=$1
    local direction=$2
    
    if [[ -z "$camera_id" || -z "$direction" ]]; then
        echo "Usage: $0 ptz <camera-id> <direction>"
        echo "Directions: left, right, up, down, zoomin, zoomout"
        exit 1
    fi
    
    api_request "entry.cgi" "api=SYNO.SurveillanceStation.PTZ&method=Move&version=1&cameraId=${camera_id}&direction=${direction}&speed=3"
}

# PTZ Preset
syno_preset() {
    local camera_id=$1
    local position=$2
    
    if [[ -z "$camera_id" || -z "$position" ]]; then
        echo "Usage: $0 preset <camera-id> <preset-number>"
        exit 1
    fi
    
    api_request "entry.cgi" "api=SYNO.SurveillanceStation.PTZ&method=GoPreset&version=1&cameraId=${camera_id}&position=${position}"
}

# Main
CMD=$1
shift

case "$CMD" in
    login)
        syno_login
        ;;
    logout)
        syno_logout
        ;;
    cameras)
        syno_cameras
        ;;
    snapshot)
        syno_snapshot "$1"
        ;;
    record)
        syno_record "$1" "$2"
        ;;
    events)
        syno_events "$1"
        ;;
    stream)
        syno_stream "$1"
        ;;
    ptz)
        syno_ptz "$1" "$2"
        ;;
    preset)
        syno_preset "$1" "$2"
        ;;
    *)
        show_help
        exit 1
        ;;
esac
