#!/usr/bin/env bash
# Timestamp files using OpenTimestamps
# Usage: ots-stamp.sh [file1] [file2] ...
set -euo pipefail

OTS="${OTS_BIN:-ots}"
WORKSPACE="${WORKSPACE:-$(cd "$(dirname "$0")/../../.." && pwd)}"

if [ $# -eq 0 ]; then
    echo "Usage: ots-stamp.sh <file1> [file2] ..."
    echo "Creates .ots proof files alongside each input file."
    exit 1
fi

stamped=0
skipped=0
failed=0

for file in "$@"; do
    if [ ! -f "$file" ]; then
        echo "SKIP: $file (not found)"
        ((skipped++)) || true
        continue
    fi

    ots_file="${file}.ots"

    # Skip if .ots exists and is newer than the source file
    if [ -f "$ots_file" ] && [ "$ots_file" -nt "$file" ]; then
        echo "SKIP: $file (already stamped, unchanged)"
        ((skipped++)) || true
        continue
    fi

    # Archive old proof if source changed
    if [ -f "$ots_file" ]; then
        archive_dir="$(dirname "$file")/.ots-archive/$(basename "$file")"
        mkdir -p "$archive_dir"
        timestamp=$(date -r "$ots_file" +%Y-%m-%d-%H%M%S 2>/dev/null || date +%Y-%m-%d-%H%M%S)
        mv "$ots_file" "$archive_dir/$timestamp.ots"
        echo "  (archived old proof: $archive_dir/$timestamp.ots)"
    fi

    echo "STAMP: $file"
    if $OTS stamp "$file" 2>&1; then
        ((stamped++)) || true
    else
        # Check if .ots was created despite non-zero exit (calendar timeout)
        if [ -f "$ots_file" ]; then
            echo "  (partial — some calendars may have failed, but proof created)"
            ((stamped++)) || true
        else
            echo "FAIL: $file"
            ((failed++)) || true
        fi
    fi
done

echo ""
echo "Done: $stamped stamped, $skipped skipped, $failed failed"
