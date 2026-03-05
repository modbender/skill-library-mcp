#!/bin/bash
# Immediate sync: pull then push

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Immediate Sync ==="
echo ""

# Pull first
echo "[1/2] Pulling remote changes..."
if "$SCRIPT_DIR/sync-pull"; then
    echo "✓ Pull complete"
else
    echo "⚠ Pull had issues (conflict or no connection)"
fi
echo ""

# Then push
echo "[2/2] Pushing local changes..."
if "$SCRIPT_DIR/sync-push"; then
    echo "✓ Push complete"
else
    echo "⚠ Push failed (will retry on next cycle)"
    exit 1
fi

echo ""
echo "=== Sync Complete ==="
