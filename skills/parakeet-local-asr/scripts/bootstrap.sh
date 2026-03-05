#!/usr/bin/env bash
set -euo pipefail

PARAKEET_DIR="${PARAKEET_DIR:-$HOME/parakeet-asr}"
REPO_URL="${PARAKEET_REPO_URL:-https://github.com/rundax/parakeet-asr.git}"

if [ -d "$PARAKEET_DIR/.git" ]; then
  echo "Updating existing repo at $PARAKEET_DIR"
  git -C "$PARAKEET_DIR" pull --ff-only
else
  echo "Cloning repo to $PARAKEET_DIR"
  git clone "$REPO_URL" "$PARAKEET_DIR"
fi

cd "$PARAKEET_DIR"
./setup.sh

echo "Bootstrap complete"
