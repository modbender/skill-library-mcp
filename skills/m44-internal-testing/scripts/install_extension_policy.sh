#!/usr/bin/env bash
set -euo pipefail

# Install Chromium/Chrome extension policies that allow installation from the Chrome Web Store,
# and optionally force-install a specific extension id.
#
# Usage:
#   ./install_extension_policy.sh [extension-id]
# Example:
#   ./install_extension_policy.sh bonfdkhbkkdoipfojcnimjagphdnfedb

EXT_ID="${1:-}"
UPDATE_URL="https://clients2.google.com/service/update2/crx"

if [ "$(id -u)" -ne 0 ]; then
  SUDO="sudo"
else
  SUDO=""
fi

write_policy_file() {
  local dir="$1"
  local file="$dir/openclaw-extension-policy.json"

  ${SUDO} mkdir -p "$dir"

  if [ -n "$EXT_ID" ]; then
    cat <<EOF | ${SUDO} tee "$file" >/dev/null
{
  "ExtensionInstallSources": [
    "https://chrome.google.com/*",
    "https://clients2.google.com/*",
    "https://chromewebstore.google.com/*"
  ],
  "ExtensionInstallForcelist": [
    "${EXT_ID};${UPDATE_URL}"
  ]
}
EOF
  else
    cat <<'EOF' | ${SUDO} tee "$file" >/dev/null
{
  "ExtensionInstallSources": [
    "https://chrome.google.com/*",
    "https://clients2.google.com/*",
    "https://chromewebstore.google.com/*"
  ]
}
EOF
  fi

  ${SUDO} chmod 644 "$file"
  echo "WROTE:$file"
}

# Debian/Ubuntu Google Chrome + Chromium package locations
write_policy_file "/etc/opt/chrome/policies/managed"
write_policy_file "/etc/chromium/policies/managed"

# Chromium Snap common managed policy paths used in many headless/server setups
write_policy_file "/var/snap/chromium/current/policies/managed"
write_policy_file "/var/snap/chromium/current/chromium-browser/policies/managed"

echo "OK:policy-installed"
echo "NEXT: restart the browser process (or gateway) and verify at chrome://policy"