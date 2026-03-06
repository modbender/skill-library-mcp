#!/usr/bin/env bash
# Generate a QR code for Clawket to scan and connect to the local Gateway.
# Requires: qrencode (brew install qrencode / apt install qrencode / choco install qrencode)
# Works on: macOS, Linux, Windows (Git Bash / WSL)
set -euo pipefail

CONFIG="$HOME/.openclaw/openclaw.json"
OUT_DIR="$HOME/.openclaw/media"
OUT_FILE="$OUT_DIR/clawket-qr.png"

mkdir -p "$OUT_DIR"

# --- Read config ---
if [[ ! -f "$CONFIG" ]]; then
  echo "Error: Config not found at $CONFIG" >&2
  exit 1
fi

TOKEN=$(python3 -c "
import json, sys
try:
    c = json.load(open('$CONFIG'))
    print(c['gateway']['auth']['token'])
except Exception as e:
    print(f'Error: {e}', file=sys.stderr)
    sys.exit(1)
")

PORT=$(python3 -c "
import json
c = json.load(open('$CONFIG'))
print(c.get('gateway', {}).get('port', 18789))
")

# --- Detect LAN IP (cross-platform) ---
detect_lan_ip() {
  local ip=""
  case "$(uname -s)" in
    Darwin)
      # macOS: scan all interfaces via ifconfig
      ip=$(/sbin/ifconfig 2>/dev/null \
        | grep "inet " \
        | grep -v "127.0.0.1" \
        | awk '{print $2}' \
        | grep -E "^(192\.168\.|10\.|172\.(1[6-9]|2[0-9]|3[01])\.)" \
        | head -1)
      ;;
    Linux)
      # Linux: try ip command first, fallback to hostname -I
      if command -v ip &>/dev/null; then
        ip=$(ip -4 route get 1.1.1.1 2>/dev/null | awk '{print $7; exit}')
      fi
      if [[ -z "$ip" ]] && command -v hostname &>/dev/null; then
        ip=$(hostname -I 2>/dev/null | awk '{print $1}')
      fi
      ;;
    MINGW*|MSYS*|CYGWIN*)
      # Windows (Git Bash / MSYS2 / Cygwin)
      if command -v powershell.exe &>/dev/null; then
        ip=$(powershell.exe -NoProfile -Command "
          (Get-NetIPAddress -AddressFamily IPv4 |
           Where-Object { \$_.IPAddress -notmatch '^127\.' -and \$_.PrefixOrigin -ne 'WellKnown' } |
           Select-Object -First 1).IPAddress
        " 2>/dev/null | tr -d '\r')
      elif command -v ipconfig.exe &>/dev/null; then
        ip=$(ipconfig.exe 2>/dev/null \
          | grep -i "IPv4" \
          | grep -oE "[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+" \
          | grep -v "^127\." \
          | head -1)
      fi
      ;;
  esac
  echo "${ip:-127.0.0.1}"
}

LAN_IP=$(detect_lan_ip)
if [[ "$LAN_IP" == "127.0.0.1" ]]; then
  echo "Warning: Could not detect LAN IP, using $LAN_IP" >&2
fi

# --- Build payload ---
PAYLOAD=$(python3 -c "
import json
print(json.dumps({
    'host': '$LAN_IP',
    'port': int('$PORT'),
    'token': '$TOKEN',
    'tls': False
}, separators=(',', ':')))
")

echo "Gateway: ws://$LAN_IP:$PORT"
echo "Payload: $PAYLOAD"
echo ""

# --- Generate QR ---
if ! command -v qrencode &>/dev/null; then
  echo "Error: qrencode not found." >&2
  echo "  macOS:   brew install qrencode" >&2
  echo "  Linux:   sudo apt install qrencode" >&2
  echo "  Windows: choco install qrencode" >&2
  exit 1
fi

# PNG file
qrencode -o "$OUT_FILE" -s 10 -m 2 -l M "$PAYLOAD"
echo "QR code saved to: $OUT_FILE"
echo ""

# ASCII to terminal
qrencode -t UTF8 -m 1 "$PAYLOAD"
