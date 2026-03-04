#!/bin/bash
# fetch-batch-from-file.sh — Fetch skills from lines START to END of a file
# Usage: bash fetch-batch-from-file.sh <paths-file> <start-line> <count>

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FILE="$1"
START="$2"
COUNT="$3"

sed -n "${START},$((START + COUNT - 1))p" "$FILE" | while IFS= read -r path; do
    [ -z "$path" ] && continue
    bash "$SCRIPT_DIR/fetch-skill.sh" "$path" 2>/dev/null
    echo ""
done
