#!/usr/bin/env bash
# session-health-monitor: rotate.sh
# Archive daily memory files older than KEEP_DAYS.
# macOS + Linux compatible.

set -euo pipefail

KEEP_DAYS="${KEEP_DAYS:-3}"

# Auto-detect memory directory
if [[ -n "${MEMORY_DIR:-}" ]]; then
    memory_dir="$MEMORY_DIR"
elif [[ -d "$HOME/.openclaw/workspace/memory" ]]; then
    memory_dir="$HOME/.openclaw/workspace/memory"
else
    memory_dir="$HOME/.claude/memory"
fi

if [[ ! -d "$memory_dir" ]]; then
    echo "Memory directory not found: $memory_dir"
    exit 0
fi

archive_dir="$memory_dir/archive"

# Calculate cutoff date (macOS vs Linux)
if date -v -1d &>/dev/null 2>&1; then
    # macOS
    cutoff=$(date -v "-${KEEP_DAYS}d" +%Y-%m-%d)
else
    # Linux
    cutoff=$(date -d "-${KEEP_DAYS} days" +%Y-%m-%d)
fi

archived=0

for file in "$memory_dir"/[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].md; do
    [[ -f "$file" ]] || continue

    filename=$(basename "$file")
    file_date="${filename%.md}"

    # String comparison works for YYYY-MM-DD format
    if [[ "$file_date" < "$cutoff" ]]; then
        mkdir -p "$archive_dir"
        mv "$file" "$archive_dir/"
        archived=$((archived + 1))
    fi
done

if [[ "$archived" -gt 0 ]]; then
    echo "Archived $archived file(s) to $archive_dir/"
else
    echo "No files older than $KEEP_DAYS days to archive."
fi
