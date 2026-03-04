#!/usr/bin/env bash
# Fía Signals — OpenClaw Skill Script v2.0.0
# Free + Premium crypto intelligence for AI agents
# Free endpoints: no auth, no payment. Premium: x402 USDC.
set -euo pipefail

API_BASE="https://api.fiasignals.com"
ACTION="${1:-help}"
ARG2="${2:-}"
ARG3="${3:-}"

fetch() {
    local endpoint="$1"
    local result http_code body
    result=$(curl -s --max-time 20 -w "\n%{http_code}" "${API_BASE}${endpoint}" 2>/dev/null)
    http_code=$(echo "$result" | tail -1)
    body=$(echo "$result" | sed '$d')
    if [[ "$http_code" == "402" ]] || echo "$body" | grep -q "x402 payment required" 2>/dev/null; then
        echo "💰 Premium endpoint — requires x402 USDC payment"
        echo "   Pay via: https://x402.fiasignals.com${endpoint}"
        echo "   Discovery: https://x402.fiasignals.com/.well-known/x402.json"
        echo ""
        echo "$body"
        return 0
    fi
    if [[ "$http_code" != "200" ]]; then
        echo "Error: HTTP $http_code for ${endpoint}" >&2
        echo "$body" >&2
        return 1
    fi
    echo "$body"
}

case "$ACTION" in

    # ═══ FREE ENDPOINTS ═══════════════════════════════════════════════════════

    gas|gas-prices)
        CHAIN="${ARG2:-}"
        if [[ -n "$CHAIN" ]]; then
            fetch "/v1/gas/prices/${CHAIN}"
        else
            fetch "/v1/gas/prices"
        fi
        ;;

    gas-history)
        CHAIN="${ARG2:-ethereum}"
        fetch "/v1/gas/history/${CHAIN}"
        ;;

    trending|solana-trending)
        fetch "/v1/solana/trending"
        ;;

    staking|solana-staking)
        fetch "/v1/solana/staking"
        ;;

    top-wallets)
        fetch "/v1/solana/top-wallets"
        ;;

    mev-bots|bots)
        fetch "/v1/mev/bots"
        ;;

    dd|due-diligence)
        SYM="${ARG2:-BTC}"
        fetch "/v1/dd/quick/${SYM}"
        ;;

    research|topics)
        fetch "/v1/research/topics"
        ;;

    yields|yield-rates)
        fetch "/v1/yield/rates"
        ;;

    health|status)
        fetch "/v1/health"
        ;;

    # ═══ PREMIUM ENDPOINTS (x402 gated) ═══════════════════════════════════════

    new-launches|launches)
        fetch "/v1/solana/new-launches"
        ;;

    new-pools|pools)
        fetch "/v1/solana/new-pools"
        ;;

    smart-money)
        if [[ -n "$ARG2" ]]; then
            fetch "/v1/solana/smart-money/${ARG2}"
        else
            fetch "/v1/solana/smart-money"
        fi
        ;;

    whales)
        fetch "/v1/solana/whales"
        ;;

    solana-yields)
        fetch "/v1/solana/yields"
        ;;

    mev-scan|mev-risk)
        fetch "/v1/mev/scan"
        ;;

    audit|audit-quick)
        ADDR="${ARG2:?Usage: fia_signals.sh audit <contract_address>}"
        fetch "/v1/audit/quick/${ADDR}"
        ;;

    wallet-risk)
        fetch "/v1/wallet/risk"
        ;;

    wallet-profile|wallet)
        ADDR="${ARG2:?Usage: fia_signals.sh wallet <address>}"
        fetch "/v1/wallet/profile/${ADDR}"
        ;;

    # ═══ DISCOVERY ═════════════════════════════════════════════════════════════

    discover|endpoints)
        curl -s --max-time 15 "${API_BASE}/.well-known/x402.json" 2>/dev/null || \
            curl -s --max-time 15 "https://x402.fiasignals.com/.well-known/x402.json" 2>/dev/null
        ;;

    # ═══ HELP ══════════════════════════════════════════════════════════════════

    help|--help|-h)
        cat <<'HELP'
Fía Signals v2.0 — Crypto Intelligence for AI Agents

FREE (no auth needed):
  gas [chain]          Multi-chain gas prices
  gas-history [chain]  Gas price history
  trending             Top 20 trending Solana tokens
  staking              Solana staking rates
  top-wallets          Most active Solana wallets
  mev-bots             Known MEV bot addresses
  dd <symbol>          Quick due diligence (e.g. dd BTC)
  research             Current crypto research topics
  yields               Best DeFi yield rates
  health               API status

PREMIUM (x402 USDC payment):
  new-launches         Newly launched Solana tokens
  new-pools            New liquidity pools
  smart-money [token]  Smart money tracking
  whales               Whale movement alerts
  solana-yields        Solana yield opportunities
  mev-scan             Full MEV risk scan
  audit <address>      Smart contract risk assessment
  wallet <address>     Wallet profile and PnL

DISCOVERY:
  discover             Full endpoint directory

API: https://api.fiasignals.com
x402: https://x402.fiasignals.com/.well-known/x402.json
HELP
        ;;

    *)
        echo "Unknown: '$ACTION'. Run 'help' for usage." >&2
        exit 1
        ;;
esac
