#!/bin/bash
# validate_meta.sh — Validate skill metadata JSON shape.
# Run: ./scripts/validate_meta.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
META_FILE="$SCRIPT_DIR/../_meta.json"

if [[ ! -f "$META_FILE" ]]; then
  echo "Missing metadata file: $META_FILE" >&2
  exit 1
fi

if command -v jq >/dev/null 2>&1; then
  jq -e '
    .name and (.name | type == "string") and
    .description and (.description | type == "string") and
    .metadata.openclaw and
    (.metadata.openclaw["disable-model-invocation"] | type == "boolean") and
    (.metadata.openclaw["user-invocable"] | type == "boolean")
  ' "$META_FILE" >/dev/null
else
  python3 - "$META_FILE" <<'PY'
import json
import sys
path = sys.argv[1]
with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

assert isinstance(data.get("name"), str) and data["name"], "name missing"
assert isinstance(data.get("description"), str) and data["description"], "description missing"
openclaw = data.get("metadata", {}).get("openclaw", {})
assert isinstance(openclaw.get("disable-model-invocation"), bool), "disable-model-invocation must be boolean"
assert isinstance(openclaw.get("user-invocable"), bool), "user-invocable must be boolean"
PY
fi

echo "Metadata valid: $META_FILE"
