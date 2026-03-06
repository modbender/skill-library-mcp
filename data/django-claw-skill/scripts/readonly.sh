#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/load-config.sh"

CONFIG_FILE="$HOME/.openclaw/skills/django-claw/config.json"
ACTION="${1:-status}"

case "$ACTION" in
  on)
    /usr/bin/python3 - << 'PYEOF'
import json, sys
config_file = __import__('os').path.expanduser("~/.openclaw/skills/django-claw/config.json")
with open(config_file) as f:
    config = json.load(f)
config["read_only"] = True
with open(config_file, "w") as f:
    json.dump(config, f, indent=2)
print("✅ Read-only mode enabled. Shell and migrate commands are now blocked.")
PYEOF
    ;;
  off)
    /usr/bin/python3 - << 'PYEOF'
import json, sys
config_file = __import__('os').path.expanduser("~/.openclaw/skills/django-claw/config.json")
with open(config_file) as f:
    config = json.load(f)
config["read_only"] = False
with open(config_file, "w") as f:
    json.dump(config, f, indent=2)
print("✅ Read-only mode disabled. All commands are now available.")
PYEOF
    ;;
  *)
    if [ "$READ_ONLY" = "true" ]; then
      echo "🔒 Read-only mode is ON. Shell and migrate commands are blocked."
    else
      echo "🔓 Read-only mode is OFF. All commands are available."
    fi
    ;;
esac
