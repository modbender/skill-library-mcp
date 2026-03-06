#!/usr/bin/env bash
# ipeaky v5 — register_key_path.sh
# Usage: bash register_key_path.sh <SERVICE_NAME> <OPENCLAW_CONFIG_PATH>
# Records which openclaw config path holds this service's key.
# Called by store scripts after saving a key.

set -euo pipefail

SERVICE="${1:?Usage: register_key_path.sh <SERVICE_NAME> <CONFIG_PATH>}"
CONFIG_PATH="${2:?Usage: register_key_path.sh <SERVICE_NAME> <CONFIG_PATH>}"

KEY_PATHS_DIR="$HOME/.ipeaky/key-paths"
mkdir -p "$KEY_PATHS_DIR"

echo "$CONFIG_PATH" > "$KEY_PATHS_DIR/${SERVICE}.txt"
echo "Registered: $SERVICE → $CONFIG_PATH"
