#!/usr/bin/env bash
# First-time setup for the STT skill.
# Run once after `clawhub install sergei-mikhailov-stt`.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== STT Skill Setup ==="

# 1. Python virtual environment
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv
else
    echo "Virtual environment already exists."
fi

echo "Installing Python dependencies..."
.venv/bin/pip install --quiet -r requirements.txt

# 2. Configuration files
if [ ! -f ".env" ]; then
    cp assets/env.example .env
    echo "Created .env from template."
else
    echo ".env already exists, skipping."
fi

if [ ! -f "config.json" ]; then
    cp assets/config.example.json config.json
    echo "Created config.json from template."
else
    echo "config.json already exists, skipping."
fi

echo ""
echo "=== Setup complete ==="
echo ""
echo "Next step: add your API keys in one of these ways:"
echo "  1. (Recommended) Add to ~/.openclaw/openclaw.json:"
echo "     \"skills\": { \"entries\": { \"sergei-mikhailov-stt\": { \"env\": {"
echo "       \"YANDEX_API_KEY\": \"...\", \"YANDEX_FOLDER_ID\": \"...\" } } } }"
echo ""
echo "  2. Edit .env in this folder and fill in YANDEX_API_KEY and YANDEX_FOLDER_ID"
echo ""
echo "Then restart OpenClaw: openclaw gateway stop && openclaw gateway start"
