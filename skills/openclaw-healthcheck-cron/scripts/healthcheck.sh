#!/usr/bin/env bash
set -euo pipefail

OUT_ROOT="${HEALTHCHECK_OUTPUT_DIR:-/tmp/openclaw-healthcheck}"
EXCLUDE_RAW="${HEALTHCHECK_EXCLUDE:-small model,sandbox,groupPolicy}"
TS="$(date +%H%M%S)"
DAY="$(date +%F)"
OUT_DIR="${OUT_ROOT}/${DAY}/${TS}"
mkdir -p "$OUT_DIR"

LOG="$OUT_DIR/run.log"
SUMMARY_JSON="$OUT_DIR/summary.json"

# Keep this script read-only.
# If your environment has a richer checker, replace this section with that command.

passed=0
warn=0
fail=0
issues=()

check_cmd() {
  local name="$1"
  shift
  if "$@" >/dev/null 2>&1; then
    passed=$((passed+1))
    echo "PASS: $name" >> "$LOG"
  else
    warn=$((warn+1))
    issues+=("$name")
    echo "WARN: $name" >> "$LOG"
  fi
}

{
  echo "[healthcheck] started: $(date -Is)"
  echo "[healthcheck] out_dir: $OUT_DIR"
  echo "[healthcheck] exclude: $EXCLUDE_RAW"
} > "$LOG"

check_cmd "openclaw binary available" command -v openclaw
check_cmd "gateway status command" openclaw gateway status
check_cmd "openclaw status command" openclaw status

if [[ $fail -gt 0 ]]; then
  verdict="NEEDS_ATTENTION"
elif [[ $warn -gt 0 ]]; then
  verdict="MONITOR"
else
  verdict="OK"
fi

cat > "$SUMMARY_JSON" <<EOF
{
  "verdict": "$verdict",
  "passed": $passed,
  "warn": $warn,
  "fail": $fail,
  "artifact_path": "$OUT_DIR",
  "issues": [$(printf '"%s",' "${issues[@]:-}" | sed 's/,$//')]
}
EOF

echo "VERDICT=$verdict PASSED=$passed WARN=$warn FAIL=$fail ARTIFACT=$OUT_DIR"
