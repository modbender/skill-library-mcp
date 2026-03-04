#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOME_DIR="${HOME}"
BIN_DIR="$HOME_DIR/bin"
LAUNCH_DIR="$HOME_DIR/Library/LaunchAgents"
STATE_LOG_DIR="$HOME_DIR/.openclaw/logs"

OPENCLAW_BIN="${OPENCLAW_BIN:-$(command -v openclaw || true)}"
if [[ -z "${OPENCLAW_BIN}" ]]; then
  echo "[install] openclaw binary not found in PATH"
  exit 1
fi
OPENCLAW_BIN_DIR="$(dirname "$OPENCLAW_BIN")"

mkdir -p "$BIN_DIR" "$LAUNCH_DIR" "$STATE_LOG_DIR"

install -m 755 "$SCRIPT_DIR/openclaw-session-rotator.sh" "$BIN_DIR/openclaw-session-rotator.sh"

PLIST_TEMPLATE="$SCRIPT_DIR/ai.openclaw.session.rotator.plist.template"
PLIST_TARGET="$LAUNCH_DIR/ai.openclaw.session.rotator.plist"

python3 - "$PLIST_TEMPLATE" "$PLIST_TARGET" "$HOME_DIR" "$OPENCLAW_BIN" "$OPENCLAW_BIN_DIR" <<'PY'
import pathlib, sys
tpl, out, home, oc_bin, oc_bin_dir = map(pathlib.Path, sys.argv[1:6])
text = tpl.read_text(encoding="utf-8")
text = text.replace("__HOME__", str(home))
text = text.replace("__OPENCLAW_BIN__", str(oc_bin))
text = text.replace("__OPENCLAW_BIN_DIR__", str(oc_bin_dir))
out.write_text(text, encoding="utf-8")
PY

launchctl bootout "gui/$(id -u)" "$PLIST_TARGET" >/dev/null 2>&1 || true
launchctl bootstrap "gui/$(id -u)" "$PLIST_TARGET"
launchctl kickstart -k "gui/$(id -u)/ai.openclaw.session.rotator"

echo "[install] done"
echo "[install] script: $BIN_DIR/openclaw-session-rotator.sh"
echo "[install] plist : $PLIST_TARGET"
