#!/usr/bin/env bash
set -euo pipefail

# Stratos SDS Upload Script
# Usage: upload.sh <file_path>

SPFS_GATEWAY="${STRATOS_SPFS_GATEWAY:-http://localhost:18452}"
NODE_DIR="${STRATOS_NODE_DIR:-$HOME/rsnode}"

if [ $# -lt 1 ]; then
    echo "ERROR: Missing file path argument"
    echo "Usage: upload.sh <file_path>"
    exit 1
fi

FILE_PATH="$1"

# Resolve ~ in path
FILE_PATH="${FILE_PATH/#\~/$HOME}"

if [ ! -f "$FILE_PATH" ]; then
    echo "ERROR: File not found: $FILE_PATH"
    exit 1
fi

FILE_SIZE=$(stat -f%z "$FILE_PATH" 2>/dev/null || stat -c%s "$FILE_PATH" 2>/dev/null || echo "unknown")
FILE_NAME=$(basename "$FILE_PATH")
echo "Uploading: $FILE_NAME ($FILE_SIZE bytes)"

# Try SPFS HTTP API first
try_spfs_upload() {
    local response
    response=$(curl -s -w "\n%{http_code}" -X POST \
        -F "file=@${FILE_PATH}" \
        "${SPFS_GATEWAY}/api/v0/add" 2>/dev/null)

    local http_code
    http_code=$(echo "$response" | tail -1)
    local body
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" = "200" ]; then
        local cid
        cid=$(echo "$body" | grep -o '"Hash":"[^"]*"' | head -1 | cut -d'"' -f4)
        if [ -n "$cid" ]; then
            echo "SUCCESS: File uploaded via SPFS API"
            echo "CID: $cid"
            return 0
        fi
    fi
    return 1
}

# Fallback to ppd CLI
try_ppd_upload() {
    if ! command -v ppd &>/dev/null; then
        echo "ERROR: ppd command not found in PATH"
        return 1
    fi

    local node_dir
    node_dir="${NODE_DIR/#\~/$HOME}"

    if [ ! -d "$node_dir" ]; then
        echo "ERROR: Node directory not found: $node_dir"
        return 1
    fi

    local output
    output=$(cd "$node_dir" && ppd terminal put "$FILE_PATH" 2>&1)
    local exit_code=$?

    if [ $exit_code -eq 0 ]; then
        echo "SUCCESS: File uploaded via ppd CLI"
        echo "$output"
        # Try to extract file hash from ppd output
        local hash
        hash=$(echo "$output" | grep -oE '[a-fA-F0-9]{64}|Qm[a-zA-Z0-9]{44,}' | head -1)
        if [ -n "$hash" ]; then
            echo "CID: $hash"
        fi
        return 0
    else
        echo "ERROR: ppd upload failed (exit code: $exit_code)"
        echo "$output"
        return 1
    fi
}

# Try SPFS first, fall back to ppd
echo "Attempting SPFS API upload..."
if try_spfs_upload; then
    exit 0
fi

echo "SPFS API unavailable, falling back to ppd CLI..."
if try_ppd_upload; then
    exit 0
fi

echo "ERROR: Both SPFS API and ppd CLI failed. Please check that your Stratos SDS node is running."
exit 1
