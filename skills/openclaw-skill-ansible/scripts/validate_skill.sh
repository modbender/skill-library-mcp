#!/usr/bin/env bash
set -euo pipefail
SKILL_DIR=${1:-.}
REPORT="$SKILL_DIR/validation_report.txt"
: > "$REPORT"
echo "Validating skill: $SKILL_DIR" | tee -a "$REPORT"
# basic checks
if [ ! -f "$SKILL_DIR/SKILL.md" ]; then
  echo "ERROR: SKILL.md missing" | tee -a "$REPORT"
  exit 2
fi
if [ ! -f "$SKILL_DIR/metadata.yaml" ] && [ ! -f "$SKILL_DIR/metadata.json" ]; then
  echo "WARN: metadata missing" | tee -a "$REPORT"
fi
# run json schema validation if present
if [ -f "$SKILL_DIR/schemas/task.schema.json" ]; then
  echo "Found schema in skill; running basic json parse" | tee -a "$REPORT"
  python3 -m json.tool < "$SKILL_DIR/schemas/task.schema.json" >/dev/null 2>&1 || echo "Schema parse warning" | tee -a "$REPORT"
fi
# run smoke test if present
if [ -x "$SKILL_DIR/test_smoke.sh" ]; then
  echo "Running smoke test" | tee -a "$REPORT"
  (cd "$SKILL_DIR" && ./test_smoke.sh) && echo "Smoke OK" | tee -a "$REPORT" || echo "Smoke FAILED" | tee -a "$REPORT"
fi
# dependency audit placeholders
if [ -f "$SKILL_DIR/package.json" ]; then
  echo "npm deps detected; please run npm audit separately" | tee -a "$REPORT"
fi
if [ -f "$SKILL_DIR/requirements.txt" ]; then
  echo "python deps detected; consider running pip-audit" | tee -a "$REPORT"
fi
echo "Validation complete: $REPORT" | tee -a "$REPORT"
