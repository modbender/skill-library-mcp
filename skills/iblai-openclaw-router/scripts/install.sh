#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ROUTER_DIR="$HOME/.openclaw/workspace/router"
SERVICE_NAME="iblai-router"
PORT=8402

echo "⚡ Installing iblai-router..."

# 1. Copy router files
mkdir -p "$ROUTER_DIR"
cp "$SKILL_DIR/server.js" "$ROUTER_DIR/server.js"

# Only copy config if it doesn't exist (preserve user customizations)
if [ ! -f "$ROUTER_DIR/config.json" ]; then
  cp "$SKILL_DIR/config.json" "$ROUTER_DIR/config.json"
  echo "  ✓ Copied default config.json"
else
  echo "  ✓ config.json already exists — preserved"
fi
echo "  ✓ Copied server.js to $ROUTER_DIR"

# 2. Detect Anthropic API key
API_KEY=""
AUTH_FILE="$HOME/.openclaw/agents/main/agent/auth-profiles.json"
if [ -f "$AUTH_FILE" ]; then
  API_KEY=$(grep -o '"key": "[^"]*"' "$AUTH_FILE" 2>/dev/null | head -1 | cut -d'"' -f4 || true)
fi

if [ -z "$API_KEY" ]; then
  echo ""
  echo "  ⚠ Could not auto-detect Anthropic API key."
  echo "  Edit /etc/systemd/system/$SERVICE_NAME.service and set ANTHROPIC_API_KEY manually."
  API_KEY="sk-ant-YOUR-KEY-HERE"
fi

# 3. Create systemd service
NODE_BIN=$(which node)
sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null << EOF
[Unit]
Description=iblai-router - Cost-optimizing Claude model routing
After=network.target

[Service]
Type=simple
ExecStart=$NODE_BIN $ROUTER_DIR/server.js
Environment=ANTHROPIC_API_KEY=$API_KEY
Environment=ROUTER_CONFIG=$ROUTER_DIR/config.json
Environment=ROUTER_PORT=$PORT
Environment=ROUTER_LOG=1
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF
echo "  ✓ Created systemd service"

# 4. Start the service
sudo systemctl daemon-reload
sudo systemctl enable --now "$SERVICE_NAME"
echo "  ✓ Service started on port $PORT"

# 5. Wait for it to be ready
sleep 1
if curl -sf "http://127.0.0.1:$PORT/health" > /dev/null 2>&1; then
  echo "  ✓ Health check passed"
else
  echo "  ⚠ Service started but health check failed — check: journalctl -u $SERVICE_NAME -f"
fi

# 6. Register with OpenClaw config
OPENCLAW_JSON="$HOME/.openclaw/openclaw.json"
if [ -f "$OPENCLAW_JSON" ] && command -v python3 &> /dev/null; then
  python3 - "$OPENCLAW_JSON" "$PORT" << 'PYEOF'
import json, sys

config_path, port = sys.argv[1], sys.argv[2]
with open(config_path) as f:
    cfg = json.load(f)

# Add model provider
providers = cfg.setdefault("models", {}).setdefault("providers", {})
if "iblai-router" not in providers:
    providers["iblai-router"] = {
        "baseUrl": f"http://127.0.0.1:{port}",
        "apiKey": "passthrough",
        "api": "anthropic-messages",
        "models": [{
            "id": "auto",
            "name": "iblai-router (auto)",
            "reasoning": True,
            "input": ["text", "image"],
            "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0},
            "contextWindow": 200000,
            "maxTokens": 8192
        }]
    }
    print("  ✓ Registered model provider in openclaw.json")
else:
    print("  ✓ Model provider already registered")

# Add to model allowlist (agents.defaults.models) if it exists
models_allowlist = cfg.get("agents", {}).get("defaults", {}).get("models")
if models_allowlist is not None and "iblai-router/auto" not in models_allowlist:
    models_allowlist["iblai-router/auto"] = {}
    print("  ✓ Added iblai-router/auto to model allowlist")

with open(config_path, "w") as f:
    json.dump(cfg, f, indent=2)
    f.write("\n")
PYEOF
  echo ""
  echo "  ⚠ Restart OpenClaw to pick up the new model provider:"
  echo "    openclaw gateway restart"
  echo "    # or: /config reload (from chat)"
  echo "    # or: kill -USR1 \$(pgrep -f 'openclaw.*gateway')"
else
  echo ""
  echo "  Now register the model in your OpenClaw session:"
  echo ""
  echo '  /config set models.providers.iblai-router.baseUrl http://127.0.0.1:'"$PORT"
  echo '  /config set models.providers.iblai-router.api anthropic-messages'
  echo '  /config set models.providers.iblai-router.apiKey passthrough'
  echo '  /config set models.providers.iblai-router.models [{"id":"auto","name":"iblai-router (auto)","reasoning":true,"input":["text","image"],"contextWindow":200000,"maxTokens":8192}]'
fi
echo ""
echo "  Then use: /model iblai-router/auto"
echo ""
echo "⚡ Done! Check stats: curl http://127.0.0.1:$PORT/stats"
