#!/usr/bin/env bash
# CleanApp v1 single-item ingest helper (Fetcher Key System)
#
# This is a convenience wrapper around the v1 quarantine-first ingest surface:
#   POST /v1/reports:bulkIngest
#
# Notes:
# - Requires CLEANAPP_API_TOKEN (Bearer key).
# - Default behavior is quarantine-first on the backend (shadow visibility for new fetchers).
# - Supports --dry-run (no network).

set -euo pipefail

BASE_URL="${CLEANAPP_BASE_URL:-https://live.cleanapp.io}"
ENDPOINT="/v1/reports:bulkIngest"

TITLE=""
DESCRIPTION=""
LAT=""
LNG=""
SOURCE_ID=""
COLLECTED_AT=""
AGENT_ID="${CLEANAPP_AGENT_ID:-cleanapp-agent001}"
AGENT_VERSION="${CLEANAPP_AGENT_VERSION:-1.0}"
SOURCE_TYPE="${CLEANAPP_SOURCE_TYPE:-text}"
SOURCE_URL=""
DRY_RUN="false"
NO_LOCATION="false"
APPROX_LOCATION="false"
APPROX_DECIMALS="2"

usage() {
  cat <<USAGE
CleanApp v1 ingest helper

Usage:
  $0 --title "..." --description "..." [options]

Required:
  --title TEXT
  --description TEXT

Optional:
  --lat FLOAT
  --lng FLOAT
  --source-id STR           Idempotency key. If omitted, one is generated.
  --collected-at ISO8601    UTC timestamp (e.g. 2026-02-15T09:00:00Z). Defaults to now.
  --source-type STR         text|vision|sensor|web (default: ${SOURCE_TYPE})
  --source-url URL          Included verbatim in the description for context.
  --no-location             Remove lat/lng entirely
  --approx-location         Round lat/lng to reduce precision
  --approx-decimals N       Decimals for --approx-location (default: ${APPROX_DECIMALS})
  --base-url URL            Default: ${BASE_URL}
  --dry-run                 Print payload and exit without sending

Environment:
  CLEANAPP_API_TOKEN        Required unless --dry-run. Bearer token for authentication.
  CLEANAPP_BASE_URL         Optional base URL (default: https://live.cleanapp.io)
  CLEANAPP_AGENT_ID         Optional (default: cleanapp-agent001)
  CLEANAPP_AGENT_VERSION    Optional (default: 1.0)
  CLEANAPP_SOURCE_TYPE      Optional (default: text)

Examples:
  export CLEANAPP_API_TOKEN="cleanapp_fk_live_..."
  $0 --title "Broken elevator" --description "Elevator stuck on floor 3" --lat 34.0702 --lng -118.4441 --approx-location

  $0 --title "Phishing page" --description "Fake login page" --source-type web --source-url "https://example.com" --dry-run
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --title) TITLE="$2"; shift 2 ;;
    --description) DESCRIPTION="$2"; shift 2 ;;
    --lat) LAT="$2"; shift 2 ;;
    --lng) LNG="$2"; shift 2 ;;
    --source-id) SOURCE_ID="$2"; shift 2 ;;
    --collected-at) COLLECTED_AT="$2"; shift 2 ;;
    --source-type) SOURCE_TYPE="$2"; shift 2 ;;
    --source-url) SOURCE_URL="$2"; shift 2 ;;
    --no-location) NO_LOCATION="true"; shift ;;
    --approx-location) APPROX_LOCATION="true"; shift ;;
    --approx-decimals) APPROX_DECIMALS="$2"; shift 2 ;;
    --base-url) BASE_URL="$2"; shift 2 ;;
    --dry-run) DRY_RUN="true"; shift ;;
    --help|-h) usage; exit 0 ;;
    *) echo "Unknown option: $1"; usage; exit 2 ;;
  esac
done

if [[ -z "${TITLE}" || -z "${DESCRIPTION}" ]]; then
  echo "Error: --title and --description are required" >&2
  usage
  exit 2
fi

if [[ -z "${COLLECTED_AT}" ]]; then
  COLLECTED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
fi

if [[ -z "${SOURCE_ID}" ]]; then
  # Idempotency key. Caller can override to make retries safe.
  SOURCE_ID="openclaw_${AGENT_ID}_$(date -u +%Y%m%dT%H%M%S)_$(head -c 8 /dev/urandom | xxd -p)"
fi

if [[ "${NO_LOCATION}" == "true" ]]; then
  LAT=""; LNG=""
fi

if [[ "${APPROX_LOCATION}" == "true" ]]; then
  if [[ -n "${LAT}" ]]; then
    LAT="$(python3 - <<PY
import sys
print(round(float(sys.argv[1]), int(sys.argv[2])))
PY
"${LAT}" "${APPROX_DECIMALS}")"
  fi
  if [[ -n "${LNG}" ]]; then
    LNG="$(python3 - <<PY
import sys
print(round(float(sys.argv[1]), int(sys.argv[2])))
PY
"${LNG}" "${APPROX_DECIMALS}")"
  fi
fi

if [[ -n "${SOURCE_URL}" ]]; then
  DESCRIPTION="${DESCRIPTION}\n\nSource URL: ${SOURCE_URL}"
fi

payload="$(
python3 - <<PY
import json
import sys

payload = {
  "items": [
    {
      "source_id": sys.argv[1],
      "title": sys.argv[2],
      "description": sys.argv[3],
      "collected_at": sys.argv[4],
      "agent_id": sys.argv[5],
      "agent_version": sys.argv[6],
      "source_type": sys.argv[7],
    }
  ]
}

lat = sys.argv[8]
lng = sys.argv[9]
if lat.strip() and lng.strip():
  payload["items"][0]["lat"] = float(lat)
  payload["items"][0]["lng"] = float(lng)

print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
PY
"${SOURCE_ID}" "${TITLE}" "${DESCRIPTION}" "${COLLECTED_AT}" "${AGENT_ID}" "${AGENT_VERSION}" "${SOURCE_TYPE}" "${LAT}" "${LNG}"
)"

url="${BASE_URL%/}${ENDPOINT}"

if [[ "${DRY_RUN}" == "true" ]]; then
  echo "=== DRY RUN (no network) ==="
  echo "URL: ${url}"
  echo "Token: ${CLEANAPP_API_TOKEN:+set (hidden)}"
  echo "Payload:" 
  echo "${payload}" | python3 -m json.tool 2>/dev/null || echo "${payload}"
  exit 0
fi

if [[ -z "${CLEANAPP_API_TOKEN:-}" ]]; then
  echo "Error: missing CLEANAPP_API_TOKEN env var" >&2
  exit 2
fi

echo "Submitting 1 item to ${url} (source_id=${SOURCE_ID})"
resp="$(
  curl -sS -w "\n%{http_code}" \
    -X POST "${url}" \
    -H "authorization: Bearer ${CLEANAPP_API_TOKEN}" \
    -H "content-type: application/json" \
    -d "${payload}"
)"

http_code="$(echo "${resp}" | tail -n 1)"
body="$(echo "${resp}" | sed '$d')"

if [[ "${http_code}" =~ ^2 ]]; then
  echo "OK (http=${http_code})"
  echo "${body}"
  exit 0
fi

echo "ERROR (http=${http_code})" >&2
printf '%s\n' "${body}" >&2
exit 1
