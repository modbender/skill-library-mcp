#!/usr/bin/env bash
set -euo pipefail

# Smoke-test detached runner support used by publish.sh.
#
# Usage:
#   bash skills/leak-publish/scripts/smoke_persistent_runner.sh
#   bash skills/leak-publish/scripts/smoke_persistent_runner.sh --mode auto
#   bash skills/leak-publish/scripts/smoke_persistent_runner.sh --mode tmux
#   bash skills/leak-publish/scripts/smoke_persistent_runner.sh --sleep-seconds 20
#   bash skills/leak-publish/scripts/smoke_persistent_runner.sh --keep

MODE="auto"
SLEEP_SECONDS=20
KEEP_RUNNING=0
BACKEND=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --mode)
      if [ "$#" -lt 2 ]; then
        echo "[smoke] ERROR: --mode requires a value."
        exit 1
      fi
      MODE="$2"
      shift 2
      ;;
    --mode=*)
      MODE="${1#--mode=}"
      shift
      ;;
    --sleep-seconds)
      if [ "$#" -lt 2 ]; then
        echo "[smoke] ERROR: --sleep-seconds requires a value."
        exit 1
      fi
      SLEEP_SECONDS="$2"
      shift 2
      ;;
    --sleep-seconds=*)
      SLEEP_SECONDS="${1#--sleep-seconds=}"
      shift
      ;;
    --keep)
      KEEP_RUNNING=1
      shift
      ;;
    -h|--help)
      sed -n '1,24p' "$0"
      exit 0
      ;;
    *)
      echo "[smoke] ERROR: unknown argument: $1"
      exit 1
      ;;
  esac
done

if ! [[ "$SLEEP_SECONDS" =~ ^[0-9]+$ ]] || [ "$SLEEP_SECONDS" -lt 5 ]; then
  echo "[smoke] ERROR: --sleep-seconds must be an integer >= 5."
  exit 1
fi

if [ "$MODE" != "auto" ] && [ "$MODE" != "systemd" ] && [ "$MODE" != "launchd" ] && [ "$MODE" != "tmux" ] && [ "$MODE" != "screen" ] && [ "$MODE" != "nohup" ]; then
  echo "[smoke] ERROR: invalid --mode '$MODE' (expected: auto|systemd|launchd|tmux|screen|nohup)."
  exit 1
fi

can_systemd() {
  command -v systemd-run >/dev/null 2>&1 \
    && command -v systemctl >/dev/null 2>&1 \
    && systemctl --user show-environment >/dev/null 2>&1
}

can_launchd() {
  [ "$(uname -s)" = "Darwin" ] && command -v launchctl >/dev/null 2>&1
}

can_tmux() {
  command -v tmux >/dev/null 2>&1
}

can_screen() {
  command -v screen >/dev/null 2>&1
}

STARTED_AT="$(date +%Y%m%d-%H%M%S)"
JOB_ID="leak-smoke-${STARTED_AT}-$$"
TMP_ROOT="${TMPDIR:-/tmp}/${JOB_ID}"
WORKER_SCRIPT="${TMP_ROOT}/worker.sh"
PID_FILE="${TMP_ROOT}/worker.pid"
READY_FILE="${TMP_ROOT}/worker.ready"
DONE_FILE="${TMP_ROOT}/worker.done"
LOG_FILE="${TMP_ROOT}/worker.log"

mkdir -p "$TMP_ROOT"

cat >"$WORKER_SCRIPT" <<EOF
#!/usr/bin/env bash
set -euo pipefail
echo "\$\$" >"$PID_FILE"
date +%s >"$READY_FILE"
echo "[worker] started pid=\$\$ at \$(date -u +"%Y-%m-%dT%H:%M:%SZ")" >>"$LOG_FILE"
sleep "$SLEEP_SECONDS"
echo "[worker] done at \$(date -u +"%Y-%m-%dT%H:%M:%SZ")" >>"$LOG_FILE"
date +%s >"$DONE_FILE"
EOF
chmod 700 "$WORKER_SCRIPT"

RUNNER_PID=""
WORKER_PID=""
cleanup() {
  if [ "$KEEP_RUNNING" -eq 1 ]; then
    return 0
  fi
  case "$BACKEND" in
    systemd)
      systemctl --user stop "$JOB_ID" >/dev/null 2>&1 || true
      ;;
    launchd)
      launchctl remove "$JOB_ID" >/dev/null 2>&1 || true
      ;;
    tmux)
      tmux kill-session -t "$JOB_ID" >/dev/null 2>&1 || true
      ;;
    screen)
      screen -S "$JOB_ID" -X quit >/dev/null 2>&1 || true
      ;;
    nohup)
      if [ -n "$RUNNER_PID" ]; then
        kill "$RUNNER_PID" >/dev/null 2>&1 || true
      fi
      ;;
  esac
}
trap cleanup EXIT INT TERM

echo "[smoke] requested mode: $MODE"
echo "[smoke] job id:         $JOB_ID"
echo "[smoke] log:            $LOG_FILE"

start_backend() {
  local target="$1"
  case "$target" in
    systemd)
      if can_systemd && systemd-run --user --collect --unit "$JOB_ID" "$WORKER_SCRIPT" >/dev/null 2>&1; then
        BACKEND="systemd"
        return 0
      fi
      return 1
      ;;
    launchd)
      if can_launchd && launchctl submit -l "$JOB_ID" -- "$WORKER_SCRIPT" >/dev/null 2>&1; then
        BACKEND="launchd"
        return 0
      fi
      return 1
      ;;
    tmux)
      if can_tmux && tmux new-session -d -s "$JOB_ID" "$WORKER_SCRIPT" >/dev/null 2>&1; then
        BACKEND="tmux"
        return 0
      fi
      return 1
      ;;
    screen)
      if can_screen && screen -dmS "$JOB_ID" "$WORKER_SCRIPT" >/dev/null 2>&1; then
        BACKEND="screen"
        return 0
      fi
      return 1
      ;;
    nohup)
      nohup "$WORKER_SCRIPT" >/dev/null 2>&1 &
      RUNNER_PID="$!"
      BACKEND="nohup"
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

stop_backend() {
  case "$BACKEND" in
    systemd)
      systemctl --user stop "$JOB_ID" >/dev/null 2>&1 || true
      ;;
    launchd)
      launchctl remove "$JOB_ID" >/dev/null 2>&1 || true
      ;;
    tmux)
      tmux kill-session -t "$JOB_ID" >/dev/null 2>&1 || true
      ;;
    screen)
      screen -S "$JOB_ID" -X quit >/dev/null 2>&1 || true
      ;;
    nohup)
      if [ -n "$RUNNER_PID" ]; then
        kill "$RUNNER_PID" >/dev/null 2>&1 || true
      fi
      ;;
  esac
}

wait_for_worker_ready() {
  local loops="$1"
  for _ in $(seq 1 "$loops"); do
    if [ -s "$PID_FILE" ] && [ -s "$READY_FILE" ]; then
      WORKER_PID="$(cat "$PID_FILE")"
      if kill -0 "$WORKER_PID" >/dev/null 2>&1; then
        return 0
      fi
    fi
    sleep 0.1
  done
  return 1
}

if [ "$MODE" = "auto" ]; then
  for candidate in systemd launchd tmux screen nohup; do
    if start_backend "$candidate"; then
      if wait_for_worker_ready 30; then
        break
      fi
      echo "[smoke] backend '$candidate' started but did not become healthy; trying next."
      stop_backend
      BACKEND=""
      RUNNER_PID=""
    fi
  done
else
  if ! start_backend "$MODE"; then
    echo "[smoke] ERROR: requested backend '$MODE' is not available or failed to start on this host."
    exit 1
  fi
  if ! wait_for_worker_ready 50; then
    echo "[smoke] FAIL: backend '$MODE' did not become healthy."
    exit 1
  fi
fi

if [ -z "$BACKEND" ]; then
  echo "[smoke] FAIL: could not start any detached backend."
  exit 1
fi

echo "[smoke] backend: $BACKEND"

echo "[smoke] PASS: detached worker is alive (pid=$WORKER_PID)."
if [ "$KEEP_RUNNING" -eq 1 ]; then
  echo "[smoke] KEEP mode is enabled; process will continue for ${SLEEP_SECONDS}s."
  echo "[smoke] stop manually with:"
  case "$BACKEND" in
    systemd) echo "  systemctl --user stop $JOB_ID" ;;
    launchd) echo "  launchctl remove $JOB_ID" ;;
    tmux) echo "  tmux kill-session -t $JOB_ID" ;;
    screen) echo "  screen -S $JOB_ID -X quit" ;;
    nohup) echo "  kill $RUNNER_PID" ;;
  esac
fi
