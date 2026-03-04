#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_ROOT="$(cd "$SKILL_DIR/.." && pwd)"
ENV_FILE="${OPENCLAW_DISPATCH_ENV:-$SKILLS_ROOT/dispatch.env.local}"

# Safe env loader (no `source`): only accepts KEY=VALUE for allowlisted keys.
ALLOWED_KEYS=(
  REPOS_ROOT RESULTS_BASE LAUNCH_LOG_DIR
  DISPATCH_PERMISSION_MODE DISPATCH_TEAMMATE_MODE DISPATCH_TIMEOUT_SEC
  ENABLE_CALLBACK CODEHOOK_GROUP_DEFAULT TELEGRAM_GROUP
  OPENCLAW_BIN OPENCLAW_CONFIG OPENCLAW_TELEGRAM_ACCOUNT CLAUDE_CODE_BIN
  DISPATCH_DRY_RUN
)

load_env_file() {
  local file="$1"
  [[ -f "$file" ]] || return 0

  while IFS= read -r line || [[ -n "$line" ]]; do
    [[ "$line" =~ ^[[:space:]]*# ]] && continue
    [[ -z "${line//[[:space:]]/}" ]] && continue
    [[ "$line" =~ ^[A-Za-z_][A-Za-z0-9_]*= ]] || continue

    local key="${line%%=*}"
    local val="${line#*=}"

    key="$(echo "$key" | tr -d '[:space:]')"
    val="${val#"${val%%[![:space:]]*}"}"

    # Strip simple surrounding quotes.
    if [[ "$val" =~ ^\".*\"$ ]]; then val="${val:1:-1}"; fi
    if [[ "$val" =~ ^\'.*\'$ ]]; then val="${val:1:-1}"; fi

    case " ${ALLOWED_KEYS[*]} " in
      *" $key "*) export "$key=$val" ;;
      *) ;;
    esac
  done < "$file"
}

load_env_file "$ENV_FILE"

REPOS_ROOT="${REPOS_ROOT:-/home/miniade/repos}"
RESULTS_BASE="${RESULTS_BASE:-/home/miniade/clawd/data/claude-code-results}"
LAUNCH_LOG_DIR="${LAUNCH_LOG_DIR:-/home/miniade/clawd/data/dispatch-launch}"
DISPATCH_PERMISSION_MODE="${DISPATCH_PERMISSION_MODE:-}"
DISPATCH_TEAMMATE_MODE="${DISPATCH_TEAMMATE_MODE:-}"
DISPATCH_TIMEOUT_SEC="${DISPATCH_TIMEOUT_SEC:-7200}"
ENABLE_CALLBACK="${ENABLE_CALLBACK:-0}"
CODEHOOK_GROUP_DEFAULT="${CODEHOOK_GROUP_DEFAULT:--1002547895616}"
TELEGRAM_GROUP="${TELEGRAM_GROUP:-$CODEHOOK_GROUP_DEFAULT}"
DISPATCH_DRY_RUN="${DISPATCH_DRY_RUN:-0}"

OPENCLAW_BIN="${OPENCLAW_BIN:-$(command -v openclaw 2>/dev/null || echo "$HOME/.npm-global/bin/openclaw")}"
OPENCLAW_CONFIG="${OPENCLAW_CONFIG:-$HOME/.openclaw/openclaw.json}"
OPENCLAW_TELEGRAM_ACCOUNT="${OPENCLAW_TELEGRAM_ACCOUNT:-coder}"
CLAUDE_CODE_BIN="${CLAUDE_CODE_BIN:-/home/miniade/.local/bin/claude}"

if [[ $# -lt 3 ]]; then
  echo "Usage: /dispatch <project> <task-name> <prompt...>" >&2
  exit 2
fi

DISPATCH_SH="$SKILL_DIR/scripts/vendor/dispatch.sh"
if [[ ! -f "$DISPATCH_SH" ]]; then
  echo "Error: bundled dispatch script not found: $DISPATCH_SH" >&2
  exit 2
fi

PROJECT="$1"
TASK_NAME="$2"
shift 2
PROMPT="$*"

WORKDIR="${REPOS_ROOT}/${PROJECT}"
mkdir -p "$WORKDIR" "$LAUNCH_LOG_DIR"

NEED_TEAMS=0
if echo "$PROMPT" | grep -Eiq '(Agent Team|Agent Teams|多智能体|并行|testing agent)'; then
  NEED_TEAMS=1
fi

RUN_ID="$(date -u +%Y%m%d-%H%M%S)-${PROJECT}-${TASK_NAME}"
RESULT_DIR="$RESULTS_BASE/$PROJECT/$RUN_ID"
RUN_LOG="$LAUNCH_LOG_DIR/${RUN_ID}.log"
mkdir -p "$RESULT_DIR"

export RESULT_DIR DISPATCH_TIMEOUT_SEC OPENCLAW_BIN OPENCLAW_CONFIG OPENCLAW_TELEGRAM_ACCOUNT CLAUDE_CODE_BIN

CMD=(bash "$DISPATCH_SH"
  -n "$TASK_NAME"
  -w "$WORKDIR"
  -p "$PROMPT"
)

if [[ "$ENABLE_CALLBACK" == "1" ]]; then
  CMD+=(-g "$TELEGRAM_GROUP")
fi

if [[ -n "$DISPATCH_PERMISSION_MODE" ]]; then
  CMD+=(--permission-mode "$DISPATCH_PERMISSION_MODE")
fi

if [[ "$NEED_TEAMS" -eq 1 ]]; then
  CMD+=(--agent-teams)
  if [[ -n "$DISPATCH_TEAMMATE_MODE" ]]; then
    CMD+=(--teammate-mode "$DISPATCH_TEAMMATE_MODE")
  fi
fi

if [[ "$DISPATCH_DRY_RUN" == "1" ]]; then
  printf 'DRY_RUN dispatch cmd: %q ' "${CMD[@]}"
  echo
  echo "DRY_RUN result_dir=$RESULT_DIR"
  exit 0
fi

nohup "${CMD[@]}" >"$RUN_LOG" 2>&1 &
PID=$!

# Quick startup sanity check: allow immediate successful completion,
# but fail fast if process died before initializing result metadata.
sleep 1
if ! ps -p "$PID" >/dev/null 2>&1 && [[ ! -f "$RESULT_DIR/task-meta.json" ]]; then
  echo "Error: dispatch process exited before startup. See log: $RUN_LOG" >&2
  tail -n 40 "$RUN_LOG" >&2 || true
  exit 1
fi

echo "DISPATCH_STARTED pid=$PID project=$PROJECT task=$TASK_NAME workdir=$WORKDIR teams=$NEED_TEAMS run_id=$RUN_ID result_dir=$RESULT_DIR log=$RUN_LOG callback=$ENABLE_CALLBACK"
