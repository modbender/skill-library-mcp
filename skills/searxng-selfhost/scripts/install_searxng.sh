#!/bin/bash
# SearXNG install script for OpenClaw agents
# Installs SearXNG as a local search aggregator on port 8888
# Tested on Ubuntu 22.04/24.04

set -e

SEARXNG_HOME="/usr/local/searxng"
SEARXNG_PORT=8888
SEARXNG_USER="searxng"

echo "[1/6] Installing system dependencies..."
apt-get update -qq
apt-get install -y -qq git python3-pip

# Install uv via pip if not present
if ! command -v uv &>/dev/null; then
  pip3 install -q uv --break-system-packages
fi

echo "[2/6] Creating searxng user and directories..."
id -u $SEARXNG_USER &>/dev/null || /usr/sbin/useradd -r -d $SEARXNG_HOME -s /bin/false $SEARXNG_USER
mkdir -p $SEARXNG_HOME
chown $SEARXNG_USER:$SEARXNG_USER $SEARXNG_HOME

echo "[3/6] Cloning SearXNG..."
if [ -d "$SEARXNG_HOME/searxng-src" ]; then
  echo "  Already cloned — skipping"
else
  git clone https://github.com/searxng/searxng "$SEARXNG_HOME/searxng-src" --depth=1
fi

echo "[4/6] Installing dependencies with uv..."
cd "$SEARXNG_HOME/searxng-src"
uv venv "$SEARXNG_HOME/searx-venv" --python python3
uv pip install --python "$SEARXNG_HOME/searx-venv/bin/python" \
  -r "$SEARXNG_HOME/searxng-src/requirements.txt"

echo "[5/6] Writing config..."
mkdir -p /etc/searxng
cat > /etc/searxng/settings.yml << EOF
use_default_settings: true
server:
  bind_address: "127.0.0.1"
  port: ${SEARXNG_PORT}
  secret_key: "$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
  limiter: false
  public_instance: false
search:
  formats:
    - html
    - json
engines:
  - name: google
    engine: google
    shortcut: g
  - name: bing
    engine: bing
    shortcut: bi
  - name: brave
    engine: brave
    shortcut: br
  - name: startpage
    engine: startpage
    shortcut: sp
  - name: duckduckgo
    engine: duckduckgo
    shortcut: ddg
  - name: wikipedia
    engine: wikipedia
    shortcut: wp
EOF
chown -R $SEARXNG_USER:$SEARXNG_USER /etc/searxng

echo "[6/6] Installing systemd service..."
cat > /etc/systemd/system/searxng.service << EOF
[Unit]
Description=SearXNG (local search aggregator for OpenClaw)
After=network.target

[Service]
Type=simple
User=${SEARXNG_USER}
Environment=SEARXNG_SETTINGS_PATH=/etc/searxng/settings.yml
Environment=PYTHONPATH=${SEARXNG_HOME}/searxng-src
ExecStart=${SEARXNG_HOME}/searx-venv/bin/python -m searx.webapp
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable searxng
systemctl restart searxng

echo ""
echo "SearXNG installed and running."
echo "Health check: curl 'http://127.0.0.1:${SEARXNG_PORT}/search?q=test&format=json'"
echo "Logs: journalctl -u searxng -f"
