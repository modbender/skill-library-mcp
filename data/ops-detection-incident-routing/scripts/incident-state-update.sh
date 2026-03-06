#!/usr/bin/env bash
set -euo pipefail

STATE_FILE="./incident-state.json"
ACTION=""
CHECK_ID=""
SEVERITY="Sev-3"
COOLDOWN_MIN=30

usage() {
  cat <<USAGE
Usage: incident-state-update.sh --action <start|complete|fail> --check-id <id> [options]

Options:
  --action <name>        start | complete | fail (required)
  --check-id <id>        Check identifier (required)
  --severity <level>     Severity label (default: Sev-3)
  --state-file <file>    Guard state file path (default: ./incident-state.json)
  --cooldown-min <n>     Cooldown minutes on complete (default: 30)
  -h, --help             Show help
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --action) ACTION="$2"; shift 2 ;;
    --check-id) CHECK_ID="$2"; shift 2 ;;
    --severity) SEVERITY="$2"; shift 2 ;;
    --state-file) STATE_FILE="$2"; shift 2 ;;
    --cooldown-min) COOLDOWN_MIN="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 2 ;;
  esac
done

[[ -n "$ACTION" ]] || { echo "--action is required" >&2; exit 2; }
[[ -n "$CHECK_ID" ]] || { echo "--check-id is required" >&2; exit 2; }
[[ "$COOLDOWN_MIN" =~ ^[0-9]+$ ]] || { echo "--cooldown-min must be an integer" >&2; exit 2; }
(( COOLDOWN_MIN >= 0 )) || { echo "--cooldown-min must be >= 0" >&2; exit 2; }

case "$ACTION" in
  start|complete|fail) ;;
  *) echo "Invalid --action: $ACTION" >&2; exit 2 ;;
esac

python3 - "$STATE_FILE" "$ACTION" "$CHECK_ID" "$SEVERITY" "$COOLDOWN_MIN" <<'PY'
import json
import os
import sys
from datetime import datetime, timedelta, timezone

state_file, action, check_id, severity, cooldown_min = sys.argv[1:6]
cooldown_min = int(cooldown_min)


def now_utc():
    return datetime.now(timezone.utc)


def iso(dt: datetime) -> str:
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_state(path: str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
    except FileNotFoundError:
        pass
    except json.JSONDecodeError:
        pass
    return {}


def write_state(path: str, state: dict):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=True)
        f.write("\n")
    os.replace(tmp, path)

state = load_state(state_file)
entry = state.get(check_id, {})
ts = now_utc()

entry.setdefault("in_flight", False)
entry.setdefault("flow_started_utc", None)
entry.setdefault("last_completed_utc", None)
entry.setdefault("last_severity", None)
entry.setdefault("cooldown_until_utc", None)

if action == "start":
    entry["in_flight"] = True
    entry["flow_started_utc"] = iso(ts)
    entry["last_severity"] = severity
elif action == "complete":
    entry["in_flight"] = False
    entry["last_completed_utc"] = iso(ts)
    entry["last_severity"] = severity
    entry["cooldown_until_utc"] = iso(ts + timedelta(minutes=cooldown_min))
elif action == "fail":
    entry["in_flight"] = False
    entry["last_completed_utc"] = iso(ts)
    entry["last_severity"] = severity

state[check_id] = entry
write_state(state_file, state)

print(json.dumps({"ok": True, "action": action, "check_id": check_id, "entry": entry}, ensure_ascii=True))
PY
