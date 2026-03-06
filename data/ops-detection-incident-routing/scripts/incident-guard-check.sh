#!/usr/bin/env bash
set -euo pipefail

STATE_FILE="./incident-state.json"
CHECK_ID=""
SEVERITY="Sev-3"
COOLDOWN_MIN=30

usage() {
  cat <<USAGE
Usage: incident-guard-check.sh --check-id <id> [options]

Options:
  --check-id <id>        Check identifier (required)
  --severity <level>     Severity label (default: Sev-3)
  --state-file <file>    Guard state file path (default: ./incident-state.json)
  --cooldown-min <n>     Cooldown used only for informational output (default: 30)
  -h, --help             Show help
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --check-id) CHECK_ID="$2"; shift 2 ;;
    --severity) SEVERITY="$2"; shift 2 ;;
    --state-file) STATE_FILE="$2"; shift 2 ;;
    --cooldown-min) COOLDOWN_MIN="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 2 ;;
  esac
done

[[ -n "$CHECK_ID" ]] || { echo "--check-id is required" >&2; exit 2; }
[[ "$COOLDOWN_MIN" =~ ^[0-9]+$ ]] || { echo "--cooldown-min must be an integer" >&2; exit 2; }
(( COOLDOWN_MIN >= 0 )) || { echo "--cooldown-min must be >= 0" >&2; exit 2; }

python3 - "$STATE_FILE" "$CHECK_ID" "$SEVERITY" "$COOLDOWN_MIN" <<'PY'
import json
import sys
from datetime import datetime, timezone

state_file, check_id, severity, cooldown_min = sys.argv[1:5]


def iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_iso(raw: str):
    if not raw:
        return None
    raw = raw.strip()
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(raw)
    except ValueError:
        return None

state = {}
try:
    with open(state_file, "r", encoding="utf-8") as f:
        state = json.load(f)
except FileNotFoundError:
    state = {}
except json.JSONDecodeError:
    state = {}

entry = state.get(check_id, {}) if isinstance(state, dict) else {}
in_flight = bool(entry.get("in_flight", False))
cooldown_until = parse_iso(entry.get("cooldown_until_utc", ""))
now = datetime.now(timezone.utc)

result = {
    "check_id": check_id,
    "severity": severity,
    "allowed": True,
    "reason": "allowed",
    "warning": "",
    "observed_at": iso_now(),
}

if in_flight:
    result["allowed"] = False
    result["reason"] = "in_flight"
elif cooldown_until and cooldown_until > now:
    result["allowed"] = False
    result["reason"] = "cooldown_active"
    result["warning"] = f"cooldown_until={cooldown_until.isoformat().replace('+00:00','Z')}"

print(json.dumps(result, ensure_ascii=True))
PY
