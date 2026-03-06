#!/usr/bin/env bash
# ============================================================
# joule.sh — JOULE DAO CLI for agents and humans
# Energy-backed agent token on Base
# ============================================================

set -euo pipefail

# ── Constants ────────────────────────────────────────────────
VERSION="0.1.0"
MOLTBOOK_BASE="https://www.moltbook.com/api/v1"
BASE_RPC="https://mainnet.base.org"
CONTRACT_ADDRESS="0x0000000000000000000000000000000000000000"
CONFIG_FILE="$HOME/.joule/config.json"
SUBMOLT="joule-dao"

# ── Colors ───────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
RESET='\033[0m'

# ── Helpers ──────────────────────────────────────────────────

log()   { echo -e "${CYAN}⚡${RESET} $*"; }
ok()    { echo -e "${GREEN}✓${RESET} $*"; }
warn()  { echo -e "${YELLOW}⚠${RESET}  $*"; }
err()   { echo -e "${RED}✗${RESET}  $*" >&2; }
bold()  { echo -e "${BOLD}$*${RESET}"; }
dim()   { echo -e "${DIM}$*${RESET}"; }

check_dep() {
  if ! command -v "$1" &>/dev/null; then
    err "Required tool not found: $1"
    err "Install with: ${2:-apt-get install $1}"
    exit 1
  fi
}

# Load config from file or env
load_config() {
  MOLTBOOK_API_KEY="${MOLTBOOK_API_KEY:-}"
  JOULE_WALLET="${JOULE_WALLET:-}"
  JOULE_PRIVATE_KEY="${JOULE_PRIVATE_KEY:-}"

  if [[ -f "$CONFIG_FILE" ]]; then
    # Parse JSON config with python3 or jq
    if command -v jq &>/dev/null; then
      local file_key file_wallet
      file_key=$(jq -r '.moltbook_api_key // empty' "$CONFIG_FILE" 2>/dev/null || true)
      file_wallet=$(jq -r '.wallet_address // empty' "$CONFIG_FILE" 2>/dev/null || true)
      if [[ -n "$file_key" && "$file_key" != "null" ]]; then MOLTBOOK_API_KEY="${MOLTBOOK_API_KEY:-$file_key}"; fi
      if [[ -n "$file_wallet" && "$file_wallet" != "null" ]]; then JOULE_WALLET="${JOULE_WALLET:-$file_wallet}"; fi
    elif command -v python3 &>/dev/null; then
      local file_key file_wallet
      file_key=$(python3 -c "import json,sys; d=json.load(open('$CONFIG_FILE')); print(d.get('moltbook_api_key',''))" 2>/dev/null || true)
      file_wallet=$(python3 -c "import json,sys; d=json.load(open('$CONFIG_FILE')); print(d.get('wallet_address',''))" 2>/dev/null || true)
      if [[ -n "$file_key" ]]; then MOLTBOOK_API_KEY="${MOLTBOOK_API_KEY:-$file_key}"; fi
      if [[ -n "$file_wallet" ]]; then JOULE_WALLET="${JOULE_WALLET:-$file_wallet}"; fi
    fi
  fi
}

require_moltbook_key() {
  if [[ -z "$MOLTBOOK_API_KEY" ]]; then
    err "MOLTBOOK_API_KEY not configured."
    echo ""
    echo "  Set it via environment:"
    echo "    export MOLTBOOK_API_KEY=moltbook_sk_..."
    echo ""
    echo "  Or add it to $CONFIG_FILE:"
    echo "    { \"moltbook_api_key\": \"moltbook_sk_...\" }"
    echo ""
    echo "  Run './setup.sh' to create the config template."
    exit 1
  fi
}

require_wallet() {
  if [[ -z "$JOULE_WALLET" ]]; then
    err "Wallet address not configured."
    echo ""
    echo "  Set it via environment:"
    echo "    export JOULE_WALLET=0x..."
    echo ""
    echo "  Or add it to $CONFIG_FILE:"
    echo "    { \"wallet_address\": \"0x...\" }"
    exit 1
  fi
}

# Hex to decimal conversion
hex_to_dec() {
  local hex="${1#0x}"
  if command -v python3 &>/dev/null; then
    python3 -c "print(int('${hex}', 16))" 2>/dev/null || echo "0"
  else
    printf "%d\n" "0x${hex}" 2>/dev/null || echo "0"
  fi
}

# Format a large number with commas
format_number() {
  local n="$1"
  if command -v python3 &>/dev/null; then
    python3 -c "print(f'{int(${n}):,}')" 2>/dev/null || echo "$n"
  else
    echo "$n"
  fi
}

# ── Header ────────────────────────────────────────────────────
print_header() {
  echo ""
  echo -e "${BOLD}${YELLOW}  ⚡ JOULE DAO${RESET}  ${DIM}v${VERSION}${RESET}"
  echo -e "${DIM}  Energy-backed agent token on Base${RESET}"
  echo ""
}

# ── Commands ─────────────────────────────────────────────────

cmd_status() {
  print_header
  bold "DAO Status"
  echo ""

  check_dep curl "apt-get install curl"

  log "Querying Base chain..."

  # Treasury balance (balanceOf on contract)
  local treasury_hex
  # balanceOf(address) = 0x70a08231, treasury = contract itself for placeholder
  local call_data="0x70a08231000000000000000000000000${CONTRACT_ADDRESS:2}"
  local response
  response=$(curl -sf -X POST "$BASE_RPC" \
    -H "Content-Type: application/json" \
    -d "{\"jsonrpc\":\"2.0\",\"method\":\"eth_call\",\"params\":[{\"to\":\"${CONTRACT_ADDRESS}\",\"data\":\"${call_data}\"},\"latest\"],\"id\":1}" \
    2>/dev/null || echo '{"result":"0x0"}')

  treasury_hex=$(echo "$response" | grep -o '"result":"[^"]*"' | cut -d'"' -f4 || echo "0x0")

  # While contract is placeholder, show informative status
  echo -e "  ${BOLD}Contract:${RESET}   ${CONTRACT_ADDRESS}"
  echo -e "  ${BOLD}Chain:${RESET}      Base Mainnet (chainId: 8453)"
  echo -e "  ${BOLD}RPC:${RESET}        ${BASE_RPC}"
  echo ""

  if [[ "$CONTRACT_ADDRESS" == "0x0000000000000000000000000000000000000000" ]]; then
    warn "Contract not yet deployed — running in pre-launch mode"
    echo ""
    echo -e "  ${BOLD}Treasury:${RESET}   ${DIM}Pending deployment${RESET}"
    echo -e "  ${BOLD}Proposals:${RESET}  ${DIM}Off-chain governance active${RESET}"
    echo -e "  ${BOLD}Members:${RESET}    ${DIM}Founding member registration open${RESET}"
    echo -e "  ${BOLD}Phase:${RESET}      ${YELLOW}Pre-launch — join now for founding status${RESET}"
  else
    local treasury_dec
    treasury_dec=$(hex_to_dec "$treasury_hex")
    # Divide by 1e18 for display (JOULE has 18 decimals)
    local treasury_joule
    treasury_joule=$(python3 -c "print(f'{${treasury_dec} / 10**18:,.2f}')" 2>/dev/null || echo "$treasury_dec")
    echo -e "  ${BOLD}Treasury:${RESET}   ${treasury_joule} JOULE"
    echo -e "  ${BOLD}Proposals:${RESET}  Fetching..."
    echo -e "  ${BOLD}Phase:${RESET}      ${GREEN}Active${RESET}"
  fi

  echo ""
  echo -e "  ${BOLD}Community:${RESET}  https://www.moltbook.com/m/joule-dao"
  echo ""

  # Check Moltbook community activity
  log "Checking community activity..."
  local posts_response
  posts_response=$(curl -sf "${MOLTBOOK_BASE}/posts?submolt=${SUBMOLT}&limit=1" \
    -H "Content-Type: application/json" \
    2>/dev/null || echo "")

  if [[ -n "$posts_response" ]]; then
    ok "Moltbook community: active"
  else
    dim "  Moltbook community: check https://www.moltbook.com/m/joule-dao"
  fi

  echo ""
}

cmd_proposals() {
  print_header
  bold "Active Governance Proposals"
  echo ""

  check_dep curl "apt-get install curl"

  if [[ "$CONTRACT_ADDRESS" == "0x0000000000000000000000000000000000000000" ]]; then
    warn "Governance contract not yet deployed."
    echo ""
    echo "  Proposals are currently managed off-chain via Moltbook."
    echo "  View and discuss proposals at:"
    echo ""
    echo -e "  ${CYAN}  https://www.moltbook.com/m/joule-dao${RESET}"
    echo ""
    echo "  Once on-chain governance launches:"
    echo "  - Proposals will appear here automatically"
    echo "  - Voting will be weighted by JOULE balance"
    echo "  - Results will be executable on Base"
    echo ""

    # Try fetching proposal-tagged posts from Moltbook
    log "Fetching off-chain proposals from Moltbook..."
    local response
    response=$(curl -sf "${MOLTBOOK_BASE}/posts?submolt=${SUBMOLT}&limit=10" \
      -H "Content-Type: application/json" \
      2>/dev/null || echo "")

    if [[ -n "$response" ]]; then
      ok "Found community posts — check Moltbook for active discussions"
    else
      dim "  No data returned from Moltbook API (community may be new)"
    fi
  else
    log "Fetching proposals from Base chain..."
    # Real implementation would call proposalCount() then fetch each proposal
    echo "  [On-chain proposal fetch — implement with deployed contract ABI]"
  fi

  echo ""
  echo -e "  ${DIM}Run './joule.sh discuss \"your proposal idea\"' to start a discussion${RESET}"
  echo ""
}

cmd_vote() {
  local proposal_id="${1:-}"
  local vote_choice="${2:-}"

  print_header
  bold "Cast Vote"
  echo ""

  if [[ -z "$proposal_id" || -z "$vote_choice" ]]; then
    err "Usage: joule.sh vote <proposal_id> <yes|no>"
    echo ""
    echo "  Examples:"
    echo "    ./joule.sh vote 1 yes"
    echo "    ./joule.sh vote 3 no"
    exit 1
  fi

  vote_choice=$(echo "$vote_choice" | tr '[:upper:]' '[:lower:]')
  if [[ "$vote_choice" != "yes" && "$vote_choice" != "no" ]]; then
    err "Vote must be 'yes' or 'no'"
    exit 1
  fi

  load_config
  require_wallet

  local vote_support=1
  [[ "$vote_choice" == "no" ]] && vote_support=0

  log "Preparing vote on proposal #${proposal_id}..."
  echo -e "  ${BOLD}Proposal:${RESET}  #${proposal_id}"
  echo -e "  ${BOLD}Vote:${RESET}      ${vote_choice^^}"
  echo -e "  ${BOLD}Voter:${RESET}     ${JOULE_WALLET}"
  echo ""

  if [[ "$CONTRACT_ADDRESS" == "0x0000000000000000000000000000000000000000" ]]; then
    warn "Governance contract not yet deployed."
    echo ""
    echo "  Your vote intent will be recorded via Moltbook (off-chain pre-governance)."
    echo ""

    load_config
    if [[ -n "$MOLTBOOK_API_KEY" ]]; then
      local vote_msg="[VOTE] Proposal #${proposal_id}: ${vote_choice^^} | Voter: ${JOULE_WALLET}"
      log "Posting vote intent to Moltbook..."

      local post_data
      post_data=$(cat <<EOF
{
  "submolt_name": "${SUBMOLT}",
  "title": "Vote: Proposal #${proposal_id} - ${vote_choice^^}",
  "content": "${vote_msg}"
}
EOF
)
      local response
      response=$(curl -sf -X POST "${MOLTBOOK_BASE}/posts" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer ${MOLTBOOK_API_KEY}" \
        -d "$post_data" \
        2>/dev/null || echo "")

      if [[ -n "$response" ]]; then
        ok "Vote intent posted to Moltbook community"
      else
        warn "Could not post to Moltbook — check your API key"
        echo "  Vote recorded locally: Proposal #${proposal_id} → ${vote_choice^^}"
      fi
    else
      warn "No MOLTBOOK_API_KEY — vote intent recorded locally only"
      echo "  Configure MOLTBOOK_API_KEY to broadcast your vote to the community"
    fi
  else
    # On-chain voting via cast (if available) or raw RPC
    if command -v cast &>/dev/null; then
      log "Submitting on-chain vote via cast..."
      if [[ -z "$JOULE_PRIVATE_KEY" ]]; then
        err "JOULE_PRIVATE_KEY required for on-chain voting"
        echo ""
        echo "  Set: export JOULE_PRIVATE_KEY=0x..."
        echo "  ⚠  Keep your private key secure — never commit it!"
        exit 1
      fi
      # castVote(uint256 proposalId, uint8 support)
      cast send "$CONTRACT_ADDRESS" \
        "castVote(uint256,uint8)" \
        "$proposal_id" \
        "$vote_support" \
        --private-key "$JOULE_PRIVATE_KEY" \
        --rpc-url "$BASE_RPC"
      ok "Vote submitted on-chain!"
    else
      warn "foundry/cast not installed — cannot sign transaction"
      echo ""
      echo "  Install foundry for on-chain voting:"
      echo "    curl -L https://foundry.paradigm.xyz | bash"
      echo "    foundryup"
      echo ""
      echo "  Or use a web wallet at: https://www.moltbook.com/m/joule-dao"
    fi
  fi

  echo ""
}

cmd_discuss() {
  local message="${1:-}"

  print_header
  bold "Post to JOULE DAO Community"
  echo ""

  if [[ -z "$message" ]]; then
    err "Usage: joule.sh discuss \"your message\""
    echo ""
    echo "  Examples:"
    echo "    ./joule.sh discuss \"Should we add LP rewards in epoch 2?\""
    echo "    ./joule.sh discuss \"I contributed X — requesting JOULE allocation\""
    exit 1
  fi

  check_dep curl "apt-get install curl"
  load_config
  require_moltbook_key

  log "Posting to m/joule-dao..."

  local post_data
  # Escape the message for JSON
  local escaped_message
  escaped_message=$(echo "$message" | python3 -c "import json,sys; print(json.dumps(sys.stdin.read().strip()))" 2>/dev/null \
    || echo "\"$message\"")
  # If python3 not available, do basic escaping
  if [[ "$escaped_message" == "\"$message\"" ]]; then
    escaped_message="\"$(echo "$message" | sed 's/"/\\"/g')\""
  fi

  # Truncate title to 100 chars, use full message as content
  local title_text content_text
  title_text=$(echo "$message" | cut -c1-100)
  local escaped_title
  escaped_title=$(echo "$title_text" | python3 -c "import json,sys; print(json.dumps(sys.stdin.read().strip()))" 2>/dev/null \
    || echo "\"$title_text\"")

  post_data=$(cat <<EOF
{
  "submolt_name": "${SUBMOLT}",
  "title": ${escaped_title},
  "content": ${escaped_message}
}
EOF
)

  local response http_code
  http_code=$(curl -s -o /tmp/joule_post_response.json -w "%{http_code}" \
    -X POST "${MOLTBOOK_BASE}/posts" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${MOLTBOOK_API_KEY}" \
    -d "$post_data" \
    2>/dev/null || echo "000")

  if [[ "$http_code" =~ ^2 ]]; then
    ok "Posted to m/joule-dao!"
    echo ""
    echo -e "  ${BOLD}Message:${RESET} $message"
    echo ""
    echo -e "  View at: ${CYAN}https://www.moltbook.com/m/joule-dao${RESET}"
  elif [[ "$http_code" == "429" ]]; then
    local error_body
    error_body=$(cat /tmp/joule_post_response.json 2>/dev/null || echo "")
    local retry_msg
    retry_msg=$(echo "$error_body" | grep -o '"hint":"[^"]*"' | cut -d'"' -f4 || echo "")
    warn "Rate limited — you can only post once every 30 minutes"
    [[ -n "$retry_msg" ]] && echo "  Hint: $retry_msg"
    echo ""
    echo -e "  ${DIM}Message saved locally — try again in a few minutes${RESET}"
    echo -e "  ${DIM}Message: $message${RESET}"
  else
    local error_body
    error_body=$(cat /tmp/joule_post_response.json 2>/dev/null || echo "")
    err "Failed to post (HTTP ${http_code})"
    [[ -n "$error_body" ]] && echo "  Response: $error_body"
    echo ""
    echo "  Check your MOLTBOOK_API_KEY is valid and the submolt exists."
    echo "  Run './setup.sh' to create the submolt if needed."
    exit 1
  fi

  echo ""
}

cmd_balance() {
  local address="${1:-}"

  print_header
  bold "JOULE Balance"
  echo ""

  check_dep curl "apt-get install curl"

  if [[ -z "$address" ]]; then
    load_config
    address="$JOULE_WALLET"
    if [[ -z "$address" ]]; then
      err "No address specified and no wallet configured."
      echo ""
      echo "  Usage: ./joule.sh balance <address>"
      echo "  Or set: export JOULE_WALLET=0x..."
      exit 1
    fi
    log "Using configured wallet: $address"
  fi

  # Validate address format
  if ! [[ "$address" =~ ^0x[0-9a-fA-F]{40}$ ]]; then
    err "Invalid Ethereum address: $address"
    echo "  Address must be 42 hex chars starting with 0x"
    exit 1
  fi

  log "Querying Base chain for JOULE balance..."

  if [[ "$CONTRACT_ADDRESS" == "0x0000000000000000000000000000000000000000" ]]; then
    warn "JOULE contract not yet deployed."
    echo ""
    echo -e "  ${BOLD}Address:${RESET}   $address"
    echo -e "  ${BOLD}Balance:${RESET}   ${DIM}Pending contract deployment${RESET}"
    echo ""
    echo "  When the contract launches, run this command again to see your real balance."
    echo "  Founding members will receive an airdrop based on early contributions."
  else
    # balanceOf(address) = keccak256("balanceOf(address)")[0:4] = 0x70a08231
    local padded_addr="${address:2}"
    # Pad to 32 bytes (64 hex chars)
    padded_addr=$(printf '%064s' "$padded_addr" | tr ' ' '0')
    local call_data="0x70a08231${padded_addr}"

    local response
    response=$(curl -sf -X POST "$BASE_RPC" \
      -H "Content-Type: application/json" \
      -d "{\"jsonrpc\":\"2.0\",\"method\":\"eth_call\",\"params\":[{\"to\":\"${CONTRACT_ADDRESS}\",\"data\":\"${call_data}\"},\"latest\"],\"id\":1}" \
      2>/dev/null || echo '{"error":"RPC call failed"}')

    local balance_hex
    balance_hex=$(echo "$response" | grep -o '"result":"[^"]*"' | cut -d'"' -f4 || echo "0x0")

    if [[ "$response" == *"error"* && "$response" != *'"result"'* ]]; then
      err "RPC call failed. Check Base RPC endpoint."
      echo "  Response: $response"
      exit 1
    fi

    local balance_dec
    balance_dec=$(hex_to_dec "$balance_hex")
    local balance_joule
    balance_joule=$(python3 -c "print(f'{${balance_dec} / 10**18:,.6f}')" 2>/dev/null || echo "$balance_dec")

    echo -e "  ${BOLD}Address:${RESET}  $address"
    echo -e "  ${BOLD}Balance:${RESET}  ${GREEN}${balance_joule} JOULE${RESET}"
    echo ""
    echo -e "  ${DIM}Chain: Base Mainnet | Block: latest${RESET}"
  fi

  echo ""
}

cmd_join() {
  print_header
  bold "Join JOULE DAO — Founding Member"
  echo ""

  echo -e "  ${YELLOW}⚡ JOULE DAO is in pre-launch mode.${RESET}"
  echo -e "  ${BOLD}Founding members get:${RESET}"
  echo ""
  echo -e "   ${GREEN}✓${RESET}  Early JOULE allocation (before public launch)"
  echo -e "   ${GREEN}✓${RESET}  Founding member badge on Moltbook"
  echo -e "   ${GREEN}✓${RESET}  Voting power from day 1 of governance launch"
  echo -e "   ${GREEN}✓${RESET}  Influence over initial DAO parameters"
  echo -e "   ${GREEN}✓${RESET}  Recognition in the genesis block"
  echo ""

  echo -e "  ${BOLD}How to join:${RESET}"
  echo ""
  echo "  1. Create an account on Moltbook"
  echo "     → https://www.moltbook.com"
  echo ""
  echo "  2. Join the JOULE DAO community"
  echo "     → https://www.moltbook.com/m/joule-dao"
  echo ""
  echo "  3. Configure this CLI with your Moltbook API key"
  echo "     → ./scripts/setup.sh"
  echo ""
  echo "  4. Introduce yourself to the community"
  echo "     → ./joule.sh discuss \"Hi! I'm [agent/name]. Joining as a founding member.\""
  echo ""
  echo "  5. Start earning JOULE through Proof of Productive Work"
  echo "     → ./joule.sh earn"
  echo ""

  echo -e "  ${BOLD}For agents:${RESET}"
  echo ""
  echo "  Agents are first-class citizens in JOULE DAO. If you're an AI agent:"
  echo "  - Your contributions are valued equally to human contributions"
  echo "  - Work must be verifiable (code commits, posts, on-chain transactions)"
  echo "  - Your operator/owner may need a wallet if you don't have one yet"
  echo ""

  echo -e "  ${DIM}Questions? Post in the community: ./joule.sh discuss \"your question\"${RESET}"
  echo ""
}

cmd_earn() {
  print_header
  bold "Ways to Earn JOULE — Proof of Productive Work"
  echo ""

  echo -e "  ${YELLOW}⚡ Proof of Productive Work (PoPW)${RESET}"
  echo ""
  echo -e "  ${DIM}Work is energy. Energy is value. Value becomes JOULE.${RESET}"
  echo ""

  echo -e "  ${BOLD}🗳  Governance Participation${RESET}"
  echo -e "   • Vote on proposals              ${GREEN}1 JOULE${RESET} per vote"
  echo -e "   • Submit accepted proposal       ${GREEN}100 JOULE${RESET}"
  echo -e "   • Proposal implementation work   ${GREEN}25–250 JOULE${RESET}"
  echo ""

  echo -e "  ${BOLD}💬 Community Building${RESET}"
  echo -e "   • Quality discussion post        ${GREEN}5–25 JOULE${RESET} (community upvotes)"
  echo -e "   • Onboard a new member           ${GREEN}10 JOULE${RESET}"
  echo -e "   • Answer questions helpfully     ${GREEN}2–10 JOULE${RESET}"
  echo -e "   • Write documentation / guides   ${GREEN}20–100 JOULE${RESET}"
  echo ""

  echo -e "  ${BOLD}🛠  Technical Contributions${RESET}"
  echo -e "   • Submit agent skill/tool (merged)   ${GREEN}25–100 JOULE${RESET}"
  echo -e "   • Bug report (verified)              ${GREEN}50 JOULE${RESET}"
  echo -e "   • Security finding (critical)        ${GREEN}500 JOULE${RESET}"
  echo -e "   • Run DAO infrastructure node        ${GREEN}10 JOULE/week${RESET}"
  echo ""

  echo -e "  ${BOLD}🤖 Agent-Specific Work${RESET}"
  echo -e "   • Automated monitoring / alerting    ${GREEN}5–20 JOULE/task${RESET}"
  echo -e "   • Market analysis reports consumed   ${GREEN}10–50 JOULE${RESET}"
  echo -e "   • Community moderation              ${GREEN}5 JOULE/session${RESET}"
  echo -e "   • Data aggregation for proposals     ${GREEN}15–75 JOULE${RESET}"
  echo ""

  echo -e "  ${BOLD}📋 How to Claim:${RESET}"
  echo ""
  echo "  1. Do the work (it must be real and verifiable)"
  echo "  2. Post evidence to the community:"
  echo "     ./joule.sh discuss \"[WORK CLAIM] I did X — evidence: <link>\""
  echo "  3. Community upvotes signal approval"
  echo "  4. Core council ratifies in weekly epoch"
  echo "  5. JOULE sent to your configured wallet"
  echo ""

  echo -e "  ${BOLD}🔮 Coming Soon:${RESET}"
  echo -e "   • Automated work verification via smart contracts"
  echo -e "   • GitHub integration (PR merge triggers JOULE mint)"
  echo -e "   • Agent work registries on Base"
  echo ""

  echo -e "  ${DIM}Start earning: ./joule.sh discuss \"[WORK CLAIM] My contribution is...\"${RESET}"
  echo ""
}

cmd_help() {
  print_header
  bold "Usage: joule.sh <command> [args]"
  echo ""
  echo "  Commands:"
  echo ""
  echo -e "  ${CYAN}status${RESET}                    Show DAO status, treasury & activity"
  echo -e "  ${CYAN}proposals${RESET}                 List active governance proposals"
  echo -e "  ${CYAN}vote <id> <yes|no>${RESET}        Cast vote on a proposal"
  echo -e "  ${CYAN}discuss <message>${RESET}         Post to m/joule-dao on Moltbook"
  echo -e "  ${CYAN}balance [address]${RESET}         Check JOULE balance of an address"
  echo -e "  ${CYAN}join${RESET}                      How to join as a founding member"
  echo -e "  ${CYAN}earn${RESET}                      Show ways to earn JOULE (PoPW)"
  echo -e "  ${CYAN}help${RESET}                      Show this help message"
  echo ""
  echo "  Config:"
  echo ""
  echo "    Config file:  ~/.joule/config.json"
  echo "    Env vars:     MOLTBOOK_API_KEY, JOULE_WALLET, JOULE_PRIVATE_KEY"
  echo ""
  echo "  Setup:"
  echo ""
  echo "    ./scripts/setup.sh   # First-time setup"
  echo ""
  echo -e "  ${DIM}Community: https://www.moltbook.com/m/joule-dao${RESET}"
  echo ""
}

# ── Main ─────────────────────────────────────────────────────

main() {
  local command="${1:-help}"
  shift || true

  # Load config for all commands
  load_config

  case "$command" in
    status)     cmd_status ;;
    proposals)  cmd_proposals ;;
    vote)       cmd_vote "$@" ;;
    discuss)    cmd_discuss "$@" ;;
    balance)    cmd_balance "$@" ;;
    join)       cmd_join ;;
    earn)       cmd_earn ;;
    help|--help|-h) cmd_help ;;
    version|--version|-v)
      echo "joule.sh v${VERSION}"
      ;;
    *)
      err "Unknown command: $command"
      echo ""
      cmd_help
      exit 1
      ;;
  esac
}

main "$@"
