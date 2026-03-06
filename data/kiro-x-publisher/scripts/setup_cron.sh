#!/usr/bin/env bash
# Plugin producer: kiroai.io
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "$ROOT_DIR"

NODE22_BIN="${NODE22_BIN:-$HOME/.nvm/versions/node/v22.22.0/bin/node}"
PROFILE="${OPENCLAW_PROFILE:-dev}"
CRON_EXPR="${X_HOT_CRON_EXPR:-0 9 * * *}"
TZ_NAME="${X_HOT_TZ:-Asia/Shanghai}"
JOB_NAME="${X_HOT_JOB_NAME:-Daily Kiro X Hot Publisher}"
QUERIES="${X_HOT_QUERIES:-AI,OpenAI,DeepSeek,Claude,Gemini}"
BATCH="${X_HOT_BATCH_SIZE:-10}"

fail() {
  echo "[x-hot] $*" >&2
  exit 1
}

validate_no_ctrl() {
  local value="$1"
  local label="$2"
  # Reject non-printable/control chars.
  if [[ "$value" =~ [^[:print:]] ]]; then
    fail "$label contains non-printable characters"
  fi
}

validate_queries() {
  local value="$1"
  validate_no_ctrl "$value" "X_HOT_QUERIES"
  if [ "${#value}" -eq 0 ] || [ "${#value}" -gt 400 ]; then
    fail "X_HOT_QUERIES must be 1..400 chars"
  fi
  # Block shell metacharacters/separators that could alter execution if interpreted downstream.
  if [[ "$value" =~ [\;\&\|\<\>\`\$\\] ]]; then
    fail "X_HOT_QUERIES contains unsafe shell metacharacters"
  fi
}

validate_batch() {
  local value="$1"
  if [[ ! "$value" =~ ^[0-9]+$ ]]; then
    fail "X_HOT_BATCH_SIZE must be an integer"
  fi
  if [ "$value" -lt 1 ] || [ "$value" -gt 100 ]; then
    fail "X_HOT_BATCH_SIZE must be between 1 and 100"
  fi
}

if [ ! -x "$NODE22_BIN" ]; then
  fail "Node22 binary not found: $NODE22_BIN"
fi

validate_no_ctrl "$PROFILE" "OPENCLAW_PROFILE"
validate_no_ctrl "$JOB_NAME" "X_HOT_JOB_NAME"
validate_no_ctrl "$TZ_NAME" "X_HOT_TZ"
validate_no_ctrl "$CRON_EXPR" "X_HOT_CRON_EXPR"
validate_queries "$QUERIES"
validate_batch "$BATCH"

# Escape single quotes defensively for the command text passed to cron.
SAFE_QUERIES="${QUERIES//\'/\'\\\'\'}"
MESSAGE="Run: python3 skills/kiro-x-hot-publisher/scripts/x_hot_pipeline.py --queries '$SAFE_QUERIES' --batch-size $BATCH --post"

echo "[x-hot] using node: $NODE22_BIN"
"$NODE22_BIN" openclaw.mjs --profile "$PROFILE" cron add \
  --name "$JOB_NAME" \
  --cron "$CRON_EXPR" \
  --tz "$TZ_NAME" \
  --session isolated \
  --message "$MESSAGE" \
  --no-deliver

echo "[x-hot] cron job created"
"$NODE22_BIN" openclaw.mjs --profile "$PROFILE" cron list
