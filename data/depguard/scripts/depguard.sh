#!/usr/bin/env bash
# DepGuard — Main CLI entry point
# Usage: depguard.sh <command> [args...]

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
DIM='\033[2m'
NC='\033[0m'

log_info()    { echo -e "${BLUE}[DepGuard]${NC} $*"; }
log_success() { echo -e "${GREEN}[DepGuard]${NC} $*"; }
log_warn()    { echo -e "${YELLOW}[DepGuard]${NC} $*"; }
log_error()   { echo -e "${RED}[DepGuard]${NC} $*" >&2; }

show_version() {
  echo -e "${BOLD}DepGuard${NC} v${VERSION}"
  echo "  Dependency audit & license compliance"
  echo "  https://depguard.pages.dev"
}

show_help() {
  show_version
  echo ""
  echo -e "${BOLD}USAGE${NC}"
  echo "  depguard <command> [options]"
  echo ""
  echo -e "${BOLD}FREE COMMANDS${NC}"
  echo "  scan [directory]          Vulnerability & license scan"
  echo "  report [directory]        Generate dependency health report"
  echo ""
  echo -e "${BOLD}PRO COMMANDS${NC} (\$19/user/month)"
  echo "  hooks install             Install pre-commit hooks"
  echo "  hooks uninstall           Remove DepGuard hooks"
  echo "  watch [directory]         Continuous monitoring"
  echo "  fix [directory]           Auto-fix vulnerabilities"
  echo ""
  echo -e "${BOLD}TEAM COMMANDS${NC} (\$39/user/month)"
  echo "  policy [directory]        Enforce dependency policy"
  echo "  sbom [directory]          Generate SBOM (CycloneDX/SPDX)"
  echo "  compliance [directory]    License compliance report"
  echo ""
  echo -e "${BOLD}OTHER${NC}"
  echo "  status                    Show license and config info"
  echo "  --help, -h                Show this help"
  echo "  --version, -v             Show version"
  echo ""
  echo "Get a license at ${CYAN}https://depguard.pages.dev${NC}"
}

# ─── License ────────────────────────────────────────────────────────────────

require_license() {
  local required_tier="${1:-pro}"
  source "$SCRIPT_DIR/license.sh"
  check_depguard_license "$required_tier"
}

# ─── Command dispatch ───────────────────────────────────────────────────────

main() {
  local cmd="${1:-}"
  shift || true

  case "$cmd" in
    scan)
      local target="${1:-.}"
      local flags="${2:-}"
      log_info "Scanning dependencies in ${BOLD}$target${NC}"
      source "$SCRIPT_DIR/scanner.sh"
      do_scan "$target" "$flags"
      ;;

    report)
      local target="${1:-.}"
      log_info "Generating dependency report for ${BOLD}$target${NC}"
      source "$SCRIPT_DIR/scanner.sh"
      do_report "$target"
      ;;

    hooks)
      require_license "pro"
      local subcmd="${1:-}"
      case "$subcmd" in
        install)
          source "$SCRIPT_DIR/hooks.sh"
          do_depguard_hooks_install
          ;;
        uninstall)
          source "$SCRIPT_DIR/hooks.sh"
          do_depguard_hooks_uninstall
          ;;
        *)
          log_error "Unknown hooks subcommand: $subcmd"
          echo "  Usage: depguard hooks [install|uninstall]"
          exit 1
          ;;
      esac
      ;;

    watch)
      require_license "pro"
      local target="${1:-.}"
      log_info "Starting continuous monitoring in ${BOLD}$target${NC}"
      source "$SCRIPT_DIR/scanner.sh"
      do_watch "$target"
      ;;

    fix)
      require_license "pro"
      local target="${1:-.}"
      log_info "Auto-fixing vulnerabilities in ${BOLD}$target${NC}"
      source "$SCRIPT_DIR/scanner.sh"
      do_fix "$target"
      ;;

    policy)
      require_license "team"
      local target="${1:-.}"
      log_info "Enforcing dependency policy in ${BOLD}$target${NC}"
      source "$SCRIPT_DIR/policy.sh"
      do_policy "$target"
      ;;

    sbom)
      require_license "team"
      local target="${1:-.}"
      log_info "Generating SBOM for ${BOLD}$target${NC}"
      source "$SCRIPT_DIR/sbom.sh"
      do_sbom "$target"
      ;;

    compliance)
      require_license "team"
      local target="${1:-.}"
      log_info "Generating compliance report for ${BOLD}$target${NC}"
      source "$SCRIPT_DIR/policy.sh"
      do_compliance "$target"
      ;;

    status)
      show_version
      echo ""
      source "$SCRIPT_DIR/license.sh"
      show_depguard_status
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
      show_help
      exit 1
      ;;
  esac
}

main "$@"
