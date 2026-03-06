#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   export HA_URL_LOCAL=http://homeassistant.local:8123
#   # or export HA_URL_PUBLIC=https://your-home.example.com
#   export HA_TOKEN=...
#   ./scripts/examples.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CALL="$SCRIPT_DIR/ha_call.sh"

echo "1) List all states"
"$CALL" GET /api/states | head -c 1200; echo -e "\n"

echo "2) Check one entity"
"$CALL" GET /api/states/light.example_living_room | head -c 1200; echo -e "\n"

echo "3) Turn on a light"
"$CALL" POST /api/services/light/turn_on '{"entity_id":"light.example_living_room","brightness_pct":60}'
