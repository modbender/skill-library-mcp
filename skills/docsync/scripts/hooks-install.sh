#!/usr/bin/env bash
# DocSync — Git Hooks Installation Module
# Installs/uninstalls lefthook-based pre-commit hooks for drift detection

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# ─── Helpers ────────────────────────────────────────────────────────────────

check_lefthook() {
  if ! command -v lefthook &>/dev/null; then
    echo -e "${RED}[DocSync]${NC} lefthook is not installed."
    echo ""
    echo "Install it with one of:"
    echo "  brew install lefthook"
    echo "  npm install -g @evilmartians/lefthook"
    echo "  go install github.com/evilmartians/lefthook@latest"
    echo ""
    echo "Then run ${CYAN}docsync hooks install${NC} again."
    return 1
  fi
}

check_git_repo() {
  if ! git rev-parse --git-dir &>/dev/null 2>&1; then
    echo -e "${RED}[DocSync]${NC} Not inside a git repository."
    return 1
  fi
}

get_repo_root() {
  git rev-parse --show-toplevel 2>/dev/null
}

# ─── Install hooks ─────────────────────────────────────────────────────────

do_hooks_install() {
  check_lefthook || return 1
  check_git_repo || return 1

  local repo_root
  repo_root=$(get_repo_root)

  echo -e "${BLUE}[DocSync]${NC} Installing git hooks in ${BOLD}$repo_root${NC}"
  echo ""

  # Copy lefthook config
  local lefthook_config="$repo_root/lefthook.yml"
  local docsync_config="$SKILL_DIR/config/lefthook.yml"

  if [[ -f "$lefthook_config" ]]; then
    # Merge with existing config
    echo -e "${YELLOW}[DocSync]${NC} Existing lefthook.yml found — merging DocSync hooks"

    # Check if DocSync hooks already present
    if grep -q "docsync" "$lefthook_config" 2>/dev/null; then
      echo -e "${GREEN}[DocSync]${NC} DocSync hooks already configured in lefthook.yml"
    else
      # Append DocSync hooks section
      echo "" >> "$lefthook_config"
      echo "# ─── DocSync hooks ───────────────────────────" >> "$lefthook_config"
      cat "$docsync_config" | grep -A 100 "pre-commit:" >> "$lefthook_config"
      echo -e "${GREEN}✓${NC} Appended DocSync hooks to existing lefthook.yml"
    fi
  else
    # Create fresh config
    cp "$docsync_config" "$lefthook_config"
    echo -e "${GREEN}✓${NC} Created ${BOLD}lefthook.yml${NC}"
  fi

  # Install lefthook into git hooks
  (cd "$repo_root" && lefthook install)
  echo ""
  echo -e "${GREEN}[DocSync]${NC} Git hooks installed successfully!"
  echo ""
  echo "DocSync will now check for documentation drift on every commit."
  echo ""
  echo "  ${BOLD}How it works:${NC}"
  echo "  1. On each commit, DocSync analyzes staged source files"
  echo "  2. Compares code symbols against existing documentation"
  echo "  3. Blocks the commit if critical drift is detected"
  echo "  4. Suggests running ${CYAN}docsync auto-fix${NC} to regenerate stale docs"
  echo ""
  echo "  To skip the check once: ${CYAN}git commit --no-verify${NC}"
  echo "  To remove hooks: ${CYAN}docsync hooks uninstall${NC}"
}

# ─── Uninstall hooks ───────────────────────────────────────────────────────

do_hooks_uninstall() {
  check_git_repo || return 1

  local repo_root
  repo_root=$(get_repo_root)

  echo -e "${BLUE}[DocSync]${NC} Removing DocSync hooks from ${BOLD}$repo_root${NC}"

  local lefthook_config="$repo_root/lefthook.yml"

  if [[ -f "$lefthook_config" ]]; then
    # Check if there are non-DocSync hooks
    local non_docsync_lines
    non_docsync_lines=$(grep -v -i "docsync" "$lefthook_config" | grep -v "^#" | grep -v "^$" | wc -l | tr -d ' ')

    if [[ "$non_docsync_lines" -gt 2 ]]; then
      # Other hooks exist — just remove DocSync section
      # Remove lines between DocSync markers
      local tmp
      tmp=$(mktemp)
      sed '/# ─── DocSync hooks/,/^$/d' "$lefthook_config" > "$tmp"
      # Also remove any docsync-specific entries
      grep -v "docsync" "$tmp" > "$lefthook_config" 2>/dev/null || mv "$tmp" "$lefthook_config"
      rm -f "$tmp"
      echo -e "${GREEN}✓${NC} Removed DocSync section from lefthook.yml (other hooks preserved)"
    else
      # Only DocSync hooks — remove the whole file
      rm -f "$lefthook_config"
      echo -e "${GREEN}✓${NC} Removed lefthook.yml"

      # Uninstall lefthook from git
      if command -v lefthook &>/dev/null; then
        (cd "$repo_root" && lefthook uninstall 2>/dev/null || true)
      fi
    fi
  else
    echo -e "${YELLOW}[DocSync]${NC} No lefthook.yml found — nothing to uninstall"
  fi

  echo -e "${GREEN}[DocSync]${NC} Hooks uninstalled."
}
