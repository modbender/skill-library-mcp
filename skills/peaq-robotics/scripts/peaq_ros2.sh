#!/usr/bin/env bash
set -euo pipefail

SCRIPT_NAME="$(basename "$0")"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB_DIR="$SCRIPT_DIR/lib"

usage() {
  cat <<'USAGE'
peaq_ros2.sh - helper for peaq-robotics-ros2 ROS 2 nodes/services

Usage:
  peaq_ros2.sh env
  peaq_ros2.sh check

  peaq_ros2.sh core-start
  peaq_ros2.sh core-start-fg
  peaq_ros2.sh core-stop
  peaq_ros2.sh core-configure
  peaq_ros2.sh core-activate
  peaq_ros2.sh core-info
  peaq_ros2.sh core-info-json
  peaq_ros2.sh core-address
  peaq_ros2.sh core-did

  peaq_ros2.sh storage-start
  peaq_ros2.sh storage-start-fg
  peaq_ros2.sh storage-stop

  peaq_ros2.sh events-start
  peaq_ros2.sh events-start-fg
  peaq_ros2.sh events-stop

  peaq_ros2.sh humanoid-start
  peaq_ros2.sh humanoid-start-fg
  peaq_ros2.sh humanoid-stop

  peaq_ros2.sh did-create [metadata_json|@json_file]
  peaq_ros2.sh did-read
  peaq_ros2.sh identity-card-json [name] [roles_csv] [endpoints_json] [metadata_json]
  peaq_ros2.sh identity-card-did-create [name] [roles_csv] [endpoints_json] [metadata_json]
  peaq_ros2.sh identity-card-did-read

  peaq_ros2.sh fund-request [amount] [reason]

  peaq_ros2.sh store-add <key> <value_json> [mode]
  peaq_ros2.sh store-read <key>

  peaq_ros2.sh access-create-role <role> [description]
  peaq_ros2.sh access-create-permission <permission> [description]
  peaq_ros2.sh access-assign-permission <permission> <role>
  peaq_ros2.sh access-grant-role <role> <user>

Notes:
  - Set PEAQ_ROS2_ROOT to the peaq-robotics-ros2 repo root.
  - Set PEAQ_ROS2_CONFIG_YAML to your peaq_robot.yaml path.
  - Set ROS_DOMAIN_ID to avoid collisions when multiple ROS 2 graphs are running.
  - Funding requests are informational only; value transfer commands are intentionally excluded from core.
  - LOG/PID dirs default to ~/.peaq_ros2/logs-<ROS_DOMAIN_ID> and ~/.peaq_ros2/pids-<ROS_DOMAIN_ID>.
USAGE
}

# shellcheck source=lib/utils.sh
source "$LIB_DIR/utils.sh"
# shellcheck source=lib/env.sh
source "$LIB_DIR/env.sh"
# shellcheck source=lib/nodes.sh
source "$LIB_DIR/nodes.sh"
# shellcheck source=lib/core.sh
source "$LIB_DIR/core.sh"
# shellcheck source=lib/wallet.sh
source "$LIB_DIR/wallet.sh"

ROOT=""
CONFIG=""

auto_set_ros_domain_id
ROS_DOMAIN_SUFFIX=""
if [[ -n "${ROS_DOMAIN_ID:-}" ]]; then
  ROS_DOMAIN_SUFFIX="-$ROS_DOMAIN_ID"
fi
LOG_DIR="${PEAQ_ROS2_LOG_DIR:-$HOME/.peaq_ros2/logs${ROS_DOMAIN_SUFFIX}}"
PID_DIR="${PEAQ_ROS2_PID_DIR:-$HOME/.peaq_ros2/pids${ROS_DOMAIN_SUFFIX}}"

CORE_NODE_NAME="${PEAQ_ROS2_CORE_NODE_NAME:-peaq_core_node}"
STORAGE_NODE_NAME="${PEAQ_ROS2_STORAGE_NODE_NAME:-peaq_storage_bridge_node}"
EVENTS_NODE_NAME="${PEAQ_ROS2_EVENTS_NODE_NAME:-peaq_events_node}"
HUMANOID_NODE_NAME="${PEAQ_ROS2_HUMANOID_NODE_NAME:-peaq_humanoid_bridge_node}"

cmd="${1:-}"
shift || true

case "$cmd" in
  ""|"-h"|"--help"|"help")
    usage
    exit 0
    ;;
  env)
    require_root
    cat <<'ENV'
PEAQ_ROS2_ROOT=$ROOT
PEAQ_ROS2_CONFIG_YAML=$CONFIG
LOG_DIR=$LOG_DIR
PID_DIR=$PID_DIR
CORE_NODE_NAME=$CORE_NODE_NAME
STORAGE_NODE_NAME=$STORAGE_NODE_NAME
EVENTS_NODE_NAME=$EVENTS_NODE_NAME
HUMANOID_NODE_NAME=$HUMANOID_NODE_NAME
ROS_DOMAIN_ID=${ROS_DOMAIN_ID:-}
ENV
    exit 0
    ;;
  check)
    ensure_env
    ros2 --help >/dev/null
    exit 0
    ;;

  core-start)
    ensure_env
    run_bg "$CORE_NODE_NAME" ros2 run peaq_ros2_core core_node --ros-args -p config.yaml_path:="$CONFIG"
    ;;
  core-start-fg)
    ensure_env
    ros2 run peaq_ros2_core core_node --ros-args -p config.yaml_path:="$CONFIG"
    ;;
  core-stop)
    stop_bg "$CORE_NODE_NAME"
    ;;
  core-configure)
    ensure_env
    state="$(core_state)"
    if [[ "$state" == "inactive" || "$state" == "active" ]]; then
      exit 0
    fi
    for attempt in 1 2 3; do
      out="$(ros2 lifecycle set "/$CORE_NODE_NAME" configure 2>&1 || true)"
      echo "$out"
      if echo "$out" | grep -q "Transitioning successful"; then
        exit 0
      fi
      if echo "$out" | grep -q "Unknown transition requested"; then
        exit 0
      fi
      if echo "$out" | grep -q "Node not found"; then
        sleep 2
        continue
      fi
      break
    done
    fatal "core-configure failed"
    ;;
  core-activate)
    ensure_env
    state="$(core_state)"
    if [[ "$state" == "active" ]]; then
      exit 0
    fi
    if [[ "$state" == "unconfigured" ]]; then
      "$0" core-configure
    fi
    out="$(ros2 lifecycle set "/$CORE_NODE_NAME" activate 2>&1 || true)"
    echo "$out"
    if echo "$out" | grep -q "Transitioning successful"; then
      exit 0
    fi
    if echo "$out" | grep -q "Unknown transition requested"; then
      exit 0
    fi
    fatal "core-activate failed"
    ;;
  core-info)
    ensure_env
    ros2 service call "/$CORE_NODE_NAME/info" peaq_ros2_interfaces/srv/GetNodeInfo
    ;;
  core-info-json)
    core_info_json
    ;;
  core-address)
    info_json="$(core_info_json)"
    python3 - <<'PY' "$info_json"
import json
import sys

info = json.loads(sys.argv[1])
print(info.get("wallet_address", ""))
PY
    ;;
  core-did)
    info_json="$(core_info_json)"
    python3 - <<'PY' "$info_json"
import json
import sys

info = json.loads(sys.argv[1])
print(info.get("did", ""))
PY
    ;;

  storage-start)
    ensure_env
    run_bg "$STORAGE_NODE_NAME" ros2 run peaq_ros2_core storage_bridge_node --ros-args -p config.yaml_path:="$CONFIG"
    ;;
  storage-start-fg)
    ensure_env
    ros2 run peaq_ros2_core storage_bridge_node --ros-args -p config.yaml_path:="$CONFIG"
    ;;
  storage-stop)
    stop_bg "$STORAGE_NODE_NAME"
    ;;

  events-start)
    ensure_env
    run_bg "$EVENTS_NODE_NAME" ros2 run peaq_ros2_core events_node --ros-args -p config.yaml_path:="$CONFIG"
    ;;
  events-start-fg)
    ensure_env
    ros2 run peaq_ros2_core events_node --ros-args -p config.yaml_path:="$CONFIG"
    ;;
  events-stop)
    stop_bg "$EVENTS_NODE_NAME"
    ;;

  humanoid-start)
    ensure_env
    run_bg "$HUMANOID_NODE_NAME" ros2 run peaq_ros2_humanoids humanoid_bridge_node --ros-args -p config.yaml_path:="$CONFIG"
    ;;
  humanoid-start-fg)
    ensure_env
    ros2 run peaq_ros2_humanoids humanoid_bridge_node --ros-args -p config.yaml_path:="$CONFIG"
    ;;
  humanoid-stop)
    stop_bg "$HUMANOID_NODE_NAME"
    ;;

  did-create)
    ensure_env
    if [[ -z "${1:-}" ]]; then
      metadata='{"type":"robot"}'
    else
      if ! metadata="$(read_json_arg "$1")"; then
        fatal "Invalid DID metadata JSON input"
      fi
    fi
    payload="$(python3 - <<'PY' "$metadata"
import json, sys
print(json.dumps({"metadata_json": sys.argv[1]}, separators=(",", ":")))
PY
)"
    ros2_service_call_json "/$CORE_NODE_NAME/identity/create" peaq_ros2_interfaces/srv/IdentityCreate "$payload"
    ;;
  did-read)
    ensure_env
    ros2_service_call_json "/$CORE_NODE_NAME/identity/read" peaq_ros2_interfaces/srv/IdentityRead "{}"
    ;;
  fund-request)
    ensure_env
    amount="${1:-}"; reason="${2:-}"
    fund_request_line "$amount" "$reason"
    ;;

  store-add)
    ensure_env
    key="${1:-}"; value_json="${2:-}"; mode="${3:-FAST}"
    [[ -n "$key" ]] || fatal "store-add requires <key>"
    [[ -n "$value_json" ]] || fatal "store-add requires <value_json>"
    require_safe_token "$key" "storage key"
    if ! value_json="$(read_json_arg "$value_json")"; then
      fatal "Invalid storage JSON input"
    fi
    payload="$(python3 - <<'PY' "$key" "$value_json" "$mode"
import json, sys
print(json.dumps({
    "key": sys.argv[1],
    "value_json": sys.argv[2],
    "mode": sys.argv[3],
}, separators=(",", ":")))
PY
)"
    ros2_service_call_json "/$CORE_NODE_NAME/storage/add" peaq_ros2_interfaces/srv/StoreAddData "$payload"
    ;;
  store-read)
    ensure_env
    key="${1:-}"
    [[ -n "$key" ]] || fatal "store-read requires <key>"
    require_safe_token "$key" "storage key"
    payload="$(python3 - <<'PY' "$key"
import json, sys
print(json.dumps({"key": sys.argv[1]}, separators=(",", ":")))
PY
)"
    ros2_service_call_json "/$CORE_NODE_NAME/storage/read" peaq_ros2_interfaces/srv/StoreReadData "$payload"
    ;;
  identity-card-json)
    ensure_env
    name="${1:-}"; roles="${2:-}"; endpoints="${3:-}"; meta="${4:-}"
    identity_card_json "$name" "$roles" "$endpoints" "$meta"
    ;;
  identity-card-did-create)
    ensure_env
    name="${1:-}"; roles="${2:-}"; endpoints="${3:-}"; meta="${4:-}"
    card_json="$(identity_card_json "$name" "$roles" "$endpoints" "$meta")"
    payload="$(python3 - <<'PY' "$card_json"
import json, sys
print(json.dumps({"metadata_json": sys.argv[1]}, separators=(",", ":")))
PY
)"
    ros2_service_call_json "/$CORE_NODE_NAME/identity/create" peaq_ros2_interfaces/srv/IdentityCreate "$payload"
    ;;
  identity-card-did-read)
    ensure_env
    doc_json="$(did_read_json)"
    python3 - <<'PY' "$doc_json"
import json, sys

doc = json.loads(sys.argv[1])
decoded = doc.get("decoded_data") or {}
services = decoded.get("services") or []

def parse_identity_card(data_str: str):
    try:
        obj = json.loads(data_str)
    except Exception:
        return None
    if isinstance(obj, dict):
        if obj.get("schema") == "peaq.identityCard.v1":
            return obj
    return None

for svc in services:
    if not isinstance(svc, dict):
        continue
    data = svc.get("data") or ""
    card = parse_identity_card(data)
    if card:
        print(json.dumps(card, indent=2))
        sys.exit(0)

print("{}")
PY
    ;;

  access-create-role)
    ensure_env
    role="${1:-}"; description="${2:-}"
    [[ -n "$role" ]] || fatal "access-create-role requires <role>"
    require_safe_token "$role" "role"
    payload="$(python3 - <<'PY' "$role" "$description"
import json, sys
print(json.dumps({
    "role": sys.argv[1],
    "description": sys.argv[2],
}, separators=(",", ":")))
PY
)"
    ros2_service_call_json "/$CORE_NODE_NAME/access/create_role" peaq_ros2_interfaces/srv/AccessCreateRole "$payload"
    ;;
  access-create-permission)
    ensure_env
    permission="${1:-}"; description="${2:-}"
    [[ -n "$permission" ]] || fatal "access-create-permission requires <permission>"
    require_safe_token "$permission" "permission"
    payload="$(python3 - <<'PY' "$permission" "$description"
import json, sys
print(json.dumps({
    "permission": sys.argv[1],
    "description": sys.argv[2],
}, separators=(",", ":")))
PY
)"
    ros2_service_call_json "/$CORE_NODE_NAME/access/create_permission" peaq_ros2_interfaces/srv/AccessCreatePermission "$payload"
    ;;
  access-assign-permission)
    ensure_env
    permission="${1:-}"; role="${2:-}"
    [[ -n "$permission" ]] || fatal "access-assign-permission requires <permission>"
    [[ -n "$role" ]] || fatal "access-assign-permission requires <role>"
    require_safe_token "$permission" "permission"
    require_safe_token "$role" "role"
    payload="$(python3 - <<'PY' "$permission" "$role"
import json, sys
print(json.dumps({
    "permission": sys.argv[1],
    "role": sys.argv[2],
}, separators=(",", ":")))
PY
)"
    ros2_service_call_json "/$CORE_NODE_NAME/access/assign_permission" peaq_ros2_interfaces/srv/AccessAssignPermToRole "$payload"
    ;;
  access-grant-role)
    ensure_env
    role="${1:-}"; user="${2:-}"
    [[ -n "$role" ]] || fatal "access-grant-role requires <role>"
    [[ -n "$user" ]] || fatal "access-grant-role requires <user>"
    require_safe_token "$role" "role"
    require_safe_token "$user" "user"
    payload="$(python3 - <<'PY' "$role" "$user"
import json, sys
print(json.dumps({
    "role": sys.argv[1],
    "user": sys.argv[2],
}, separators=(",", ":")))
PY
)"
    ros2_service_call_json "/$CORE_NODE_NAME/access/grant_role" peaq_ros2_interfaces/srv/AccessGrantRole "$payload"
    ;;

  *)
    fatal "Unknown command: $cmd"
    ;;
esac
