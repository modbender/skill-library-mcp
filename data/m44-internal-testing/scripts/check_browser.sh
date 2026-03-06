#!/usr/bin/env bash
set -euo pipefail

# Check browser availability for DataHive installer.
# Env:
#   BROWSER=auto|chrome|chromium (default: auto)

BROWSER="${BROWSER:-auto}"

check_chrome() {
  if command -v google-chrome >/dev/null 2>&1; then
    v="$(google-chrome --version 2>/dev/null || echo 'version-unknown')"
    echo "FOUND:chrome:$v"
    return 0
  fi
  return 1
}

check_chromium() {
  if command -v chromium >/dev/null 2>&1; then
    v="$(chromium --version 2>/dev/null || echo 'version-unknown')"
    echo "FOUND:chromium:$v"
    return 0
  fi
  if command -v chromium-browser >/dev/null 2>&1; then
    v="$(chromium-browser --version 2>/dev/null || echo 'version-unknown')"
    echo "FOUND:chromium-browser:$v"
    return 0
  fi
  return 1
}

case "$BROWSER" in
  chrome)
    check_chrome || { echo "FOUND:none"; exit 1; }
    ;;
  chromium)
    check_chromium || { echo "FOUND:none"; exit 1; }
    ;;
  auto)
    check_chrome || check_chromium || { echo "FOUND:none"; exit 1; }
    ;;
  *)
    echo "ERROR: unsupported BROWSER='$BROWSER' (use auto|chrome|chromium)" >&2
    exit 2
    ;;
esac
