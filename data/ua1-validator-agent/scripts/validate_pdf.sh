#!/usr/bin/env bash
set -euo pipefail

FILE_PATH="${1:-}"
if [[ -z "$FILE_PATH" ]]; then
  echo "Usage: $0 <pdf-file>" >&2
  exit 1
fi

if [[ ! -f "$FILE_PATH" ]]; then
  echo "File not found: $FILE_PATH" >&2
  exit 1
fi

UA1_API_BASE="${UA1_API_BASE:-https://api.ua1.dev}"
UA1_FORMAT="${UA1_FORMAT:-compact}"

if [[ "$UA1_FORMAT" == "compact" ]]; then
  URL="$UA1_API_BASE/api/validate?format=compact"
else
  URL="$UA1_API_BASE/api/validate"
fi

TMP_BODY="$(mktemp)"
TMP_HEADERS="$(mktemp)"

HTTP_CODE="$(curl -sS -D "$TMP_HEADERS" -o "$TMP_BODY" -w '%{http_code}' \
  -X POST "$URL" \
  -F "file=@${FILE_PATH}")"

if [[ "$HTTP_CODE" != "200" ]]; then
  echo "UA1 API error: HTTP $HTTP_CODE" >&2
  cat "$TMP_BODY" >&2
  rm -f "$TMP_BODY" "$TMP_HEADERS"
  exit 1
fi

cat "$TMP_BODY"

VERDICT="$(jq -r '.verdict // empty' "$TMP_BODY" 2>/dev/null || true)"
rm -f "$TMP_BODY" "$TMP_HEADERS"

if [[ "$VERDICT" == "pass" ]]; then
  exit 0
fi

if [[ "$VERDICT" == "fail" ]]; then
  exit 2
fi

exit 1
