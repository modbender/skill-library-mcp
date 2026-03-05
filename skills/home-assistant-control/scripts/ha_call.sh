#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/ha_env.sh"

: "${HA_TOKEN:?Missing HA_TOKEN}"
: "${HA_URL_PUBLIC:?Missing HA_URL_PUBLIC}"

METHOD="${1:-GET}"   # GET/POST
METHOD="$(printf '%s' "$METHOD" | tr '[:lower:]' '[:upper:]')"
PATH_PART="${2:-/api/states}"
DATA="${3:-}"

if [[ "$METHOD" != "GET" && "$METHOD" != "POST" ]]; then
  echo "Error: Unsupported method '$METHOD'. Use GET or POST." >&2
  exit 1
fi

if [[ "$PATH_PART" != /api/* ]]; then
  echo "Error: Path must start with /api/ (got: $PATH_PART)" >&2
  exit 1
fi

# URL resolution:
# 1) HA_URL (explicit override; no fallback)
# 2) HA_URL_LOCAL (preferred)
# 3) HA_URL_PUBLIC (fallback if local transport fails)

CANDIDATES=()
if [[ -n "${HA_URL:-}" ]]; then
  CANDIDATES+=("${HA_URL%/}")
elif [[ -n "${HA_URL_LOCAL:-}" ]]; then
  CANDIDATES+=("${HA_URL_LOCAL%/}")
  if [[ -n "${HA_URL_PUBLIC:-}" && "${HA_URL_PUBLIC%/}" != "${HA_URL_LOCAL%/}" ]]; then
    CANDIDATES+=("${HA_URL_PUBLIC%/}")
  fi
else
  CANDIDATES+=("${HA_URL_PUBLIC%/}")
fi

for base in "${CANDIDATES[@]}"; do
  if [[ "$base" != http://* && "$base" != https://* ]]; then
    echo "Error: Invalid URL scheme in '$base'. Use http:// or https://" >&2
    exit 1
  fi
done

attempt_request() {
  local base_url="$1"

  if [[ "$METHOD" == "GET" ]]; then
    curl -sS \
      --connect-timeout 8 \
      --max-time 20 \
      -H "Authorization: Bearer $HA_TOKEN" \
      -H "Content-Type: application/json" \
      "$base_url$PATH_PART"
  else
    curl -sS -X "$METHOD" \
      --connect-timeout 8 \
      --max-time 20 \
      -H "Authorization: Bearer $HA_TOKEN" \
      -H "Content-Type: application/json" \
      -d "$DATA" \
      "$base_url$PATH_PART"
  fi
}

LAST_ERR=""
for i in "${!CANDIDATES[@]}"; do
  base="${CANDIDATES[$i]}"
  if output="$(attempt_request "$base" 2>&1)"; then
    if [[ "$i" -gt 0 ]]; then
      echo "[ha_call] Switched to fallback URL: $base" >&2
    fi
    printf '%s' "$output"
    exit 0
  fi
  LAST_ERR="$output"
  # Fallback is only for transport-level errors (DNS/refused/timeout/etc).
  # HTTP API errors are handled by caller scripts based on response body.
  if [[ "$i" -lt $((${#CANDIDATES[@]} - 1)) ]]; then
    echo "[ha_call] Primary URL failed, trying fallback..." >&2
  fi
done

echo "$LAST_ERR" >&2
exit 1
