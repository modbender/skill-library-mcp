#!/usr/bin/env bash
set -euo pipefail

# Stratos SDS Download Script
# Usage: download.sh <file_hash_or_cid> <output_path>

SPFS_GATEWAY="${STRATOS_SPFS_GATEWAY:-http://localhost:18452}"
NODE_DIR="${STRATOS_NODE_DIR:-$HOME/rsnode}"

if [ $# -lt 2 ]; then
    echo "ERROR: Missing arguments"
    echo "Usage: download.sh <file_hash_or_cid> <output_path>"
    exit 1
fi

FILE_HASH="$1"
OUTPUT_PATH="$2"

# Resolve ~ in path
OUTPUT_PATH="${OUTPUT_PATH/#\~/$HOME}"

# Check if output file already exists
if [ -e "$OUTPUT_PATH" ]; then
    echo "ERROR: Output path already exists: $OUTPUT_PATH"
    echo "Please choose a different output path or confirm overwrite."
    exit 1
fi

# Ensure output directory exists
OUTPUT_DIR=$(dirname "$OUTPUT_PATH")
if [ ! -d "$OUTPUT_DIR" ]; then
    mkdir -p "$OUTPUT_DIR"
    echo "Created output directory: $OUTPUT_DIR"
fi

echo "Downloading: $FILE_HASH"
echo "Destination: $OUTPUT_PATH"

# Try SPFS HTTP API first
try_spfs_download() {
    local http_code
    http_code=$(curl -s -w "%{http_code}" -X POST \
        "${SPFS_GATEWAY}/api/v0/get?arg=${FILE_HASH}" \
        -o "$OUTPUT_PATH" 2>/dev/null)

    if [ "$http_code" = "200" ] && [ -f "$OUTPUT_PATH" ] && [ -s "$OUTPUT_PATH" ]; then
        local file_size
        file_size=$(stat -f%z "$OUTPUT_PATH" 2>/dev/null || stat -c%s "$OUTPUT_PATH" 2>/dev/null || echo "unknown")
        echo "SUCCESS: File downloaded via SPFS API"
        echo "Size: $file_size bytes"
        echo "Saved to: $OUTPUT_PATH"
        return 0
    else
        # Clean up partial download
        rm -f "$OUTPUT_PATH"
        return 1
    fi
}

# Fallback to ppd CLI
try_ppd_download() {
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
    output=$(cd "$node_dir" && ppd terminal get "$FILE_HASH" "$OUTPUT_PATH" 2>&1)
    local exit_code=$?

    if [ $exit_code -eq 0 ] && [ -f "$OUTPUT_PATH" ]; then
        local file_size
        file_size=$(stat -f%z "$OUTPUT_PATH" 2>/dev/null || stat -c%s "$OUTPUT_PATH" 2>/dev/null || echo "unknown")
        echo "SUCCESS: File downloaded via ppd CLI"
        echo "Size: $file_size bytes"
        echo "Saved to: $OUTPUT_PATH"
        echo "$output"
        return 0
    else
        echo "ERROR: ppd download failed (exit code: $exit_code)"
        echo "$output"
        rm -f "$OUTPUT_PATH"
        return 1
    fi
}

# Try SPFS first, fall back to ppd
echo "Attempting SPFS API download..."
if try_spfs_download; then
    exit 0
fi

echo "SPFS API unavailable, falling back to ppd CLI..."
if try_ppd_download; then
    exit 0
fi

echo "ERROR: Both SPFS API and ppd CLI failed. Please check that your Stratos SDS node is running."
exit 1
