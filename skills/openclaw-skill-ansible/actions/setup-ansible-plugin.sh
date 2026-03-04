#!/usr/bin/env bash
set -euo pipefail

TASK_FILE="$1"
TASK_ID=$(jq -r '.task_id' "$TASK_FILE")
ARTROOT=${OPENCLAW_ARTIFACT_ROOT:-/var/lib/openclaw/artifacts}
mkdir -p "$ARTROOT"

SOURCE=$(jq -r '.params.source // "github"' "$TASK_FILE")
PLUGIN_REF=$(jq -r '.params.plugin_ref // ""' "$TASK_FILE")
RUN_SETUP=$(jq -r '.params.run_setup // true' "$TASK_FILE")
VERIFY_STATUS=$(jq -r '.params.verify_status // true' "$TASK_FILE")
RESTART_GATEWAY=$(jq -r '.params.restart_gateway // false' "$TASK_FILE")

LOG="$ARTROOT/${TASK_ID}-setup-plugin.log"
OUT="$ARTROOT/${TASK_ID}-setup-plugin.json"

run_cmd() {
  local label="$1"
  shift
  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $label :: $*" | tee -a "$LOG"
  "$@" >>"$LOG" 2>&1
}

INSTALL_TARGET=""
case "$SOURCE" in
  github)
    INSTALL_TARGET=${PLUGIN_REF:-likesjx/openclaw-plugin-ansible}
    ;;
  npm)
    INSTALL_TARGET=${PLUGIN_REF:-@jaredlikes/openclaw-plugin-ansible}
    ;;
  path)
    if [ -z "$PLUGIN_REF" ]; then
      echo "path source requires params.plugin_ref" | tee -a "$LOG" >&2
      exit 2
    fi
    INSTALL_TARGET="$PLUGIN_REF"
    ;;
  *)
    echo "unsupported source: $SOURCE" | tee -a "$LOG" >&2
    exit 2
    ;;
esac

run_cmd "plugin-install" openclaw plugins install "$INSTALL_TARGET"

if [ "$RUN_SETUP" = "true" ]; then
  run_cmd "ansible-setup" openclaw ansible setup
fi

if [ "$RESTART_GATEWAY" = "true" ]; then
  run_cmd "gateway-restart" openclaw gateway restart
fi

if [ "$VERIFY_STATUS" = "true" ]; then
  run_cmd "ansible-status" openclaw ansible status
  if openclaw gateway --help >/dev/null 2>&1; then
    run_cmd "gateway-health" openclaw gateway health || true
  fi
fi

jq -n \
  --arg task_id "$TASK_ID" \
  --arg status "completed" \
  --arg action "setup-ansible-plugin" \
  --arg source "$SOURCE" \
  --arg plugin_ref "$INSTALL_TARGET" \
  --argjson run_setup "$RUN_SETUP" \
  --argjson verify_status "$VERIFY_STATUS" \
  --argjson restart_gateway "$RESTART_GATEWAY" \
  --arg artifact_log "$LOG" \
  '{task_id:$task_id,status:$status,action:$action,source:$source,plugin_ref:$plugin_ref,run_setup:$run_setup,verify_status:$verify_status,restart_gateway:$restart_gateway,artifact_log:$artifact_log}' > "$OUT"

echo "setup-ansible-plugin complete: $OUT" | tee -a "$LOG"
