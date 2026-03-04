#!/usr/bin/env bash
# audit.sh — Main entry point for skill-trust-auditor
#
# Usage:
#   bash scripts/audit.sh <skill-name-or-url> [--llm] [--json-only]
#
# Examples:
#   bash scripts/audit.sh steipete/git-summary
#   bash scripts/audit.sh https://clawhub.ai/someuser/someskill
#   bash scripts/audit.sh steipete/git-summary --llm
#   bash scripts/audit.sh someuser/someskill --json-only

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ANALYZER="$SCRIPT_DIR/analyze_skill.py"

# ── Colour helpers ─────────────────────────────────────────────────────────────
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

err()  { echo -e "${RED}ERROR:${RESET} $*" >&2; }
info() { echo -e "${CYAN}==>${RESET} $*" >&2; }
ok()   { echo -e "${GREEN}✓${RESET} $*" >&2; }

# ── Argument parsing ──────────────────────────────────────────────────────────
if [[ $# -lt 1 ]]; then
  echo "Usage: bash scripts/audit.sh <skill-name-or-url> [--llm] [--json-only]"
  echo ""
  echo "Examples:"
  echo "  bash scripts/audit.sh steipete/git-summary"
  echo "  bash scripts/audit.sh https://clawhub.ai/someuser/someskill"
  echo "  bash scripts/audit.sh someuser/someskill --llm"
  echo "  bash scripts/audit.sh someuser/someskill --json-only"
  exit 2
fi

SKILL_INPUT="$1"
shift
EXTRA_ARGS=("$@")

# ── Dependency checks ─────────────────────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
  err "python3 not found. Run: bash scripts/setup.sh"
  exit 2
fi

if [[ ! -f "$ANALYZER" ]]; then
  err "analyze_skill.py not found at $ANALYZER"
  exit 2
fi

if [[ ! -f "$SCRIPT_DIR/patterns.json" ]]; then
  err "patterns.json not found. Reinstall skill-trust-auditor."
  exit 2
fi

# Check for requests module
if ! python3 -c "import requests" &>/dev/null 2>&1; then
  err "Python 'requests' module not installed. Run: bash scripts/setup.sh"
  exit 2
fi

# ── Input validation ──────────────────────────────────────────────────────────
# Basic sanity check on skill name / URL
if [[ "$SKILL_INPUT" != http* ]] && [[ "$SKILL_INPUT" != */* ]]; then
  err "Invalid skill name '$SKILL_INPUT'. Expected 'user/skill' or a full URL."
  echo "  Examples:"
  echo "    steipete/git-summary"
  echo "    https://clawhub.ai/someuser/someskill"
  exit 2
fi

# Disallow obviously malformed inputs
if [[ ${#SKILL_INPUT} -gt 256 ]]; then
  err "Input too long (max 256 chars)"
  exit 2
fi

# ── JSON-only mode ────────────────────────────────────────────────────────────
JSON_ONLY=false
LLM_FLAG=""
REMAINING_ARGS=()
for arg in "${EXTRA_ARGS[@]:-}"; do
  case "$arg" in
    --json-only) JSON_ONLY=true ;;
    --llm)       LLM_FLAG="--llm" ;;
    *)           REMAINING_ARGS+=("$arg") ;;
  esac
done

# ── Run audit ─────────────────────────────────────────────────────────────────
if [[ "$JSON_ONLY" == false ]]; then
  echo ""
  echo -e "${BOLD}🛡️  Skill Trust Auditor${RESET}"
  echo -e "   Auditing: ${CYAN}${SKILL_INPUT}${RESET}"
  if [[ -n "$LLM_FLAG" ]]; then
    echo -e "   LLM-as-judge: ${GREEN}enabled${RESET}"
  fi
  echo ""
fi

# Build analyzer command
ANALYZER_CMD=(python3 "$ANALYZER" "$SKILL_INPUT")
[[ -n "$LLM_FLAG" ]] && ANALYZER_CMD+=("$LLM_FLAG")
[[ "$JSON_ONLY" == true ]] && ANALYZER_CMD+=("--json-only")

# Run and capture exit code
set +e
"${ANALYZER_CMD[@]}"
EXIT_CODE=$?
set -e

# ── Exit code handling ────────────────────────────────────────────────────────
if [[ "$JSON_ONLY" == false ]]; then
  case $EXIT_CODE in
    0)
      echo -e "${GREEN}Audit complete.${RESET}" >&2
      ;;
    1)
      echo -e "${RED}⛔  DO NOT INSTALL — high-risk patterns detected.${RESET}" >&2
      ;;
    2)
      echo -e "${RED}Audit failed — check errors above.${RESET}" >&2
      ;;
  esac
fi

exit $EXIT_CODE
