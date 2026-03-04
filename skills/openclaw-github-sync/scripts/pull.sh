#!/usr/bin/env bash
set -euo pipefail

# Pull the synced context repo and copy changes back into the OpenClaw workspace.
#
# This is the inverse of sync.sh:
#   - updates the local sync repo to origin/main (hard reset)
#   - copies files from the sync repo -> workspace, overwriting workspace copies
#
# Required env:
#   SYNC_REMOTE   e.g. git@github.com:YOUR_ORG/YOUR_REPO.git
# Optional env:
#   WORKSPACE_DIR default: $HOME/.openclaw/workspace
#   SYNC_REPO_DIR      default: $WORKSPACE_DIR/openclaw-sync-repo
#   PULL_DELETE   default: 0 (if 1, delete workspace files that were removed from the sync repo for targeted dirs)
#   PULL_DRY_RUN  default: 0 (if 1, show what would change but do not write)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=bootstrap.sh
source "$SCRIPT_DIR/bootstrap.sh"
openclaw_github_sync_load_env \
  WORKSPACE_DIR SYNC_REPO_DIR SYNC_REMOTE PULL_DELETE PULL_DRY_RUN OPENCLAW_CONFIG

WORKSPACE_DIR="${WORKSPACE_DIR:-$HOME/.openclaw/workspace}"
SYNC_REPO_DIR="${SYNC_REPO_DIR:-$WORKSPACE_DIR/openclaw-sync-repo}"
SYNC_REMOTE="${SYNC_REMOTE:-}"
PULL_DELETE="${PULL_DELETE:-0}"
PULL_DRY_RUN="${PULL_DRY_RUN:-0}"

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

# Update local sync repo to match remote.
if git -C "$SYNC_REPO_DIR" ls-remote --exit-code --heads origin main >/dev/null 2>&1; then
  git -C "$SYNC_REPO_DIR" fetch origin main
  git -C "$SYNC_REPO_DIR" reset --hard origin/main
else
  echo "Remote has no main branch yet: $SYNC_REMOTE" >&2
  exit 3
fi

# rsync flags
DRY=()
if [[ "$PULL_DRY_RUN" == "1" ]]; then
  DRY=(--dry-run)
fi

# Only delete for targeted dirs if explicitly enabled.
DEL=()
if [[ "$PULL_DELETE" == "1" ]]; then
  DEL=(--delete)
fi

# 1) Pull ALL skills (full directory contents) -> workspace/skills
if [[ -d "$SYNC_REPO_DIR/skills" ]]; then
  mkdir -p "$WORKSPACE_DIR/skills"
  rsync -a "${DRY[@]}" "${DEL[@]}" \
    --exclude '.git/' \
    --exclude 'node_modules/' \
    --exclude '__pycache__/' \
    --exclude '*.pyc' \
    "$SYNC_REPO_DIR/skills/" "$WORKSPACE_DIR/skills/"
fi

# 2) Pull ALL markdown files anywhere in the sync repo (excluding .git, node_modules)
#    into the workspace at the same relative paths.
#    This overwrites workspace copies where paths collide.
RSYNC_FILTERS=(
  --exclude '.git/'
  --exclude 'node_modules/'
  --exclude '__pycache__/'
  --exclude '*.pyc'
  --include '*/'
  --include '*.md'
  --exclude '*'
)

rsync -a "${DRY[@]}" \
  "${RSYNC_FILTERS[@]}" \
  "$SYNC_REPO_DIR/" "$WORKSPACE_DIR/"

# 3) Pull agent-specific skills + markdown/persona files into each agent workspace.
# The sync repo stores these at:
#   agents/<agentId>/skills/
#   agents/<agentId>/**/*.md (including {IDENTITY,SOUL,USER,TOOLS}.md at root)
OPENCLAW_CONFIG="${OPENCLAW_CONFIG:-$HOME/.openclaw/openclaw.json}"
if command -v jq >/dev/null 2>&1 && [[ -f "$OPENCLAW_CONFIG" ]] && [[ -d "$SYNC_REPO_DIR/agents" ]]; then
  mapfile -t agent_rows < <(jq -r '.agents.list[] | [.id, (.workspace // "")] | @tsv' "$OPENCLAW_CONFIG")
  for row in "${agent_rows[@]}"; do
    agent_id="$(echo "$row" | cut -f1)"
    agent_ws="$(echo "$row" | cut -f2)"

    [[ -z "$agent_ws" ]] && continue
    # Main workspace is already handled above.
    [[ "$agent_ws" == "$WORKSPACE_DIR" ]] && continue

    src_base="$SYNC_REPO_DIR/agents/$agent_id"
    [[ ! -d "$src_base" ]] && continue

    # Agent skills (full directory)
    if [[ -d "$src_base/skills" ]]; then
      mkdir -p "$agent_ws/skills"
      rsync -a "${DRY[@]}" "${DEL[@]}" \
        --exclude '.git/' \
        --exclude 'node_modules/' \
        --exclude '__pycache__/' \
        --exclude '*.pyc' \
        "$src_base/skills/" "$agent_ws/skills/"
    fi

    # Agent markdown (md-only), excluding skills/ (already handled).
    AGENT_MD_FILTERS=(
      --exclude 'skills/'
      --exclude '.git/'
      --exclude 'node_modules/'
      --exclude '__pycache__/'
      --exclude '*.pyc'
      --include '*/'
      --include '*.md'
      --exclude '*'
    )

    rsync -a "${DRY[@]}" \
      "${AGENT_MD_FILTERS[@]}" \
      "$src_base/" "$agent_ws/"
  done
else
  echo "WARN: jq/openclaw config not available or no agents/ dir in sync repo; skipping agent workspace pull" >&2
fi

if [[ "$PULL_DRY_RUN" == "1" ]]; then
  echo "(dry-run) Pull complete. No files were modified."
else
  echo "Pulled skills/ + *.md into $WORKSPACE_DIR (and agent workspaces when configured) from $SYNC_REMOTE"
fi
