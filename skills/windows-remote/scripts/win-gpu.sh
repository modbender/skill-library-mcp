#!/bin/bash
# Check GPU status on remote Windows
# Usage: win-gpu.sh [--query]

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if [ "$1" = "--query" ]; then
    # Compact query format
    "$SCRIPT_DIR/win-exec.sh" "nvidia-smi --query-gpu=name,memory.used,memory.total,utilization.gpu --format=csv,noheader"
else
    # Full nvidia-smi output
    "$SCRIPT_DIR/win-exec.sh" "nvidia-smi"
fi
