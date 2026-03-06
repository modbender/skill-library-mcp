#!/bin/bash
# rotate-logs.sh — truncate oversized watchdog logs (launchd stdout/stderr + main log)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="${SCRIPT_DIR}/../logs"
MAX_BYTES=$((1024 * 1024))
KEEP_LINES=500

normalize_int() {
    local val
    val=$(echo "${1:-}" | tr -dc '0-9')
    echo "${val:-0}"
}

trim_if_oversized() {
    local file="$1"
    [ -f "$file" ] || return 0

    local size
    size=$(wc -c < "$file" 2>/dev/null || echo 0)
    size=$(normalize_int "$size")

    if [ "$size" -le "$MAX_BYTES" ]; then
        return 0
    fi

    local tmp
    tmp=$(mktemp "${file}.XXXXXX")
    tail -n "$KEEP_LINES" "$file" > "$tmp" 2>/dev/null || : > "$tmp"
    mv -f "$tmp" "$file"
}

trim_if_oversized "${LOG_DIR}/watchdog-stdout.log"
trim_if_oversized "${LOG_DIR}/watchdog-stderr.log"
trim_if_oversized "${LOG_DIR}/watchdog.log"
