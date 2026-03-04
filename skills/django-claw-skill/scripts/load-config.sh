#!/usr/bin/env bash
# Shared config loader — sourced by every script
# Priority: env vars > ~/.openclaw/skills/django-claw/config.json > setup wizard

CONFIG_FILE="$HOME/.openclaw/skills/django-claw/config.json"

_read_json() {
  /usr/bin/python3 -c "import json; d=json.load(open('$CONFIG_FILE')); print(d.get('$1',''))" 2>/dev/null
}

if [ -f "$CONFIG_FILE" ]; then
  PROJECT_PATH="${DJANGO_PROJECT_PATH:-$(_read_json project_path)}"
  VENV_PATH="${DJANGO_VENV_PATH:-$(_read_json venv_path)}"
  SETTINGS="${DJANGO_SETTINGS_MODULE:-$(_read_json settings_module)}"
else
  PROJECT_PATH="${DJANGO_PROJECT_PATH:-}"
  VENV_PATH="${DJANGO_VENV_PATH:-}"
  SETTINGS="${DJANGO_SETTINGS_MODULE:-}"
fi

# If still empty, trigger setup wizard
if [ -z "$PROJECT_PATH" ] || [ -z "$VENV_PATH" ] || [ -z "$SETTINGS" ]; then
  echo "⚙️  Django-Claw is not configured yet. Running setup wizard..."
  bash "$(dirname "$0")/setup.sh"
  PROJECT_PATH=$(_read_json project_path)
  VENV_PATH=$(_read_json venv_path)
  SETTINGS=$(_read_json settings_module)
fi

# Resolve Python binary
PYTHON="$VENV_PATH/bin/python3"
[ -f "$PYTHON" ] || PYTHON="$VENV_PATH/bin/python"
[ -f "$PYTHON" ] || PYTHON="/usr/bin/python3"

READ_ONLY="${DJANGO_READ_ONLY:-$(_read_json read_only)}"
READ_ONLY=$(echo "${READ_ONLY:-false}" | tr '[:upper:]' '[:lower:]')
export PROJECT_PATH VENV_PATH SETTINGS PYTHON READ_ONLY
