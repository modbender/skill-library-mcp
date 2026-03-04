#!/bin/bash
# videochat-withme setup — fully automatic or interactive
# Usage: bash setup.sh [--agent-name "Name"] [--user-name "Name"] [--port 8766] [--auto]
set -e

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPTS_DIR="$SKILL_DIR/scripts"
CERTS_DIR="$SKILL_DIR/certs"
PORT=8766
AGENT_NAME=""
USER_NAME=""
AUTO=false
PLIST_LABEL="com.openclaw.videochat-withme"

# Parse args
while [[ $# -gt 0 ]]; do
  case $1 in
    --agent-name) AGENT_NAME="$2"; shift 2 ;;
    --user-name)  USER_NAME="$2"; shift 2 ;;
    --port)       PORT="$2"; shift 2 ;;
    --auto)       AUTO=true; shift ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

# Defaults for auto mode
[ -z "$AGENT_NAME" ] && AGENT_NAME="${AGENT_NAME:-AI Assistant}"
[ -z "$USER_NAME" ]  && USER_NAME="${USER_NAME:-User}"

echo "🎥 videochat-withme setup"
echo "====================="

# 1. Check dependencies
echo ""
echo "📦 Checking dependencies..."
MISSING=""
command -v python3 >/dev/null 2>&1 || MISSING="$MISSING python3"
command -v ffmpeg  >/dev/null 2>&1 || MISSING="$MISSING ffmpeg"

if [ -n "$MISSING" ]; then
  if command -v brew >/dev/null 2>&1; then
    echo "   Installing:$MISSING"
    brew install $MISSING
  else
    echo "❌ Missing:$MISSING"
    echo "   Install with: brew install$MISSING"
    exit 1
  fi
fi
echo "   ✅ python3 $(python3 --version 2>&1 | awk '{print $2}')"
echo "   ✅ ffmpeg"

# 2. Install Python deps
echo ""
echo "📦 Installing Python dependencies..."
pip3 install --break-system-packages -q fastapi uvicorn python-multipart httpx edge-tts 2>/dev/null || \
  pip3 install -q fastapi uvicorn python-multipart httpx edge-tts
echo "   ✅ Done"

# 3. Check Groq API key
echo ""
echo "🔑 Checking Groq API key..."
GROQ_KEY="${GROQ_API_KEY:-}"
if [ -z "$GROQ_KEY" ] && [ -f "$HOME/.openclaw/secrets/groq_api_key.txt" ]; then
  GROQ_KEY=$(cat "$HOME/.openclaw/secrets/groq_api_key.txt" | tr -d '[:space:]')
fi
if [ -z "$GROQ_KEY" ]; then
  if [ "$AUTO" = true ]; then
    echo "   ⚠️  No Groq API key found. STT won't work."
    echo "   Set GROQ_API_KEY or put it in ~/.openclaw/secrets/groq_api_key.txt"
  else
    echo "   ⚠️  Groq API key not found."
    read -p "   Paste your Groq API key (or Enter to skip): " INPUT_KEY
    if [ -n "$INPUT_KEY" ]; then
      mkdir -p "$HOME/.openclaw/secrets"
      echo "$INPUT_KEY" > "$HOME/.openclaw/secrets/groq_api_key.txt"
      echo "   ✅ Saved"
    fi
  fi
else
  echo "   ✅ Found"
fi

# 4. Check chatCompletions
echo ""
echo "🔧 Checking chatCompletions..."
CONFIG="$HOME/.openclaw/openclaw.json"
if [ -f "$CONFIG" ]; then
  if python3 -c "
import json, sys
c = json.load(open('$CONFIG'))
enabled = c.get('gateway',{}).get('http',{}).get('endpoints',{}).get('chatCompletions',{}).get('enabled', False)
sys.exit(0 if enabled else 1)
" 2>/dev/null; then
    echo "   ✅ Enabled"
  else
    echo "   ⚠️  chatCompletions not enabled."
    if [ "$AUTO" = true ]; then
      echo "   Agent should enable it via gateway config."
    else
      echo '   Add to ~/.openclaw/openclaw.json: {"gateway":{"http":{"endpoints":{"chatCompletions":{"enabled":true}}}}}'
    fi
  fi
fi

# 5. Generate SSL certs
echo ""
echo "🔒 Setting up SSL..."
if [ -d "$CERTS_DIR" ] && ls "$CERTS_DIR"/*.pem >/dev/null 2>&1; then
  echo "   ✅ Certs exist"
else
  LOCAL_IP=$(python3 -c "import socket; s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM); s.connect(('8.8.8.8',80)); print(s.getsockname()[0]); s.close()" 2>/dev/null || echo "")

  if ! command -v mkcert >/dev/null 2>&1; then
    if command -v brew >/dev/null 2>&1; then
      echo "   Installing mkcert..."
      brew install mkcert 2>/dev/null
    fi
  fi

  if command -v mkcert >/dev/null 2>&1; then
    mkdir -p "$CERTS_DIR"
    CERT_NAMES="localhost 127.0.0.1"
    [ -n "$LOCAL_IP" ] && CERT_NAMES="$LOCAL_IP $CERT_NAMES"
    (cd "$CERTS_DIR" && mkcert $CERT_NAMES 2>/dev/null)
    echo "   ✅ SSL certs generated"
  else
    echo "   ⚠️  mkcert not available. Mobile access won't have mic/camera."
  fi
fi

# 6. Prompt for names (interactive only)
if [ "$AUTO" = false ]; then
  read -p "🤖 Agent display name [$AGENT_NAME]: " INPUT_NAME
  AGENT_NAME="${INPUT_NAME:-$AGENT_NAME}"
  read -p "👤 Your display name [$USER_NAME]: " INPUT_USER
  USER_NAME="${INPUT_USER:-$USER_NAME}"
fi

# 7. Install launchd service
echo ""
echo "🚀 Installing launchd service..."

SSL_CERT=""
SSL_KEY=""
if [ -d "$CERTS_DIR" ]; then
  for f in "$CERTS_DIR"/*.pem; do
    case "$f" in
      *-key.pem) SSL_KEY="$f" ;;
      *.pem)     SSL_CERT="$f" ;;
    esac
  done
fi

PLIST="$HOME/Library/LaunchAgents/${PLIST_LABEL}.plist"
launchctl stop "$PLIST_LABEL" 2>/dev/null || true
launchctl unload "$PLIST" 2>/dev/null || true

cat > "$PLIST" << PLISTEOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>${PLIST_LABEL}</string>
    <key>ProgramArguments</key>
    <array>
        <string>$(which python3)</string>
        <string>${SCRIPTS_DIR}/server.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>${SKILL_DIR}</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
    </dict>
    <key>ThrottleInterval</key>
    <integer>5</integer>
    <key>StandardOutPath</key>
    <string>/tmp/videochat-withme.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/videochat-withme.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>AGENT_NAME</key>
        <string>${AGENT_NAME}</string>
        <key>USER_NAME</key>
        <string>${USER_NAME}</string>
        <key>PORT</key>
        <string>${PORT}</string>
        <key>PATH</key>
        <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
PLISTEOF

if [ -n "$SSL_CERT" ] && [ -n "$SSL_KEY" ]; then
cat >> "$PLIST" << SSLEOF
        <key>SSL_CERT</key>
        <string>${SSL_CERT}</string>
        <key>SSL_KEY</key>
        <string>${SSL_KEY}</string>
SSLEOF
fi

cat >> "$PLIST" << ENDEOF
    </dict>
</dict>
</plist>
ENDEOF

launchctl load "$PLIST"
sleep 3

# 8. Verify
echo ""
PROTO="https"
RESP=$(curl -sk "https://localhost:$PORT/api/config" 2>/dev/null || echo "")
if [ -z "$RESP" ]; then
  PROTO="http"
  RESP=$(curl -s "http://localhost:$PORT/api/config" 2>/dev/null || echo "")
fi

LOCAL_IP=$(python3 -c "import socket; s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM); s.connect(('8.8.8.8',80)); print(s.getsockname()[0]); s.close()" 2>/dev/null || echo "localhost")

if echo "$RESP" | grep -q "agent_name"; then
  echo "✅ Setup complete!"
  echo ""
  echo "🖥  Desktop: ${PROTO}://localhost:${PORT}"
  echo "📱  Mobile:  ${PROTO}://${LOCAL_IP}:${PORT}"
  echo "📋  Logs:    tail -f /tmp/videochat-withme.log"
else
  echo "❌ Service not responding. Check: tail /tmp/videochat-withme.log"
  exit 1
fi
