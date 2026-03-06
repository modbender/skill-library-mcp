#!/usr/bin/env bash
set -euo pipefail

OPENCLAW_BIN="${OPENCLAW_BIN:-$(command -v openclaw 2>/dev/null || echo /opt/homebrew/bin/openclaw)}"
PYTHON_BIN="${PYTHON_BIN:-$(command -v python3 2>/dev/null || echo /usr/bin/python3)}"

BASE_DIR="${GW_WATCHDOG_BASE_DIR:-$HOME/.openclaw/watchdogs/gateway-discord}"
STATE_FILE="$BASE_DIR/state.json"
BACKUP_DIR="$BASE_DIR/backups"
EVENT_LOG="$BASE_DIR/events.jsonl"
LOCK_DIR="$BASE_DIR/lock"
BASELINE_PROMOTE_STATE_FILE="$BASE_DIR/baseline-promote-state.json"
CONFIG_ENV_FILE="$BASE_DIR/config.env"
OPENCLAW_DIR="${OPENCLAW_DIR:-$HOME/.openclaw}"
CONFIG_FILE="${GW_WATCHDOG_CONFIG_FILE:-$OPENCLAW_DIR/openclaw.json}"
CONFIG_BASELINE_FILE="${GW_WATCHDOG_CONFIG_BASELINE_FILE:-$OPENCLAW_DIR/openclaw.json.good}"

FAIL_THRESHOLD="${GW_WATCHDOG_FAIL_THRESHOLD:-2}"
COOLDOWN_SECONDS="${GW_WATCHDOG_COOLDOWN_SECONDS:-300}"
HEALTH_TIMEOUT_MS="${GW_WATCHDOG_HEALTH_TIMEOUT_MS:-10000}"
ENABLE_RESTART="${GW_WATCHDOG_ENABLE_RESTART:-0}"
MAX_RESTART_ATTEMPTS="${GW_WATCHDOG_MAX_RESTART_ATTEMPTS:-2}"
KEEP_BACKUPS="${GW_WATCHDOG_KEEP_BACKUPS:-50}"
AUTO_HEAL_ON_ALERT="${GW_WATCHDOG_AUTO_HEAL_ON_ALERT:-1}"
AUTO_ROLLBACK_ON_CONFIG_INVALID="${GW_WATCHDOG_AUTO_ROLLBACK_ON_CONFIG_INVALID:-1}"

DISCORD_WEBHOOK_URL="${DISCORD_WEBHOOK_URL:-}"
DISCORD_BOT_TOKEN="${DISCORD_BOT_TOKEN:-}"
DISCORD_CHANNEL_ID="${DISCORD_CHANNEL_ID:-}"

mkdir -p "$BASE_DIR" "$BACKUP_DIR"

if [[ -f "$CONFIG_ENV_FILE" ]]; then
  # shellcheck disable=SC1090
  source "$CONFIG_ENV_FILE"
fi

SOURCE_TAG="${GW_WATCHDOG_SOURCE:-unknown}"

if [[ ! -x "$OPENCLAW_BIN" ]]; then
  "$PYTHON_BIN" - "$EVENT_LOG" <<PY
import json
entry = {
  "time": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "event": "error",
  "severity": "critical",
  "reason": "openclaw_bin_missing",
  "source": "$SOURCE_TAG",
  "details": "OPENCLAW_BIN=$OPENCLAW_BIN is not executable"
}
with open("$EVENT_LOG", "a", encoding="utf-8") as f:
  f.write(json.dumps(entry, ensure_ascii=True) + "\\n")
PY
  exit 2
fi

if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "watchdog lock exists, exiting"
  exit 0
fi
cleanup() { rmdir "$LOCK_DIR" >/dev/null 2>&1 || true; }
trap cleanup EXIT

now_epoch() { date +%s; }
now_iso() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
sha256_file() { shasum -a 256 "$1" | awk '{print $1}'; }
get_current_version() {
  "$OPENCLAW_BIN" --version 2>/dev/null | tr -d '[:space:]' || echo "unknown"
}

load_state() {
  if [[ ! -f "$STATE_FILE" ]]; then
    cat <<EOF
healthy 0 none 0 0 0 none 0 none
EOF
    return
  fi
  "$PYTHON_BIN" - "$STATE_FILE" <<'PY'
import json, sys
path = sys.argv[1]
try:
    obj = json.load(open(path, "r", encoding="utf-8"))
except Exception:
    print("healthy 0 none 0 0 0 none 0 none")
    raise SystemExit(0)

status = str(obj.get("status", "healthy")).replace(" ", "_")
consecutive = int(obj.get("consecutive_failures", 0))
reason = str(obj.get("last_reason", "none")).replace(" ", "_")
last_alert = int(obj.get("last_alert_at", 0))
last_recovered = int(obj.get("last_recovered_at", 0))
restart_attempts = int(obj.get("restart_attempts", 0))
last_alert_key = str(obj.get("last_alert_key", "none")).replace(" ", "_")
outage_started_at = int(obj.get("outage_started_at", 0))
version = str(obj.get("last_known_version", "none")).replace(" ", "_")
print(status, consecutive, reason, last_alert, last_recovered, restart_attempts, last_alert_key, outage_started_at, version)
PY
}

backup_state() {
  if [[ -f "$STATE_FILE" ]]; then
    cp "$STATE_FILE" "$BACKUP_DIR/state-$(date +%Y%m%d-%H%M%S).json"
  fi
  "$PYTHON_BIN" - "$BACKUP_DIR" "$KEEP_BACKUPS" <<'PY'
import glob, os, sys
base = sys.argv[1]
keep = int(sys.argv[2])
files = sorted(glob.glob(os.path.join(base, "state-*.json")))
if len(files) > keep:
    for p in files[:-keep]:
        try:
            os.remove(p)
        except OSError:
            pass
PY
}

write_state() {
  local status="$1"
  local consecutive="$2"
  local reason="$3"
  local last_alert_at="$4"
  local last_recovered_at="$5"
  local restart_attempts="$6"
  local last_alert_key="$7"
  local outage_started_at="$8"
  local last_known_version="${9:-none}"
  backup_state
  "$PYTHON_BIN" - "$STATE_FILE" <<PY
import json
obj = {
  "status": "$status",
  "consecutive_failures": int("$consecutive"),
  "last_reason": "$reason",
  "last_alert_at": int("$last_alert_at"),
  "last_recovered_at": int("$last_recovered_at"),
  "restart_attempts": int("$restart_attempts"),
  "last_alert_key": "$last_alert_key",
  "outage_started_at": int("$outage_started_at"),
  "last_known_version": "$last_known_version",
  "updated_at": "$(now_iso)",
  "source": "$SOURCE_TAG"
}
open("$STATE_FILE", "w", encoding="utf-8").write(json.dumps(obj, ensure_ascii=True, indent=2))
PY
}

format_duration() {
  local seconds="${1:-0}"
  if ! [[ "$seconds" =~ ^[0-9]+$ ]]; then
    seconds=0
  fi
  if (( seconds < 0 )); then
    seconds=0
  fi

  local d h m s
  d=$((seconds / 86400))
  h=$(((seconds % 86400) / 3600))
  m=$(((seconds % 3600) / 60))
  s=$((seconds % 60))

  local out=""
  if (( d > 0 )); then out+="${d}天"; fi
  if (( h > 0 )); then out+="${h}小时"; fi
  if (( m > 0 )); then out+="${m}分"; fi
  if (( s > 0 || ${#out} == 0 )); then out+="${s}秒"; fi
  echo "$out"
}

summarize_command_output() {
  local text="${1:-}"
  text="${text//$'\r'/}"
  text="$(printf '%s' "$text" | tr '\n' ' ' | sed 's/[[:space:]]\+/ /g; s/^ //; s/ $//')"
  if [[ -z "$text" ]]; then
    echo "(no output)"
    return
  fi
  if (( ${#text} > 180 )); then
    echo "${text:0:180}..."
  else
    echo "$text"
  fi
}

json_change_summary() {
  local before_file="$1"
  local after_file="$2"
  "$PYTHON_BIN" - "$before_file" "$after_file" <<'PY'
import json
import os
import sys

before_file, after_file = sys.argv[1], sys.argv[2]

def load_json(path):
    if not path or not os.path.exists(path):
        return None, "missing"
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f), None
    except Exception as e:
        return None, f"invalid_json:{e.__class__.__name__}"

def flatten(obj, prefix=""):
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{prefix}.{k}" if prefix else str(k)
            out.update(flatten(v, p))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            p = f"{prefix}[{i}]"
            out.update(flatten(v, p))
    else:
        out[prefix or "$"] = obj
    return out

def mask(path, value):
    low_path = path.lower()
    if any(k in low_path for k in ("token", "secret", "key", "bearer", "password")):
        return "<masked>"
    if isinstance(value, str):
        if len(value) > 24:
            return value[:8] + "..." + value[-4:]
        return value
    return value

before, before_err = load_json(before_file)
after, after_err = load_json(after_file)

if before_err == "missing" and after_err == "missing":
    print("openclaw.json 不存在（修复前后都未找到）")
    raise SystemExit(0)
if before_err and before_err != "missing":
    print("openclaw.json 修复前不是有效 JSON，无法字段对比")
    raise SystemExit(0)
if after_err and after_err != "missing":
    print("openclaw.json 修复后不是有效 JSON，无法字段对比")
    raise SystemExit(0)
if before is None and after is not None:
    print("openclaw.json 新建（修复前不存在）")
    raise SystemExit(0)
if before is not None and after is None:
    print("openclaw.json 丢失（修复后不存在）")
    raise SystemExit(0)

fb = flatten(before)
fa = flatten(after)
all_keys = sorted(set(fb.keys()) | set(fa.keys()))

changes = []
for k in all_keys:
    in_b = k in fb
    in_a = k in fa
    if in_b and not in_a:
        changes.append(f"- 删除 `{k}`")
    elif in_a and not in_b:
        v = mask(k, fa[k])
        changes.append(f"- 新增 `{k}` = {json.dumps(v, ensure_ascii=False)}")
    else:
        if fb[k] != fa[k]:
            vb = mask(k, fb[k])
            va = mask(k, fa[k])
            changes.append(
                f"- 修改 `{k}`: {json.dumps(vb, ensure_ascii=False)} -> {json.dumps(va, ensure_ascii=False)}"
            )

if not changes:
    print("openclaw.json 字段无变化")
    raise SystemExit(0)

limit = 10
shown = changes[:limit]
rest = len(changes) - len(shown)
for line in shown:
    print(line)
if rest > 0:
    print(f"- ... 其余 {rest} 项未展示")
PY
}

restore_last_good_config() {
  if [[ ! -f "$CONFIG_BASELINE_FILE" ]]; then
    echo "baseline_missing: $CONFIG_BASELINE_FILE"
    return 2
  fi
  if ! cp "$CONFIG_BASELINE_FILE" "$CONFIG_FILE" 2>/dev/null; then
    echo "restore_failed: cannot copy baseline to config"
    return 3
  fi
  echo "restored_from_good"
}

run_auto_heal_sequence() {
  local incident_reason="${1:-unknown}"
  local before_file="$BASE_DIR/.openclaw.before.json"
  local after_file="$BASE_DIR/.openclaw.after.json"
  local rollback_out="skipped"
  local doctor_out=""
  local restart_out=""
  local status_out=""
  local rollback_rc=0
  local doctor_rc=0
  local restart_rc=0
  local status_rc=0
  local did_rollback=0

  if [[ -f "$CONFIG_FILE" ]]; then
    cp "$CONFIG_FILE" "$before_file" 2>/dev/null || true
  else
    : > "$before_file"
  fi

  if [[ "$AUTO_ROLLBACK_ON_CONFIG_INVALID" == "1" && ( "$incident_reason" == "config_rewritten" || "$incident_reason" == "config_invalid" ) ]]; then
    did_rollback=1
    rollback_out="$(restore_last_good_config 2>&1)" || rollback_rc=$?
  fi

  if (( did_rollback == 1 )); then
    doctor_out="skipped (rollback-first strategy)"
  else
    doctor_out="$("$OPENCLAW_BIN" doctor --fix 2>&1)" || doctor_rc=$?
  fi
  restart_out="$("$OPENCLAW_BIN" gateway restart 2>&1)" || restart_rc=$?
  status_out="$("$OPENCLAW_BIN" status --all 2>&1)" || status_rc=$?

  if [[ -f "$CONFIG_FILE" ]]; then
    cp "$CONFIG_FILE" "$after_file" 2>/dev/null || true
  else
    : > "$after_file"
  fi

  local json_changes=""
  json_changes="$(json_change_summary "$before_file" "$after_file" 2>/dev/null || echo "openclaw.json 对比失败")"

  cat <<EOF
自动自愈:
- rollback to .good: $([[ "$did_rollback" -eq 1 ]] && ([[ "$rollback_rc" -eq 0 ]] && echo "ok" || echo "exit=$rollback_rc") || echo "skipped") | $(summarize_command_output "$rollback_out")
- doctor --fix: $([[ "$doctor_rc" -eq 0 ]] && echo "ok" || echo "exit=$doctor_rc") | $(summarize_command_output "$doctor_out")
- gateway restart: $([[ "$restart_rc" -eq 0 ]] && echo "ok" || echo "exit=$restart_rc") | $(summarize_command_output "$restart_out")
- status --all: $([[ "$status_rc" -eq 0 ]] && echo "ok" || echo "exit=$status_rc") | $(summarize_command_output "$status_out")
openclaw.json 变更:
$json_changes
EOF
}

append_event() {
  local event_type="$1"
  local severity="$2"
  local reason="$3"
  local details="$4"
  EVENT_TYPE="$event_type" EVENT_SEVERITY="$severity" EVENT_REASON="$reason" EVENT_DETAILS="$details" EVENT_SOURCE="$SOURCE_TAG" EVENT_TIME="$(now_iso)" \
  "$PYTHON_BIN" - "$EVENT_LOG" <<'PY'
import json
import os
path = os.sys.argv[1]
entry = {
  "time": os.environ["EVENT_TIME"],
  "event": os.environ["EVENT_TYPE"],
  "severity": os.environ["EVENT_SEVERITY"],
  "reason": os.environ["EVENT_REASON"],
  "source": os.environ["EVENT_SOURCE"],
  "details": os.environ["EVENT_DETAILS"],
}
with open(path, "a", encoding="utf-8") as f:
  f.write(json.dumps(entry, ensure_ascii=True) + "\\n")
PY
}

config_drift_status() {
  if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "config_missing"
    return
  fi
  if [[ ! -f "$CONFIG_BASELINE_FILE" ]]; then
    echo "no_baseline"
    return
  fi
  local cur_hash base_hash
  cur_hash="$(sha256_file "$CONFIG_FILE" 2>/dev/null || true)"
  base_hash="$(sha256_file "$CONFIG_BASELINE_FILE" 2>/dev/null || true)"
  if [[ -z "$cur_hash" || -z "$base_hash" ]]; then
    echo "hash_error"
    return
  fi
  if [[ "$cur_hash" == "$base_hash" ]]; then
    echo "no_drift"
  else
    echo "drifted"
  fi
}

update_config_state_metadata() {
  local source_tag="${1:-watchdog}"
  local config_state_file="$BASE_DIR/config-state.json"
  mkdir -p "$BASE_DIR"
  "$PYTHON_BIN" - "$config_state_file" "$CONFIG_FILE" "$CONFIG_BASELINE_FILE" "$source_tag" <<'PY'
import hashlib
import json
import os
import sys
from datetime import datetime, timezone

state_file, config_file, baseline_file, source_tag = sys.argv[1:]

def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

state = {}
if os.path.exists(state_file):
    try:
        with open(state_file, "r", encoding="utf-8") as f:
            state = json.load(f)
    except Exception:
        state = {}

version = int(state.get("version", 0)) + 1
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

obj = {
    "version": version,
    "lastPromotedAt": now,
    "source": source_tag,
    "openclawHash": sha256(config_file) if os.path.exists(config_file) else "missing",
    "goodHash": sha256(baseline_file) if os.path.exists(baseline_file) else "missing",
}

with open(state_file, "w", encoding="utf-8") as f:
    json.dump(obj, f, ensure_ascii=False, indent=2)
PY
}

load_baseline_promote_state() {
  if [[ ! -f "$BASELINE_PROMOTE_STATE_FILE" ]]; then
    echo "0 none"
    return
  fi
  "$PYTHON_BIN" - "$BASELINE_PROMOTE_STATE_FILE" <<'PY'
import json
import sys

path = sys.argv[1]
try:
    with open(path, "r", encoding="utf-8") as f:
        obj = json.load(f)
except Exception:
    print("0 none")
    raise SystemExit(0)

streak = int(obj.get("healthyStreak", 0))
candidate_hash = str(obj.get("candidateHash", "none")).replace(" ", "_")
print(streak, candidate_hash)
PY
}

write_baseline_promote_state() {
  local streak="${1:-0}"
  local candidate_hash="${2:-none}"
  "$PYTHON_BIN" - "$BASELINE_PROMOTE_STATE_FILE" <<PY
import json

obj = {
  "healthyStreak": int("$streak"),
  "candidateHash": "$candidate_hash",
  "updatedAt": "$(now_iso)"
}

with open("$BASELINE_PROMOTE_STATE_FILE", "w", encoding="utf-8") as f:
  json.dump(obj, f, ensure_ascii=True, indent=2)
PY
}

promote_config_baseline_if_needed() {
  if [[ ! -f "$CONFIG_FILE" ]]; then
    return 0
  fi
  local drift
  drift="$(config_drift_status)"
  if [[ "$drift" == "no_drift" ]]; then
    write_baseline_promote_state 0 "none"
    return 0
  fi
  if [[ "$drift" != "drifted" ]]; then
    return 0
  fi

  local candidate_hash
  candidate_hash="$(sha256_file "$CONFIG_FILE" 2>/dev/null || true)"
  if [[ -z "$candidate_hash" ]]; then
    return 1
  fi

  local prev_streak prev_hash new_streak
  read -r prev_streak prev_hash <<<"$(load_baseline_promote_state)"
  if [[ "$candidate_hash" == "$prev_hash" ]]; then
    new_streak=$((prev_streak + 1))
  else
    new_streak=1
  fi

  if (( new_streak < 2 )); then
    write_baseline_promote_state "$new_streak" "$candidate_hash"
    append_event "baseline_promotion_pending" "info" "baseline_pending" "healthy pass recorded for candidate config; streak=${new_streak}/2"
    return 0
  fi

  if [[ -f "$CONFIG_BASELINE_FILE" ]]; then
    cp "$CONFIG_BASELINE_FILE" "${CONFIG_BASELINE_FILE}.prev" 2>/dev/null || true
  fi

  if cp "$CONFIG_FILE" "$CONFIG_BASELINE_FILE" 2>/dev/null; then
    write_baseline_promote_state 0 "none"
    update_config_state_metadata "watchdog-healthy-promote" || true
    append_event "baseline_updated" "info" "baseline_promoted" "openclaw.json.good updated after 2 consecutive healthy checks"
    return 0
  fi

  append_event "baseline_update_failed" "warn" "baseline_promote_failed" "failed to refresh openclaw.json.good from healthy config"
  return 1
}

summarize_config_issue() {
  local raw="$1"
  local lowered
  lowered="$(echo "$raw" | tr '[:upper:]' '[:lower:]')"
  if [[ "$lowered" == *"models.providers.google.baseurl"* && "$lowered" == *"models.providers.google.models"* ]]; then
    echo "google provider 配置被截断（缺少 baseUrl/models）"
  elif [[ "$lowered" == *"invalid config"* ]]; then
    echo "openclaw.json 配置校验失败"
  else
    echo "配置异常（建议查看 watchdog events.jsonl 详情）"
  fi
}

enrich_config_reason() {
  local raw_reason="$1"
  if [[ "$raw_reason" != "config_invalid" ]]; then
    echo "$raw_reason"
    return
  fi
  local drift
  drift="$(config_drift_status)"
  if [[ "$drift" == "drifted" ]]; then
    echo "config_rewritten"
  else
    echo "config_invalid"
  fi
}

classify_reason() {
  local raw="$1"
  local lowered
  lowered="$(echo "$raw" | tr '[:upper:]' '[:lower:]')"
  if [[ "$lowered" == *"unauthorized"* || "$lowered" == *"forbidden"* || "$lowered" == *"token"* ]]; then
    echo "auth_mismatch"
  elif [[ "$lowered" == *"invalid config"* || "$lowered" == *"config"* ]]; then
    echo "config_invalid"
  elif [[ "$lowered" == *"rpc probe"* ]]; then
    echo "rpc_probe_failed"
  elif [[ "$lowered" == *"runtime: stopped"* ]]; then
    echo "runtime_stopped"
  elif [[ "$lowered" == *"timeout"* || "$lowered" == *"unreachable"* ]]; then
    echo "health_unreachable"
  else
    echo "gateway_check_failed"
  fi
}

reason_label() {
  local reason="$1"
  case "$reason" in
    config_rewritten) echo "疑似 openclaw.json 被改写" ;;
    config_invalid) echo "配置无效" ;;
    runtime_stopped) echo "Gateway 进程未运行" ;;
    upgrade_restart) echo "升级重启（版本变更）" ;;
    rpc_probe_failed) echo "RPC 探活失败" ;;
    health_unreachable) echo "健康检查不可达" ;;
    auth_mismatch) echo "鉴权不匹配" ;;
    gateway_check_failed) echo "网关状态检查失败" ;;
    recovered) echo "服务已恢复" ;;
    *) echo "$reason" ;;
  esac
}

suggestion_for_reason() {
  local reason="$1"
  case "$reason" in
    config_rewritten)
      echo "建议：先对比并恢复 ${CONFIG_FILE} 与 ${CONFIG_BASELINE_FILE}，再重启 gateway。"
      ;;
    config_invalid)
      echo "建议：检查 openclaw 配置语法和字段完整性，修复后重启 gateway。"
      ;;
    upgrade_restart)
      echo "检测到版本号变更，Gateway 正在升级重启，通常自动恢复，无需手动处理。"
      ;;
    runtime_stopped|health_unreachable|rpc_probe_failed)
      echo "建议：先执行 openclaw gateway status，再确认端口与进程状态。"
      ;;
    auth_mismatch)
      echo "建议：核对 token / auth profile，并确认运行环境变量一致。"
      ;;
    *)
      echo "建议：查看 $EVENT_LOG 获取详细上下文。"
      ;;
  esac
}

build_alert_message() {
  local severity="$1"
  local reason="$2"
  local failures="$3"
  local details="$4"
  local outage_seconds="$5"
  local label tip
  label="$(reason_label "$reason")"
  tip="$(suggestion_for_reason "$reason")"
  local outage_text
  outage_text="$(format_duration "$outage_seconds")"
  cat <<EOF
来源: $SOURCE_TAG
级别: $severity
连续失败: $failures
已断连: $outage_text
原因判断: $label
现象: $details
$tip
EOF
}

build_recovery_message() {
  local prev_reason="$1"
  local outage_seconds="$2"
  local outage_text
  outage_text="$(format_duration "$outage_seconds")"
  cat <<EOF
来源: $SOURCE_TAG
状态: Gateway 已恢复正常
上次故障原因: $(reason_label "$prev_reason")
本次断连总时长: $outage_text
说明: runtime / rpc / health 检查均通过
EOF
}

send_discord_webhook() {
  local title="$1"
  local message="$2"
  if [[ -n "$DISCORD_WEBHOOK_URL" ]]; then
    GW_TITLE="$title" GW_MESSAGE="$message" \
    "$PYTHON_BIN" -c '
import json, os
payload = {"content": "**{}**\n{}".format(os.environ["GW_TITLE"], os.environ["GW_MESSAGE"])}
print(json.dumps(payload, ensure_ascii=True))
' | curl -sS -X POST "$DISCORD_WEBHOOK_URL" -H "Content-Type: application/json" --data @- >/dev/null || true
    return 0
  fi

  if [[ -n "$DISCORD_BOT_TOKEN" && -n "$DISCORD_CHANNEL_ID" ]]; then
    local api_url="https://discord.com/api/v10/channels/${DISCORD_CHANNEL_ID}/messages"
    GW_TITLE="$title" GW_MESSAGE="$message" \
    "$PYTHON_BIN" -c '
import json, os
payload = {"content": "**{}**\n{}".format(os.environ["GW_TITLE"], os.environ["GW_MESSAGE"])}
print(json.dumps(payload, ensure_ascii=True))
' | curl -sS -X POST "$api_url" -H "Authorization: Bot $DISCORD_BOT_TOKEN" -H "Content-Type: application/json" --data @- >/dev/null || true
  fi
}

attempt_restart() {
  local output
  if output="$("$OPENCLAW_BIN" gateway restart 2>&1)"; then
    append_event "restart_attempt" "warn" "restart_requested" "restart ok"
    echo "restart_ok"
  else
    append_event "restart_attempt" "error" "restart_failed" "$output"
    echo "restart_failed"
  fi
}

check_gateway() {
  local status_json=""
  local status_err=""
  local health_err=""
  local reason="none"
  local runtime_state=""
  local rpc_state=""
  local health_ok=0
  local status_err_file="$BASE_DIR/.status.err"
  local health_err_file="$BASE_DIR/.health.err"
  local config_hint=""

  if ! status_json="$("$OPENCLAW_BIN" gateway status --json 2>"$status_err_file")"; then
    status_err="$(<"$status_err_file")"
    if [[ -z "$status_err" ]]; then
      status_err="$("$OPENCLAW_BIN" gateway status 2>&1 || true)"
    fi
    reason="$(classify_reason "$status_err")"
    reason="$(enrich_config_reason "$reason")"
    if [[ "$reason" == "config_rewritten" || "$reason" == "config_invalid" ]]; then
      config_hint="$(summarize_config_issue "$status_err")"
      echo "fail|critical|$reason|status_command_failed; $config_hint"
      return 0
    fi
    if [[ "$reason" == "gateway_check_failed" ]]; then
      reason="runtime_stopped"
    fi
    if [[ "$reason" == "runtime_stopped" ]]; then
      local cur_ver
      cur_ver="$(get_current_version)"
      if [[ -n "$PREV_KNOWN_VERSION" && "$PREV_KNOWN_VERSION" != "none" \
            && "$PREV_KNOWN_VERSION" != "$cur_ver" ]]; then
        echo "fail|critical|upgrade_restart|runtime_not_running version=${PREV_KNOWN_VERSION}->${cur_ver}"
        return 0
      fi
    fi
    echo "fail|critical|$reason|status_command_failed"
    return 0
  fi

  runtime_state="$("$PYTHON_BIN" - "$status_json" <<'PY'
import json
import sys
text = sys.argv[1]
start = text.find('{')
if start == -1:
    print("unknown")
    raise SystemExit(1)
doc = json.loads(text[start:])
runtime = doc.get("service", {}).get("runtime", {}).get("status", "unknown")
print(str(runtime).strip().lower())
PY
)"

  rpc_state="$("$PYTHON_BIN" - "$status_json" <<'PY'
import json
import sys
text = sys.argv[1]
start = text.find('{')
if start == -1:
    print("unknown")
    raise SystemExit(0)
doc = json.loads(text[start:])
rpc = doc.get("rpc", {})
if isinstance(rpc, dict) and rpc.get("ok") is True:
    print("ok")
elif isinstance(rpc, dict) and rpc.get("ok") is False:
    print("failed")
else:
    print("unknown")
PY
)"

  if [[ "$status_json" == *"Invalid config"* || -s "$status_err_file" ]]; then
    config_hint="$(summarize_config_issue "$status_json $(<"$status_err_file" 2>/dev/null || true)")"
  fi

  if [[ "$runtime_state" != "running" ]]; then
    if [[ -n "$config_hint" ]]; then
      local c_reason
      c_reason="$(enrich_config_reason "config_invalid")"
      echo "fail|critical|$c_reason|runtime_not_running; $config_hint"
      return 0
    fi
    local cur_ver
    cur_ver="$(get_current_version)"
    if [[ -n "$PREV_KNOWN_VERSION" && "$PREV_KNOWN_VERSION" != "none" \
          && "$PREV_KNOWN_VERSION" != "$cur_ver" ]]; then
      echo "fail|critical|upgrade_restart|runtime_not_running version=${PREV_KNOWN_VERSION}->${cur_ver}"
      return 0
    fi
    echo "fail|critical|runtime_stopped|runtime_not_running"
    return 0
  fi

  if [[ "$rpc_state" == "unknown" ]]; then
    # Accept unknown rpc field, but require health endpoint below.
    :
  elif [[ "$rpc_state" != "ok" ]]; then
    echo "fail|warn|rpc_probe_failed|rpc_probe_not_ok"
    return 0
  fi

  if "$OPENCLAW_BIN" health --json --timeout "$HEALTH_TIMEOUT_MS" >/dev/null 2>"$health_err_file"; then
    health_ok=1
  else
    health_err="$(<"$health_err_file")"
  fi

  if [[ "$health_ok" -ne 1 ]]; then
    reason="$(classify_reason "${health_err:-health_unreachable}")"
    reason="$(enrich_config_reason "$reason")"
    if [[ "$reason" == "config_rewritten" || "$reason" == "config_invalid" ]]; then
      config_hint="$(summarize_config_issue "$health_err")"
      echo "fail|critical|$reason|health_probe_failed; $config_hint"
      return 0
    fi
    echo "fail|critical|$reason|health_probe_failed"
    return 0
  fi

  echo "pass|info|healthy|all_checks_ok"
}

read -r prev_status prev_failures prev_reason prev_alert_at prev_recovered_at \
        prev_restart_attempts prev_alert_key prev_outage_started_at prev_known_version \
        <<<"$(load_state)"
PREV_KNOWN_VERSION="$prev_known_version"
now="$(now_epoch)"

IFS="|" read -r check_result severity reason details <<<"$(check_gateway)"

if [[ "$check_result" == "pass" ]]; then
  promote_config_baseline_if_needed || true
  cur_ver="$(get_current_version)"
  if [[ "$prev_status" != "healthy" ]]; then
    outage_started_at="$prev_outage_started_at"
    if (( outage_started_at <= 0 )); then
      outage_started_at="$prev_alert_at"
    fi
    if (( outage_started_at <= 0 )); then
      outage_started_at="$now"
    fi
    outage_seconds=$((now - outage_started_at))
    msg="$(build_recovery_message "$prev_reason" "$outage_seconds")"
    send_discord_webhook "Gateway 已恢复" "$msg"
    append_event "recovered" "info" "recovered" "$msg"
    write_state "healthy" 0 "none" "$prev_alert_at" "$now" 0 "none" 0 "$cur_ver"
  else
    write_state "healthy" 0 "none" "$prev_alert_at" "$prev_recovered_at" 0 "$prev_alert_key" 0 "$cur_ver"
  fi
  exit 0
fi

new_failures=$((prev_failures + 1))
new_status="degraded"
[[ "$severity" == "critical" ]] && new_status="critical"
alert_key="${reason}:${new_status}"
should_alert=0

if [[ "$new_failures" -ge "$FAIL_THRESHOLD" ]]; then
  if [[ "$prev_alert_key" != "$alert_key" ]]; then
    should_alert=1
  elif (( now - prev_alert_at >= COOLDOWN_SECONDS )); then
    should_alert=1
  fi
fi

restart_attempts="$prev_restart_attempts"
if [[ "$AUTO_HEAL_ON_ALERT" != "1" && "$ENABLE_RESTART" == "1" && "$new_failures" -ge "$FAIL_THRESHOLD" && "$restart_attempts" -lt "$MAX_RESTART_ATTEMPTS" ]]; then
  restart_attempts=$((restart_attempts + 1))
  restart_result="$(attempt_restart)"
  details="$details restart=$restart_result"
fi

outage_started_at="$prev_outage_started_at"
if [[ "$prev_status" == "healthy" || "$outage_started_at" == "0" ]]; then
  if [[ "$prev_status" == "healthy" ]]; then
    outage_started_at="$now"
  elif (( prev_alert_at > 0 )); then
    outage_started_at="$prev_alert_at"
  else
    outage_started_at="$now"
  fi
fi
outage_seconds=$((now - outage_started_at))

if [[ "$should_alert" -eq 1 ]]; then
  auto_heal_report=""
  if [[ "$AUTO_HEAL_ON_ALERT" == "1" && "$new_status" == "critical" ]]; then
    auto_heal_report="$(run_auto_heal_sequence "$reason")"
  fi
  msg="$(build_alert_message "$new_status" "$reason" "$new_failures" "$details" "$outage_seconds")"
  if [[ -n "$auto_heal_report" ]]; then
    msg="${msg}"$'\n'"${auto_heal_report}"
  fi
  send_discord_webhook "Gateway 告警" "$msg"
  append_event "alert" "$new_status" "$reason" "$msg"
  write_state "$new_status" "$new_failures" "$reason" "$now" "$prev_recovered_at" "$restart_attempts" "$alert_key" "$outage_started_at" "$prev_known_version"
else
  append_event "suppressed" "$new_status" "$reason" "告警被抑制（未到阈值或冷却中）；failures=$new_failures; details=$details"
  write_state "$new_status" "$new_failures" "$reason" "$prev_alert_at" "$prev_recovered_at" "$restart_attempts" "$prev_alert_key" "$outage_started_at" "$prev_known_version"
fi
