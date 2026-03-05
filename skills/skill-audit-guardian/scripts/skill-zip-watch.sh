#!/usr/bin/env bash
set -euo pipefail

WATCH_DIR="${1:-$HOME/Desktop/skill-drop}"
AUDIT_SCRIPT="/Users/gascomp/.openclaw/workspace/scripts/skill-zip-audit.sh"
DASH_SCRIPT="/Users/gascomp/.openclaw/workspace/scripts/generate-skill-audit-pro.py"
SAFE_DIR="$WATCH_DIR/safe"
CAUTION_DIR="$WATCH_DIR/caution"
REMOVE_DIR="$WATCH_DIR/remove"
FAILED_DIR="$WATCH_DIR/failed"
LOG_FILE="$WATCH_DIR/watch.log"

mkdir -p "$WATCH_DIR" "$SAFE_DIR" "$CAUTION_DIR" "$REMOVE_DIR" "$FAILED_DIR"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] watching: $WATCH_DIR" | tee -a "$LOG_FILE"
echo "Drop .zip files into: $WATCH_DIR" | tee -a "$LOG_FILE"

# Track processed files in this run
PROCESSED_FILE="$WATCH_DIR/.processed.list"
touch "$PROCESSED_FILE"

move_by_risk() {
  local zip_path="$1"
  local report_path="$2"
  local risk="UNKNOWN"

  if [[ -f "$report_path" ]]; then
    risk="$(grep -E '^- Risk: \*\*.*\*\*$' "$report_path" | sed -E 's/^- Risk: \*\*(.*)\*\*$/\1/' | tr '[:lower:]' '[:upper:]' | head -n1 || true)"
  fi

  case "$risk" in
    SAFE)
      mv "$zip_path" "$SAFE_DIR/"
      echo "[$(date '+%Y-%m-%d %H:%M:%S')] SAFE -> moved to $SAFE_DIR" | tee -a "$LOG_FILE"
      ;;
    CAUTION)
      mv "$zip_path" "$CAUTION_DIR/"
      echo "[$(date '+%Y-%m-%d %H:%M:%S')] CAUTION -> moved to $CAUTION_DIR" | tee -a "$LOG_FILE"
      ;;
    REMOVE)
      mv "$zip_path" "$REMOVE_DIR/"
      echo "[$(date '+%Y-%m-%d %H:%M:%S')] REMOVE -> moved to $REMOVE_DIR" | tee -a "$LOG_FILE"
      ;;
    *)
      mv "$zip_path" "$CAUTION_DIR/"
      echo "[$(date '+%Y-%m-%d %H:%M:%S')] UNKNOWN risk -> moved to $CAUTION_DIR" | tee -a "$LOG_FILE"
      ;;
  esac
}

while true; do
  shopt -s nullglob
  for z in "$WATCH_DIR"/*.zip; do
    # skip if already processed in this watcher run
    if grep -Fxq "$z" "$PROCESSED_FILE" 2>/dev/null; then
      continue
    fi

    echo "$z" >> "$PROCESSED_FILE"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] auditing: $z" | tee -a "$LOG_FILE"

    set +e
    audit_output="$($AUDIT_SCRIPT "$z" 2>&1)"
    audit_status=$?
    set -e

    echo "$audit_output" >> "$LOG_FILE"

    if [[ $audit_status -eq 0 ]]; then
      report_path="$(printf '%s\n' "$audit_output" | sed -n 's/^Report: //p' | tail -n1)"
      if [[ -z "$report_path" ]]; then
        report_path=""
      fi
      move_by_risk "$z" "$report_path"

      # refresh dashboard after each successful audit
      if [[ -x "$DASH_SCRIPT" ]]; then
        set +e
        "$DASH_SCRIPT" >> "$LOG_FILE" 2>&1
        set -e
      fi
    else
      mv "$z" "$FAILED_DIR/" 2>/dev/null || true
      echo "[$(date '+%Y-%m-%d %H:%M:%S')] FAIL -> moved to $FAILED_DIR" | tee -a "$LOG_FILE"
    fi
  done
  sleep 5
done
