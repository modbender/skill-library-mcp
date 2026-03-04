#!/usr/bin/env bash
# RAGFlow health check (ops-only)
# Usage: bash healthcheck.sh
#
# This script intentionally focuses on runtime operations:
# - container status (if docker is available)
# - API liveness/readiness using skill-local helpers
# - basic host resource snapshot
#
# Configuration:
# - Required: RAGFLOW_BASE_URL
# - Optional: RAGFLOW_API_KEY (enables readiness/status checks)
#
# Note: this script focuses on RAGFlow API-level health.
# For backend/datastore checks, rely on `docker compose ps` and logs.

set -euo pipefail

echo "=========================================="
echo "          RAGFlow Health Check"
echo "=========================================="
echo

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

section() {
  echo "$1"
  echo "-------------------------------------------"
}

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PING_PY="$SCRIPT_DIR/ragflow_ping.py"
STATUS_PY="$SCRIPT_DIR/ragflow_status.py"

section "0) Environment"
if [[ -z "${RAGFLOW_BASE_URL:-}" ]]; then
  echo -e "${RED}ERROR${NC}: RAGFLOW_BASE_URL is not set"
  echo "Example: export RAGFLOW_BASE_URL=http://127.0.0.1:9380"
  exit 2
fi

echo "RAGFLOW_BASE_URL=$RAGFLOW_BASE_URL"
if [[ -n "${RAGFLOW_API_KEY:-}" ]]; then
  echo "RAGFLOW_API_KEY=set"
else
  echo "RAGFLOW_API_KEY=not set (readiness checks will be skipped)"
fi

echo
section "1) Container status (if docker is available)"
if command -v docker >/dev/null 2>&1; then
  docker compose ps --format "table {{.Name}}\t{{.Status}}" 2>/dev/null || \
    docker ps --filter "name=ragflow" --format "table {{.Names}}\t{{.Status}}" || true
else
  echo -e "${YELLOW}WARN${NC}: docker is not installed/in PATH"
fi

echo
section "2) API liveness/readiness (ragflow_ping.py)"
if python3 "$PING_PY"; then
  echo -e "${GREEN}OK${NC}: ping"
else
  rc=$?
  echo -e "${RED}ERROR${NC}: ping failed (exit=$rc)"
fi

echo
section "3) API status summary (ragflow_status.py)"
if [[ -n "${RAGFLOW_API_KEY:-}" ]]; then
  if python3 "$STATUS_PY"; then
    echo -e "${GREEN}OK${NC}: status"
  else
    rc=$?
    echo -e "${YELLOW}WARN${NC}: status failed (exit=$rc)"
  fi
else
  echo "SKIP: requires RAGFLOW_API_KEY"
fi

echo
section "4) Disk usage"
df -h | head -n 10 || true

echo
section "5) Memory usage"
free -h 2>/dev/null || echo "N/A"

echo
echo "=========================================="
echo "             Health Check Done"
echo "=========================================="
