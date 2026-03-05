#!/bin/bash
# rednote-mac install script
# Transparent: this script does exactly 4 things listed below.

set -e
SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== rednote-mac installer ==="
echo "Skill dir: $SKILL_DIR"
echo ""
echo "This script will:"
echo "  1. Check for cliclick (required binary for mouse control)"
echo "  2. Install Python deps: atomacos, pyobjc-framework-Quartz, mcp"
echo "  3. Create symlink: ~/.openclaw/extensions/rednote-mac -> $SKILL_DIR"
echo "  4. Print the two commands needed to enable the plugin"
echo ""
read -p "Continue? [y/N] " confirm
[[ "$confirm" =~ ^[Yy]$ ]] || { echo "Aborted."; exit 1; }

# 1. Check cliclick
echo ""
echo "[1/4] Checking cliclick..."
CLICLICK_PATH="/opt/homebrew/bin/cliclick"
if [ -x "$CLICLICK_PATH" ]; then
  echo "  ✓ Found at $CLICLICK_PATH"
else
  echo "  Not found. Installing via Homebrew..."
  if command -v brew &>/dev/null; then
    brew install cliclick
  else
    echo "  ❌ Homebrew not found. Install cliclick manually: https://github.com/BlueM/cliclick"
    echo "     brew install cliclick"
    exit 1
  fi
fi

# 2. Install Python deps (minimal — no LLM clients)
echo ""
echo "[2/4] Installing Python dependencies..."
echo "  Packages: atomacos, pyobjc-framework-Quartz, pyobjc-framework-ApplicationServices, mcp"
if command -v uv &>/dev/null; then
  cd "$SKILL_DIR" && uv sync
else
  pip install "atomacos>=3.3.0" "pyobjc-framework-Quartz>=12.1" "pyobjc-framework-ApplicationServices>=12.1" "mcp>=1.26.0"
fi

# 3. Register as OpenClaw plugin
echo ""
echo "[3/4] Registering OpenClaw plugin..."
PLUGIN_DIR="$HOME/.openclaw/extensions/rednote-mac"
if [ -L "$PLUGIN_DIR" ]; then
  echo "  Already exists: $PLUGIN_DIR"
else
  ln -sf "$SKILL_DIR" "$PLUGIN_DIR"
  echo "  Created: $PLUGIN_DIR -> $SKILL_DIR"
fi

# 4. Print next steps
echo ""
echo "[4/4] Done! Run these two commands to activate:"
echo ""
echo "  openclaw config set tools.allow '[\"rednote-mac\"]'"
echo "  openclaw gateway restart"
echo ""
echo "Verify: openclaw plugins list | grep rednote-mac"
echo ""
echo "⚠️  Required: System Settings → Privacy & Security → Accessibility → enable Terminal"
