#!/usr/bin/env bash

resolve_root() {
  if [[ -n "${PEAQ_ROS2_ROOT:-}" ]]; then
    echo "$PEAQ_ROS2_ROOT"
    return
  fi

  for guess in \
    "$HOME/peaq-robotics-ros2" \
    "$HOME/Work/peaq/peaq-robotics-ros2" \
    "/work/peaq-robotics-ros2"; do
    if [[ -d "$guess/peaq_ros2_core" ]]; then
      echo "$guess"
      return
    fi
  done

  echo ""
}

auto_set_ros_domain_id() {
  if [[ -n "${ROS_DOMAIN_ID:-}" && "${ROS_DOMAIN_ID:-}" != "0" ]]; then
    return
  fi
  local workspace
  workspace="$(resolve_openclaw_workspace)"
  if [[ -z "$workspace" ]]; then
    return
  fi
  # Stable-ish per-workspace ROS domain (100-199) to avoid collisions.
  local hash
  hash="$(printf "%s" "$workspace" | cksum | awk '{print $1}')"
  local id=$(( (hash % 100) + 100 ))
  export ROS_DOMAIN_ID="$id"
}

load_root() {
  if [[ -n "$ROOT" ]]; then
    return
  fi

  local found
  found="$(resolve_root)"
  if [[ -z "$found" ]]; then
    return
  fi

  ROOT="$(cd "$found" && pwd)"
  if [[ -n "${PEAQ_ROS2_CONFIG_YAML:-}" ]]; then
    CONFIG="$PEAQ_ROS2_CONFIG_YAML"
    return
  fi

  local workspace
  workspace="$(resolve_openclaw_workspace)"
  if [[ -n "$workspace" && -f "$workspace/.peaq_robot/peaq_robot.yaml" ]]; then
    CONFIG="$workspace/.peaq_robot/peaq_robot.yaml"
    return
  fi

  CONFIG="$ROOT/peaq_ros2_examples/config/peaq_robot.yaml"
}

require_root() {
  load_root
  if [[ -z "$ROOT" ]]; then
    fatal "PEAQ_ROS2_ROOT not set and repo not found. Set PEAQ_ROS2_ROOT."
  fi
}

ensure_ros_environment_ready() {
  command -v ros2 >/dev/null 2>&1 || fatal "ros2 command not found. Install ROS 2 and initialize its environment first."

  if ! ros2 pkg prefix peaq_ros2_core >/dev/null 2>&1; then
    fatal "ROS environment is not initialized for peaq_ros2_core. Initialize ROS and workspace overlay before running this command."
  fi
}

ensure_env() {
  require_root
  [[ -f "$CONFIG" ]] || fatal "Config file not found at $CONFIG"
  ensure_ros_environment_ready
}
