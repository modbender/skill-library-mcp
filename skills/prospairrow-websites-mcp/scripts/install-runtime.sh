#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNTIME_DIR="${WEBSITES_MCP_DIR:-$HOME/.openclaw/runtime/websites-mcp}"
RUNTIME_SRC="$SKILL_DIR"

if [[ ! -d "$RUNTIME_SRC/src" ]]; then
  echo "Runtime source not found at: $RUNTIME_SRC/src" >&2
  echo "Run this script from the websites-mcp repo layout." >&2
  exit 1
fi

echo "Installing runtime from repository source..."
echo "  Source : $RUNTIME_SRC"
echo "  Target : $RUNTIME_DIR"

mkdir -p "$RUNTIME_DIR"

cp "$RUNTIME_SRC/package.json" "$RUNTIME_DIR/package.json"
cp "$RUNTIME_SRC/tsconfig.json" "$RUNTIME_DIR/tsconfig.json"
cp "$RUNTIME_SRC/site-registry.json" "$RUNTIME_DIR/site-registry.json"
[[ -f "$RUNTIME_SRC/API_SCHEMA.md" ]] && cp "$RUNTIME_SRC/API_SCHEMA.md" "$RUNTIME_DIR/API_SCHEMA.md"
[[ -f "$RUNTIME_SRC/package-lock.json" ]] && cp "$RUNTIME_SRC/package-lock.json" "$RUNTIME_DIR/package-lock.json"
[[ -f "$RUNTIME_SRC/pnpm-lock.yaml" ]] && cp "$RUNTIME_SRC/pnpm-lock.yaml" "$RUNTIME_DIR/pnpm-lock.yaml"
[[ -f "$RUNTIME_SRC/test.mjs" ]] && cp "$RUNTIME_SRC/test.mjs" "$RUNTIME_DIR/test.mjs"

rm -rf "$RUNTIME_DIR/src"
cp -R "$RUNTIME_SRC/src" "$RUNTIME_DIR/src"

cd "$RUNTIME_DIR"
echo "Installing dependencies..."
npm install --ignore-scripts

echo
echo "Runtime ready at: $RUNTIME_DIR"
echo "Next: configure ~/.openclaw/openclaw.json per docs/CONFIGURATION.md"
echo "Then run: PROSPAIRROW_API_KEY='...' npm run mcp:writes"
