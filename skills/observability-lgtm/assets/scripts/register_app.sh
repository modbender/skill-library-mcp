#!/usr/bin/env bash
# register_app.sh <service_name> <port>
# Adds a native Mac app to Prometheus file-based service discovery.
# Prometheus hot-reloads the target within 30 seconds (no restart needed).
#
# Usage:
#   ./scripts/register_app.sh image-gen-studio 7860
#   ./scripts/register_app.sh hybrid-control-plane 8765

set -euo pipefail

SERVICE="${1:?Usage: $0 <service_name> <port>}"
PORT="${2:?Usage: $0 <service_name> <port>}"

TARGETS_DIR="$(cd "$(dirname "$0")/../config/prometheus/targets" && pwd)"
TARGET_FILE="${TARGETS_DIR}/${SERVICE}.json"

cat > "${TARGET_FILE}" <<JSON
[
  {
    "targets": ["host.docker.internal:${PORT}"],
    "labels": {
      "job": "${SERVICE}",
      "service": "${SERVICE}",
      "env": "dev"
    }
  }
]
JSON

echo "✅ Registered: ${SERVICE} → host.docker.internal:${PORT}"
echo "   Target file: ${TARGET_FILE}"
echo "   Prometheus will pick this up within 30 seconds."
echo ""
echo "   Verify:  curl -s localhost:9091/api/v1/targets | jq '.data.activeTargets[] | select(.labels.service == \"${SERVICE}\")'"
