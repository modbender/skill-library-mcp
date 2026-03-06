#!/usr/bin/env bash
set -euo pipefail

SERVICE_NAME="iblai-router"
ROUTER_DIR="$HOME/.openclaw/workspace/router"

echo "Removing iblai-router..."

# 1. Stop and disable service
if systemctl is-active --quiet "$SERVICE_NAME" 2>/dev/null; then
  sudo systemctl stop "$SERVICE_NAME"
  echo "  ✓ Service stopped"
fi

if systemctl is-enabled --quiet "$SERVICE_NAME" 2>/dev/null; then
  sudo systemctl disable "$SERVICE_NAME"
fi

# 2. Remove service file
if [ -f "/etc/systemd/system/$SERVICE_NAME.service" ]; then
  sudo rm "/etc/systemd/system/$SERVICE_NAME.service"
  sudo systemctl daemon-reload
  echo "  ✓ Systemd unit removed"
fi

# 3. Remove router files
if [ -d "$ROUTER_DIR" ]; then
  rm -rf "$ROUTER_DIR"
  echo "  ✓ Router files removed from $ROUTER_DIR"
fi

# 4. Clean up OpenClaw config
OPENCLAW_JSON="$HOME/.openclaw/openclaw.json"
if [ -f "$OPENCLAW_JSON" ] && command -v python3 &> /dev/null; then
  python3 - "$OPENCLAW_JSON" << 'PYEOF'
import json, sys

config_path = sys.argv[1]
with open(config_path) as f:
    cfg = json.load(f)

changed = False

# Remove model provider
providers = cfg.get("models", {}).get("providers", {})
if "iblai-router" in providers:
    del providers["iblai-router"]
    # Clean up empty parents
    if not providers:
        cfg["models"].pop("providers", None)
    if not cfg.get("models"):
        cfg.pop("models", None)
    changed = True
    print("  ✓ Removed model provider from openclaw.json")

# Remove from model allowlist
models_allowlist = cfg.get("agents", {}).get("defaults", {}).get("models", {})
if "iblai-router/auto" in models_allowlist:
    del models_allowlist["iblai-router/auto"]
    changed = True
    print("  ✓ Removed iblai-router/auto from model allowlist")

# Remove legacy smart-router provider if present
if "smart-router" in cfg.get("models", {}).get("providers", {}):
    del cfg["models"]["providers"]["smart-router"]
    changed = True
    print("  ✓ Removed legacy smart-router provider")

if changed:
    with open(config_path, "w") as f:
        json.dump(cfg, f, indent=2)
        f.write("\n")
else:
    print("  ✓ openclaw.json already clean")
PYEOF
fi

# 5. Clean up cached models.json
MODELS_JSON="$HOME/.openclaw/agents/main/agent/models.json"
if [ -f "$MODELS_JSON" ] && command -v python3 &> /dev/null; then
  python3 - "$MODELS_JSON" << 'PYEOF'
import json, sys

models_path = sys.argv[1]
with open(models_path) as f:
    data = json.load(f)

changed = False
providers = data.get("providers", {})
for key in ["iblai-router", "smart-router"]:
    if key in providers:
        del providers[key]
        changed = True

if changed:
    with open(models_path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    print("  ✓ Cleaned up cached models.json")
PYEOF
fi

echo ""
echo "  ⚠ Restart OpenClaw to apply changes:"
echo "    openclaw gateway restart"
echo ""
echo "  If any cron jobs or subagents used iblai-router/auto, switch them"
echo "  to a direct model (e.g. anthropic/claude-sonnet-4-20250514)."
echo ""
echo "Done."
