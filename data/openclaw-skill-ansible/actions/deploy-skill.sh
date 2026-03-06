#!/usr/bin/env bash
set -euo pipefail

TASK_FILE="$1"
TASK_ID=$(jq -r '.task_id' "$TASK_FILE")
URL=$(jq -r '.params.artifact_url // ""' "$TASK_FILE")
NAME=$(jq -r '.params.name // ""' "$TASK_FILE")
SHA_EXPECT=$(jq -r '.params.sha // ""' "$TASK_FILE")

ARTROOT=${OPENCLAW_ARTIFACT_ROOT:-/var/lib/openclaw/artifacts}
mkdir -p "$ARTROOT"
LOG="$ARTROOT/${TASK_ID}-deploy.log"
OUT="$ARTROOT/${TASK_ID}-deploy.json"

if [ -z "$URL" ] || [ -z "$NAME" ]; then
  echo "artifact_url and name are required" | tee -a "$LOG" >&2
  exit 2
fi
if [[ "$URL" != https://* ]]; then
  echo "artifact_url must use https" | tee -a "$LOG" >&2
  exit 2
fi
if [ -z "$SHA_EXPECT" ]; then
  echo "sha is required and must be sha256" | tee -a "$LOG" >&2
  exit 2
fi
if [[ ! "$SHA_EXPECT" =~ ^[a-fA-F0-9]{64}$ ]]; then
  echo "sha must be a 64-char hex digest" | tee -a "$LOG" >&2
  exit 2
fi

if [ "${OPENCLAW_ALLOW_DEPLOY_SKILL:-0}" != "1" ]; then
  echo "deploy-skill disabled: set OPENCLAW_ALLOW_DEPLOY_SKILL=1" | tee -a "$LOG" >&2
  exit 3
fi

TMP_DIR="/tmp/${TASK_ID}"
mkdir -p "$TMP_DIR"
ARCHIVE="$TMP_DIR/artifact.tar.gz"

echo "Downloading $URL" | tee -a "$LOG"
curl -fsSL "$URL" -o "$ARCHIVE"

if command -v sha256sum >/dev/null 2>&1; then
  SHA_ACT=$(sha256sum "$ARCHIVE" | awk '{print $1}')
else
  SHA_ACT=$(shasum -a 256 "$ARCHIVE" | awk '{print $1}')
fi

if [ "$SHA_EXPECT" != "$SHA_ACT" ]; then
  echo "SHA mismatch expected=$SHA_EXPECT actual=$SHA_ACT" | tee -a "$LOG" >&2
  exit 4
fi

DEST="/opt/openclaw/skills/$NAME"
mkdir -p "$DEST"

echo "Extracting into $DEST" | tee -a "$LOG"
tar -xzf "$ARCHIVE" -C "$DEST"

if [ -x "$DEST/test_smoke.sh" ]; then
  echo "Running smoke test" | tee -a "$LOG"
  (cd "$DEST" && ./test_smoke.sh) || { echo "Smoke failed" | tee -a "$LOG" >&2; exit 5; }
fi

jq -n \
  --arg task_id "$TASK_ID" \
  --arg status "completed" \
  --arg name "$NAME" \
  --arg destination "$DEST" \
  --arg url "$URL" \
  --arg sha256 "$SHA_ACT" \
  '{task_id:$task_id,status:$status,name:$name,destination:$destination,artifact_url:$url,sha256:$sha256}' > "$OUT"

echo "Deployed $NAME to $DEST" | tee -a "$LOG"
