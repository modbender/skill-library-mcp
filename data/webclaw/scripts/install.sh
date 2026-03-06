#!/bin/bash
# Webclaw post-install script.
# Sets up backend (venv), frontend (npm build), database, nginx, and systemd.
#
# Privileges required: sudo (for nginx config, systemd services, certbot)
# What this script does:
#   1. Clones full source from GitHub if api/web dirs are missing
#   2. Creates Python venv + installs pip dependencies
#   3. Runs npm install + next build for the frontend
#   4. Initializes SQLite database (~/.openclaw/webclaw/webclaw.sqlite)
#   5. Configures nginx reverse proxy (writes to /etc/nginx/sites-enabled/)
#   6. Creates and enables systemd services (webclaw-api, webclaw-web)
#
# Run by OpenClaw after copying skill files to ~/clawd/skills/webclaw/
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INSTALL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
CURRENT_USER="${SUDO_USER:-$(whoami)}"
USER_HOME=$(eval echo "~$CURRENT_USER")
DB_DIR="$USER_HOME/.openclaw/webclaw"
DB_PATH="$DB_DIR/webclaw.sqlite"

log() { echo "[webclaw] $1"; }
err() { echo "{\"status\":\"error\",\"message\":\"$1\"}"; exit 1; }

# Source repo — HTTPS clone (no SSH key required)
REPO_URL="https://github.com/avansaber/webclaw.git"
RELEASE_TAG="v1.0.10"

# ── Phase 0: Clone full source if not present ────────────────────────────
# The publish package is a lightweight metadata package (SKILL.md + scripts).
# The full source (api/, web/, templates/) is fetched from GitHub at a pinned
# release tag. This ensures reproducible installs — no arbitrary HEAD code.

if [ ! -d "$INSTALL_DIR/api" ] || [ ! -d "$INSTALL_DIR/web" ]; then
    log "Source directories missing. Cloning $REPO_URL @ $RELEASE_TAG ..."
    TEMP_CLONE=$(mktemp -d)
    git clone --depth 1 --branch "$RELEASE_TAG" "$REPO_URL" "$TEMP_CLONE" || err "Failed to clone webclaw repo from $REPO_URL (tag: $RELEASE_TAG)"
    # Copy source into install dir, preserving any existing files (SKILL.md, scripts/)
    rsync -a --ignore-existing "$TEMP_CLONE/" "$INSTALL_DIR/" --exclude='.git/'
    rm -rf "$TEMP_CLONE"
    log "Source cloned into $INSTALL_DIR (tag: $RELEASE_TAG)"
fi

# ── Phase 1: Backend (Python venv + dependencies) ──────────────────────────

log "Setting up Python backend..."

if [ ! -d "$INSTALL_DIR/.venv" ]; then
    python3 -m venv "$INSTALL_DIR/.venv"
fi

"$INSTALL_DIR/.venv/bin/pip" install --quiet --upgrade pip
"$INSTALL_DIR/.venv/bin/pip" install --quiet -r "$INSTALL_DIR/api/requirements.txt"

log "Backend ready."

# ── Phase 2: Frontend (npm install + build) ─────────────────────────────────

log "Building frontend..."

cd "$INSTALL_DIR/web"
npm install --silent 2>/dev/null || npm install
npm run build

log "Frontend built."

# ── Phase 3: Database ───────────────────────────────────────────────────────

log "Initializing database..."

mkdir -p "$DB_DIR"

# Create tables if they don't exist, then verify
"$INSTALL_DIR/.venv/bin/python3" -c "
import sys, os, sqlite3
sys.path.insert(0, '$INSTALL_DIR/api')
os.environ['WEBCLAW_DB_PATH'] = '$DB_PATH'
from db import get_connection
conn = get_connection('$DB_PATH')
tables = conn.execute(\"SELECT COUNT(*) FROM sqlite_master WHERE type='table'\").fetchone()[0]
if tables < 5:
    print(f'ERROR: Only {tables} tables created, expected 9+', file=sys.stderr)
    sys.exit(1)
conn.close()
print(f'Database initialized at $DB_PATH ({tables} tables)')
"

# Set secure permissions and correct ownership on the database file
chmod 600 "$DB_PATH" 2>/dev/null || true
chown "$CURRENT_USER:$CURRENT_USER" "$DB_DIR" "$DB_PATH" 2>/dev/null || true

log "Database ready."

# ── Phase 4: Nginx + SSL ──────────────────────────────────────────────────

log "Configuring nginx..."

# Determine server name: env var > first script argument > auto-detect IP
SERVER_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "_")
DOMAIN="${WEBCLAW_DOMAIN:-${1:-$SERVER_IP}}"
log "Server name: $DOMAIN"

# Check if a working nginx config already exists (e.g. with SSL from prior install)
EXISTING_CONF=""
if [ -f /etc/nginx/sites-enabled/webclaw ]; then
    EXISTING_CONF="/etc/nginx/sites-enabled/webclaw"
fi

if [ -n "$EXISTING_CONF" ] && sudo nginx -t 2>/dev/null; then
    sudo systemctl reload nginx
    log "Nginx: reusing existing config at $EXISTING_CONF"
else
    # Generate self-signed SSL cert (works with Cloudflare Full mode)
    CERT_DIR="/etc/ssl/webclaw"
    if [ ! -f "$CERT_DIR/cert.pem" ]; then
        log "Generating self-signed SSL certificate..."
        sudo mkdir -p "$CERT_DIR"
        sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout "$CERT_DIR/key.pem" -out "$CERT_DIR/cert.pem" \
            -subj "/CN=$DOMAIN" 2>/dev/null
        sudo chmod 600 "$CERT_DIR/key.pem"
        log "Self-signed cert created at $CERT_DIR/"
    fi

    # Use HTTPS template with self-signed cert
    NGINX_CONF="$INSTALL_DIR/templates/nginx-https.conf"
    if [ ! -f "$NGINX_CONF" ]; then
        # Fallback to HTTP if HTTPS template missing
        NGINX_CONF="$INSTALL_DIR/templates/nginx-http.conf"
    fi

    TEMP_CONF=$(mktemp)
    sed -e "s|{{DOMAIN}}|$DOMAIN|g" \
        -e "s|{{SSL_CERT}}|$CERT_DIR/cert.pem|g" \
        -e "s|{{SSL_KEY}}|$CERT_DIR/key.pem|g" \
        "$NGINX_CONF" > "$TEMP_CONF"
    sudo cp "$TEMP_CONF" /etc/nginx/sites-enabled/webclaw
    rm -f "$TEMP_CONF"
    sudo rm -f /etc/nginx/sites-enabled/default 2>/dev/null || true

    if sudo nginx -t 2>/dev/null; then
        sudo systemctl reload nginx
        log "Nginx configured (HTTPS on port 443, self-signed cert)."
    else
        err "Nginx config test failed. Check /etc/nginx/sites-enabled/webclaw"
    fi
fi

# ── Phase 5: Systemd services ──────────────────────────────────────────────

log "Setting up systemd services (webclaw-api, webclaw-web)..."

# Generate API service from template
TEMP_SVC=$(mktemp)
sed -e "s|{{INSTALL_DIR}}|$INSTALL_DIR|g" \
    -e "s|{{USER}}|$CURRENT_USER|g" \
    "$INSTALL_DIR/templates/webclaw-api.service" > "$TEMP_SVC"
sudo cp "$TEMP_SVC" /etc/systemd/system/webclaw-api.service
rm -f "$TEMP_SVC"

# Generate web service
TEMP_SVC=$(mktemp)
sed -e "s|{{INSTALL_DIR}}|$INSTALL_DIR|g" \
    -e "s|{{USER}}|$CURRENT_USER|g" \
    "$INSTALL_DIR/templates/webclaw-web.service" > "$TEMP_SVC"
sudo cp "$TEMP_SVC" /etc/systemd/system/webclaw-web.service
rm -f "$TEMP_SVC"

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable webclaw-api webclaw-web
sudo systemctl restart webclaw-api webclaw-web

# Wait for services to start
sleep 3

# Verify API is up
if curl -sf http://127.0.0.1:8001/api/v1/health > /dev/null 2>&1; then
    log "API service running."
else
    log "WARNING: API service may not be ready yet. Check: journalctl -u webclaw-api"
fi

# Fix ownership if run via sudo (venv, node_modules, .next created as root)
if [ "$CURRENT_USER" != "$(whoami)" ]; then
    chown -R "$CURRENT_USER:$CURRENT_USER" "$INSTALL_DIR" 2>/dev/null || true
fi

# ── Phase 6: Report ────────────────────────────────────────────────────────

PROTO="https"
if [ ! -f /etc/ssl/webclaw/cert.pem ]; then
    PROTO="http"
fi

cat <<EOF
{"status":"ok","message":"Web dashboard installed and running!\n\nAccess: $PROTO://$DOMAIN\nCreate your admin account: $PROTO://$DOMAIN/setup\n\nSSL: Self-signed certificate installed (works with Cloudflare Full mode).\nFor Let's Encrypt, point a domain to $SERVER_IP and say:\n  'Set up SSL for yourdomain.com'"}
EOF
