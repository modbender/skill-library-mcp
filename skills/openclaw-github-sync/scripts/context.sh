#!/usr/bin/env bash
set -euo pipefail

# Wrapper for openclaw-github-sync.
#
# Usage:
#   ./context.sh push        # workspace -> sync repo -> remote
#   ./context.sh pull        # remote -> sync repo -> workspace
#   ./context.sh status      # show sync repo git status
#
# Environment:
#   SYNC_REMOTE   (optional if SYNC_REPO_DIR already has origin)
#   WORKSPACE_DIR default: $HOME/.openclaw/workspace
#   SYNC_REPO_DIR      default: $WORKSPACE_DIR/openclaw-sync-repo
#   PULL_DRY_RUN=1, PULL_DELETE=1 (for pull)
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=bootstrap.sh
source "$SCRIPT_DIR/bootstrap.sh"
openclaw_github_sync_load_env \
  WORKSPACE_DIR SYNC_REPO_DIR SYNC_REMOTE PULL_DRY_RUN PULL_DELETE

WORKSPACE_DIR="${WORKSPACE_DIR:-$HOME/.openclaw/workspace}"
SYNC_REPO_DIR="${SYNC_REPO_DIR:-$WORKSPACE_DIR/openclaw-sync-repo}"
SYNC_REMOTE="${SYNC_REMOTE:-}"

CMD="${1:-}"
shift || true

# If still missing, try to infer from existing sync repo.
if [[ -z "$SYNC_REMOTE" ]] && [[ -d "$SYNC_REPO_DIR/.git" ]]; then
  set +e
  inferred=$(git -C "$SYNC_REPO_DIR" remote get-url origin 2>/dev/null)
  code=$?
  set -e
  if [[ $code -eq 0 ]] && [[ -n "${inferred:-}" ]]; then
    SYNC_REMOTE="$inferred"
  fi
fi

usage() {
  cat <<EOF
openclaw-github-sync wrapper

Usage:
  $(basename "$0") push
  $(basename "$0") pull
  $(basename "$0") status

Env:
  SYNC_REMOTE=git@github.com:ORG/REPO.git   (optional if $SYNC_REPO_DIR has origin)
  WORKSPACE_DIR=$WORKSPACE_DIR
  SYNC_REPO_DIR=$SYNC_REPO_DIR

Pull options:
  PULL_DRY_RUN=1
  PULL_DELETE=1
EOF
}

if [[ -z "$CMD" ]]; then
  usage
  exit 2
fi

case "$CMD" in
  push)
    SYNC_REMOTE="$SYNC_REMOTE" "$SCRIPT_DIR/sync.sh"
    ;;
  pull)
    SYNC_REMOTE="$SYNC_REMOTE" "$SCRIPT_DIR/pull.sh"
    ;;
  status)
    if [[ -d "$SYNC_REPO_DIR/.git" ]]; then
      git -C "$SYNC_REPO_DIR" status
    else
      echo "No sync repo found at: $SYNC_REPO_DIR" >&2
      exit 3
    fi
    ;;
  -h|--help|help)
    usage
    ;;
  *)
    echo "Unknown command: $CMD" >&2
    usage
    exit 2
    ;;
esac
