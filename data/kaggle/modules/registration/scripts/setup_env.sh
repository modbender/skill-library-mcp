#!/usr/bin/env bash
# Set up Kaggle credentials from available environment variables.
#
# Reads from .env if present, then ensures ~/.kaggle/kaggle.json exists
# so both kagglehub and kaggle-cli work.
#
# Usage:
#   bash scripts/setup_env.sh
#   OR: source scripts/setup_env.sh  (also exports env vars in current shell)

set -euo pipefail

# Load .env if present
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

# Resolve API key: prefer KAGGLE_KEY, then KAGGLE_TOKEN
KEY="${KAGGLE_KEY:-${KAGGLE_TOKEN:-}}"

if [ -z "$KEY" ]; then
    if [ -f "$KAGGLE_JSON" ]; then
        echo "[OK] kaggle.json already exists at ${KAGGLE_JSON}"
        exit 0
    fi
    # No credentials available — silent exit (not an error during SessionStart)
    exit 0
fi

# Export the correct env var names (only effective if script is sourced)
export KAGGLE_KEY="$KEY"
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

echo "[OK] Kaggle environment ready"
