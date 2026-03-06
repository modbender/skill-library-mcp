#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

SKILL_DIR="$(pwd)"
DIGEST_FILE="${SKILL_DIR}/.pinned-digest"
IMAGE="ghcr.io/asachs01/autotask-mcp:latest"

# Get the current image digest
FULL_DIGEST=$(docker inspect --format='{{index .RepoDigests 0}}' "$IMAGE" 2>/dev/null || echo "")

if [[ -z "$FULL_DIGEST" ]]; then
  echo "Error: Image not found locally. Pull it first with: ./scripts/mcp_pull.sh"
  exit 1
fi

# Extract sha256:... from repo@sha256:...
SHA="${FULL_DIGEST##*@}"

echo "Current image digest:"
echo "  ${SHA}"
echo ""

if [[ -f "$DIGEST_FILE" ]]; then
  OLD_PIN=$(< "$DIGEST_FILE")
  echo "Previously pinned digest:"
  echo "  ${OLD_PIN}"
  echo ""
fi

read -rp "Pin this digest? [y/N] " confirm
if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
  echo "Aborted."
  exit 0
fi

echo "$SHA" > "$DIGEST_FILE"
echo "Digest pinned to ${DIGEST_FILE}"
echo ""
echo "The update script will now refuse to restart if a pulled image"
echo "does not match this digest. Run this script again after reviewing"
echo "a new image version to update the pin."
