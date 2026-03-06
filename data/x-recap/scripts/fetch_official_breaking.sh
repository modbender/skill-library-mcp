#!/usr/bin/env bash
set -euo pipefail

# Fetch official X timelines (AnthropicAI + claudeai) and save full-page screenshots.
# Uses actionbook-rs (workspace/bin/actionbook) with profile=x.

ROOT="$(cd "$(dirname "$0")/.." && pwd)"        # .../skills/x-recap
WS="$(cd "$ROOT/../.." && pwd)"                   # .../workspace (absolute)
AB="$WS/bin/actionbook"
OUT="$WS/output/x-claude-breaking"
mkdir -p "$OUT"
TS="$(date +%Y%m%d_%H%M%S)"

open_and_shot() {
  local url="$1"
  local out="$2"

  echo "[x-recap] open: $url"
  "$AB" --profile x browser open "$url"

  # X is often slow / spinner-y; take a few attempts and require a non-trivial file size.
  local attempt=1
  local max_attempts=4
  while (( attempt <= max_attempts )); do
    echo "[x-recap] screenshot attempt ${attempt}/${max_attempts}: $out"
    rm -f "$out" || true
    "$AB" --profile x browser screenshot --full-page "$out" || true

    if [[ -s "$out" ]]; then
      # Require at least 50KB so we don't accept tiny error/blank artifacts.
      local bytes
      bytes=$(wc -c <"$out" | tr -d ' ')
      if (( bytes >= 51200 )); then
        echo "[x-recap] ok: wrote $(numfmt --to=iec "$bytes" 2>/dev/null || echo "${bytes}B") -> $out"
        return 0
      fi
      echo "[x-recap] warning: screenshot too small (${bytes}B), retrying…"
    else
      echo "[x-recap] warning: screenshot missing/empty, retrying…"
    fi

    attempt=$((attempt+1))
    sleep 5
  done

  echo "[x-recap] ERROR: failed to write a valid screenshot for $url -> $out" >&2
  return 1
}

open_and_shot "https://x.com/AnthropicAI" "$OUT/${TS}_anthropicai.png"
open_and_shot "https://x.com/claudeai"    "$OUT/${TS}_claudeai.png"

echo "Wrote screenshots to: $OUT (prefix $TS)"