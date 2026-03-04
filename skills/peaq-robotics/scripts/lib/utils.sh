#!/usr/bin/env bash

PEAQ_ROS2_UTILS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

fatal() {
  echo "${SCRIPT_NAME}: $*" >&2
  exit 2
}

resolve_openclaw_workspace() {
  local dir="${PWD:-$(pwd)}"
  while [[ -n "$dir" && "$dir" != "/" ]]; do
    if [[ -f "$dir/AGENTS.md" && -f "$dir/TOOLS.md" ]]; then
      echo "$dir"
      return
    fi
    dir="$(dirname "$dir")"
  done
  echo ""
}

get_openclaw_agent_id() {
  if [[ -n "${OPENCLAW_AGENT_ID:-}" ]]; then
    echo "$OPENCLAW_AGENT_ID"
    return
  fi
  if [[ -n "${OPENCLAW_AGENT_DIR:-}" ]]; then
    basename "$(dirname "$OPENCLAW_AGENT_DIR")"
    return
  fi
  echo ""
}

get_hostname() {
  hostname 2>/dev/null || uname -n 2>/dev/null || echo ""
}

resolve_realpath() {
  python3 - <<'PY' "$1"
import os
import sys

path = os.path.expanduser(sys.argv[1])
print(os.path.realpath(path))
PY
}

path_is_within() {
  local candidate="$1"
  local root="$2"
  local root_prefix="${root%/}/"
  [[ "$candidate" == "$root" || "$candidate" == "$root_prefix"* ]]
}

resolve_skill_root() {
  if [[ -n "${SCRIPT_DIR:-}" ]]; then
    dirname "$SCRIPT_DIR"
    return
  fi
  dirname "$(dirname "$PEAQ_ROS2_UTILS_DIR")"
}

validate_json_file_arg() {
  local raw_path="$1"
  local real_path size max_size
  local -a allowed_roots=()
  local workspace skill_root root root_real allowed=0

  real_path="$(resolve_realpath "$raw_path")"
  [[ -f "$real_path" ]] || fatal "JSON file not found: $raw_path"
  [[ "$real_path" == *.json ]] || fatal "Only .json files are allowed with @path"

  max_size="${PEAQ_ROS2_MAX_JSON_FILE_BYTES:-262144}"
  [[ "$max_size" =~ ^[0-9]+$ ]] || fatal "PEAQ_ROS2_MAX_JSON_FILE_BYTES must be an integer"
  size="$(wc -c <"$real_path" | tr -d '[:space:]')"
  if (( size > max_size )); then
    fatal "JSON file too large (${size} bytes > ${max_size} bytes)"
  fi

  skill_root="$(resolve_skill_root)"
  [[ -n "$skill_root" ]] && allowed_roots+=("$skill_root")

  if [[ -n "${PEAQ_ROS2_ROOT:-}" ]]; then
    allowed_roots+=("$PEAQ_ROS2_ROOT")
  fi

  workspace="$(resolve_openclaw_workspace)"
  if [[ -n "$workspace" ]]; then
    allowed_roots+=("$workspace/.peaq_robot")
  fi

  for root in "${allowed_roots[@]}"; do
    [[ -e "$root" ]] || continue
    root_real="$(resolve_realpath "$root")"
    if path_is_within "$real_path" "$root_real"; then
      allowed=1
      break
    fi
  done

  [[ "$allowed" == "1" ]] || fatal "JSON file path is outside allowed roots"
  echo "$real_path"
}

json_compact() {
  python3 - <<'PY' "$1"
import json
import sys

raw = sys.argv[1]
try:
    obj = json.loads(raw)
except Exception as exc:
    raise SystemExit(f"Invalid JSON input: {exc}")
print(json.dumps(obj, separators=(',', ':')))
PY
}

read_json_arg() {
  local arg="${1:-}"
  if [[ -z "$arg" ]]; then
    echo "{}"
    return
  fi
  if [[ "$arg" == @* ]]; then
    local path="${arg#@}"
    if ! path="$(validate_json_file_arg "$path")"; then
      return 2
    fi
    python3 - <<'PY' "$path"
import json
import sys

with open(sys.argv[1], "r") as f:
    obj = json.load(f)
print(json.dumps(obj, separators=(',', ':')))
PY
    return
  fi
  json_compact "$arg"
}

require_safe_token() {
  local value="${1:-}"
  local label="${2:-value}"
  [[ -n "$value" ]] || fatal "$label cannot be empty"
  if [[ ! "$value" =~ ^[A-Za-z0-9._:@/-]+$ ]]; then
    fatal "$label contains unsupported characters"
  fi
}

ros2_service_call_json() {
  local service="$1"
  local service_type="$2"
  local payload_json="{}"
  if [[ $# -ge 3 ]]; then
    payload_json="$3"
  fi
  python3 - <<'PY' "$service" "$service_type" "$payload_json"
import json
import subprocess
import sys

service = sys.argv[1]
service_type = sys.argv[2]
payload_raw = sys.argv[3]

try:
    payload = json.loads(payload_raw or "{}")
except Exception as exc:
    raise SystemExit(f"Invalid service payload JSON: {exc}")

if not isinstance(payload, dict):
    raise SystemExit("Service payload must be a JSON object")

payload_arg = json.dumps(payload, separators=(",", ":"))
subprocess.run(
    ["ros2", "service", "call", service, service_type, payload_arg],
    check=True,
)
PY
}
