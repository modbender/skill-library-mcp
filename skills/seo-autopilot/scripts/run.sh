#!/usr/bin/env bash
set -euo pipefail

SITE="${1:-boll-koll.se}"

if [[ "$SITE" != "boll-koll.se" && "$SITE" != "hyresbyte.se" ]]; then
  echo "ERROR: invalid site: $SITE"
  exit 2
fi

OUT="$(seo-autopilot "$SITE" 2>&1 || true)"

PR_URL="$(printf "%s\n" "$OUT" | sed -n 's/^PR: \(https\?:\/\/\S\+\).*$/\1/p' | head -n 1)"

echo "PR: ${PR_URL:-}"
echo "$OUT"
