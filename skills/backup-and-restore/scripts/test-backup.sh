#!/usr/bin/env bash
# test-backup.sh — Validate backup setup: encryption + all cloud destinations.
# Part of the OpenClaw backup skill.
set -euo pipefail

# ---------------------------------------------------------------------------
# Paths & defaults
# ---------------------------------------------------------------------------
OPENCLAW_DIR="$HOME/.openclaw"
SKILL_DIR="$OPENCLAW_DIR/workspace/skills/backup"
CONFIG_FILE="$SKILL_DIR/config.json"
CRED_DIR="$OPENCLAW_DIR/credentials/backup"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
log()  { echo "[test] $(date '+%H:%M:%S') $*"; }
die()  { echo "[test] ERROR: $*" >&2; exit 1; }
warn() { echo "[test] WARNING: $*" >&2; }
pass() { echo "[test] ✓ $*"; }
fail() { echo "[test] ✗ $*" >&2; }

safe_load_creds() {
  # Safely read KEY=VALUE pairs from a credential file without executing arbitrary shell
  local file="$1"
  [[ -f "$file" ]] || return 1
  while IFS='=' read -r key value; do
    # Skip comments and empty lines
    [[ -z "$key" || "$key" =~ ^[[:space:]]*# ]] && continue
    # Strip 'export ' prefix if present
    key="${key#export }"
    # Trim whitespace
    key="$(echo "$key" | xargs)"
    # Strip surrounding quotes from value
    value="${value#\"}"
    value="${value%\"}"
    value="${value#\'}"
    value="${value%\'}"
    export "$key=$value"
  done < "$file"
}

WORK_DIR="$(mktemp -d)"
trap 'rm -rf "$WORK_DIR"' EXIT

FAILURES=0

# ---------------------------------------------------------------------------
# Check prerequisites
# ---------------------------------------------------------------------------
log "Checking prerequisites..."

if command -v jq &>/dev/null; then
  pass "jq installed"
else
  fail "jq not installed (sudo apt install jq)"
  ((FAILURES++))
fi

# ---------------------------------------------------------------------------
# Test encryption
# ---------------------------------------------------------------------------
log "Testing encryption..."

ENCRYPT="true"
if [[ -f "$CONFIG_FILE" ]] && command -v jq &>/dev/null; then
  ENCRYPT=$(jq -r '.encrypt // true' "$CONFIG_FILE")
fi

if [[ "$ENCRYPT" == "true" ]]; then
  PASSPHRASE="${BACKUP_PASSPHRASE:-}"
  if [[ -z "$PASSPHRASE" && -f "$CRED_DIR/backup-passphrase" ]]; then
    PASSPHRASE="$(cat "$CRED_DIR/backup-passphrase")"
  fi

  if [[ -z "$PASSPHRASE" ]]; then
    fail "Encryption enabled but no passphrase found"
    ((FAILURES++))
  else
    # Create test file, encrypt, decrypt, verify
    TEST_FILE="$WORK_DIR/test-data.txt"
    echo "openclaw-backup-test-$(date +%s)" > "$TEST_FILE"

    gpg --batch --yes --symmetric --cipher-algo AES256 \
      --passphrase "$PASSPHRASE" \
      --output "$TEST_FILE.gpg" \
      "$TEST_FILE" 2>/dev/null

    gpg --batch --yes --decrypt \
      --passphrase "$PASSPHRASE" \
      --output "$TEST_FILE.dec" \
      "$TEST_FILE.gpg" 2>/dev/null

    if diff -q "$TEST_FILE" "$TEST_FILE.dec" &>/dev/null; then
      pass "Encryption round-trip OK"
    else
      fail "Encryption round-trip failed — decrypted data doesn't match"
      ((FAILURES++))
    fi
  fi
else
  log "Encryption disabled, skipping test"
fi

# ---------------------------------------------------------------------------
# Test cloud destinations
# ---------------------------------------------------------------------------
if [[ -f "$CONFIG_FILE" ]] && command -v jq &>/dev/null; then
  DEST_COUNT=$(jq '.destinations | length' "$CONFIG_FILE")
else
  DEST_COUNT=0
fi

if [[ "$DEST_COUNT" -eq 0 ]]; then
  log "No cloud destinations configured — skipping upload tests"
else
  # Create a tiny test file for upload
  TEST_UPLOAD="$WORK_DIR/openclaw-test-$(date +%s).txt"
  echo "openclaw backup connectivity test" > "$TEST_UPLOAD"
  TEST_NAME="$(basename "$TEST_UPLOAD")"

  for i in $(seq 0 $((DEST_COUNT - 1))); do
    DEST=$(jq ".destinations[$i]" "$CONFIG_FILE")
    DTYPE=$(echo "$DEST" | jq -r '.type')

    log "Testing $DTYPE destination..."

    case "$DTYPE" in
      s3)
        BUCKET=$(echo "$DEST" | jq -r '.bucket')
        REGION=$(echo "$DEST" | jq -r '.region // "us-east-1"')
        safe_load_creds "$CRED_DIR/aws-credentials" || true

        if aws s3 cp "$TEST_UPLOAD" "${BUCKET%/}/$TEST_NAME" --region "$REGION" 2>&1 && \
           aws s3 rm "${BUCKET%/}/$TEST_NAME" --region "$REGION" 2>&1; then
          pass "S3 upload + cleanup OK"
        else
          fail "S3 upload failed"; ((FAILURES++))
        fi
        ;;

      r2)
        BUCKET=$(echo "$DEST" | jq -r '.bucket')
        ENDPOINT=$(echo "$DEST" | jq -r '.endpoint')
        safe_load_creds "$CRED_DIR/r2-credentials" || true

        if aws s3 cp "$TEST_UPLOAD" "s3://${BUCKET}/$TEST_NAME" --endpoint-url "$ENDPOINT" 2>&1 && \
           aws s3 rm "s3://${BUCKET}/$TEST_NAME" --endpoint-url "$ENDPOINT" 2>&1; then
          pass "R2 upload + cleanup OK"
        else
          fail "R2 upload failed"; ((FAILURES++))
        fi
        ;;

      b2)
        BUCKET=$(echo "$DEST" | jq -r '.bucket')
        safe_load_creds "$CRED_DIR/b2-credentials" || true

        if b2 upload-file "$BUCKET" "$TEST_UPLOAD" "$TEST_NAME" 2>&1; then
          b2 delete-file-version "$TEST_NAME" 2>/dev/null || true
          pass "B2 upload OK"
        else
          fail "B2 upload failed"; ((FAILURES++))
        fi
        ;;

      gcs)
        BUCKET=$(echo "$DEST" | jq -r '.bucket')
        [[ -f "$CRED_DIR/gcs-key.json" ]] && \
          gcloud auth activate-service-account --key-file="$CRED_DIR/gcs-key.json" 2>/dev/null || true

        if gsutil cp "$TEST_UPLOAD" "${BUCKET%/}/$TEST_NAME" 2>&1 && \
           gsutil rm "${BUCKET%/}/$TEST_NAME" 2>&1; then
          pass "GCS upload + cleanup OK"
        else
          fail "GCS upload failed"; ((FAILURES++))
        fi
        ;;

      gdrive)
        FOLDER=$(echo "$DEST" | jq -r '.folder // "OpenClaw Backups"')
        RCLONE_CONF="$CRED_DIR/rclone.conf"

        if [[ ! -f "$RCLONE_CONF" ]]; then
          fail "rclone.conf not found"; ((FAILURES++))
        elif rclone copy "$TEST_UPLOAD" "gdrive:$FOLDER/" --config "$RCLONE_CONF" 2>&1 && \
             rclone delete "gdrive:$FOLDER/$TEST_NAME" --config "$RCLONE_CONF" 2>&1; then
          pass "Google Drive upload + cleanup OK"
        else
          fail "Google Drive upload failed"; ((FAILURES++))
        fi
        ;;

      rsync)
        TARGET=$(echo "$DEST" | jq -r '.target')
        if rsync -avz "$TEST_UPLOAD" "$TARGET/" 2>&1; then
          pass "rsync upload OK"
        else
          fail "rsync upload failed"; ((FAILURES++))
        fi
        ;;

      *)
        fail "Unknown destination type: $DTYPE"; ((FAILURES++))
        ;;
    esac
  done
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
if [[ "$FAILURES" -eq 0 ]]; then
  log "All tests passed ✓"
  exit 0
else
  log "$FAILURES test(s) failed ✗"
  exit 1
fi
