#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8080}"
MODE="${1:-}"
ARG="${2:-}"
TIMEOUT="${TIMEOUT:-20}"

if [[ -z "$MODE" ]]; then
  echo '{"error":"usage: route_whatsapp.sh <process|decode> <text|image_path>"}'
  exit 2
fi

case "$MODE" in
  process)
    if [[ -z "$ARG" ]]; then
      echo '{"error":"missing text argument for process mode"}'
      exit 2
    fi

    # JSON-encode the arbitrary input safely via python.
    PAYLOAD="$(python3 - <<'PY' "$ARG"
import json,sys
print(json.dumps({"number": sys.argv[1]}, ensure_ascii=False))
PY
)"

    curl --silent --show-error --max-time "$TIMEOUT" \
      -X POST "$BASE_URL/process" \
      -H 'Content-Type: application/json' \
      -d "$PAYLOAD"
    ;;

  decode)
    if [[ -z "$ARG" ]]; then
      echo '{"error":"missing image path argument for decode mode"}'
      exit 2
    fi
    if [[ ! -f "$ARG" ]]; then
      printf '{"error":"image file not found: %s"}\n' "$ARG"
      exit 2
    fi

    curl --silent --show-error --max-time "$TIMEOUT" \
      -X POST "$BASE_URL/decode-qr" \
      -F "image=@$ARG"
    ;;

  *)
    echo '{"error":"invalid mode; use process or decode"}'
    exit 2
    ;;
esac
