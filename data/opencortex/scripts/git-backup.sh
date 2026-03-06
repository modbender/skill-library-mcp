#!/bin/bash
# OpenCortex — Safe auto-commit workspace changes
#
# SECURITY: Secrets are scrubbed in a temp copy only.
# Workspace files are NEVER modified — no exposure window.
#
# Usage:
#   git-backup.sh          # commit locally only
#   git-backup.sh --push   # commit and push to remote
set -euo pipefail

WORKSPACE="$(cd "$(dirname "$0")/.." && pwd)"
cd "$WORKSPACE"

# Nothing to commit?
if git diff --quiet && git diff --cached --quiet && \
   [ -z "$(git ls-files --others --exclude-standard)" ]; then
  exit 0
fi

PUSH="${1:-}"
SECRETS_FILE="$WORKSPACE/.secrets-map"

# Safety: critical paths must be gitignored before any git operations
for SENSITIVE in ".vault" ".secrets-map"; do
  if [ -e "$WORKSPACE/$SENSITIVE" ]; then
    if ! git check-ignore -q "$SENSITIVE" 2>/dev/null; then
      echo "❌ ABORT: $SENSITIVE is not gitignored. Add it to .gitignore first."
      exit 1
    fi
  fi
done

# Set up temp workspace
TMPDIR_BASE=$(mktemp -d)
SCRUB_DIR="$TMPDIR_BASE/scrub"
TMPINDEX="$TMPDIR_BASE/git-index"
FILE_LIST="$TMPDIR_BASE/files.txt"
DELETED_LIST="$TMPDIR_BASE/deleted.txt"
mkdir -p "$SCRUB_DIR"

cleanup() { rm -rf "$TMPDIR_BASE"; }
trap cleanup EXIT

# Collect file lists BEFORE touching any index
{ git ls-files; git ls-files --others --exclude-standard; } | sort -u > "$FILE_LIST"
git diff --name-only --diff-filter=D HEAD 2>/dev/null > "$DELETED_LIST" || touch "$DELETED_LIST"

# Step 1: Copy all files to commit into the scrub dir
# Workspace originals are NEVER modified — only this copy is scrubbed
while IFS= read -r f; do
  [ -f "$WORKSPACE/$f" ] || continue
  mkdir -p "$SCRUB_DIR/$(dirname "$f")"
  cp "$WORKSPACE/$f" "$SCRUB_DIR/$f"
done < "$FILE_LIST"

# Step 2: Scrub secrets in the copy (only SCRUB_DIR is touched)
if [ -f "$SECRETS_FILE" ]; then
  while IFS='|' read -r secret placeholder; do
    case "$secret" in '#'*|'') continue ;; esac
    secret="$(printf '%s' "$secret" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
    [ -z "$secret" ] && continue

    # Scrub all non-binary tracked files (matches verification scope)
    while IFS= read -r -d '' f; do
      file -b --mime-encoding "$f" 2>/dev/null | grep -q "binary" && continue
      grep -qF "$secret" "$f" 2>/dev/null && sed -i "s|$secret|$placeholder|g" "$f"
    done < <(find "$SCRUB_DIR" -type f -print0)
  done < "$SECRETS_FILE"

  # Step 3: Verify no secrets remain in the scrubbed copy
  LEAK_FOUND=0
  while IFS='|' read -r secret placeholder; do
    case "$secret" in '#'*|'') continue ;; esac
    secret="$(printf '%s' "$secret" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
    [ -z "$secret" ] && continue
    if grep -rlF "$secret" "$SCRUB_DIR" 2>/dev/null | grep -q .; then
      echo "❌ Secret found in scrubbed copy — aborting. Your workspace files are untouched."
      LEAK_FOUND=1
      break
    fi
  done < "$SECRETS_FILE"
  [ "$LEAK_FOUND" -eq 1 ] && exit 1
fi

# Step 4: Build git commit from scrubbed copy using git plumbing
# The real git index (and working tree) are NEVER touched.
# GIT_INDEX_FILE points to a temporary index file in TMPDIR_BASE.
export GIT_INDEX_FILE="$TMPINDEX"

# Seed the temp index from the current HEAD tree
git read-tree HEAD 2>/dev/null || git read-tree --empty

# Stage each scrubbed file into the temp index as a git blob
while IFS= read -r f; do
  [ -f "$SCRUB_DIR/$f" ] || continue
  mode=$(git ls-files --stage "$f" 2>/dev/null | awk '{print $1; exit}')
  [ -z "$mode" ] && mode="100644"
  blob=$(git hash-object -w "$SCRUB_DIR/$f")
  git update-index --add --cacheinfo "$mode,$blob,$f"
done < "$FILE_LIST"

# Remove deleted tracked files from the temp index
while IFS= read -r f; do
  [ -z "$f" ] && continue
  git update-index --remove "$f" 2>/dev/null || true
done < "$DELETED_LIST"

# Write tree → commit → update branch ref
TREE=$(git write-tree)
PARENT=$(git rev-parse HEAD 2>/dev/null || echo "")
COMMIT_MSG="Auto-backup: $(date '+%Y-%m-%d %H:%M')"

if [ -n "$PARENT" ]; then
  COMMIT=$(git commit-tree -p "$PARENT" -m "$COMMIT_MSG" "$TREE")
else
  COMMIT=$(git commit-tree -m "$COMMIT_MSG" "$TREE")
fi

unset GIT_INDEX_FILE

# Update the current branch to point to the new commit
BRANCH=$(git symbolic-ref --short HEAD 2>/dev/null || echo "")
if [ -n "$BRANCH" ]; then
  git update-ref "refs/heads/$BRANCH" "$COMMIT"
else
  git update-ref HEAD "$COMMIT"
fi

echo "✅ Committed (workspace files untouched — secrets scrubbed in isolated copy)."

if [ "$PUSH" = "--push" ]; then
  git push --quiet 2>/dev/null
  echo "✅ Pushed to remote."
else
  echo "   Run with --push to push to remote. Or: git push"
fi
