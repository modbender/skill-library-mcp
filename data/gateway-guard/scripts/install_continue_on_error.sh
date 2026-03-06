#!/usr/bin/env bash
# Install the combined gateway-guard watcher (one daemon: gateway-back + continue-on-error).
# Redirects to install_watcher.sh so users only ever have one LaunchAgent.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/install_watcher.sh" "$@"
