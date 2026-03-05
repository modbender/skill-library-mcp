#!/usr/bin/env bash
# Auto-timestamp key workspace files
# Timestamps: memory/*.md, MEMORY.md, SOUL.md, AGENTS.md
# Skips files already stamped and unchanged
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKSPACE="${WORKSPACE:-$(cd "$SCRIPT_DIR/../../.." && pwd)}"

# Collect target files
targets=()

# Core identity files
for f in MEMORY.md SOUL.md AGENTS.md USER.md; do
    [ -f "$WORKSPACE/$f" ] && targets+=("$WORKSPACE/$f")
done

# Memory directory
if [ -d "$WORKSPACE/memory" ]; then
    for f in "$WORKSPACE"/memory/*.md; do
        [ -f "$f" ] && targets+=("$f")
    done
fi

if [ ${#targets[@]} -eq 0 ]; then
    echo "No files to timestamp"
    exit 0
fi

echo "Auto-timestamping ${#targets[@]} workspace file(s)..."
echo ""

exec "$SCRIPT_DIR/ots-stamp.sh" "${targets[@]}"
