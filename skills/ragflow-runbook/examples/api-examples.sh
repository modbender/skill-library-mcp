#!/usr/bin/env bash
# RAGFlow ops API examples (system endpoints only)
#
# Before running:
# - Export RAGFLOW_BASE_URL and (optionally) RAGFLOW_API_KEY
#
# NOTE: API paths may differ across versions. When in doubt, check:
#   curl -sS "$RAGFLOW_BASE_URL/openapi.json" | head

set -euo pipefail

for bin in curl; do
  if ! command -v "$bin" >/dev/null 2>&1; then
    echo "ERROR: required dependency '$bin' is not installed/in PATH."
    exit 1
  fi
done

RAGFLOW_BASE_URL=${RAGFLOW_BASE_URL:-"http://localhost:9380"}
RAGFLOW_API_KEY=${RAGFLOW_API_KEY:-""}

echo "=========================================="
echo "      RAGFlow Ops API Examples"
echo "=========================================="
echo

echo "0) Liveness: openapi.json"
echo "-------------------------------------------"
curl -sS -o /dev/null -w "HTTP %{http_code}\n" "$RAGFLOW_BASE_URL/openapi.json" || true
echo

echo "1) System ping"
echo "-------------------------------------------"
if [[ -n "$RAGFLOW_API_KEY" ]]; then
  curl -sS -o /dev/null -w "HTTP %{http_code}\n" "$RAGFLOW_BASE_URL/v1/system/ping" \
    -H "Authorization: Bearer $RAGFLOW_API_KEY" || true
else
  curl -sS -o /dev/null -w "HTTP %{http_code}\n" "$RAGFLOW_BASE_URL/v1/system/ping" || true
fi
echo

echo "2) System status (requires auth)"
echo "-------------------------------------------"
if [[ -z "$RAGFLOW_API_KEY" ]]; then
  echo "SKIP: RAGFLOW_API_KEY is not set."
else
  curl -sS -o /dev/null -w "HTTP %{http_code}\n" "$RAGFLOW_BASE_URL/v1/system/status" \
    -H "Authorization: Bearer $RAGFLOW_API_KEY" || true
fi
echo

echo "=========================================="
echo "              Examples Done"
echo "=========================================="
