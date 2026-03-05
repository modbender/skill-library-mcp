#!/usr/bin/env bash
# Google Search skill installer
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "📦 Installing Google Search skill..."

# Install Python dependencies
pip install --break-system-packages --quiet google-genai 2>/dev/null || {
    echo "⚠️  pip install failed, trying without --break-system-packages..."
    pip install --quiet google-genai 2>/dev/null || {
        echo "❌ Failed to install google-genai. Install manually: pip install google-genai"
        exit 1
    }
}

# Verify API key
if [ -z "${GOOGLE_API_KEY:-}" ]; then
    echo "⚠️  GOOGLE_API_KEY not set. Set it in OpenClaw config before using."
else
    echo "✅ GOOGLE_API_KEY found"
fi

# Quick smoke test
if python3 "$SCRIPT_DIR/lib/google_search.py" --help >/dev/null 2>&1; then
    echo "✅ Google Search skill ready."
else
    echo "⚠️  Smoke test failed - check Python dependencies."
    exit 1
fi
