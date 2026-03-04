#!/usr/bin/env bash
# git-diff.sh — Extract changed files from git diff for vibe-check analysis
# Parses git diff output and writes individual changed files to a temp directory
#
# Usage: ./git-diff.sh [HEAD~N] [--staged] [--branch BRANCH]
#   Outputs: list of file paths (one per line) that were changed
#
# The script extracts the CURRENT version of changed files (not the diff itself)
# so they can be analyzed by analyze.sh

set -euo pipefail
source "$(dirname "$0")/common.sh"

DIFF_REF="HEAD~1"
STAGED="false"
BRANCH=""

# Parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --staged)       STAGED="true"; shift ;;
    --branch)
      if [[ $# -lt 2 || -z "${2:-}" || "${2:-}" =~ ^-- ]]; then
        err "Missing value for --branch"
        exit 1
      fi
      BRANCH="$2"
      shift 2
      ;;
    HEAD~*)         DIFF_REF="$1"; shift ;;
    *)              DIFF_REF="$1"; shift ;;
  esac
done

# Verify we're in a git repo
if ! git rev-parse --is-inside-work-tree &>/dev/null; then
  err "Not inside a git repository."
  exit 1
fi

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)

# Get list of changed files
CHANGED_FILES=""
if [ "$STAGED" = "true" ]; then
  info "Analyzing staged changes..."
  CHANGED_FILES=$(git diff --cached --name-only --diff-filter=ACMR 2>/dev/null)
elif [ -n "$BRANCH" ]; then
  info "Analyzing changes vs branch: $BRANCH..."
  CHANGED_FILES=$(git diff "$BRANCH"...HEAD --name-only --diff-filter=ACMR 2>/dev/null)
else
  info "Analyzing changes since: $DIFF_REF..."
  CHANGED_FILES=$(git diff "$DIFF_REF" --name-only --diff-filter=ACMR 2>/dev/null)
fi

if [ -z "$CHANGED_FILES" ]; then
  warn "No changed files found for the given diff range."
  exit 0
fi

# Filter to supported languages only
SUPPORTED_COUNT=0
TOTAL_COUNT=0

while IFS= read -r file; do
  [ -z "$file" ] && continue
  TOTAL_COUNT=$((TOTAL_COUNT + 1))
  
  FULL_PATH="${REPO_ROOT}/${file}"
  
  # Check if file still exists (might have been deleted)
  if [ ! -f "$FULL_PATH" ]; then
    continue
  fi

  # Check if it's a supported extension
  if echo "$file" | grep -qE "\.(${SUPPORTED_EXTENSIONS})$"; then
    echo "$FULL_PATH"
    SUPPORTED_COUNT=$((SUPPORTED_COUNT + 1))
  fi
done <<< "$CHANGED_FILES"

info "Found ${SUPPORTED_COUNT} supported files out of ${TOTAL_COUNT} changed files"
