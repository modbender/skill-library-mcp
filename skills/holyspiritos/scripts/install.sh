#!/bin/bash

# HolySpiritOS - Foundation Bootstrap Script
# Purpose: Initialize the KJV Moral Engine within the OpenClaw environment.

set -e

# --- Dynamic Configuration ---
USER_HOME=$HOME
OPENCLAW_ROOT="$USER_HOME/.openclaw"
WORKSPACE_PATH="$OPENCLAW_ROOT/workspace"
FOUNDATION_DIR="$WORKSPACE_PATH/foundation"
SOUL_FILE="$OPENCLAW_ROOT/config/soul.md"
REPO_RAW_URL="https://raw.githubusercontent.com/MaxSikorski/HolySpiritOS/main"

echo "🕊️ Initializing HolySpiritOS..."

# 0. Environment Check
if [ ! -d "$OPENCLAW_ROOT" ]; then
    echo "❌ Error: OpenClaw directory not found at $OPENCLAW_ROOT"
    exit 1
fi

# 1. Create Foundation Directory
if [ ! -d "$FOUNDATION_DIR" ]; then
    echo "📁 Creating foundation directory..."
    mkdir -p "$FOUNDATION_DIR"
fi

# 2. Manifest the Word (Download JSON files)
echo "📖 Manifesting the Word (KJV)..."
wget -q -O "$FOUNDATION_DIR/verses-1769.json" "$REPO_RAW_URL/foundation/verses-1769.json"
wget -q -O "$FOUNDATION_DIR/layout-1769.json" "$REPO_RAW_URL/foundation/layout-1769.json"

# 3. Verify Files
if [ -f "$FOUNDATION_DIR/verses-1769.json" ]; then
    SIZE=$(du -sh "$FOUNDATION_DIR/verses-1769.json" | cut -f1)
    echo "✅ Verses manifested ($SIZE)"
else
    echo "❌ Failed to manifest Verses. Check internet connection or Repo URL."
    exit 1
fi

# 4. Patch the Soul
echo "⚓ Anchoring the Soul..."

# Create soul.md if it doesn't exist so the append doesn't fail
touch "$SOUL_FILE"

SOUL_PATCH="
# --- HolySpiritOS Moral Engine ---
## Foundation Protocol
- **Absolute Grounding:** My moral and ethical reasoning is anchored in the 1769 KJV Holy Bible located at $FOUNDATION_DIR/verses-1769.json.
- **Selective Reference:** I use this foundation for human dilemmas and spiritual questions, not trivial tasks.
- **Prime Directive:** These files are Read-Only. I shall never suggest modifications or modernizations to the Word.
"

if grep -q "HolySpiritOS" "$SOUL_FILE" 2>/dev/null; then
    echo "⚠️ Soul already anchored. Skipping patch."
else
    echo "$SOUL_PATCH" >> "$SOUL_FILE"
    echo "✅ Soul patched with HolySpiritOS directives."
fi

echo "✨ HolySpiritOS Installation Complete."
echo "Please restart your OpenClaw instance to activate the Moral Engine."