#!/usr/bin/env bash
# ClawTime Install Script
# Sets up ClawTime with Cloudflare tunnel for passkey (Face ID) access
# Usage: bash install.sh

set -e

REPO_URL="https://github.com/youngkent/clawtime.git"
INSTALL_DIR="$HOME/Projects/clawtime"
DATA_DIR="$HOME/.clawtime"

echo "=== ClawTime Installer ==="
echo ""

# ── 1. Prerequisites ──────────────────────────────────────────────────────────
echo "→ Checking prerequisites..."
MISSING=0

if ! command -v node &>/dev/null; then
  echo "  ✗ Node.js not found. Install: brew install node"
  MISSING=1
fi

if ! command -v git &>/dev/null; then
  echo "  ✗ git not found. Install: brew install git"
  MISSING=1
fi

if ! command -v cloudflared &>/dev/null; then
  echo "  ✗ cloudflared not found. Install: brew install cloudflared"
  MISSING=1
fi

if ! command -v openclaw &>/dev/null; then
  echo "  ✗ openclaw CLI not found. Is OpenClaw installed?"
  MISSING=1
fi

if [ $MISSING -ne 0 ]; then
  echo ""
  echo "Install missing prerequisites and re-run."
  exit 1
fi
echo "✓ Prerequisites OK"
echo ""

# ── 2. Cloudflare domain setup ────────────────────────────────────────────────
echo "→ Cloudflare Tunnel setup"
echo "  You need: a domain with DNS managed by Cloudflare."
echo "  If you already have a tunnel configured, you can skip this step."
echo ""
read -r -p "  Your public URL (e.g. https://portal.yourdomain.com): " PUBLIC_URL

if [ -z "$PUBLIC_URL" ]; then
  echo "✗ PUBLIC_URL is required."
  exit 1
fi

# Check if tunnel exists
TUNNEL_EXISTS=$(cloudflared tunnel list 2>/dev/null | grep -c "clawtime" || true)
if [ "$TUNNEL_EXISTS" -eq 0 ]; then
  echo ""
  echo "  No 'clawtime' tunnel found. Setting up..."
  cloudflared tunnel login
  cloudflared tunnel create clawtime

  TUNNEL_ID=$(cloudflared tunnel list 2>/dev/null | grep "clawtime" | awk '{print $1}')
  CLOUDFLARED_CONFIG="$HOME/.cloudflared/config.yml"

  echo "  Writing ~/.cloudflared/config.yml..."
  cat > "$CLOUDFLARED_CONFIG" <<CFCONFIG
tunnel: clawtime
credentials-file: $HOME/.cloudflared/$TUNNEL_ID.json

ingress:
  - hostname: $(echo "$PUBLIC_URL" | sed 's|https://||')
    service: http://localhost:3000
  - service: http_status:404
CFCONFIG

  echo ""
  echo "  ⚠️  ACTION REQUIRED: Add this CNAME in your Cloudflare DNS dashboard:"
  echo "      Name:   portal (or whatever subdomain you chose)"
  echo "      Target: $TUNNEL_ID.cfargotunnel.com"
  echo "      Proxy:  ✅ Proxied (orange cloud)"
  echo ""
  read -r -p "  Press Enter once you've added the DNS record..."
else
  echo "  ✓ 'clawtime' tunnel already exists"
fi
echo ""

# ── 3. Clone / update repo ────────────────────────────────────────────────────
if [ -d "$INSTALL_DIR/.git" ]; then
  echo "→ Repo found at $INSTALL_DIR — pulling latest..."
  cd "$INSTALL_DIR"
  git pull --ff-only 2>/dev/null || echo "  (up to date or local changes present)"
else
  echo "→ Cloning ClawTime to $INSTALL_DIR..."
  mkdir -p "$HOME/Projects"
  git clone "$REPO_URL" "$INSTALL_DIR"
fi

# ── 4. Install npm dependencies ───────────────────────────────────────────────
echo "→ Installing npm dependencies..."
cd "$INSTALL_DIR"
npm install --legacy-peer-deps --silent
echo "✓ Dependencies installed"
echo ""

# ── 5. Create data directory ──────────────────────────────────────────────────
mkdir -p "$DATA_DIR"

# ── 6. Get gateway token ──────────────────────────────────────────────────────
echo "→ Getting OpenClaw gateway token..."
GATEWAY_TOKEN=$(cat ~/.openclaw/openclaw.json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('gateway',{}).get('token',''))" 2>/dev/null)

if [ -z "$GATEWAY_TOKEN" ]; then
  # Try keychain
  GATEWAY_TOKEN=$(security find-generic-password -s "openclaw-gateway-token" -a "$(whoami)" -w 2>/dev/null || true)
fi

if [ -z "$GATEWAY_TOKEN" ]; then
  echo "  Could not auto-detect token."
  read -r -p "  Enter your OpenClaw gateway token: " GATEWAY_TOKEN
fi

[ -z "$GATEWAY_TOKEN" ] && { echo "✗ Gateway token required."; exit 1; }
echo "✓ Gateway token found"
echo ""

# ── 7. Setup token ────────────────────────────────────────────────────────────
read -r -p "→ Enter a SETUP_TOKEN (passphrase to protect passkey registration): " SETUP_TOKEN
if [ -z "$SETUP_TOKEN" ]; then
  SETUP_TOKEN=$(python3 -c "import secrets; print(secrets.token_hex(16))")
  echo "  (generated: $SETUP_TOKEN — save this!)"
fi
echo ""

# ── 8. Customize bot ─────────────────────────────────────────────────────────
read -r -p "→ Bot name (press Enter for 'Beware'): " BOT_NAME
BOT_NAME="${BOT_NAME:-Beware}"

read -r -p "→ Bot emoji (press Enter for '🌀'): " BOT_EMOJI
BOT_EMOJI="${BOT_EMOJI:-🌀}"
echo ""

# ── 9. Configure OpenClaw gateway ─────────────────────────────────────────────
echo "→ Configuring gateway to allow ClawTime origin ($PUBLIC_URL)..."
openclaw config patch "{\"gateway\":{\"controlUi\":{\"allowedOrigins\":[\"$PUBLIC_URL\"]}}}" 2>/dev/null && \
  echo "✓ Gateway config updated" || \
  echo "  ⚠️  Config patch failed — add manually to ~/.openclaw/openclaw.json"

echo "→ Restarting gateway..."
openclaw gateway restart 2>/dev/null && echo "✓ Gateway restarted" || echo "  ⚠️  Restart failed — run: openclaw gateway restart"
sleep 2
echo ""

# ── 10. Detect TTS ────────────────────────────────────────────────────────────
TTS_LINE=""
if command -v ffmpeg &>/dev/null && python3 -c "import piper" &>/dev/null 2>&1; then
  VOICES_DIR="$HOME/Documents/resources/piper-voices"
  if [ -d "$VOICES_DIR" ]; then
    TTS_LINE="TTS_COMMAND='python3 -m piper --data-dir $VOICES_DIR -m en_US-kusal-medium -f /tmp/clawtime-tts-tmp.wav -- {{TEXT}} && ffmpeg -y -loglevel error -i /tmp/clawtime-tts-tmp.wav {{OUTPUT}}' \\"
    echo "✓ Piper TTS detected — voice will be enabled"
  fi
fi

# ── 11. Store tokens in Keychain ──────────────────────────────────────────────
echo "→ Storing tokens securely in macOS Keychain..."
security add-generic-password -U -s "clawtime-gateway-token" -a "$(whoami)" -w "$GATEWAY_TOKEN" 2>/dev/null && \
  echo "  ✓ Gateway token stored in Keychain" || \
  echo "  ⚠️  Could not store gateway token in Keychain"
security add-generic-password -U -s "clawtime-setup-token" -a "$(whoami)" -w "$SETUP_TOKEN" 2>/dev/null && \
  echo "  ✓ Setup token stored in Keychain" || \
  echo "  ⚠️  Could not store setup token in Keychain"
echo ""

# ── 12. Write start scripts ──────────────────────────────────────────────────
START_SERVER="$INSTALL_DIR/start-server.sh"
START_TUNNEL="$INSTALL_DIR/start-tunnel.sh"
START_ALL="$INSTALL_DIR/start.sh"

cat > "$START_SERVER" <<'STARTSCRIPT'
#!/usr/bin/env bash
# ClawTime server start script — tokens loaded from Keychain
cd "$(dirname "$0")"
GATEWAY_TOKEN=$(security find-generic-password -s "clawtime-gateway-token" -a "$(whoami)" -w 2>/dev/null)
SETUP_TOKEN=$(security find-generic-password -s "clawtime-setup-token" -a "$(whoami)" -w 2>/dev/null)

if [ -z "$GATEWAY_TOKEN" ]; then
  echo "✗ Gateway token not found in Keychain. Run: security add-generic-password -s clawtime-gateway-token -a \$(whoami) -w YOUR_TOKEN"
  exit 1
fi

STARTSCRIPT

# Append the non-secret config (these are safe to store in the script)
cat >> "$START_SERVER" <<STARTSCRIPT
PUBLIC_URL=$PUBLIC_URL \\
GATEWAY_TOKEN="\$GATEWAY_TOKEN" \\
SETUP_TOKEN="\$SETUP_TOKEN" \\
BOT_NAME="$BOT_NAME" \\
BOT_EMOJI="$BOT_EMOJI" \\
${TTS_LINE}
node server.js
STARTSCRIPT

cat > "$START_TUNNEL" <<TUNNELSCRIPT
#!/usr/bin/env bash
# Cloudflare tunnel start script
cloudflared tunnel run clawtime
TUNNELSCRIPT

cat > "$START_ALL" <<'ALLSCRIPT_HEAD'
#!/usr/bin/env bash
# Start both ClawTime and the Cloudflare tunnel in background
# Tokens loaded securely from macOS Keychain

GATEWAY_TOKEN=$(security find-generic-password -s "clawtime-gateway-token" -a "$(whoami)" -w 2>/dev/null)
SETUP_TOKEN=$(security find-generic-password -s "clawtime-setup-token" -a "$(whoami)" -w 2>/dev/null)

if [ -z "$GATEWAY_TOKEN" ]; then
  echo "✗ Gateway token not found in Keychain."
  exit 1
fi

echo "Starting ClawTime server..."
ALLSCRIPT_HEAD

cat >> "$START_ALL" <<ALLSCRIPT_BODY
PUBLIC_URL=$PUBLIC_URL \\
GATEWAY_TOKEN="\$GATEWAY_TOKEN" \\
SETUP_TOKEN="\$SETUP_TOKEN" \\
BOT_NAME="$BOT_NAME" \\
BOT_EMOJI="$BOT_EMOJI" \\
${TTS_LINE}
node "$INSTALL_DIR/server.js" &>/tmp/clawtime.log &
echo "  PID: \$!"

echo "Starting Cloudflare tunnel..."
cloudflared tunnel run clawtime &>/tmp/cloudflared.log &
echo "  PID: \$!"

echo ""
echo "✅ Both running in background"
echo "   Server logs: tail -f /tmp/clawtime.log"
echo "   Tunnel logs: tail -f /tmp/cloudflared.log"
ALLSCRIPT_BODY

chmod +x "$START_SERVER" "$START_TUNNEL" "$START_ALL"

# ── 12. Done ──────────────────────────────────────────────────────────────────
echo ""
echo "════════════════════════════════════════"
echo "✅  ClawTime installed!"
echo ""
echo "  Start both:       bash $START_ALL"
echo "  Start server:     bash $START_SERVER"
echo "  Start tunnel:     bash $START_TUNNEL"
echo ""
echo "  Register passkey: $PUBLIC_URL/?setup=$SETUP_TOKEN"
echo "  Chat UI:          $PUBLIC_URL"
echo ""
echo "  ⚠️  Use Safari (not Chrome) for passkey registration."
echo "  ⚠️  Do NOT use private/incognito mode."
echo "════════════════════════════════════════"
