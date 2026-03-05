#!/usr/bin/env bash
# ipeaky - Native macOS secure key input
# Usage: ./secure_input_mac.sh <KEY_NAME>
# Pops a native macOS dialog with hidden input, outputs the key to stdout.
# The caller (agent) captures stdout and stores via gateway config.patch.

set -euo pipefail

KEY_NAME="${1:?Usage: secure_input_mac.sh <KEY_NAME>}"

# Sanitize KEY_NAME to prevent AppleScript injection via special characters
# Removes quotes, backticks, dollar signs, and other chars that could break
# out of the AppleScript string or trigger shell expansion in the heredoc.
SAFE_KEY_NAME=$(echo "$KEY_NAME" | sed 's/["`$;\\|&<>(){}!'\'']//_/g' | tr -s '_')

# Native macOS hidden-input dialog → outputs key to stdout
KEY=$(osascript -e "set theKey to text returned of (display dialog \"Paste your ${SAFE_KEY_NAME}:\" default answer \"\" with hidden answer with title \"ipeaky\" with icon caution)" -e "return theKey" 2>/dev/null)

if [ -z "$KEY" ]; then
  echo "ERROR: No key provided" >&2
  exit 1
fi

echo -n "$KEY"
