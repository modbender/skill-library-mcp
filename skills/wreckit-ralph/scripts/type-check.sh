#!/usr/bin/env bash
# wreckit — Type Check gate
# Detects and runs the type checker for the project
# Usage: ./type-check.sh [project-path]
# Output: JSON with status PASS/FAIL/ERROR

set -euo pipefail
PROJECT="${1:-.}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT="$(cd "$PROJECT" && pwd)"
cd "$PROJECT"

STACK_JSON=$("$SCRIPT_DIR/detect-stack.sh" "$PROJECT" 2>/dev/null || true)
TYPE_CMD=$(echo "$STACK_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('commands',{}).get('typeCheck','none'))" 2>/dev/null || echo "none")
TYPE_CHECKER=$(echo "$STACK_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('typeChecker','none'))" 2>/dev/null || echo "none")

if [ -z "$TYPE_CMD" ] || [ "$TYPE_CMD" = "none" ]; then
  python3 - <<'PYEOF'
import json
print(json.dumps({
  "status": "ERROR",
  "tool": "none",
  "errors": 0,
  "warnings": 0,
  "output": "No type checker detected.",
  "confidence": 0.5
}))
PYEOF
  exit 1
fi

TOOL="$TYPE_CHECKER"
case "$TYPE_CHECKER" in
  rustc) TOOL="cargo check" ;;
  go) TOOL="go vet" ;;
  tsc|pyright|mypy) TOOL="$TYPE_CHECKER" ;;
  *) TOOL="$TYPE_CHECKER" ;;
esac

TYPE_EXIT=0
OUTPUT=$(eval "$TYPE_CMD" 2>&1) || TYPE_EXIT=$?
OUTPUT=${OUTPUT:-}

ERRORS=$(echo "$OUTPUT" | { grep -ciE '\berror\b' 2>/dev/null || true; })
ERRORS=${ERRORS:-0}
WARNINGS=$(echo "$OUTPUT" | { grep -ciE '\bwarn(ing)?\b' 2>/dev/null || true; })
WARNINGS=${WARNINGS:-0}

STATUS="PASS"
if [ -z "$OUTPUT" ]; then
  STATUS="PASS"
elif [ "$TYPE_EXIT" -ne 0 ] && [ "$ERRORS" -gt 0 ]; then
  STATUS="FAIL"
elif [ "$TYPE_EXIT" -ne 0 ] && [ "$ERRORS" -eq 0 ]; then
  STATUS="WARN"
else
  STATUS="PASS"
fi

CONFIDENCE="0.0"
if [ "$ERRORS" -gt 0 ] 2>/dev/null; then
  CONFIDENCE="1.0"
elif [ "$TYPE_EXIT" -ne 0 ] 2>/dev/null; then
  CONFIDENCE="0.5"
fi

python3 - "$STATUS" "$TOOL" "$ERRORS" "$WARNINGS" "$CONFIDENCE" <<'PYEOF'
import json, sys
status, tool, errors, warnings, confidence = sys.argv[1:]
output = sys.stdin.read()
if len(output) > 4000:
    output = output[:4000] + "\n...truncated..."
print(json.dumps({
  "status": status,
  "tool": tool,
  "errors": int(errors),
  "warnings": int(warnings),
  "output": output,
  "confidence": float(confidence)
}))
PYEOF
