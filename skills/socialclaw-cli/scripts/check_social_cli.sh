#!/usr/bin/env sh
set -eu

MIN_VERSION="${1:-0.2.13}"

if ! command -v social >/dev/null 2>&1; then
  echo "ERROR: social CLI not found in PATH. Install with: npm install -g @vishalgojha/social-cli" >&2
  exit 2
fi

VERSION_OUTPUT="$(social --version 2>/dev/null || true)"
if [ -z "$VERSION_OUTPUT" ]; then
  echo "ERROR: social CLI was found but version check failed." >&2
  exit 3
fi

DETECTED="$(printf '%s' "$VERSION_OUTPUT" | sed -E 's/[^0-9]*([0-9]+\.[0-9]+\.[0-9]+).*/\1/')"
if ! printf '%s' "$DETECTED" | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+$'; then
  echo "social CLI detected (raw version: $VERSION_OUTPUT)"
  exit 0
fi

version_ge() {
  awk -v a="$1" -v b="$2" '
    BEGIN {
      na = split(a, aa, ".")
      nb = split(b, bb, ".")
      for (i = 1; i <= 3; i++) {
        va = (i <= na ? aa[i] + 0 : 0)
        vb = (i <= nb ? bb[i] + 0 : 0)
        if (va > vb) exit 0
        if (va < vb) exit 1
      }
      exit 0
    }
  '
}

if ! version_ge "$DETECTED" "$MIN_VERSION"; then
  echo "ERROR: social CLI version $DETECTED is older than required $MIN_VERSION. Upgrade with: npm install -g @vishalgojha/social-cli" >&2
  exit 4
fi

echo "social CLI ready (version $DETECTED)."
