#!/usr/bin/env bash
# Adds a magnet link to a detected torrent client.
# Usage: ./add-torrent.sh "<magnet_url>" [--client transmission|aria2] [--download-dir /path]
#
# Exit codes:
#   0 - Success
#   1 - Invalid parameters
#   2 - No torrent client found
#   3 - Client error (failed to add)

set -euo pipefail

# --- Parse Arguments ---
magnet_url=""
client=""
download_dir=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --client)
      client="$2"
      shift 2
      ;;
    --download-dir)
      download_dir="$2"
      shift 2
      ;;
    -*)
      echo "Error: Unknown option $1" >&2
      exit 1
      ;;
    *)
      if [ -z "$magnet_url" ]; then
        magnet_url="$1"
      fi
      shift
      ;;
  esac
done

if [ -z "$magnet_url" ]; then
  echo "Error: Magnet URL is required" >&2
  echo "Usage: $0 \"<magnet_url>\" [--client transmission|aria2] [--download-dir /path]" >&2
  exit 1
fi

# --- Validate magnet URL format ---
if [[ ! "$magnet_url" =~ ^magnet:\?xt=urn:btih:[a-fA-F0-9]{40} ]] && \
   [[ ! "$magnet_url" =~ ^magnet:\?xt=urn:btih:[a-zA-Z2-7]{32} ]]; then
  echo "Error: Invalid magnet URL format. Expected: magnet:?xt=urn:btih:<hash>" >&2
  exit 1
fi

# --- Auto-detect client if not specified ---
if [ -z "$client" ]; then
  if command -v transmission-remote >/dev/null 2>&1; then
    client="transmission"
  elif command -v aria2c >/dev/null 2>&1; then
    client="aria2"
  else
    echo "Error: No torrent client detected. Install transmission-cli or aria2." >&2
    exit 2
  fi
fi

# --- Add torrent ---
case "$client" in
  transmission)
    args=(-a "$magnet_url")
    if [ -n "$download_dir" ]; then
      args+=(-w "$download_dir")
    fi
    echo "Adding to Transmission..."
    if transmission-remote "${args[@]}"; then
      echo "Torrent added to Transmission successfully."
    else
      echo "Error: Failed to add torrent to Transmission. Is the daemon running?" >&2
      echo "Start it with: transmission-daemon" >&2
      exit 3
    fi
    ;;
  aria2)
    # Check if aria2 RPC is running
    if curl -sf http://localhost:6800/jsonrpc -d '{"jsonrpc":"2.0","id":"test","method":"aria2.getVersion"}' >/dev/null 2>&1; then
      echo "Adding to aria2 via RPC..."
      if [ -n "$download_dir" ]; then
        payload=$(jq -n --arg url "$magnet_url" --arg dir "$download_dir" \
          '{"jsonrpc":"2.0","id":"add","method":"aria2.addUri","params":[[$url],{"dir":$dir}]}')
      else
        payload=$(jq -n --arg url "$magnet_url" \
          '{"jsonrpc":"2.0","id":"add","method":"aria2.addUri","params":[[$url]]}')
      fi
      result=$(curl -sf http://localhost:6800/jsonrpc -d "$payload")
      if echo "$result" | grep -q '"result"'; then
        echo "Torrent added to aria2 successfully."
      else
        echo "Error: aria2 RPC rejected the request." >&2
        exit 3
      fi
    else
      # Direct download mode
      echo "Adding to aria2 (direct mode)..."
      args=("$magnet_url")
      if [ -n "$download_dir" ]; then
        args+=(--dir="$download_dir")
      fi
      aria2c "${args[@]}" &
      echo "aria2 download started in background (PID: $!)."
    fi
    ;;
  *)
    echo "Error: Unknown client '$client'. Supported: transmission, aria2" >&2
    exit 1
    ;;
esac
