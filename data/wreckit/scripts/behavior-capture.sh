#!/usr/bin/env bash
# wreckit — Behavior Capture gate (REBUILD mode)
# Captures golden fixtures from current implementation before rebuilding
# Usage: ./behavior-capture.sh [project-path] [test-cmd]
# Output: JSON + writes .wreckit/behavior-snapshots/ with captured outputs

set -euo pipefail
PROJECT="${1:-.}"
TEST_CMD="${2:-}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT="$(cd "$PROJECT" && pwd)"
cd "$PROJECT"

STACK_JSON=$("$SCRIPT_DIR/detect-stack.sh" "$PROJECT" 2>/dev/null || true)
LANG=$(echo "$STACK_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('language','unknown'))" 2>/dev/null || echo "unknown")
if [ -z "$TEST_CMD" ]; then
  TEST_CMD=$(echo "$STACK_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('commands',{}).get('test','none'))" 2>/dev/null || echo "none")
fi

SNAP_DIR="$PROJECT/.wreckit/behavior-snapshots/$(date +%Y%m%d%H%M%S)"
mkdir -p "$SNAP_DIR"

STATUS="PASS"

if [ -z "$TEST_CMD" ] || [ "$TEST_CMD" = "none" ]; then
  STATUS="WARN"
  TEST_OUTPUT="No test command detected."
else
  TEST_EXIT=0
  TEST_OUTPUT=$(eval "$TEST_CMD" 2>&1) || TEST_EXIT=$?
  if [ "$TEST_EXIT" -ne 0 ]; then
    STATUS="FAIL"
  fi
fi

echo "$TEST_OUTPUT" > "$SNAP_DIR/test-output.txt"

# Capture function signatures
SIGNATURES_FILE="$SNAP_DIR/signatures.txt"
APIS_FILE="$SNAP_DIR/api-shapes.txt"
CLI_FILE="$SNAP_DIR/cli-examples.txt"

case "$LANG" in
  typescript|javascript)
    rg -n "export (async )?function|export const|module\.exports" . --glob '!node_modules/**' --glob '!dist/**' --glob '!\.git/**' | head -200 > "$SIGNATURES_FILE" || true
    rg -n "^(export )?(interface|type|class) " . --glob '!node_modules/**' --glob '!dist/**' --glob '!\.git/**' | head -200 > "$APIS_FILE" || true
    if [ -f package.json ]; then
      rg -n '"bin"|"cli"' package.json | head -200 > "$CLI_FILE" || true
    else
      echo "No package.json found" > "$CLI_FILE"
    fi
    ;;
  python)
    rg -n "^def |^class " . --glob '!venv/**' --glob '!\.git/**' --glob '!__pycache__/**' | head -200 > "$SIGNATURES_FILE" || true
    rg -n "^class " . --glob '!venv/**' --glob '!\.git/**' --glob '!__pycache__/**' | head -200 > "$APIS_FILE" || true
    rg -n "if __name__ == ['\"]__main__['\"]" . --glob '!venv/**' --glob '!\.git/**' | head -200 > "$CLI_FILE" || true
    ;;
  go)
    rg -n "^func " . --glob '!vendor/**' --glob '!\.git/**' | head -200 > "$SIGNATURES_FILE" || true
    rg -n "^type " . --glob '!vendor/**' --glob '!\.git/**' | head -200 > "$APIS_FILE" || true
    rg -n "package main|func main\(" . --glob '!vendor/**' --glob '!\.git/**' | head -200 > "$CLI_FILE" || true
    ;;
  rust)
    rg -n "^pub fn |^fn " . --glob '!target/**' --glob '!\.git/**' | head -200 > "$SIGNATURES_FILE" || true
    rg -n "^pub struct |^struct |^enum " . --glob '!target/**' --glob '!\.git/**' | head -200 > "$APIS_FILE" || true
    rg -n "fn main\(" . --glob '!target/**' --glob '!\.git/**' | head -200 > "$CLI_FILE" || true
    ;;
  shell)
    rg -n "^[a-zA-Z0-9_]+\(\)\s*\{" . --glob '!\.git/**' | head -200 > "$SIGNATURES_FILE" || true
    rg -n "^function " . --glob '!\.git/**' | head -200 > "$APIS_FILE" || true
    rg -n "^#!/usr/bin/env bash" . --glob '!\.git/**' | head -200 > "$CLI_FILE" || true
    ;;
  *)
    echo "Unknown language: $LANG" > "$SIGNATURES_FILE"
    echo "Unknown language: $LANG" > "$APIS_FILE"
    echo "Unknown language: $LANG" > "$CLI_FILE"
    ;;
esac

SNAPSHOTS_CAPTURED=$(ls -1 "$SNAP_DIR" | wc -l | tr -d ' ')

python3 - "$STATUS" "$SNAPSHOTS_CAPTURED" "$SNAP_DIR" <<'PYEOF'
import json, sys
status, count, snap_dir = sys.argv[1:]
print(json.dumps({
  "status": status,
  "snapshots_captured": int(count),
  "snapshot_dir": snap_dir
}))
PYEOF
