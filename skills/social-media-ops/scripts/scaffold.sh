#!/usr/bin/env bash
set -euo pipefail

# scaffold.sh — Social Media Ops Skill Scaffolding
# Creates directory structure, copies templates, and sets up symlinks.
# Always installs all 7 agents (Leader + 6 specialists).

# ── Defaults ──────────────────────────────────────────────────────────

BASE_DIR="${HOME}/.openclaw"
AGENTS="leader,researcher,content,designer,operator,engineer,reviewer"
SKILL_DIR=""
QUIET=false
DRY_RUN=false

# ── Usage ─────────────────────────────────────────────────────────────

usage() {
  cat <<'EOF'
Usage: scaffold.sh [OPTIONS]

Options:
  --base-dir DIR      OpenClaw root directory (default: ~/.openclaw)
  --skill-dir DIR     Path to this skill's directory (required)
  --quiet             Suppress progress messages
  --dry-run           Print what would be created without writing
  -h, --help          Show this help

Advanced:
  --agents LIST       Override agent list (default: all 7)
                      Example: leader,content,designer,engineer

Examples:
  scaffold.sh --skill-dir /path/to/social-media-ops
  scaffold.sh --base-dir /custom/openclaw --skill-dir /path/to/social-media-ops
EOF
  exit 0
}

# ── Argument Parsing ──────────────────────────────────────────────────

while [[ $# -gt 0 ]]; do
  case "$1" in
    --base-dir)   BASE_DIR="$2";   shift 2 ;;
    --agents)     AGENTS="$2";     shift 2 ;;
    --skill-dir)  SKILL_DIR="$2";  shift 2 ;;
    --quiet)      QUIET=true;      shift   ;;
    --dry-run)    DRY_RUN=true;    shift   ;;
    -h|--help)    usage ;;
    *)            echo "[ERROR] Unknown option: $1"; exit 1 ;;
  esac
done

if [[ -z "$SKILL_DIR" ]]; then
  echo "[ERROR] --skill-dir is required"
  exit 1
fi

if [[ ! -d "$SKILL_DIR/assets" ]]; then
  echo "[ERROR] Skill directory does not contain assets/: $SKILL_DIR"
  exit 1
fi

# ── Helpers ───────────────────────────────────────────────────────────

log() {
  if [[ "$QUIET" != true ]]; then
    echo "$1"
  fi
}

ok()   { log "[OK]   $1"; }
skip() { log "[SKIP] $1"; }
info() { log "[INFO] $1"; }

# Copy a file only if the destination does not exist
# Usage: copy_if_missing <src> <dst> <label>
copy_if_missing() {
  local src="$1" dst="$2" label="$3"
  if [[ ! -f "$src" ]]; then
    return
  fi
  if [[ -f "$dst" ]]; then
    skip "$label (already exists)"
    return
  fi
  if [[ "$DRY_RUN" == true ]]; then
    log "[DRY]  $label"
    return
  fi
  cp "$src" "$dst"
  ok "$label"
}

# Copy a directory only if the destination does not exist
# Usage: copy_dir_if_missing <src> <dst> <label>
copy_dir_if_missing() {
  local src="$1" dst="$2" label="$3"
  if [[ ! -d "$src" ]]; then
    return
  fi
  if [[ -d "$dst" ]]; then
    skip "$label (already exists)"
    return
  fi
  if [[ "$DRY_RUN" == true ]]; then
    log "[DRY]  $label"
    return
  fi
  cp -r "$src" "$dst"
  ok "$label"
}

# Copy file, overwriting if exists (backup if content differs)
# For skill-managed files (SOUL.md, AGENTS.md, etc.)
# Usage: copy_with_backup <src> <dst> <label>
copy_with_backup() {
  local src="$1" dst="$2" label="$3"
  if [[ ! -f "$src" ]]; then
    return
  fi
  if [[ "$DRY_RUN" == true ]]; then
    log "[DRY]  $label"
    return
  fi
  if [[ -f "$dst" ]]; then
    if diff -q "$src" "$dst" > /dev/null 2>&1; then
      skip "$label (already up to date)"
      return
    fi
    cp "$dst" "${dst}.bak"
    log "[BAK]  ${label}.bak"
  fi
  cp "$src" "$dst"
  ok "$label"
}

ASSETS="$SKILL_DIR/assets"

if [[ "$DRY_RUN" == true ]]; then
  info "DRY RUN — no files will be created or modified"
fi

# Parse agent list into array
IFS=',' read -ra AGENT_LIST <<< "$AGENTS"

# Validate that leader is always included
LEADER_FOUND=false
for agent in "${AGENT_LIST[@]}"; do
  if [[ "$agent" == "leader" ]]; then
    LEADER_FOUND=true
    break
  fi
done

if [[ "$LEADER_FOUND" != true ]]; then
  echo "[ERROR] Leader agent is required and must be in the agent list"
  exit 1
fi

# Map agent IDs to workspace directory names
agent_workspace_dir() {
  local agent="$1"
  if [[ "$agent" == "leader" ]]; then
    echo "workspace"
  else
    echo "workspace-${agent}"
  fi
}

# Map agent IDs to asset source directory names
agent_asset_dir() {
  local agent="$1"
  if [[ "$agent" == "leader" ]]; then
    echo "workspace"
  else
    echo "workspace-${agent}"
  fi
}

# ── Step 1: Verify Base Directory ─────────────────────────────────────

info "Base directory: $BASE_DIR"

if [[ ! -d "$BASE_DIR" ]]; then
  echo "[ERROR] Base directory does not exist: $BASE_DIR"
  echo "        Run 'openclaw onboard' first."
  exit 1
fi

# ── Step 2: Create Agent Workspaces ───────────────────────────────────

info "Setting up agent workspaces..."

for agent in "${AGENT_LIST[@]}"; do
  ws_dir=$(agent_workspace_dir "$agent")
  ws_path="$BASE_DIR/$ws_dir"
  asset_src=$(agent_asset_dir "$agent")

  # Create workspace directory
  mkdir -p "$ws_path"

  # Create memory directory (skip for reviewer — read-only agent)
  if [[ "$agent" != "reviewer" ]]; then
    mkdir -p "$ws_path/memory"
  fi

  # Copy skill-managed files (overwrite with backup if content differs)
  copy_with_backup "$ASSETS/$asset_src/SOUL.md" "$ws_path/SOUL.md" "$ws_dir/SOUL.md"
  copy_with_backup "$ASSETS/$asset_src/AGENTS.md" "$ws_path/AGENTS.md" "$ws_dir/AGENTS.md"

  # Leader-specific files
  if [[ "$agent" == "leader" ]]; then
    for file in HEARTBEAT.md IDENTITY.md; do
      copy_with_backup "$ASSETS/workspace/$file" "$ws_path/$file" "$ws_dir/$file"
    done

    # Create skills directory for leader
    mkdir -p "$ws_path/skills"

    # Create assets directory structure
    mkdir -p "$ws_path/assets/shared"
  fi

  # Create skills directory for non-leader agents (skip for reviewer — read-only agent)
  if [[ "$agent" != "leader" && "$agent" != "reviewer" ]]; then
    mkdir -p "$ws_path/skills"
  fi

  # Create MEMORY.md if it doesn't exist (skip for reviewer)
  if [[ "$agent" != "reviewer" && ! -f "$ws_path/MEMORY.md" ]]; then
    agent_cap="$(printf '%s' "$agent" | cut -c1 | tr '[:lower:]' '[:upper:]')$(printf '%s' "$agent" | cut -c2-)"
    echo "# MEMORY.md — $agent_cap" > "$ws_path/MEMORY.md"
    echo "" >> "$ws_path/MEMORY.md"
    echo "_Curated long-term memory. Updated during daily consolidation and significant events._" >> "$ws_path/MEMORY.md"
    ok "$ws_dir/MEMORY.md (initialized)"
  fi
done

# ── Step 3: Create Shared Knowledge Base ──────────────────────────────

info "Setting up shared knowledge base..."

SHARED="$BASE_DIR/workspace/shared"
mkdir -p "$SHARED/brands/_template"
mkdir -p "$SHARED/domain/_template"
mkdir -p "$SHARED/operations"
mkdir -p "$SHARED/errors"

# ── Step 3.5: Create Shared Media Directory ──────────────────────────
mkdir -p "$BASE_DIR/media/generated"
ok "media/generated (shared image output)"

# Copy shared KB templates (only if they don't exist)
shared_files=(
  "system-guide.md"
  "brand-guide.md"
  "compliance-guide.md"
  "team-roster.md"
  "brand-registry.md"
)

for file in "${shared_files[@]}"; do
  copy_if_missing "$ASSETS/shared/$file" "$SHARED/$file" "shared/$file"
done

# Copy brand templates
for file in profile.md content-guidelines.md; do
  copy_if_missing "$ASSETS/shared/brands/_template/$file" "$SHARED/brands/_template/$file" "shared/brands/_template/$file"
done

# Copy domain template
copy_if_missing "$ASSETS/shared/domain/_template/industry.md" "$SHARED/domain/_template/industry.md" "shared/domain/_template/industry.md"

# Copy operations templates
ops_files=(
  "communication-signals.md"
  "approval-workflow.md"
  "posting-schedule.md"
  "content-guidelines.md"
  "channel-map.md"
)

for file in "${ops_files[@]}"; do
  copy_if_missing "$ASSETS/shared/operations/$file" "$SHARED/operations/$file" "shared/operations/$file"
done

# Copy errors template
copy_if_missing "$ASSETS/shared/errors/solutions.md" "$SHARED/errors/solutions.md" "shared/errors/solutions.md"

# ── Step 4: Create Symlinks to shared/ ────────────────────────────────

info "Creating symlinks to shared knowledge base..."

for agent in "${AGENT_LIST[@]}"; do
  ws_dir=$(agent_workspace_dir "$agent")
  ws_path="$BASE_DIR/$ws_dir"
  link_path="$ws_path/shared"

  # Leader already has shared/ as real directory — skip
  if [[ "$agent" == "leader" ]]; then
    skip "$ws_dir/shared (real directory — no symlink needed)"
    continue
  fi

  if [[ -L "$link_path" ]]; then
    skip "$ws_dir/shared (symlink already exists)"
  elif [[ -d "$link_path" ]]; then
    skip "$ws_dir/shared (directory exists — not overwriting)"
  else
    ln -s "$BASE_DIR/workspace/shared" "$link_path"
    ok "$ws_dir/shared -> ../workspace/shared/"
  fi
done

# ── Step 5: Copy Sub-Skills ───────────────────────────────────────────

info "Installing sub-skills..."

LEADER_SKILLS="$BASE_DIR/workspace/skills"
if [[ "$DRY_RUN" != true ]]; then
  mkdir -p "$LEADER_SKILLS"
fi

SUB_SKILLS=(instance-setup brand-manager qmd-setup)
for skill in "${SUB_SKILLS[@]}"; do
  copy_dir_if_missing "$ASSETS/skills/$skill" "$LEADER_SKILLS/$skill" "skills/$skill"
done

# ── Step 6: Copy Cron Jobs ────────────────────────────────────────────

info "Setting up cron jobs..."

CRON_DIR="$BASE_DIR/cron"
mkdir -p "$CRON_DIR"

if [[ -f "$ASSETS/config/cron-jobs.json" ]]; then
  if [[ ! -f "$CRON_DIR/jobs.json" ]]; then
    cp "$ASSETS/config/cron-jobs.json" "$CRON_DIR/jobs.json"
    ok "cron/jobs.json"
  else
    skip "cron/jobs.json (already exists — run /instance_setup to reconfigure)"
  fi
fi

# ── Summary ───────────────────────────────────────────────────────────

info ""
info "=== Scaffold Complete ==="
info ""
info "Agents set up: ${AGENTS}"
info "Base directory: ${BASE_DIR}"
info ""
info "Next steps:"
info "  1. Run patch-config.js to update openclaw.json"
info "  2. Run instance-setup to configure owner and platform"
info "  3. Run brand-manager add to create your first brand"
info "  4. Restart gateway: openclaw gateway restart"
