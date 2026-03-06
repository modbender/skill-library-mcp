#!/usr/bin/env bash
set -euo pipefail

# Installs a *user-level* systemd service (no sudo).
# Usage:
#   cd agent-wallet-nwc-bridge
#   cp nwc.env.example nwc.env
#   ./install_systemd_user.sh

SERVICE_NAME="agent-wallet-nwc-bridge.service"

# Resolve directory of this script (project root)
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
UNIT_SRC="$SCRIPT_DIR/agent-wallet-nwc-bridge.service"
UNIT_DIR="$HOME/.config/systemd/user"
UNIT_DST="$UNIT_DIR/$SERVICE_NAME"

mkdir -p "$UNIT_DIR"

if [[ ! -f "$SCRIPT_DIR/nwc.env" ]]; then
  echo "Missing nwc.env. Create it first: cp nwc.env.example nwc.env" >&2
  exit 2
fi

# Ensure deps exist
( cd "$SCRIPT_DIR" && npm install --silent )

cp "$UNIT_SRC" "$UNIT_DST"

systemctl --user daemon-reload
systemctl --user enable --now "$SERVICE_NAME"

echo "Installed and started: $SERVICE_NAME"
echo "Check logs: journalctl --user -u $SERVICE_NAME -f"
