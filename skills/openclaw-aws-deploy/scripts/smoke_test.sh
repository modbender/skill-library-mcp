#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<USAGE
Usage: $0 --endpoint <url> --gateway-token <token> [--auth-path <path>] [--output <path>]
USAGE
}

ENDPOINT=""
TOKEN=""
AUTH_PATH="/status"
OUTPUT="./smoke-test-report.json"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --endpoint) ENDPOINT="${2:-}"; shift 2 ;;
    --gateway-token) TOKEN="${2:-}"; shift 2 ;;
    --auth-path) AUTH_PATH="${2:-}"; shift 2 ;;
    --output) OUTPUT="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $1"; usage; exit 2 ;;
  esac
done

[[ -n "$ENDPOINT" ]] || { echo "--endpoint required" >&2; exit 1; }
[[ -n "$TOKEN" ]] || { echo "--gateway-token required" >&2; exit 1; }

health_status="fail"
auth_status="fail"
health_code=$(curl -sS -o /dev/null -w "%{http_code}" "$ENDPOINT/health" || true)
auth_code=$(curl -sS -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $TOKEN" "$ENDPOINT$AUTH_PATH" || true)

if [[ "$health_code" =~ ^2[0-9][0-9]$ ]]; then health_status="pass"; fi
if [[ "$auth_code" =~ ^2[0-9][0-9]$ ]]; then auth_status="pass"; fi

overall="pass"
if [[ "$health_status" != "pass" || "$auth_status" != "pass" ]]; then
  overall="fail"
fi

mkdir -p "$(dirname "$OUTPUT")"
jq -n \
  --arg schemaVersion "1.1" \
  --arg generatedAt "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --arg overall "$overall" \
  --arg endpoint "$ENDPOINT" \
  --arg authPath "$AUTH_PATH" \
  --arg health "$health_status" \
  --arg auth "$auth_status" \
  --arg healthCode "$health_code" \
  --arg authCode "$auth_code" \
  '{schemaVersion:$schemaVersion, generatedAt:$generatedAt, overall:$overall, endpoint:$endpoint, authPath:$authPath, checks:{health:$health,auth:$auth}, http:{health:$healthCode,auth:$authCode}}' > "$OUTPUT"

echo "Smoke report: $OUTPUT"
[[ "$overall" == "pass" ]]
