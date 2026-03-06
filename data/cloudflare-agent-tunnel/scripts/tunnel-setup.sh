#!/bin/bash
# tunnel-setup.sh — Add a Cloudflare Tunnel for one OpenClaw agent
#
# Usage:
#   ./tunnel-setup.sh --agent koda --port 18789 [--domain koda.yourdomain.com]
#
# Requires cloudflared installed and authenticated (cloudflared login) before use.
# Without --domain: creates a quick tunnel (random URL, no account needed).
# With --domain: creates a named tunnel (permanent URL, requires Cloudflare account).

set -euo pipefail

AGENT=""
PORT=""
DOMAIN=""
QUICK=false

while [[ $# -gt 0 ]]; do
  case $1 in
    --agent)   AGENT="$2";  shift 2 ;;
    --port)    PORT="$2";   shift 2 ;;
    --domain)  DOMAIN="$2"; shift 2 ;;
    --quick)   QUICK=true;  shift ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

[[ -z "$AGENT" ]] && { echo "Error: --agent is required"; exit 1; }
[[ -z "$PORT"  ]] && { echo "Error: --port is required";  exit 1; }

# Install cloudflared if missing
if ! command -v cloudflared &>/dev/null; then
  echo "Installing cloudflared..."
  curl -fsSL https://pkg.cloudflare.com/cloudflare-main.gpg | tee /usr/share/keyrings/cloudflare-main.gpg >/dev/null
  echo "deb [signed-by=/usr/share/keyrings/cloudflare-main.gpg] https://pkg.cloudflare.com/cloudflared any main" \
    | tee /etc/apt/sources.list.d/cloudflared.list
  apt-get update -qq && apt-get install -y cloudflared
  echo "cloudflared installed: $(cloudflared --version)"
fi

# ─── Quick Tunnel (no account, temporary URL) ────────────────────────────────
if [[ "$QUICK" == "true" || -z "$DOMAIN" ]]; then
  echo ""
  echo "Starting quick tunnel for ${AGENT} on port ${PORT}..."
  echo "(URL is temporary and resets on restart — use named tunnels for production)"
  echo ""
  exec cloudflared tunnel --url "http://localhost:${PORT}" --no-autoupdate
fi

# ─── Named Tunnel (permanent URL, requires Cloudflare account + domain) ──────

TUNNEL_NAME="openclaw-${AGENT}"
CONFIG_DIR="/etc/cloudflared"
CONFIG_FILE="${CONFIG_DIR}/${TUNNEL_NAME}.yml"
CREDS_DIR="/root/.cloudflared"

mkdir -p "$CONFIG_DIR" "$CREDS_DIR"

# Create tunnel (idempotent — skip if already exists)
if cloudflared tunnel list 2>/dev/null | grep -q "$TUNNEL_NAME"; then
  echo "Tunnel '${TUNNEL_NAME}' already exists — reusing it"
  TUNNEL_UUID=$(cloudflared tunnel list 2>/dev/null | grep "$TUNNEL_NAME" | awk '{print $1}')
else
  echo "Creating tunnel '${TUNNEL_NAME}'..."
  TUNNEL_UUID=$(cloudflared tunnel create "$TUNNEL_NAME" 2>&1 | grep -oP '[0-9a-f-]{36}' | head -1)
  echo "Created tunnel UUID: ${TUNNEL_UUID}"
fi

CREDS_FILE="${CREDS_DIR}/${TUNNEL_UUID}.json"

# Write config file
cat > "$CONFIG_FILE" << EOF
tunnel: ${TUNNEL_UUID}
credentials-file: ${CREDS_FILE}

ingress:
  - hostname: ${DOMAIN}
    service: http://localhost:${PORT}
  - service: http_status:404
EOF

echo "Config written: ${CONFIG_FILE}"

# Route DNS (adds CNAME record in Cloudflare dashboard)
echo "Routing DNS: ${DOMAIN} → ${TUNNEL_NAME}..."
cloudflared tunnel route dns "$TUNNEL_NAME" "$DOMAIN" || {
  echo ""
  echo "⚠ DNS routing failed — you may need to add this CNAME manually in Cloudflare:"
  echo "   Name: $(echo $DOMAIN | cut -d. -f1)"
  echo "   Target: ${TUNNEL_UUID}.cfargotunnel.com"
  echo "   Proxy: ON (orange cloud)"
}

# Create systemd service
SERVICE_NAME="cloudflared-${AGENT}"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Cloudflare Tunnel for OpenClaw agent: ${AGENT}
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/bin/cloudflared tunnel --no-autoupdate --config ${CONFIG_FILE} run
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
systemctl restart "$SERVICE_NAME"
sleep 3
systemctl status "$SERVICE_NAME" --no-pager | head -10

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ Tunnel active for agent: ${AGENT}"
echo ""
echo "  URL:     https://${DOMAIN}"
echo "  Port:    localhost:${PORT}"
echo "  Tunnel:  ${TUNNEL_NAME} (${TUNNEL_UUID})"
echo "  Service: ${SERVICE_NAME}.service"
echo ""
echo "  Manage:"
echo "    systemctl status ${SERVICE_NAME}"
echo "    journalctl -u ${SERVICE_NAME} -f"
echo "    systemctl restart ${SERVICE_NAME}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
