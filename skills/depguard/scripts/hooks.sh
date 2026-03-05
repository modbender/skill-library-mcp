#!/usr/bin/env bash
# DepGuard — Git Hooks Module
# Installs lefthook pre-commit hooks for lockfile change detection

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

do_depguard_hooks_install() {
  if ! command -v lefthook &>/dev/null; then
    echo -e "${RED}[DepGuard]${NC} lefthook not installed."
    echo "  Install: brew install lefthook"
    return 1
  fi

  if ! git rev-parse --git-dir &>/dev/null 2>&1; then
    echo -e "${RED}[DepGuard]${NC} Not inside a git repository."
    return 1
  fi

  local repo_root
  repo_root=$(git rev-parse --show-toplevel)

  echo -e "${BLUE}[DepGuard]${NC} Installing hooks in ${BOLD}$repo_root${NC}"

  local config="$repo_root/lefthook.yml"

  if [[ -f "$config" ]]; then
    if grep -q "depguard" "$config" 2>/dev/null; then
      echo -e "${GREEN}[DepGuard]${NC} Hooks already configured."
      return 0
    fi

    # Append to existing config
    cat >> "$config" <<'HOOKS'

# ─── DepGuard hooks ─────────────────────────────
  depguard-lockfile-scan:
    glob: "{package-lock.json,yarn.lock,pnpm-lock.yaml,Cargo.lock,go.sum,composer.lock,Gemfile.lock,requirements.txt,Pipfile.lock}"
    run: |
      DEPGUARD_SKILL_DIR="${DEPGUARD_SKILL_DIR:-$HOME/.openclaw/skills/depguard}"
      if [[ -f "$DEPGUARD_SKILL_DIR/scripts/scanner.sh" ]]; then
        source "$DEPGUARD_SKILL_DIR/scripts/scanner.sh"
        do_scan .
      fi
    fail_text: |
      Dependency vulnerabilities detected!
      Run 'depguard fix' to auto-fix or 'git commit --no-verify' to skip.
HOOKS
    echo -e "${GREEN}✓${NC} Appended DepGuard hooks to existing lefthook.yml"
  else
    cp "$SKILL_DIR/config/lefthook.yml" "$config"
    echo -e "${GREEN}✓${NC} Created lefthook.yml"
  fi

  (cd "$repo_root" && lefthook install)
  echo ""
  echo -e "${GREEN}[DepGuard]${NC} Hooks installed! Lockfile changes will trigger security scans."
}

do_depguard_hooks_uninstall() {
  if ! git rev-parse --git-dir &>/dev/null 2>&1; then
    echo -e "${RED}[DepGuard]${NC} Not inside a git repository."
    return 1
  fi

  local repo_root
  repo_root=$(git rev-parse --show-toplevel)
  local config="$repo_root/lefthook.yml"

  if [[ -f "$config" ]]; then
    if grep -q "depguard" "$config" 2>/dev/null; then
      local tmp
      tmp=$(mktemp)
      sed '/# ─── DepGuard hooks/,/fail_text:.*$/d' "$config" > "$tmp"
      grep -v "depguard" "$tmp" > "$config" 2>/dev/null || mv "$tmp" "$config"
      rm -f "$tmp"
      echo -e "${GREEN}✓${NC} Removed DepGuard hooks"
    else
      echo -e "${YELLOW}[DepGuard]${NC} No DepGuard hooks found"
    fi
  else
    echo -e "${YELLOW}[DepGuard]${NC} No lefthook.yml found"
  fi
}

# Hook entry point — called by lefthook
hook_depguard_scan() {
  local staged
  staged=$(git diff --cached --name-only 2>/dev/null || true)

  local lockfiles="package-lock.json yarn.lock pnpm-lock.yaml Cargo.lock go.sum composer.lock Gemfile.lock requirements.txt Pipfile.lock"
  local has_lockfile=false

  for lf in $lockfiles; do
    if echo "$staged" | grep -q "$lf"; then
      has_lockfile=true
      break
    fi
  done

  if [[ "$has_lockfile" == "true" ]]; then
    echo -e "${BLUE}[DepGuard]${NC} Lockfile change detected — running security scan..."
    source "$SCRIPT_DIR/scanner.sh"
    do_scan .
  fi
}
