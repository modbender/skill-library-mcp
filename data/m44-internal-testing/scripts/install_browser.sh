#!/usr/bin/env bash
set -euo pipefail

# Install browser for DataHive installer.
# Env:
#   BROWSER=chrome|chromium|auto (default: auto)
# Notes:
# - chrome installs via apt (google-chrome-stable)
# - chromium installs via snap (chromium)

BROWSER="${BROWSER:-auto}"

if [ "$(id -u)" -ne 0 ]; then
  SUDO="sudo"
else
  SUDO=""
fi

install_chrome() {
  if ! command -v apt-get >/dev/null 2>&1; then
    echo "ERROR: apt-get not found. Chrome installer supports Debian/Ubuntu only." >&2
    return 2
  fi

  if command -v google-chrome >/dev/null 2>&1; then
    echo "INSTALLED:chrome"
    return 0
  fi

  ${SUDO} apt-get update -y
  ${SUDO} apt-get install -y wget gnupg ca-certificates
  wget -qO- https://dl.google.com/linux/linux_signing_key.pub | ${SUDO} gpg --batch --yes --dearmor -o /usr/share/keyrings/google-linux-signing-keyring.gpg
  echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-linux-signing-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" | ${SUDO} tee /etc/apt/sources.list.d/google-chrome.list >/dev/null
  ${SUDO} apt-get update -y
  ${SUDO} apt-get install -y google-chrome-stable
  echo "OK:installation-attempted:chrome"
}

install_chromium() {
  if command -v chromium >/dev/null 2>&1; then
    echo "INSTALLED:chromium"
    return 0
  fi
  if command -v chromium-browser >/dev/null 2>&1; then
    # On Ubuntu this wrapper may exist even when snap is missing; try version first.
    if chromium-browser --version >/dev/null 2>&1; then
      echo "INSTALLED:chromium-browser"
      return 0
    fi
  fi

  if ! command -v snap >/dev/null 2>&1; then
    echo "ERROR: snap not found. Chromium install requires snap in this environment." >&2
    return 2
  fi

  # Recover from stale failed install path if present.
  if [ -d /var/snap/chromium/current ] && [ ! -L /var/snap/chromium/current ]; then
    ${SUDO} rm -rf /var/snap/chromium/current || true
  fi

  ${SUDO} snap install chromium
  echo "OK:installation-attempted:chromium"
}

case "$BROWSER" in
  chrome)
    install_chrome
    ;;
  chromium)
    install_chromium
    ;;
  auto)
    install_chrome || install_chromium
    ;;
  *)
    echo "ERROR: unsupported BROWSER='$BROWSER' (use auto|chrome|chromium)" >&2
    exit 2
    ;;
esac
