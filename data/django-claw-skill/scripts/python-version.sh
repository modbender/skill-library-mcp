#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/load-config.sh"

echo "Python binary: $PYTHON"
"$PYTHON" --version
echo "Venv: $VENV_PATH"
echo "Project: $PROJECT_PATH"
