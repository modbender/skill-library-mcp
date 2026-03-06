#!/usr/bin/env bash
# watchclaw installer — curl -fsSL https://raw.githubusercontent.com/jarvis4wang/watchclaw/main/install.sh | bash
set -euo pipefail

REPO="jarvis4wang/watchclaw"
BRANCH="main"
BASE="https://raw.githubusercontent.com/${REPO}/${BRANCH}"
INSTALL_DIR="${WATCHCLAW_INSTALL_DIR:-$HOME/.local/bin}"

FILES=(watchclaw watchclaw.sh)

echo "🦞 Installing watchclaw to $INSTALL_DIR ..."

mkdir -p "$INSTALL_DIR"

for f in "${FILES[@]}"; do
  curl -fsSL "$BASE/$f" -o "$INSTALL_DIR/$f"
  chmod +x "$INSTALL_DIR/$f"
done

# Drop example config if none exists
CONF_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/watchclaw"
if [[ ! -f "$CONF_DIR/watchclaw.conf" ]]; then
  mkdir -p "$CONF_DIR"
  curl -fsSL "$BASE/watchclaw.conf.example" -o "$CONF_DIR/watchclaw.conf.example"
  echo "📄 Example config saved to $CONF_DIR/watchclaw.conf.example"
fi

# Check PATH
if ! echo "$PATH" | tr ':' '\n' | grep -qx "$INSTALL_DIR"; then
  echo ""
  echo "⚠️  $INSTALL_DIR is not in your PATH. Add it:"
  echo "   export PATH=\"$INSTALL_DIR:\$PATH\""
  echo ""
fi

echo "✅ watchclaw installed. Run: watchclaw --help"
