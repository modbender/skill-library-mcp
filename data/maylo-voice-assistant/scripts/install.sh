#!/usr/bin/env bash
set -euo pipefail

APP_DIR=${1:-}
if [[ -z "${APP_DIR}" ]]; then
  echo "Usage: install.sh <app_dir>" >&2
  exit 2
fi

cd "${APP_DIR}"

python3 -m venv venv
source venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt

# Tools used for audio output switching (optional)
if command -v brew >/dev/null 2>&1; then
  brew list switchaudio-osx >/dev/null 2>&1 || brew install switchaudio-osx || true
fi

echo "OK: venv ready in ${APP_DIR}/venv"