#!/usr/bin/env bash
# rugcheck.sh — Query RugCheck API for Solana token analysis
# Usage: rugcheck.sh <command> [args...]
#
# Commands:
#   summary <mint>     — Token risk summary (score, risks, LP lock %)
#   report <mint>      — Full detailed report (holders, markets, metadata)
#   insiders <mint>    — Insider trading graph data
#   lockers <mint>     — LP vault/locker info
#   votes <mint>       — Community votes on token
#   leaderboard        — Top voters/analysts
#   domains            — Registered Solana domains
#   trending           — Most voted tokens (24h)
#   new                — Recently detected tokens
#   recent             — Most viewed tokens (24h)
#   verified           — Recently verified tokens

set -euo pipefail

API="https://api.rugcheck.xyz"
CMD="${1:-help}"
shift 2>/dev/null || true

# --- helpers ---
json_pp() {
  python3 -m json.tool 2>/dev/null || cat
}

err() { echo "ERROR: $*" >&2; exit 1; }

# Validate Solana mint address (base58, 32-44 chars)
validate_mint() {
  local mint="$1"
  [[ "$mint" =~ ^[1-9A-HJ-NP-Za-km-z]{32,44}$ ]] || err "Invalid mint address: $mint"
}

# --- commands ---

cmd_summary() {
  local mint="${1:?Usage: rugcheck.sh summary <mint_address>}"
  validate_mint "$mint"
  curl -sf "$API/v1/tokens/$mint/report/summary" | json_pp
}

cmd_report() {
  local mint="${1:?Usage: rugcheck.sh report <mint_address>}"
  validate_mint "$mint"
  curl -sf "$API/v1/tokens/$mint/report" | json_pp
}

cmd_insiders() {
  local mint="${1:?Usage: rugcheck.sh insiders <mint_address>}"
  validate_mint "$mint"
  curl -sf "$API/v1/tokens/$mint/insiders/graph" | json_pp
}

cmd_trending() {
  curl -sf "$API/v1/stats/trending" | json_pp
}

cmd_new() {
  curl -sf "$API/v1/stats/new_tokens" | json_pp
}

cmd_recent() {
  curl -sf "$API/v1/stats/recent" | json_pp
}

cmd_verified() {
  curl -sf "$API/v1/stats/verified" | json_pp
}

cmd_lockers() {
  local mint="${1:?Usage: rugcheck.sh lockers <mint_address>}"
  validate_mint "$mint"
  curl -sf "$API/v1/tokens/$mint/lockers" | json_pp
}

cmd_votes() {
  local mint="${1:?Usage: rugcheck.sh votes <mint_address>}"
  validate_mint "$mint"
  curl -sf "$API/v1/tokens/$mint/votes" | json_pp
}

cmd_leaderboard() {
  curl -sf "$API/v1/leaderboard" | json_pp
}

cmd_domains() {
  curl -sf "$API/v1/domains" | json_pp
}

cmd_help() {
  sed -n '2,12p' "$0"
  exit 0
}

# --- dispatch ---
case "$CMD" in
  summary)   cmd_summary "$@" ;;
  report)    cmd_report "$@" ;;
  insiders)  cmd_insiders "$@" ;;
  trending)  cmd_trending ;;
  new)       cmd_new ;;
  recent)    cmd_recent ;;
  verified)  cmd_verified ;;
  lockers)   cmd_lockers "$@" ;;
  votes)     cmd_votes "$@" ;;
  leaderboard) cmd_leaderboard ;;
  domains)   cmd_domains ;;
  help|--help|-h) cmd_help ;;
  *) err "Unknown command: $CMD. Run 'rugcheck.sh help' for usage." ;;
esac
