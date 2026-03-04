#!/usr/bin/env bash
# DocSync — Main CLI entry point
# Usage: docsync.sh <command> [args...]
#
# Commands:
#   generate <target>       Generate docs for a file or directory (FREE)
#   drift [directory]       Detect documentation drift (PRO+)
#   hooks install           Install git pre-commit hooks (PRO+)
#   hooks uninstall         Remove DocSync git hooks (PRO+)
#   auto-fix [directory]    Auto-regenerate stale docs (PRO+)
#   onboarding [directory]  Generate onboarding guide (TEAM+)
#   architecture [directory] Generate architecture docs (TEAM+)
#   status                  Show DocSync status and license info

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
VERSION="1.0.0"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# ─── Helpers ────────────────────────────────────────────────────────────────

log_info()    { echo -e "${BLUE}[DocSync]${NC} $*"; }
log_success() { echo -e "${GREEN}[DocSync]${NC} $*"; }
log_warn()    { echo -e "${YELLOW}[DocSync]${NC} $*"; }
log_error()   { echo -e "${RED}[DocSync]${NC} $*" >&2; }

show_version() {
  echo -e "${BOLD}DocSync${NC} v${VERSION}"
  echo "  Living documentation for your codebase"
  echo "  https://docsync.pages.dev"
}

show_help() {
  show_version
  echo ""
  echo -e "${BOLD}USAGE${NC}"
  echo "  docsync <command> [options]"
  echo ""
  echo -e "${BOLD}FREE COMMANDS${NC}"
  echo "  generate <target>         Generate docs for a file or directory"
  echo ""
  echo -e "${BOLD}PRO COMMANDS${NC} (\$29/user/month)"
  echo "  drift [directory]         Detect documentation drift"
  echo "  hooks install             Install pre-commit hooks"
  echo "  hooks uninstall           Remove DocSync git hooks"
  echo "  auto-fix [directory]      Auto-regenerate stale docs"
  echo ""
  echo -e "${BOLD}TEAM COMMANDS${NC} (\$49/user/month)"
  echo "  onboarding [directory]    Generate onboarding guide"
  echo "  architecture [directory]  Generate architecture docs"
  echo ""
  echo -e "${BOLD}OTHER${NC}"
  echo "  status                    Show license and config info"
  echo "  --help, -h                Show this help"
  echo "  --version, -v             Show version"
  echo ""
  echo "Get a license at ${CYAN}https://docsync.pages.dev${NC}"
}

# ─── License check ──────────────────────────────────────────────────────────

require_license() {
  local required_tier="${1:-pro}"
  source "$SCRIPT_DIR/license.sh"
  check_license "$required_tier"
}

# ─── Command dispatch ───────────────────────────────────────────────────────

main() {
  local cmd="${1:-}"
  shift || true

  case "$cmd" in
    generate)
      local target="${1:-.}"
      log_info "Generating documentation for ${BOLD}$target${NC}"
      source "$SCRIPT_DIR/generate.sh"
      do_generate "$target"
      ;;

    drift)
      require_license "pro"
      local target="${1:-.}"
      log_info "Scanning for documentation drift in ${BOLD}$target${NC}"
      source "$SCRIPT_DIR/drift.sh"
      do_drift "$target"
      ;;

    hooks)
      require_license "pro"
      local subcmd="${1:-}"
      case "$subcmd" in
        install)
          source "$SCRIPT_DIR/hooks-install.sh"
          do_hooks_install
          ;;
        uninstall)
          source "$SCRIPT_DIR/hooks-install.sh"
          do_hooks_uninstall
          ;;
        *)
          log_error "Unknown hooks subcommand: $subcmd"
          echo "  Usage: docsync hooks [install|uninstall]"
          exit 1
          ;;
      esac
      ;;

    auto-fix)
      require_license "pro"
      local target="${1:-.}"
      log_info "Auto-fixing stale documentation in ${BOLD}$target${NC}"
      source "$SCRIPT_DIR/drift.sh"
      source "$SCRIPT_DIR/generate.sh"
      do_auto_fix "$target"
      ;;

    onboarding)
      require_license "team"
      local target="${1:-.}"
      log_info "Generating onboarding guide for ${BOLD}$target${NC}"
      source "$SCRIPT_DIR/generate.sh"
      do_onboarding "$target"
      ;;

    architecture)
      require_license "team"
      local target="${1:-.}"
      log_info "Generating architecture documentation for ${BOLD}$target${NC}"
      source "$SCRIPT_DIR/generate.sh"
      do_architecture "$target"
      ;;

    status)
      show_version
      echo ""
      source "$SCRIPT_DIR/license.sh"
      show_license_status
      ;;

    --help|-h|help)
      show_help
      ;;

    --version|-v)
      show_version
      ;;

    "")
      show_help
      exit 1
      ;;

    *)
      log_error "Unknown command: $cmd"
      echo ""
      show_help
      exit 1
      ;;
  esac
}

main "$@"
