#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_ROOT="$(cd "$SKILL_DIR/.." && pwd)"
ENV_FILE="${OPENCLAW_DISPATCH_ENV:-$SKILLS_ROOT/dispatch.env.local}"

# Safe env loader (no `source`): only accepts KEY=VALUE for allowlisted keys.
ALLOWED_KEYS=(
  REPOS_ROOT RESULTS_BASE LAUNCH_LOG_DIR
  DISPATCH_PERMISSION_MODE
  DISPATCHI_MAX_ITERATIONS DISPATCHI_COMPLETION_PROMISE
  AUTO_EXIT_ON_COMPLETE AUTO_EXIT_GRACE_SEC AUTO_EXIT_MAX_WAIT_SEC AUTO_EXIT_POLL_SEC
  ENABLE_CALLBACK CODEHOOK_GROUP_DEFAULT TELEGRAM_GROUP
  OPENCLAW_BIN OPENCLAW_CONFIG OPENCLAW_TELEGRAM_ACCOUNT CLAUDE_CODE_BIN
  DISPATCHI_DRY_RUN
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
DISPATCHI_MAX_ITERATIONS="${DISPATCHI_MAX_ITERATIONS:-20}"
DISPATCHI_COMPLETION_PROMISE="${DISPATCHI_COMPLETION_PROMISE:-COMPLETE}"
AUTO_EXIT_ON_COMPLETE="${AUTO_EXIT_ON_COMPLETE:-1}"
AUTO_EXIT_GRACE_SEC="${AUTO_EXIT_GRACE_SEC:-20}"
AUTO_EXIT_MAX_WAIT_SEC="${AUTO_EXIT_MAX_WAIT_SEC:-21600}"
AUTO_EXIT_POLL_SEC="${AUTO_EXIT_POLL_SEC:-5}"
ENABLE_CALLBACK="${ENABLE_CALLBACK:-0}"
CODEHOOK_GROUP_DEFAULT="${CODEHOOK_GROUP_DEFAULT:--1002547895616}"
TELEGRAM_GROUP="${TELEGRAM_GROUP:-$CODEHOOK_GROUP_DEFAULT}"
DISPATCHI_DRY_RUN="${DISPATCHI_DRY_RUN:-0}"

OPENCLAW_BIN="${OPENCLAW_BIN:-$(command -v openclaw 2>/dev/null || echo "$HOME/.npm-global/bin/openclaw")}"
OPENCLAW_CONFIG="${OPENCLAW_CONFIG:-$HOME/.openclaw/openclaw.json}"
OPENCLAW_TELEGRAM_ACCOUNT="${OPENCLAW_TELEGRAM_ACCOUNT:-coder}"
CLAUDE_CODE_BIN="${CLAUDE_CODE_BIN:-/home/miniade/.local/bin/claude}"

if [[ $# -lt 3 ]]; then
  echo "Usage: /dispatchi <project> <task-name> <prompt...>" >&2
  exit 2
fi

RUNNER="$SKILL_DIR/scripts/vendor/claude_code_run.py"
if [[ ! -f "$RUNNER" ]]; then
  echo "Error: bundled runner not found: $RUNNER" >&2
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

RUN_ID="$(date -u +%Y%m%d-%H%M%S)-${PROJECT}-${TASK_NAME}-interactive"
RESULT_DIR="$RESULTS_BASE/$PROJECT/$RUN_ID"
RUN_LOG="$LAUNCH_LOG_DIR/${RUN_ID}.log"
mkdir -p "$RESULT_DIR"

TMUX_SOCKET_DIR="/tmp/clawdbot-tmux-sockets"
mkdir -p "$TMUX_SOCKET_DIR"

PROJECT_KEY="$(printf '%s' "$PROJECT" | tr -cd '[:alnum:]-_' | cut -c1-20)"
[[ -z "$PROJECT_KEY" ]] && PROJECT_KEY="proj"
RUN_KEY="$(printf '%s' "$RUN_ID" | sha1sum | awk '{print $1}' | cut -c1-12)"
TMUX_SESSION="cc-${PROJECT_KEY}-${RUN_KEY}"
TMUX_SOCKET_NAME="cc-${PROJECT_KEY}-${RUN_KEY}.sock"
TMUX_SOCKET_PATH="$TMUX_SOCKET_DIR/$TMUX_SOCKET_NAME"

export RESULT_DIR OPENCLAW_BIN OPENCLAW_CONFIG OPENCLAW_TELEGRAM_ACCOUNT CLAUDE_CODE_BIN

TG_GROUP=""
if [[ "$ENABLE_CALLBACK" == "1" ]]; then
  TG_GROUP="$TELEGRAM_GROUP"
fi

jq -n \
  --arg name "$TASK_NAME" \
  --arg group "$TG_GROUP" \
  --arg prompt "$PROMPT" \
  --arg workdir "$WORKDIR" \
  --arg ts "$(date -Iseconds)" \
  --argjson agent_teams "$( [[ $NEED_TEAMS -eq 1 ]] && echo true || echo false )" \
  --arg mode "interactive" \
  --arg run_id "$RUN_ID" \
  --arg tmux_session "$TMUX_SESSION" \
  --arg tmux_socket_name "$TMUX_SOCKET_NAME" \
  '{task_name:$name, telegram_group:$group, prompt:$prompt, workdir:$workdir, started_at:$ts, agent_teams:$agent_teams, status:"running", dispatch_mode:$mode, run_id:$run_id, tmux_session:$tmux_session, tmux_socket_name:$tmux_socket_name}' \
  > "$RESULT_DIR/task-meta.json"
: > "$RESULT_DIR/task-output.txt"

RALPH_CMD="/ralph-loop:ralph-loop \"${PROMPT}\" --completion-promise \"${DISPATCHI_COMPLETION_PROMISE}\" --max-iterations ${DISPATCHI_MAX_ITERATIONS}"

CMD=(python3 "$RUNNER"
  --mode interactive
  --cwd "$WORKDIR"
  --tmux-session "$TMUX_SESSION"
  --tmux-socket-dir "$TMUX_SOCKET_DIR"
  --tmux-socket-name "$TMUX_SOCKET_NAME"
  -p "$RALPH_CMD"
)
if [[ -n "$DISPATCH_PERMISSION_MODE" ]]; then
  CMD+=(--permission-mode "$DISPATCH_PERMISSION_MODE")
fi
if [[ "$NEED_TEAMS" -eq 1 ]]; then
  CMD+=(--agent-teams)
fi

if [[ "$DISPATCHI_DRY_RUN" == "1" ]]; then
  printf 'DRY_RUN dispatchi cmd: %q ' "${CMD[@]}"
  echo
  echo "DRY_RUN result_dir=$RESULT_DIR"
  exit 0
fi

if ! "${CMD[@]}" >>"$RUN_LOG" 2>&1; then
  echo "ERROR: failed to start interactive dispatch" >>"$RUN_LOG"
  exit 1
fi

if ! tmux -S "$TMUX_SOCKET_PATH" has-session -t "$TMUX_SESSION" 2>/dev/null; then
  echo "ERROR: tmux session not found after startup" >>"$RUN_LOG"
  exit 1
fi

tmux -S "$TMUX_SOCKET_PATH" pipe-pane -o -t "${TMUX_SESSION}:0.0" "cat >> '$RESULT_DIR/task-output.txt'" || true

if [[ "$AUTO_EXIT_ON_COMPLETE" == "1" ]]; then
  (
    sleep "$AUTO_EXIT_GRACE_SEC"
    END_TS=$(( $(date +%s) + AUTO_EXIT_MAX_WAIT_SEC ))
    while [ "$(date +%s)" -lt "$END_TS" ]; do
      SNAP=$(tmux -S "$TMUX_SOCKET_PATH" capture-pane -p -J -t "${TMUX_SESSION}:0.0" -S -200 2>/dev/null || true)
      CLEAN=$(printf '%s' "$SNAP" | sed -r 's/\x1B\[[0-9;?]*[ -/]*[@-~]//g')

      if printf '%s\n' "$CLEAN" | grep -Eq "^[[:space:]]*${DISPATCHI_COMPLETION_PROMISE}[[:space:]]*$"; then
        tmux -S "$TMUX_SOCKET_PATH" send-keys -t "${TMUX_SESSION}:0.0" -l -- "/exit" || true
        tmux -S "$TMUX_SOCKET_PATH" send-keys -t "${TMUX_SESSION}:0.0" Enter || true
        sleep 2
        tmux -S "$TMUX_SOCKET_PATH" kill-session -t "$TMUX_SESSION" >/dev/null 2>&1 || true
        break
      fi

      sleep "$AUTO_EXIT_POLL_SEC"
    done
  ) >>"$RUN_LOG" 2>&1 &
fi

echo "DISPATCHI_STARTED pid=$$ project=$PROJECT task=$TASK_NAME workdir=$WORKDIR run_id=$RUN_ID result_dir=$RESULT_DIR log=$RUN_LOG max_iter=$DISPATCHI_MAX_ITERATIONS completion=$DISPATCHI_COMPLETION_PROMISE callback=$ENABLE_CALLBACK"
