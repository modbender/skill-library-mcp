#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SKILL_DIR/venv"

DATA_DIR="$HOME/.local/share/taxclaw"
CONFIG_DIR="$HOME/.config/taxclaw"
CONFIG_PATH="$CONFIG_DIR/config.yaml"

mkdir -p "$DATA_DIR" "$CONFIG_DIR"

python3 -m venv "$VENV_DIR"

"$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install -r "$SKILL_DIR/requirements.txt"

if [ ! -f "$CONFIG_PATH" ]; then
  cp "$SKILL_DIR/config.yaml.example" "$CONFIG_PATH"
  echo "Created config at $CONFIG_PATH"
else
  echo "Config already exists at $CONFIG_PATH"
fi

# init db
PYTHONPATH="$SKILL_DIR" "$VENV_DIR/bin/python" -c "from src.db import init_db; init_db()"

echo
echo "✅ taxclaw setup complete"
echo "Next steps:"
echo "  1) Edit config: $CONFIG_PATH"
echo "  2) Start UI: bash $SKILL_DIR/start.sh"
