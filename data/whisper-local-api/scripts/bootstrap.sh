#!/usr/bin/env bash
set -euo pipefail

WHISPER_DIR="${WHISPER_DIR:-$HOME/whisper-local-api}"
REPO_URL="${WHISPER_REPO_URL:-https://github.com/Hantok/local-whisper-backend.git}"

if [ -d "$WHISPER_DIR/.git" ]; then
  echo "Updating existing Whisper repo at $WHISPER_DIR"
  git -C "$WHISPER_DIR" pull --ff-only
else
  echo "Cloning Whisper repo to $WHISPER_DIR"
  git clone "$REPO_URL" "$WHISPER_DIR"
fi

cd "$WHISPER_DIR"
if [ ! -d ".venv" ]; then
  echo "Creating isolated local python environment..."
  python3 -m venv .venv
fi

echo "Installing secure dependencies inside virtual environment..."
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "Bootstrap complete. Safe to run start.sh."
