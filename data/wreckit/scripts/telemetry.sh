#!/usr/bin/env bash
# wreckit — Telemetry wrapper
# Source this file in other scripts or use: source telemetry.sh && run_gate "name" "script args"
# Writes to .wreckit/metrics.json (appends per-gate telemetry)

TELEMETRY_FILE="${TELEMETRY_FILE:-.wreckit/metrics.json}"

run_gate() {
  local gate_name="$1"
  shift
  local start_ms end_ms duration_ms exit_code output valid_json status

  mkdir -p "$(dirname "$TELEMETRY_FILE")"

  start_ms=$(python3 -c "import time; print(int(time.time()*1000))")
  output=$(("$@") 2>/tmp/wreckit-gate-stderr-$$ || true)
  exit_code=$?
  end_ms=$(python3 -c "import time; print(int(time.time()*1000))")
  duration_ms=$((end_ms - start_ms))

  # Validate JSON output
  valid_json="false"
  status="UNKNOWN"
  if echo "$output" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('status','UNKNOWN'))" >/tmp/wreckit-status-$$ 2>/dev/null; then
    valid_json="true"
    status=$(cat /tmp/wreckit-status-$$)
  fi

  # Get stderr
  local stderr_content
  stderr_content=$(cat /tmp/wreckit-gate-stderr-$$ 2>/dev/null | head -5 | tr '\n' ' ' | tr '"' "'")

  # Export exit code for callers
  LAST_EXIT_CODE=$exit_code
  export LAST_EXIT_CODE

  # Append to metrics JSON (newline-delimited)
  echo "{\"gate\":\"$gate_name\",\"duration_ms\":$duration_ms,\"exit_code\":$exit_code,\"valid_json\":$valid_json,\"status\":\"$status\",\"stderr\":\"$stderr_content\",\"ts\":$start_ms}" >> "$TELEMETRY_FILE"

  rm -f /tmp/wreckit-gate-stderr-$$ /tmp/wreckit-status-$$

  # Print the output for the caller
  echo "$output"
}

# Summarize telemetry at end of run
summarize_telemetry() {
  local file="${1:-$TELEMETRY_FILE}"
  if [ ! -f "$file" ]; then echo "No telemetry data"; return; fi

  python3 - "$file" <<'PYEOF'
import json, sys
lines = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
print(f"\n{'='*60}")
print(f"{'Gate':<25} {'ms':>8} {'Exit':>5} {'JSON':>5} {'Status':<10}")
print(f"{'-'*60}")
total_ms = 0
passed = failed = errored = 0
for r in lines:
    status = r.get('status','?')
    ms = r.get('duration_ms',0)
    total_ms += ms
    if status in ('PASS','SHIP'): passed += 1
    elif status in ('FAIL','BLOCKED','ERROR'): failed += 1 if r.get('exit_code',0)==0 else errored+1
    flag = '✅' if status in ('PASS','SHIP') else ('⚠️' if status in ('WARN','CAUTION') else '❌')
    print(f"{flag} {r.get('gate','?'):<23} {ms:>8}ms {r.get('exit_code',0):>5} {str(r.get('valid_json',False)):>5} {status:<10}")
print(f"{'='*60}")
print(f"Total: {len(lines)} gates | {total_ms}ms total | {passed} pass | {failed} fail")
PYEOF
}
