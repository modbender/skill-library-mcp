#!/usr/bin/env bash
set -euo pipefail

TEXT="${1:-}"
MODE="${2:-now}"

if [[ -z "$TEXT" ]]; then
  echo "Usage: $0 <text> [mode: now|next-heartbeat]" >&2
  exit 1
fi

# Canonical path (new CLI)
if openclaw gateway call wake --params "{\"text\":\"${TEXT//\"/\\\"}\",\"mode\":\"$MODE\"}" >/dev/null 2>&1; then
  echo "ok"
  exit 0
fi

# Last resort fallback for older CLIs
openclaw gateway wake "$TEXT" --mode "$MODE" >/dev/null

echo "ok"
