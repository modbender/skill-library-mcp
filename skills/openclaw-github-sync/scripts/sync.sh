#!/usr/bin/env bash
set -euo pipefail

# Export a curated subset of the OpenClaw workspace into a separate git repo and push.
#
# Required env:
#   SYNC_REMOTE   e.g. git@github.com:YOUR_ORG/YOUR_REPO.git
# Optional env:
#   WORKSPACE_DIR default: $HOME/.openclaw/workspace
#   SYNC_REPO_DIR      default: $WORKSPACE_DIR/openclaw-sync-repo

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=bootstrap.sh
source "$SCRIPT_DIR/bootstrap.sh"
openclaw_github_sync_load_env \
  WORKSPACE_DIR SYNC_REPO_DIR SYNC_REMOTE

WORKSPACE_DIR="${WORKSPACE_DIR:-$HOME/.openclaw/workspace}"
SYNC_REPO_DIR="${SYNC_REPO_DIR:-$WORKSPACE_DIR/openclaw-sync-repo}"
MANIFEST="$SCRIPT_DIR/../references/export-manifest.txt"
GROUPS_JSON="$SCRIPT_DIR/../references/groups.json"
SCAN_IGNORE_FILE="$SCRIPT_DIR/../references/secret-scan-ignore.txt"
SYNC_REMOTE="${SYNC_REMOTE:-}"

if [[ -z "$SYNC_REMOTE" ]]; then
  echo "SYNC_REMOTE is required" >&2
  exit 2
fi

mkdir -p "$SYNC_REPO_DIR"

if [[ ! -d "$SYNC_REPO_DIR/.git" ]]; then
  git -C "$SYNC_REPO_DIR" init
  git -C "$SYNC_REPO_DIR" branch -M main
  git -C "$SYNC_REPO_DIR" remote add origin "$SYNC_REMOTE"
fi

# Pull if remote has main already.
if git -C "$SYNC_REPO_DIR" ls-remote --exit-code --heads origin main >/dev/null 2>&1; then
  git -C "$SYNC_REPO_DIR" fetch origin main
  git -C "$SYNC_REPO_DIR" reset --hard origin/main
fi

# Export allowlisted files into SYNC_REPO_DIR.
# We rsync from workspace into sync dir, path by path.
while IFS= read -r path; do
  # strip comments/blank
  path="${path%%#*}"
  path="$(echo "$path" | xargs || true)"
  [[ -z "$path" ]] && continue

  src="$WORKSPACE_DIR/$path"
  if [[ -d "$src" ]]; then
    mkdir -p "$SYNC_REPO_DIR/$path"
    # Preserve directory paths exactly as listed in the manifest.
    rsync -a --delete --exclude '.git/' "$src/" "$SYNC_REPO_DIR/$path/"
  elif [[ -f "$src" ]]; then
    mkdir -p "$SYNC_REPO_DIR/$(dirname "$path")"
    rsync -a "$src" "$SYNC_REPO_DIR/$path"
  else
    echo "WARN: not found: $path" >&2
  fi

done < "$MANIFEST"

# Ensure we never accidentally commit workspace git metadata.
rm -rf "$SYNC_REPO_DIR/.git"/.openclaw 2>/dev/null || true

# Generate/update sync repo README from template + current change status.
README_TEMPLATE="$SCRIPT_DIR/../references/README_TEMPLATE.md"
README_GEN="$SCRIPT_DIR/generate_readme.py"
STATUS_FILE="$(mktemp)"
git -C "$SYNC_REPO_DIR" status --porcelain > "$STATUS_FILE"
if [[ -x "$README_GEN" ]] && [[ -f "$README_TEMPLATE" ]]; then
  "$README_GEN" "$SYNC_REPO_DIR" "$README_TEMPLATE" "$STATUS_FILE"
else
  echo "WARN: README generator/template missing; skipping README update" >&2
fi
rm -f "$STATUS_FILE"

# Secret scan (refuse to commit/push if likely secrets are present in the sync repo).
SCAN_SCRIPT="$SCRIPT_DIR/scan_secrets.py"
if [[ -x "$SCAN_SCRIPT" ]]; then
  set +e
  SCAN_OUT=$(SCAN_IGNORE_FILE="$SCAN_IGNORE_FILE" "$SCAN_SCRIPT" "$SYNC_REPO_DIR" 2>&1)
  SCAN_CODE=$?
  set -e
  echo "$SCAN_OUT"
  if [[ $SCAN_CODE -eq 3 ]]; then
    # Contract: exit 3 means secret-like material detected.
    exit 3
  elif [[ $SCAN_CODE -ne 0 ]]; then
    echo "WARN: secret scan failed (code $SCAN_CODE); refusing to commit" >&2
    exit 4
  fi
else
  echo "WARN: scan_secrets.py not found/executable; refusing to commit" >&2
  exit 4
fi

# Commit per group when there are changes.
if [[ -z "$(git -C "$SYNC_REPO_DIR" status --porcelain)" ]]; then
  echo "No changes to sync."
  exit 0
fi

# Use jq if available; fallback to single commit.
if command -v jq >/dev/null 2>&1; then
  mapfile -t group_names < <(jq -r '.groups[].name' "$GROUPS_JSON")

  for g in "${group_names[@]}"; do
    commit_msg=$(jq -r ".groups[] | select(.name==\"$g\") | .commitMessage" "$GROUPS_JSON")
    mapfile -t paths < <(jq -r ".groups[] | select(.name==\"$g\") | .paths[]" "$GROUPS_JSON")

    # Stage paths if they exist and have changes.
    staged_any=0
    for p in "${paths[@]}"; do
      if [[ -e "$SYNC_REPO_DIR/$p" ]]; then
        git -C "$SYNC_REPO_DIR" add -A -- "$p" || true
        staged_any=1
      fi
    done

    # If staging introduced something, commit it.
    if [[ $staged_any -eq 1 ]] && [[ -n "$(git -C "$SYNC_REPO_DIR" diff --cached --name-only)" ]]; then
      git -C "$SYNC_REPO_DIR" commit -m "$commit_msg" -m "$(date -u +%F\ %T) UTC"
    else
      # Reset index for this group so later groups can stage cleanly.
      git -C "$SYNC_REPO_DIR" reset
    fi
  done

  # Any remaining changes not covered by groups.
  if [[ -n "$(git -C "$SYNC_REPO_DIR" status --porcelain)" ]]; then
    git -C "$SYNC_REPO_DIR" add -A
    git -C "$SYNC_REPO_DIR" commit -m "Sync: misc" -m "$(date -u +%F\ %T) UTC"
  fi
else
  git -C "$SYNC_REPO_DIR" add -A
  git -C "$SYNC_REPO_DIR" commit -m "Sync context" -m "$(date -u +%F\ %T) UTC"
fi

git -C "$SYNC_REPO_DIR" push -u origin main
echo "Synced to $SYNC_REMOTE"
