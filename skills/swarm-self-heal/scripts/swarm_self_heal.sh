#!/usr/bin/env bash
set -u -o pipefail

SELF_NAME="swarm_self_heal"
TS="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
PING_TIMEOUT_SECONDS="${PING_TIMEOUT_SECONDS:-120}"
PASSIVE_STALE_SECONDS="${PASSIVE_STALE_SECONDS:-2400}"
ACTIVE_PING_ON_STALE="${ACTIVE_PING_ON_STALE:-1}"
LOCK_DIR="${XDG_RUNTIME_DIR:-/tmp}/swarm-self-heal.lock"
TARGETS_CSV="${TARGETS_CSV:-main,builder-1,builder-2,reviewer,designer}"

IFS=',' read -r -a TARGETS <<<"$TARGETS_CSV"
OK_AGENTS=()
FAILED_AGENTS=()
FAILED_SOFT_AGENTS=()
FAILED_INFRA_AGENTS=()
CANDIDATE_AGENTS=()
DETAILS=()
ACTIONS=()
VERDICT="healthy"
STATUS_JSON=""

trim_line() {
  local input="${1:-}"
  printf '%s' "$input" | tr '\n' ' ' | sed 's/[[:space:]]\+/ /g' | cut -c1-320
}

to_csv_or_none() {
  local items=("$@")
  if [[ ${#items[@]} -eq 0 ]]; then
    echo "none"
    return 0
  fi
  (IFS=,; echo "${items[*]}")
}

add_detail() {
  DETAILS+=("$1")
}

has_degraded_marker() {
  local text="${1:-}"
  [[ "$text" == *"pairing required"* || "$text" == *"No available auth profile"* || "$text" == *"rate limit"* || "$text" == *"cooldown"* || "$text" == *"authentication_error"* || "$text" == *"OAuth token has expired"* ]]
}

acquire_lock() {
  if mkdir "$LOCK_DIR" 2>/dev/null; then
    echo "$$" >"$LOCK_DIR/pid"
    trap 'rm -rf "$LOCK_DIR"' EXIT
    return 0
  fi

  add_detail "lock_busy:$LOCK_DIR"
  VERDICT="degraded"
  ACTIONS=("none")
  echo "timestamp=$TS"
  echo "tool=$SELF_NAME"
  echo "targets=$(to_csv_or_none "${TARGETS[@]}")"
  echo "ok_agents=none"
  echo "failed_agents=none"
  echo "failed_soft_agents=none"
  echo "failed_infra_agents=none"
  echo "actions=none"
  echo "details_start"
  for d in "${DETAILS[@]}"; do
    echo " - $d"
  done
  echo "details_end"
  echo "VERDICT=$VERDICT"
  echo "ACTION=none"
  echo "RECEIPT=swarm_self_heal:$TS:$VERDICT"
  exit 0
}

gateway_ok() {
  local health_out status_out tg_running tg_probe

  health_out="$(openclaw health 2>&1)"
  if [[ $? -ne 0 ]]; then
    add_detail "gateway_health_fail:$(trim_line "$health_out")"
    return 1
  fi

  status_out="$(openclaw channels status --json --probe 2>&1)"
  if [[ $? -ne 0 ]]; then
    add_detail "channels_status_fail:$(trim_line "$status_out")"
    return 1
  fi

  tg_running="$(jq -r '.channels.telegram.running // false' <<<"$status_out" 2>/dev/null || echo false)"
  tg_probe="$(jq -r '.channels.telegram.probe.ok // false' <<<"$status_out" 2>/dev/null || echo false)"
  if [[ "$tg_running" != "true" || "$tg_probe" != "true" ]]; then
    add_detail "telegram_not_ready:running=$tg_running:probe=$tg_probe"
    return 1
  fi

  add_detail "gateway_health_ok"
  return 0
}

restart_gateway() {
  local out rc

  if command -v systemctl >/dev/null 2>&1; then
    out="$(systemctl --user restart openclaw-gateway 2>&1)"
    rc=$?
    if [[ $rc -eq 0 ]]; then
      ACTIONS+=("restart_gateway_systemd")
      sleep 4
      if gateway_ok; then
        add_detail "gateway_restart_recovered:systemd"
        return 0
      fi
      add_detail "gateway_restart_no_recovery:systemd"
    else
      add_detail "gateway_restart_failed:systemd:$(trim_line "$out")"
    fi
  fi

  out="$(openclaw gateway restart 2>&1)"
  rc=$?
  if [[ $rc -ne 0 ]]; then
    add_detail "gateway_restart_failed:cli:$(trim_line "$out")"
    return 1
  fi

  ACTIONS+=("restart_gateway_cli")
  sleep 4
  if gateway_ok; then
    add_detail "gateway_restart_recovered:cli"
    return 0
  fi

  add_detail "gateway_restart_no_recovery:cli"
  return 1
}

load_status_json() {
  local out
  out="$(openclaw status --json 2>&1)"
  if [[ $? -ne 0 ]]; then
    add_detail "status_json_fail:$(trim_line "$out")"
    return 1
  fi
  STATUS_JSON="$out"
  add_detail "status_json_ok"
  return 0
}

collect_ping_candidates() {
  local stale_ms aid age_ms
  stale_ms=$((PASSIVE_STALE_SECONDS * 1000))

  for aid in "${TARGETS[@]}"; do
    age_ms="$(jq -r --arg aid "$aid" '[.sessions.recent[]? | select(.agentId == $aid) | .age] | min // empty' <<<"$STATUS_JSON" 2>/dev/null || true)"
    if [[ -n "$age_ms" && "$age_ms" =~ ^[0-9]+$ ]]; then
      if (( age_ms <= stale_ms )); then
        OK_AGENTS+=("$aid")
        add_detail "agent_passive_ok:$aid:age_ms=$age_ms"
      else
        CANDIDATE_AGENTS+=("$aid")
        add_detail "agent_stale:$aid:age_ms=$age_ms"
      fi
    else
      CANDIDATE_AGENTS+=("$aid")
      add_detail "agent_no_recent_session:$aid"
    fi
  done
}

ping_agent() {
  local agent_id="$1"
  local out rc status text

  out="$(openclaw agent --agent "$agent_id" --timeout "$PING_TIMEOUT_SECONDS" -m "[self-heal ping $TS] Reply ONLY: READY" --json 2>&1)"
  rc=$?
  if [[ $rc -ne 0 ]]; then
    echo "fail|exit=$rc|$(trim_line "$out")"
    return 0
  fi

  status="$(jq -r '.status // ""' <<<"$out" 2>/dev/null || true)"
  text="$(jq -r '.result.payloads[0].text // ""' <<<"$out" 2>/dev/null || true)"
  if [[ "$status" == "ok" && "$text" == *"READY"* ]]; then
    echo "ok|status=$status|$(trim_line "$text")"
  else
    if [[ -z "$text" ]]; then
      text="$(trim_line "$out")"
    fi
    echo "fail|status=$status|$(trim_line "$text")"
  fi
}

probe_agents() {
  local candidates=("$@")
  local aid result state reason detail

  for aid in "${candidates[@]}"; do
    result="$(ping_agent "$aid")"
    state="${result%%|*}"
    reason="${result#*|}"
    detail="${reason#*|}"

    if [[ "$state" == "ok" ]]; then
      OK_AGENTS+=("$aid")
      add_detail "agent_active_ok:$aid:$detail"
    else
      FAILED_AGENTS+=("$aid")
      if has_degraded_marker "$result"; then
        FAILED_SOFT_AGENTS+=("$aid")
        add_detail "agent_soft_fail:$aid:$reason:$detail"
      else
        FAILED_INFRA_AGENTS+=("$aid")
        add_detail "agent_infra_fail:$aid:$reason:$detail"
      fi
    fi
  done
}

classify_final_verdict() {
  if [[ ${#ACTIONS[@]} -gt 0 && ${#FAILED_AGENTS[@]} -eq 0 ]]; then
    VERDICT="recovered"
    return 0
  fi
  if [[ ${#FAILED_AGENTS[@]} -eq 0 ]]; then
    VERDICT="healthy"
    return 0
  fi
  if [[ ${#FAILED_INFRA_AGENTS[@]} -eq 0 && ${#FAILED_SOFT_AGENTS[@]} -gt 0 ]]; then
    VERDICT="degraded"
    return 0
  fi
  VERDICT="failed"
}

acquire_lock

if ! gateway_ok; then
  restart_gateway || true
fi

if load_status_json; then
  collect_ping_candidates
else
  CANDIDATE_AGENTS=("${TARGETS[@]}")
fi

if [[ "${ACTIVE_PING_ON_STALE}" == "1" && ${#CANDIDATE_AGENTS[@]} -gt 0 ]]; then
  probe_agents "${CANDIDATE_AGENTS[@]}"
elif [[ ${#CANDIDATE_AGENTS[@]} -gt 0 ]]; then
  FAILED_AGENTS=("${CANDIDATE_AGENTS[@]}")
  FAILED_SOFT_AGENTS=("${CANDIDATE_AGENTS[@]}")
  add_detail "active_ping_disabled_for_stale_agents"
fi

if [[ ${#FAILED_INFRA_AGENTS[@]} -gt 0 ]]; then
  infra_retry=("${FAILED_INFRA_AGENTS[@]}")
  FAILED_AGENTS=()
  FAILED_SOFT_AGENTS=()
  FAILED_INFRA_AGENTS=()
  restart_gateway || true
  probe_agents "${infra_retry[@]}"
fi

classify_final_verdict

if [[ ${#ACTIONS[@]} -eq 0 ]]; then
  ACTIONS=("none")
fi

echo "timestamp=$TS"
echo "tool=$SELF_NAME"
echo "targets=$(to_csv_or_none "${TARGETS[@]}")"
echo "ok_agents=$(to_csv_or_none "${OK_AGENTS[@]}")"
echo "failed_agents=$(to_csv_or_none "${FAILED_AGENTS[@]}")"
echo "failed_soft_agents=$(to_csv_or_none "${FAILED_SOFT_AGENTS[@]}")"
echo "failed_infra_agents=$(to_csv_or_none "${FAILED_INFRA_AGENTS[@]}")"
echo "actions=$(to_csv_or_none "${ACTIONS[@]}")"
echo "details_start"
for d in "${DETAILS[@]}"; do
  echo " - $d"
done
echo "details_end"
echo "VERDICT=$VERDICT"
echo "ACTION=$(to_csv_or_none "${ACTIONS[@]}")"
echo "RECEIPT=swarm_self_heal:$TS:$VERDICT"

exit 0
