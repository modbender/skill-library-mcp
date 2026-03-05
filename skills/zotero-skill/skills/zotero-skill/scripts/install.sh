#!/usr/bin/env bash
# Install script for Zotero skill
# Creates a Python virtual environment and installs required Python packages (pyzotero)

set -euo pipefail

VENV_DIR=".venv"
PYTHON_BIN="python3"
REQUIREMENTS=(pyzotero)

usage() {
  cat <<EOF
Usage: ./install.sh [--venv DIR] [--python PYTHON]

Options:
  --venv DIR     Virtualenv directory to create (default: .venv)
  --python BIN   Python executable to use (default: python3)
  -h, --help     Show this help
EOF
}

# Parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --venv)
      VENV_DIR="$2"; shift 2;;
    --python)
      PYTHON_BIN="$2"; shift 2;;
    -h|--help)
      usage; exit 0;;
    *)
      echo "Unknown arg: $1"; usage; exit 1;;
  esac
done

# Check python
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Error: $PYTHON_BIN not found. Install Python 3.8+ or pass --python PATH." >&2
  exit 2
fi

# Create venv
echo "Creating virtual environment in: $VENV_DIR"
"$PYTHON_BIN" -m venv "$VENV_DIR"

# Activate and upgrade pip
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
python -m pip install --upgrade pip setuptools wheel

# Install requirements
echo "Installing required packages: ${REQUIREMENTS[*]}"
python -m pip install "${REQUIREMENTS[@]}"

# Write a small activate note
cat > "$VENV_DIR/README" <<EOF
This virtual environment was created for the Zotero skill.
Activate with: source $VENV_DIR/bin/activate
To install additional packages: pip install <package>
EOF

echo "Install complete. Activate with: source $VENV_DIR/bin/activate"
