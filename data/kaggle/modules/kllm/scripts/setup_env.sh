#!/usr/bin/env bash
# Set up Kaggle credentials from available environment variables.
#
# This script handles the common case where KAGGLE_TOKEN is set but the
# tools expect KAGGLE_KEY (kaggle-cli) or KAGGLE_API_TOKEN (kagglehub).
#
# It creates ~/.kaggle/kaggle.json so both tools work without needing
# the correct env var names.
#
# Usage:
#   bash scripts/setup_env.sh
#   OR: source scripts/setup_env.sh  (also exports env vars in current shell)

set -euo pipefail

# Load .env if present (merged from registration module)
if [ -f ".env" ]; then
    set -a
    # shellcheck disable=SC1091
    source .env
    set +a
fi

KAGGLE_DIR="${HOME}/.kaggle"
KAGGLE_JSON="${KAGGLE_DIR}/kaggle.json"

# Resolve username
USERNAME="${KAGGLE_USERNAME:-}"

# Resolve API key: prefer KAGGLE_KEY, then KAGGLE_API_TOKEN, then KAGGLE_TOKEN
KEY="${KAGGLE_KEY:-${KAGGLE_API_TOKEN:-${KAGGLE_TOKEN:-}}}"

if [ -z "$KEY" ]; then
    if [ -f "$KAGGLE_JSON" ]; then
        echo "[OK] kaggle.json already exists at ${KAGGLE_JSON}"
        exit 0
    fi
    echo "[ERROR] No Kaggle API key found in KAGGLE_KEY, KAGGLE_API_TOKEN, or KAGGLE_TOKEN"
    exit 1
fi

# Export the correct env var names (only works if script is sourced)
export KAGGLE_KEY="$KEY"
export KAGGLE_API_TOKEN="$KEY"
if [ -n "$USERNAME" ]; then
    export KAGGLE_USERNAME="$USERNAME"
fi

# Create kaggle.json if it doesn't exist
if [ ! -f "$KAGGLE_JSON" ]; then
    mkdir -p "$KAGGLE_DIR"
    if [ -n "$USERNAME" ]; then
        echo "{\"username\":\"${USERNAME}\",\"key\":\"${KEY}\"}" > "$KAGGLE_JSON"
    else
        echo "{\"key\":\"${KEY}\"}" > "$KAGGLE_JSON"
    fi
    chmod 600 "$KAGGLE_JSON"
    echo "[OK] Created ${KAGGLE_JSON}"
else
    echo "[OK] ${KAGGLE_JSON} already exists"
fi

# Install dependencies if not present
if ! python3 -c "import kagglehub" 2>/dev/null; then
    echo "[INFO] Installing kagglehub..."
    pip install -q kagglehub kaggle 2>/dev/null || true
fi

echo "[OK] Kaggle environment ready"
