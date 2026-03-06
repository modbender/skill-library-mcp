#!/usr/bin/env bash
# =============================================================================
# update-skill.sh — Auto-updater for the genviral skill
# =============================================================================
#
# Checks fdarkaou/genviral-skill for updates and applies only skill-owned files.
# Safe to run anytime — never touches user-owned files (workspace/).
#
# Usage: ./update-skill.sh [--force] [--dry-run]
#
# Called daily by OpenClaw cron. Exit 0 = success (updated or already current).
# =============================================================================

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REMOTE_URL="https://github.com/fdarkaou/genviral-skill.git"
REMOTE_BRANCH="main"
LOCK_FILE="$SKILL_DIR/.update.lock"
VERSION_FILE="$SKILL_DIR/.skill-version"

# Files that are SKILL-OWNED (safe to overwrite on update)
# Everything in workspace/ is USER-OWNED and never touched.
SKILL_OWNED_FILES=(
  "SKILL.md"
  "docs/setup.md"
  "scripts/genviral.sh"
  "docs/prompts/slideshow.md"
  "docs/prompts/hooks.md"
  "scripts/update-skill.sh"
  "docs/references/analytics-loop.md"
  "docs/references/competitor-research.md"
  "docs/api/accounts-files.md"
  "docs/api/posts.md"
  "docs/api/slideshows.md"
  "docs/api/packs.md"
  "docs/api/templates.md"
  "docs/api/analytics.md"
  "docs/api/pipeline.md"
  "docs/api/errors.md"
)

DRY_RUN=false
FORCE=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=true; shift ;;
    --force)   FORCE=true; shift ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

# Prevent concurrent runs
if [[ -f "$LOCK_FILE" ]]; then
  echo "Update already in progress (lock file exists). Skipping."
  exit 0
fi
touch "$LOCK_FILE"
trap "rm -f '$LOCK_FILE'" EXIT

# Read current tracked commit
CURRENT_SHA=""
if [[ -f "$VERSION_FILE" ]]; then
  CURRENT_SHA=$(cat "$VERSION_FILE" | tr -d '[:space:]')
fi

echo "Checking for genviral skill updates..."
echo "Remote: $REMOTE_URL"
echo "Current SHA: ${CURRENT_SHA:-"(none)"}"

# Fetch latest commit SHA from GitHub API (no git required)
# Resolve GitHub token (explicit env var, or from gh CLI)
GH_TOKEN="${GITHUB_TOKEN:-$(gh auth token 2>/dev/null || echo "")}"

REMOTE_SHA=$(curl -sf \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: Bearer $GH_TOKEN" \
  "https://api.github.com/repos/fdarkaou/genviral-skill/commits/$REMOTE_BRANCH" \
  | jq -r '.sha' 2>/dev/null || echo "")

if [[ -z "$REMOTE_SHA" ]]; then
  echo "ERROR: Could not fetch remote SHA. Check network or GITHUB_TOKEN."
  exit 1
fi

echo "Remote SHA:  $REMOTE_SHA"

if [[ "$CURRENT_SHA" == "$REMOTE_SHA" && "$FORCE" != "true" ]]; then
  echo "Already up to date. Nothing to do."
  exit 0
fi

echo "Update available! Applying..."

UPDATED_FILES=()
FAILED_FILES=()

for FILE in "${SKILL_OWNED_FILES[@]}"; do
  RAW_URL="https://raw.githubusercontent.com/fdarkaou/genviral-skill/$REMOTE_SHA/$FILE"
  TARGET="$SKILL_DIR/$FILE"
  
  if [[ "$DRY_RUN" == "true" ]]; then
    echo "[DRY RUN] Would update: $FILE"
    continue
  fi

  # Fetch and write atomically
  TMPFILE=$(mktemp)
  if curl -sf "$RAW_URL" -o "$TMPFILE"; then
    mkdir -p "$(dirname "$TARGET")"
    mv "$TMPFILE" "$TARGET"
    # Make scripts executable
    [[ "$FILE" == scripts/* ]] && chmod +x "$TARGET"
    UPDATED_FILES+=("$FILE")
    echo "  ✓ Updated: $FILE"
  else
    rm -f "$TMPFILE"
    # File may not exist in remote (optional file) — not a hard error
    FAILED_FILES+=("$FILE")
    echo "  - Skipped (not found in remote): $FILE"
  fi
done

if [[ "$DRY_RUN" == "true" ]]; then
  echo "Dry run complete. No files changed."
  exit 0
fi

# Save new SHA
echo "$REMOTE_SHA" > "$VERSION_FILE"

echo ""
echo "Update complete."
echo "  Updated: ${#UPDATED_FILES[@]} files"
echo "  Skipped: ${#FAILED_FILES[@]} files"
echo "  New version: $REMOTE_SHA"

# Emit openclaw event if anything changed
if [[ ${#UPDATED_FILES[@]} -gt 0 ]]; then
  UPDATE_LIST=$(IFS=', '; echo "${UPDATED_FILES[*]}")
  openclaw system event \
    --text "genviral skill updated to ${REMOTE_SHA:0:7}: $UPDATE_LIST" \
    --mode now 2>/dev/null || true
fi

exit 0
