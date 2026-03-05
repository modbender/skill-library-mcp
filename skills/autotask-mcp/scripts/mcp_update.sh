#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

SKILL_DIR="$(pwd)"
LOGFILE="${SKILL_DIR}/logs/update.log"
DIGEST_FILE="${SKILL_DIR}/.pinned-digest"
IMAGE="ghcr.io/asachs01/autotask-mcp:latest"

mkdir -p "$(dirname "$LOGFILE")"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOGFILE"
}

# Capture current image digest before pull
OLD_DIGEST=$(docker inspect --format='{{index .RepoDigests 0}}' "$IMAGE" 2>/dev/null || echo "none")

log "Checking for Autotask MCP image updates..."
log "Current digest: ${OLD_DIGEST}"

# Pull latest image
docker compose pull 2>&1 | tee -a "$LOGFILE"

# Capture new image digest after pull
NEW_DIGEST=$(docker inspect --format='{{index .RepoDigests 0}}' "$IMAGE" 2>/dev/null || echo "unknown")

log "Pulled digest: ${NEW_DIGEST}"

# --- Supply chain verification ---
# If a pinned digest file exists, verify the pulled image matches it.
# Users can pin a known-good digest by running:
#   ./scripts/mcp_pin_digest.sh
if [[ -f "$DIGEST_FILE" ]]; then
  PINNED=$(< "$DIGEST_FILE")
  # Extract just the sha256:... portion from the full repo@sha256:... string
  PULLED_SHA="${NEW_DIGEST##*@}"

  if [[ "$PULLED_SHA" != "$PINNED" ]]; then
    log "WARNING: Pulled image digest does NOT match pinned digest!"
    log "  Pinned : ${PINNED}"
    log "  Pulled : ${PULLED_SHA}"
    log "Refusing to restart. Review the new image and update the pin with:"
    log "  ./scripts/mcp_pin_digest.sh"
    exit 1
  fi
  log "Digest matches pin: ${PINNED}"
fi

if [[ "$OLD_DIGEST" != "$NEW_DIGEST" ]]; then
  log "New image detected."
  log "Recreating container with updated image..."
  docker compose up -d 2>&1 | tee -a "$LOGFILE"
  log "Update complete."
else
  log "Already on latest image. No restart needed."
fi
