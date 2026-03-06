#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="$BASE_DIR/.venv"

echo "[stealthy-google-search] baseDir: $BASE_DIR"

if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: python3 not found on PATH" >&2
  exit 1
fi

# Create venv
if [ ! -d "$VENV" ]; then
  python3 -m venv "$VENV"
fi

# Activate venv
# shellcheck disable=SC1091
source "$VENV/bin/activate"

python -m pip install -U pip

# Google search needs the fetchers extra.
python -m pip install -U "scrapling[fetchers]"

# Install browsers + system deps (may require sudo).
SCRAPLING_BIN="$VENV/bin/scrapling"
if [ -x "$SCRAPLING_BIN" ]; then
  if command -v sudo >/dev/null 2>&1; then
    echo "[stealthy-google-search] running: sudo -E $SCRAPLING_BIN install"
    sudo -E env DEBIAN_FRONTEND=noninteractive "$SCRAPLING_BIN" install
  else
    echo "[stealthy-google-search] running: $SCRAPLING_BIN install"
    env DEBIAN_FRONTEND=noninteractive "$SCRAPLING_BIN" install
  fi
else
  echo "ERROR: scrapling CLI not found at $SCRAPLING_BIN" >&2
  exit 1
fi

echo "[stealthy-google-search] done. Test:"
echo "  $VENV/bin/python $BASE_DIR/scripts/google_search.py --query \"Top Indian universities\" --top 5 --hl en --gl in"
