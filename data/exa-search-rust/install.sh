#!/usr/bin/env bash
# exa-search-rust installer
# Builds the exa-search Rust binary from bundled source and installs the skill.
set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="$HOME/.openclaw/workspace/skills/exa-search-rust"

echo "🦀 Building exa-search binary..."
cd "$SKILL_DIR"
cargo build --release
mkdir -p "$SKILL_DIR/bin"
cp target/release/exa-search "$SKILL_DIR/bin/exa-search"
echo "✅ Binary built → $SKILL_DIR/bin/exa-search"

echo "📦 Installing skill to $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR/bin"
cp "$SKILL_DIR/bin/exa-search" "$INSTALL_DIR/bin/exa-search"
cp "$SKILL_DIR/SKILL.md" "$INSTALL_DIR/SKILL.md"
echo "✅ Skill installed"

echo ""
echo "🔑 API key setup:"
echo "   Add to ~/.openclaw/workspace/.env:"
echo "   EXA_API_KEY=your_key_here"
echo ""
echo "🧪 Test it:"
EXA_BIN="$INSTALL_DIR/bin/exa-search"
echo "   echo '{\"query\":\"hello world\"}' | EXA_API_KEY=your_key $EXA_BIN | jq ."
echo ""
echo "✅ Done."
