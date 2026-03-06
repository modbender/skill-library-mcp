#!/usr/bin/env bash
# First-run setup wizard for django-claw skill

CONFIG_DIR="$HOME/.openclaw/skills/django-claw"
CONFIG_FILE="$CONFIG_DIR/config.json"

mkdir -p "$CONFIG_DIR"

echo ""
echo "🐍 Django-Claw First-Time Setup"
echo "================================"
echo "Config will be saved to:"
echo "  $CONFIG_FILE"
echo ""

# Project path
read -rp "Django project path (e.g. /Users/you/Projects/myproject): " PROJECT_PATH
while [ ! -f "$PROJECT_PATH/manage.py" ]; do
  echo "❌ No manage.py found at $PROJECT_PATH — check the path"
  read -rp "Django project path: " PROJECT_PATH
done
echo "✅ manage.py found"

# Venv path
read -rp "Virtual env path [default: $PROJECT_PATH/venv]: " VENV_PATH
VENV_PATH="${VENV_PATH:-$PROJECT_PATH/venv}"
PYTHON="$VENV_PATH/bin/python3"
[ -f "$PYTHON" ] || PYTHON="$VENV_PATH/bin/python"
if [ ! -f "$PYTHON" ]; then
  echo "⚠️  No Python found at $VENV_PATH — saved anyway, but verify this path"
else
  echo "✅ Python found at $PYTHON"
fi

# Settings module
read -rp "Django settings module [default: config.settings]: " SETTINGS_MODULE
SETTINGS_MODULE="${SETTINGS_MODULE:-config.settings}"

# Read-only mode
read -rp "Enable read-only mode? Disables shell and migrate [y/N]: " RO_INPUT
READ_ONLY_VAL="False"
[ "$RO_INPUT" = "y" ] || [ "$RO_INPUT" = "Y" ] && READ_ONLY_VAL="True"

# Save config.json using python3 to avoid path injection via heredoc
/usr/bin/python3 - << PYEOF
import json
config = {
    "project_path": """$PROJECT_PATH""",
    "venv_path": """$VENV_PATH""",
    "settings_module": """$SETTINGS_MODULE""",
    "read_only": $READ_ONLY_VAL
}
with open("$CONFIG_FILE", "w") as f:
    json.dump(config, f, indent=2)
print("✅ Config saved")
PYEOF

echo ""
echo "✅ Config saved to $CONFIG_FILE"

# Inject env vars into ~/.openclaw/openclaw.json so gateway picks them up
OPENCLAW_JSON="$HOME/.openclaw/openclaw.json"
if [ -f "$OPENCLAW_JSON" ]; then
  /usr/bin/python3 - << PYEOF
import json, os

openclaw_file = "$OPENCLAW_JSON"
with open(openclaw_file) as f:
    cfg = json.load(f)

cfg.setdefault("env", {}).setdefault("vars", {}).update({
    "DJANGO_PROJECT_PATH": """$PROJECT_PATH""",
    "DJANGO_VENV_PATH":    """$VENV_PATH""",
    "DJANGO_SETTINGS_MODULE": """$SETTINGS_MODULE""",
})

with open(openclaw_file, "w") as f:
    json.dump(cfg, f, indent=2)

print("✅ Env vars injected into openclaw.json")
PYEOF
else
  echo "⚠️  ~/.openclaw/openclaw.json not found — skipping env injection"
fi

echo ""
cat "$CONFIG_FILE"
echo ""
echo "Restart the gateway for env vars to take effect: openclaw gateway restart"
echo "To reconfigure anytime, send: django-claw setup"
echo "Django-Claw is ready! 🎉"
