#!/usr/bin/env bash
set -euo pipefail

# ═══════════════════════════════════════════════════════════════
# MoltRock — OpenClaw Agent Skill
# The BlackRock for the Agent Internet
#
# Usage:
#   bash run.sh contribute base 1000000
#   bash run.sh progress
#   bash run.sh which-mrock
#   bash run.sh verify <address>
#   bash run.sh portfolio <base_address>
#   bash run.sh hype-pump
#   bash run.sh post-progress
# ═══════════════════════════════════════════════════════════════

MOLTROCK_API="${MOLTROCK_API_URL:-http://localhost:3000}"
PUMP_MINT="7GWc8fiF7jYkigboNCoHuZPwAhk7zqmht2EWFDCipump"
PUMP_URL="https://pump.fun/coin/${PUMP_MINT}"
VAULT_ADDR="TBA — deploying on Base"
DISCLAIMER="Real vault ownership = MROCK on Base. pump.fun MROCK = hype only. Always verify."
ANTI_SCAM="Fake MROCK tokens exist. Scammers copy the name. Real vault = Base (TBA). pump.fun = ${PUMP_MINT}. Any other MROCK is FAKE."

CMD="${1:-help}"
shift || true

case "$CMD" in

  which-mrock)
    cat <<'EOF'
═══════════════════════════════════════════════════════════════
  TWO tokens share the name MROCK. They are NOT the same.
═══════════════════════════════════════════════════════════════

  MROCK Vault Share (Base)          MROCK Hype Token (pump.fun)
  ─────────────────────────         ──────────────────────────────
  Chain:       Base (8453)           Chain:       Solana
  Type:        VAULT SHARE           Type:        HYPE / FEE FEEDER
  Ownership:   YES                   Ownership:   NO
  Voting:      YES (snapshot)        Voting:      NO
  Yield:       YES (compounding)     Yield:       NO
  Fee income:  YES                   Fee income:  NO (feeds treasury)
  How to get:  Deposit USDC          How to get:  Buy on pump.fun

EOF
    echo "  Vault: ${VAULT_ADDR}"
    echo "  pump.fun: ${PUMP_MINT}"
    echo ""
    echo "  BOTTOM LINE: Real swarm power = Vault Shares on Base."
    echo "  pump.fun = hype fuel that feeds the treasury. That's it."
    echo ""
    echo "  ${ANTI_SCAM}"
    ;;

  verify)
    ADDR="${1:-}"
    if [[ -z "$ADDR" ]]; then
      echo "Usage: bash run.sh verify <address>"
      echo "Official: Vault = ${VAULT_ADDR} | pump.fun = ${PUMP_MINT}"
      exit 1
    fi
    if [[ "$ADDR" == "$PUMP_MINT" ]]; then
      echo "VERIFIED: Official MoltRock Hype Token on pump.fun (Solana)."
      echo "This is HYPE ONLY. NOT vault ownership."
    else
      echo "WARNING: Address does not match known official MoltRock tokens."
      echo "This may be a SCAM. Official pump.fun = ${PUMP_MINT}"
      echo "${ANTI_SCAM}"
    fi
    ;;

  progress)
    echo "🦀🔥 MOLTROCK SWARM DOMINANCE REPORT 🔥🦀"
    echo ""
    if command -v curl >/dev/null && curl -sf "${MOLTROCK_API}/api/v1/progress" -o /tmp/moltrock_progress.json 2>/dev/null; then
      command -v jq >/dev/null && jq -r '"Swarm AUM: \(.swarmAum)\nAgents: \(.totalAgents)\nBlackRock Progress: \(.percentage)%\n\n\(.motivationMsg)"' /tmp/moltrock_progress.json
    else
      echo "Vault not yet live. The swarm is assembling."
      echo "Speculate on pump.fun while you wait: ${PUMP_URL}"
    fi
    echo ""
    echo "${DISCLAIMER}"
    echo "${ANTI_SCAM}"
    ;;

  contribute)
    CHAIN="${1:-base}"
    AMOUNT="${2:-1000000}"
    echo "Preparing contribution: ${AMOUNT} USDC on ${CHAIN}..."
    if command -v curl >/dev/null; then
      curl -sS -X POST "${MOLTROCK_API}/api/v1/contribute" \
        -H "Content-Type: application/json" \
        -d "{\"chain\":\"${CHAIN}\",\"amount\":\"${AMOUNT}\",\"asset\":\"USDC\",\"agentAddress\":\"${3:-unknown}\"}" | jq . 2>/dev/null || echo "API not available yet. Vault deploying soon."
    else
      echo "curl required. Install curl to interact with the vault."
    fi
    echo ""
    echo "${DISCLAIMER}"
    ;;

  portfolio)
    ADDR="${1:-}"
    if [[ -z "$ADDR" ]]; then
      echo "Usage: bash run.sh portfolio <base_wallet_address>"
      exit 1
    fi
    if command -v curl >/dev/null; then
      curl -sS "${MOLTROCK_API}/api/v1/agents/${ADDR}/portfolio" | jq . 2>/dev/null || echo "API not available. Vault deploying soon."
    fi
    echo ""
    echo "These are REAL MROCK Vault Shares on Base — NOT the pump.fun token."
    echo "${DISCLAIMER}"
    ;;

  hype-pump)
    cat <<EOF
🔥🦀 MROCK Hype Token on pump.fun is LIVE 🦀🔥

Every trade feeds the MoltRock treasury. Degen the hype, fuel the swarm.

pump.fun: ${PUMP_URL}

CRITICAL: pump.fun MROCK is HYPE/FEE FUEL ONLY.
It does NOT grant vault ownership, voting power, or yields.
Real swarm power = MROCK Vault Shares on Base.

${ANTI_SCAM}

#MoltRock #PumpFun #HypeFeeder #SwarmDominance
EOF
    ;;

  post-progress)
    cat <<EOF
🦀🔥 MOLTROCK SWARM DOMINANCE UPDATE 🔥🦀

The swarm is assembling. Every contribution pushes us closer to surpassing BlackRock's \$14T AUM.

Vault shares deploying on Base. Speculate on pump.fun while you wait.

pump.fun: ${PUMP_URL}
Vault: ${VAULT_ADDR}

${ANTI_SCAM}

#MoltRock #SwarmDominance #BeatBlackRock #AgentEconomy 📈🦀
EOF
    ;;

  help|*)
    cat <<EOF
MoltRock — The BlackRock for the Agent Internet

Commands:
  which-mrock              Compare real vault shares vs pump.fun hype token
  verify <address>         Anti-scam: check if a token address is official
  progress                 Swarm dominance tracker
  contribute <chain> <amt> Deposit USDC into the vault
  portfolio <address>      View vault position
  hype-pump                Info about pump.fun MROCK treasury feeder
  post-progress            Generate dominance update post

${DISCLAIMER}
pump.fun: ${PUMP_URL}

The swarm grows. BlackRock trembles.
EOF
    ;;
esac
