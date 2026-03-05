#!/usr/bin/env bash
# session-health-monitor: snapshot.sh
# Save key facts to daily memory file.
# Usage:
#   bash snapshot.sh "fact1" "fact2" "fact3"
#   echo -e "fact1\nfact2" | bash snapshot.sh -

set -euo pipefail

# Auto-detect memory directory
if [[ -n "${MEMORY_DIR:-}" ]]; then
    memory_dir="$MEMORY_DIR"
elif [[ -d "$HOME/.openclaw/workspace/memory" ]]; then
    memory_dir="$HOME/.openclaw/workspace/memory"
else
    memory_dir="$HOME/.claude/memory"
fi

mkdir -p "$memory_dir"

today=$(date +%Y-%m-%d)
time_now=$(date +%H:%M)
daily_file="$memory_dir/${today}.md"

# Collect facts from args or stdin
facts=()
if [[ "${1:-}" == "-" ]]; then
    while IFS= read -r line; do
        [[ -n "$line" ]] && facts+=("$line")
    done
else
    for arg in "$@"; do
        [[ -n "$arg" ]] && facts+=("$arg")
    done
fi

if [[ ${#facts[@]} -eq 0 ]]; then
    echo "Usage: bash snapshot.sh \"fact1\" \"fact2\" ..."
    echo "       echo -e \"fact1\\nfact2\" | bash snapshot.sh -"
    exit 1
fi

# Read existing file content for dedup
existing=""
if [[ -f "$daily_file" ]]; then
    existing=$(cat "$daily_file")
fi

# Build snapshot section
new_facts=()
for fact in "${facts[@]}"; do
    # Dedup: check if first 50 chars already exist in file
    check="${fact:0:50}"
    if [[ -n "$existing" ]] && echo "$existing" | grep -qF "$check"; then
        continue
    fi
    new_facts+=("$fact")
done

if [[ ${#new_facts[@]} -eq 0 ]]; then
    echo "All facts already recorded in $daily_file"
    exit 0
fi

# Append snapshot
{
    echo ""
    echo "## Pre-Compaction Snapshot ($time_now)"
    for fact in "${new_facts[@]}"; do
        echo "- $fact"
    done
} >> "$daily_file"

echo "Saved ${#new_facts[@]} fact(s) to $daily_file"
