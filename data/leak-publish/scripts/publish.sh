#!/usr/bin/env bash
set -euo pipefail

PUBLIC_CONFIRM_PHRASE="I_UNDERSTAND_PUBLIC_EXPOSURE"
RUN_MODE="auto"

# Publish a file with the leak server and print a clear share link.
#
# Usage:
#   bash skills/leak-publish/scripts/publish.sh --file ./protected/asset.bin --price 0.01 --window 15m --pay-to 0x... [--network eip155:84532] [--port 4021] [--confirmed] [--public]
#   bash skills/leak-publish/scripts/publish.sh --run-mode auto --file ./protected/asset.bin --price 0.01 --window 15m --pay-to 0x...
#   bash skills/leak-publish/scripts/publish.sh --foreground --file ./protected/asset.bin --price 0.01 --window 15m --pay-to 0x...

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_DIR="$(cd "$SKILL_DIR/../.." && pwd)"

run_leak() {
  if command -v leak >/dev/null 2>&1; then
    leak "$@"
    return
  fi
  echo "[leak-publish] ERROR: leak is not installed on PATH."
  echo "[leak-publish] Install leak-cli first: npm i -g leak-cli"
  exit 1
}

exec_leak() {
  if command -v leak >/dev/null 2>&1; then
    exec leak "$@"
  fi
  echo "[leak-publish] ERROR: leak is not installed on PATH."
  echo "[leak-publish] Install leak-cli first: npm i -g leak-cli"
  exit 1
}

normalize_input_path() {
  local p="$1"
  if [[ "$p" == ~/* ]]; then
    echo "${HOME}/${p#~/}"
    return
  fi
  echo "$p"
}

resolve_abs_path() {
  local raw="$1"
  local dir
  local base
  dir="$(cd "$(dirname "$raw")" && pwd -P)" || return 1
  base="$(basename "$raw")"
  echo "${dir}/${base}"
}

is_blocked_sensitive_path() {
  local abs_path="$1"
  local prefix
  local -a blocked=(
    "${HOME}/.ssh"
    "${HOME}/.aws"
    "${HOME}/.gnupg"
    "${HOME}/.config/gcloud"
    "/etc"
    "/private/etc"
    "/proc"
    "/sys"
    "/var/run/secrets"
    "/private/var/run/secrets"
  )

  for prefix in "${blocked[@]}"; do
    case "$abs_path" in
      "$prefix"|"$prefix"/*)
        return 0
        ;;
    esac
  done

  return 1
}

# Run from repo root so relative paths behave like the README examples.
cd "$REPO_DIR"

# Build args for `leak leak ...`
ARGS=("leak")
PASSTHROUGH_ARGS=()

PORT=4021
HAS_PUBLIC=0
HAS_PUBLIC_CONFIRM=0
FILE_PATH_RAW=""
PREV=""
for ARG in "$@"; do
  if [ "$PREV" = "--run-mode" ]; then
    RUN_MODE="$ARG"
    PREV=""
    continue
  fi
  if [ "$PREV" = "--file" ]; then
    FILE_PATH_RAW="$ARG"
    PREV=""
    PASSTHROUGH_ARGS+=("$ARG")
    continue
  fi
  if [ "$PREV" = "--port" ]; then
    PORT="$ARG"
    PREV=""
    PASSTHROUGH_ARGS+=("$ARG")
    continue
  fi
  if [ "$PREV" = "--public-confirm" ]; then
    HAS_PUBLIC_CONFIRM=1
    PREV=""
    PASSTHROUGH_ARGS+=("$ARG")
    continue
  fi

  case "$ARG" in
    --run-mode)
      PREV="--run-mode"
      ;;
    --run-mode=*)
      RUN_MODE="${ARG#--run-mode=}"
      ;;
    --background|--detach|--persistent)
      RUN_MODE="background"
      ;;
    --foreground)
      RUN_MODE="foreground"
      ;;
    --file)
      PREV="--file"
      PASSTHROUGH_ARGS+=("$ARG")
      ;;
    --file=*)
      FILE_PATH_RAW="${ARG#--file=}"
      PASSTHROUGH_ARGS+=("$ARG")
      ;;
    --port)
      PREV="--port"
      PASSTHROUGH_ARGS+=("$ARG")
      ;;
    --port=*)
      PORT="${ARG#--port=}"
      PASSTHROUGH_ARGS+=("$ARG")
      ;;
    --public)
      HAS_PUBLIC=1
      PASSTHROUGH_ARGS+=("$ARG")
      ;;
    --public-confirm)
      HAS_PUBLIC_CONFIRM=1
      PREV="--public-confirm"
      PASSTHROUGH_ARGS+=("$ARG")
      ;;
    --public-confirm=*)
      HAS_PUBLIC_CONFIRM=1
      PASSTHROUGH_ARGS+=("$ARG")
      ;;
    *)
      PASSTHROUGH_ARGS+=("$ARG")
      ;;
  esac
done

if [ -z "$FILE_PATH_RAW" ]; then
  echo "[leak-publish] ERROR: --file <path> is required."
  exit 1
fi

FILE_PATH="$(normalize_input_path "$FILE_PATH_RAW")"
ABS_FILE_PATH="$(resolve_abs_path "$FILE_PATH")" || {
  echo "[leak-publish] ERROR: cannot resolve file path: $FILE_PATH_RAW"
  exit 1
}

if [ -L "$FILE_PATH" ]; then
  echo "[leak-publish] ERROR: symlink paths are not allowed: $FILE_PATH_RAW"
  exit 1
fi

if [ -d "$FILE_PATH" ]; then
  echo "[leak-publish] ERROR: directories are not allowed: $FILE_PATH_RAW"
  exit 1
fi

if [ ! -f "$FILE_PATH" ]; then
  echo "[leak-publish] ERROR: file does not exist or is not a regular file: $FILE_PATH_RAW"
  exit 1
fi

if is_blocked_sensitive_path "$ABS_FILE_PATH"; then
  echo "[leak-publish] ERROR: blocked sensitive path: $ABS_FILE_PATH"
  exit 1
fi

if [ "$HAS_PUBLIC" -eq 1 ] && [ "$HAS_PUBLIC_CONFIRM" -eq 0 ]; then
  if [ -t 0 ] && [ -t 1 ]; then
    echo "[leak-publish] You are about to expose a local file to the public internet."
    read -r -p "[leak-publish] Type ${PUBLIC_CONFIRM_PHRASE} to continue: " CONFIRM
    if [ "$CONFIRM" != "$PUBLIC_CONFIRM_PHRASE" ]; then
      echo "[leak-publish] Public exposure confirmation failed. Aborting."
      exit 1
    fi
    PASSTHROUGH_ARGS+=("--public-confirm" "$PUBLIC_CONFIRM_PHRASE")
  else
    echo "[leak-publish] ERROR: --public requires --public-confirm ${PUBLIC_CONFIRM_PHRASE} in non-interactive mode."
    exit 1
  fi
fi

ARGS+=("${PASSTHROUGH_ARGS[@]}")

if [ "$RUN_MODE" != "auto" ] && [ "$RUN_MODE" != "foreground" ] && [ "$RUN_MODE" != "background" ]; then
  echo "[leak-publish] ERROR: invalid --run-mode '$RUN_MODE' (expected: auto|foreground|background)."
  exit 1
fi

SHOULD_BACKGROUND=0
if [ "$RUN_MODE" = "background" ] || [ "$RUN_MODE" = "auto" ]; then
  SHOULD_BACKGROUND=1
fi

if [ "$SHOULD_BACKGROUND" -eq 1 ]; then
  STARTED_AT="$(date +%Y%m%d-%H%M%S)"
  SESSION_NAME="leak-publish-${STARTED_AT}"
  LOG_DIR="$REPO_DIR/.leak/logs"
  LOG_FILE="$LOG_DIR/${SESSION_NAME}.log"
  mkdir -p "$LOG_DIR"

  RECURSIVE_CMD=(bash "$SCRIPT_DIR/publish.sh" --foreground "${PASSTHROUGH_ARGS[@]}")
  printf -v RECURSIVE_CMD_STR '%q ' "${RECURSIVE_CMD[@]}"
  printf -v REPO_DIR_ESCAPED '%q' "$REPO_DIR"
  printf -v LOG_FILE_ESCAPED '%q' "$LOG_FILE"
  LAUNCH_CMD="cd ${REPO_DIR_ESCAPED} && ${RECURSIVE_CMD_STR} >> ${LOG_FILE_ESCAPED} 2>&1"

  if command -v systemd-run >/dev/null 2>&1 && command -v systemctl >/dev/null 2>&1; then
    if systemctl --user show-environment >/dev/null 2>&1; then
      if systemd-run --user --collect --unit "$SESSION_NAME" /bin/bash -lc "$LAUNCH_CMD" >/dev/null 2>&1; then
        echo "[leak-publish] Started persistent publish via systemd user unit: ${SESSION_NAME}"
        echo "[leak-publish] Log file: ${LOG_FILE}"
        echo "[leak-publish] Follow logs: tail -f ${LOG_FILE}"
        echo "[leak-publish] Stop:        systemctl --user stop ${SESSION_NAME}"
        if [ "$HAS_PUBLIC" -eq 0 ]; then
          echo "[leak-publish] Local promo link (same machine): http://127.0.0.1:${PORT}/"
          echo "[leak-publish] Local buy link (same machine):   http://127.0.0.1:${PORT}/download"
        else
          echo "[leak-publish] Public tunnel URL will be printed in the log when ready."
        fi
        exit 0
      fi
    fi
  fi

  if [ "$(uname -s)" = "Darwin" ] && command -v launchctl >/dev/null 2>&1; then
    if launchctl submit -l "$SESSION_NAME" -o "$LOG_FILE" -e "$LOG_FILE" -- /bin/bash -lc "$LAUNCH_CMD" >/dev/null 2>&1; then
      echo "[leak-publish] Started persistent publish via launchd job: ${SESSION_NAME}"
      echo "[leak-publish] Log file: ${LOG_FILE}"
      echo "[leak-publish] Stop: launchctl remove ${SESSION_NAME}"
      if [ "$HAS_PUBLIC" -eq 0 ]; then
        echo "[leak-publish] Local promo link (same machine): http://127.0.0.1:${PORT}/"
        echo "[leak-publish] Local buy link (same machine):   http://127.0.0.1:${PORT}/download"
      else
        echo "[leak-publish] Public tunnel URL will be printed in the log when ready."
      fi
      exit 0
    fi
  fi

  if command -v tmux >/dev/null 2>&1; then
    tmux new-session -d -s "$SESSION_NAME" "$LAUNCH_CMD"
    echo "[leak-publish] Started persistent publish in tmux session: ${SESSION_NAME}"
    echo "[leak-publish] Log file: ${LOG_FILE}"
    echo "[leak-publish] Attach: tmux attach -t ${SESSION_NAME}"
    echo "[leak-publish] Stop:   tmux kill-session -t ${SESSION_NAME}"
    if [ "$HAS_PUBLIC" -eq 0 ]; then
      echo "[leak-publish] Local promo link (same machine): http://127.0.0.1:${PORT}/"
      echo "[leak-publish] Local buy link (same machine):   http://127.0.0.1:${PORT}/download"
    else
      echo "[leak-publish] Public tunnel URL will be printed in the log when ready."
    fi
    exit 0
  fi

  if command -v screen >/dev/null 2>&1; then
    screen -dmS "$SESSION_NAME" /bin/bash -lc "$LAUNCH_CMD"
    echo "[leak-publish] Started persistent publish in screen session: ${SESSION_NAME}"
    echo "[leak-publish] Log file: ${LOG_FILE}"
    echo "[leak-publish] Attach: screen -r ${SESSION_NAME}"
    echo "[leak-publish] Stop:   screen -S ${SESSION_NAME} -X quit"
    if [ "$HAS_PUBLIC" -eq 0 ]; then
      echo "[leak-publish] Local promo link (same machine): http://127.0.0.1:${PORT}/"
      echo "[leak-publish] Local buy link (same machine):   http://127.0.0.1:${PORT}/download"
    else
      echo "[leak-publish] Public tunnel URL will be printed in the log when ready."
    fi
    exit 0
  fi

  nohup /bin/bash -lc "$LAUNCH_CMD" >/dev/null 2>&1 &
  BG_PID="$!"
  echo "[leak-publish] Started publish with nohup fallback, PID: ${BG_PID}"
  echo "[leak-publish] Log file: ${LOG_FILE}"
  echo "[leak-publish] Stop: kill ${BG_PID}"
  echo "[leak-publish] NOTE: nohup is the least reliable option under aggressive process-tree cleanup."
  if [ "$HAS_PUBLIC" -eq 0 ]; then
    echo "[leak-publish] Local promo link (same machine): http://127.0.0.1:${PORT}/"
    echo "[leak-publish] Local buy link (same machine):   http://127.0.0.1:${PORT}/download"
  else
    echo "[leak-publish] Public tunnel URL will be printed in the log when ready."
  fi
  exit 0
fi

if [ "$HAS_PUBLIC" -eq 1 ]; then
  TMP="$(mktemp)"
  set +e
  run_leak "${ARGS[@]}" 2>&1 | tee "$TMP"
  CODE=${PIPESTATUS[0]}
  set -e

  URL=$(grep -Eo 'https://[a-z0-9-]+\.trycloudflare\.com' "$TMP" | head -n 1 || true)
  rm -f "$TMP" || true

  if [ -n "$URL" ]; then
    echo
    echo "[leak-publish] PROMO LINK: ${URL}/"
    echo "[leak-publish] BUY LINK:   ${URL}/download"
  fi

  exit "$CODE"
else
  echo "[leak-publish] Starting leak server (no public tunnel)."
  echo "[leak-publish] Local promo link (same machine): http://127.0.0.1:${PORT}/"
  echo "[leak-publish] Local buy link (same machine):   http://127.0.0.1:${PORT}/download"
  echo "[leak-publish] Tip: to expose publicly, re-run with --public (requires cloudflared)."
  exec_leak "${ARGS[@]}"
fi
