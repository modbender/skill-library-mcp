#!/usr/bin/env bash
# Detects installed torrent clients and outputs JSON.
# Usage: ./detect-client.sh

set -euo pipefail

# --- OS Detection ---
os_name=$(uname -s)
distro="unknown"

case "$os_name" in
  Linux)
    if [ -f /etc/os-release ]; then
      # shellcheck source=/dev/null
      distro=$(. /etc/os-release && echo "${ID:-unknown}")
    fi
    ;;
  Darwin)
    distro="macos"
    ;;
  MINGW*|MSYS*|CYGWIN*)
    os_name="Windows"
    distro="windows"
    ;;
esac

# --- Client Detection ---

# Transmission
transmission_remote_path=$(command -v transmission-remote 2>/dev/null || true)
transmission_gtk_path=$(command -v transmission-gtk 2>/dev/null || true)
transmission_qt_path=$(command -v transmission-qt 2>/dev/null || true)
transmission_daemon_path=$(command -v transmission-daemon 2>/dev/null || true)
transmission_path="${transmission_remote_path:-${transmission_gtk_path:-${transmission_qt_path:-${transmission_daemon_path:-}}}}"
transmission_installed="false"
transmission_daemon="false"
transmission_remote_available="false"
transmission_variant="none"
if [ -n "$transmission_path" ]; then
  transmission_installed="true"
  if [ -n "$transmission_remote_path" ]; then
    transmission_remote_available="true"
    transmission_variant="cli"
    if transmission-remote -l >/dev/null 2>&1; then
      transmission_daemon="true"
    fi
  elif [ -n "$transmission_gtk_path" ]; then
    transmission_variant="gtk"
  elif [ -n "$transmission_qt_path" ]; then
    transmission_variant="qt"
  elif [ -n "$transmission_daemon_path" ]; then
    transmission_variant="daemon"
  fi
fi

# aria2
aria2_path=$(command -v aria2c 2>/dev/null || true)
aria2_installed="false"
aria2_daemon="false"
if [ -n "$aria2_path" ]; then
  aria2_installed="true"
  if curl -sf http://localhost:6800/jsonrpc -d '{"jsonrpc":"2.0","id":"test","method":"aria2.getVersion"}' >/dev/null 2>&1; then
    aria2_daemon="true"
  fi
fi

# --- Preferred Client ---
preferred="none"
if [ "$transmission_installed" = "true" ]; then
  preferred="transmission"
elif [ "$aria2_installed" = "true" ]; then
  preferred="aria2"
fi

# --- JSON Output ---
jq -n \
  --arg os "$os_name" \
  --arg distro "$distro" \
  --argjson t_installed "$transmission_installed" \
  --arg t_path "${transmission_path:-}" \
  --arg t_variant "$transmission_variant" \
  --argjson t_remote "$transmission_remote_available" \
  --argjson t_daemon "$transmission_daemon" \
  --argjson a_installed "$aria2_installed" \
  --arg a_path "${aria2_path:-}" \
  --argjson a_daemon "$aria2_daemon" \
  --arg preferred "$preferred" \
  '{
    os: $os,
    distro: $distro,
    clients: {
      transmission: {
        installed: $t_installed,
        path: (if $t_path == "" then null else $t_path end),
        variant: $t_variant,
        remoteAvailable: $t_remote,
        daemonRunning: $t_daemon
      },
      aria2: {
        installed: $a_installed,
        path: (if $a_path == "" then null else $a_path end),
        daemonRunning: $a_daemon
      }
    },
    preferred: $preferred
  }'
