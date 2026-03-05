#!/usr/bin/env bash
# council-brief.sh — Unified router for LLM Council skill
# Usage: council-brief.sh [install|ask <question>|status|stop|<question>|--help]
#
# Routes commands to appropriate handler:
#   install  → install.sh (setup + launch)
#   ask      → ask-council.sh (headless council query)
#   status   → status.sh (check services)
#   stop     → stop.sh (stop services)
#   <text>   → treated as question for ask mode
#   --help   → usage

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── Colors ────────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
error() { echo -e "${RED}[council-brief]${NC} $*" >&2; exit 1; }
info()  { echo -e "${GREEN}[council-brief]${NC} $*"; }
warn()  { echo -e "${YELLOW}[council-brief]${NC} $*"; }

# ── Show usage ──────────────────────────────────────────────────────────────
usage() {
  cat <<EOF
Council Brief v2.0.0 — Unified LLM Council

Usage: /council-brief [install|ask <question>|status|stop|<question>]

Commands:
  install          Install dependencies and start services
  ask <question>   Ask the council a question (headless)
  status           Check if services are running
  stop             Stop background services
  --help           Show this help
  <question>       Any other text is treated as a question

Examples:
  /council-brief install
  /council-brief ask "Should I invest in Tesla?"
  /council-brief "Is Python or Go better for microservices?"
  /council-brief status
  /council-brief stop

Two ways to use:
  • Quick answer: /council-brief "your question"
  • Full web UI:  /council-brief install → open browser at :5173
EOF
}

# ── Parse arguments ───────────────────────────────────────────────────────────
if [[ $# -eq 0 ]]; then
  usage
  exit 0
fi

CMD="${1:-}"
shift || true

# ── Route to appropriate handler ──────────────────────────────────────────────
case "$CMD" in
  install)
    bash "$SKILL_DIR/install.sh" "$@"
    ;;
  
  status)
    bash "$SKILL_DIR/status.sh" "$@"
    ;;
  
  stop)
    bash "$SKILL_DIR/stop.sh" "$@"
    ;;
  
  ask)
    # "ask" keyword with question following
    QUESTION="${*:-}"
    if [[ -z "$QUESTION" ]]; then
      error "Usage: /council-brief ask '<question>'"
    fi
    bash "$SKILL_DIR/ask-council.sh" "$QUESTION"
    ;;
  
  help|--help|-h)
    usage
    exit 0
    ;;
  
  *)
    # Any other text — treat as a question
    # Reconstruct the full input including the first "arg"
    QUESTION="$CMD ${*:-}"
    QUESTION="${QUESTION%% }"  # trim trailing space if no args
    bash "$SKILL_DIR/ask-council.sh" "$QUESTION"
    ;;
esac
