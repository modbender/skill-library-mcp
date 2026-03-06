#!/usr/bin/env bash
# OpenClaw OneBot 11 Plugin — 卸载脚本
set -euo pipefail

PLUGIN_DIR="${OPENCLAW_HOME:-$HOME/.openclaw}/plugins/onebot"

if [ -d "$PLUGIN_DIR" ]; then
  rm -rf "$PLUGIN_DIR"
  echo "✅ OneBot plugin removed from $PLUGIN_DIR"
  echo "📝 Remember to remove 'onebot' from openclaw.json channels and restart gateway"
else
  echo "⚠️ Plugin not found at $PLUGIN_DIR"
fi
