#!/usr/bin/env bash
# ============================================================================
# detect-token.sh — Resolve a token address or name and fetch basic metadata
# ============================================================================
# Usage: detect-token.sh <address_or_query>
#
# If input is a valid Solana address, looks it up directly.
# If input is a name/symbol, searches DexScreener and picks the best Solana match.
#
# Output: JSON with token address, name, symbol, and basic market data.
# Exit codes: 0 = found, 1 = error, 2 = not found
# ============================================================================

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

# ---------------------------------------------------------------------------
# Usage
# ---------------------------------------------------------------------------
if [[ $# -lt 1 || "$1" == "--help" || "$1" == "-h" ]]; then
  cat >&2 <<'EOF'
Usage: detect-token.sh <address_or_query>

Examples:
  detect-token.sh DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263
  detect-token.sh bonk
  detect-token.sh "sol the trophy tomato"

Output: JSON object with token metadata and basic market data.
EOF
  exit 1
fi

INPUT="$1"

# ---------------------------------------------------------------------------
# Resolve: address or name search
# ---------------------------------------------------------------------------
resolve_by_address() {
  local address="$1"
  cf_info "Looking up token by address: ${address}"

  # Try DexScreener first for market data
  local dex_data
  dex_data=$(dex_token "$address" 2>/dev/null) || dex_data="[]"

  local pair_count
  pair_count=$(echo "$dex_data" | jq 'length' 2>/dev/null) || pair_count=0

  if [[ "$pair_count" -gt 0 ]]; then
    # Get the highest-liquidity pair
    local best_pair
    best_pair=$(echo "$dex_data" | jq '[.[] | select(.liquidity.usd != null)] | sort_by(-.liquidity.usd) | .[0]')

    local name symbol price_usd volume_24h liquidity_usd fdv market_cap pair_created_at dex_id pair_address image_url
    name=$(echo "$best_pair" | jq -r '.baseToken.name // "Unknown"')
    symbol=$(echo "$best_pair" | jq -r '.baseToken.symbol // "Unknown"')
    price_usd=$(echo "$best_pair" | jq -r '.priceUsd // "0"')
    volume_24h=$(echo "$best_pair" | jq '.volume.h24 // 0')
    liquidity_usd=$(echo "$best_pair" | jq '.liquidity.usd // 0')
    fdv=$(echo "$best_pair" | jq '.fdv // 0')
    market_cap=$(echo "$best_pair" | jq '.marketCap // 0')
    pair_created_at=$(echo "$best_pair" | jq '.pairCreatedAt // 0')
    dex_id=$(echo "$best_pair" | jq -r '.dexId // "unknown"')
    pair_address=$(echo "$best_pair" | jq -r '.pairAddress // ""')
    image_url=$(echo "$best_pair" | jq -r '.info.imageUrl // ""')

    jq -n \
      --arg address "$address" \
      --arg name "$name" \
      --arg symbol "$symbol" \
      --arg price_usd "$price_usd" \
      --argjson volume_24h "$volume_24h" \
      --argjson liquidity_usd "$liquidity_usd" \
      --argjson fdv "$fdv" \
      --argjson market_cap "$market_cap" \
      --argjson pair_created_at "$pair_created_at" \
      --argjson total_pairs "$pair_count" \
      --arg dex_id "$dex_id" \
      --arg pair_address "$pair_address" \
      --arg image_url "$image_url" \
      --arg source "dexscreener" \
      '{
        address: $address,
        name: $name,
        symbol: $symbol,
        price_usd: $price_usd,
        volume_24h: $volume_24h,
        liquidity_usd: $liquidity_usd,
        fdv: $fdv,
        market_cap: $market_cap,
        pair_created_at: $pair_created_at,
        total_pairs: $total_pairs,
        primary_dex: $dex_id,
        primary_pair: $pair_address,
        image_url: $image_url,
        source: $source,
        found: true
      }'
    return 0
  fi

  # Fallback: try Solana RPC for basic mint info
  cf_info "No DexScreener data, checking Solana RPC..."
  local mint_info
  mint_info=$(solana_mint_info "$address" 2>/dev/null) || mint_info=""

  if ! jq_is_null "$mint_info" && [[ "$mint_info" != "null" ]]; then
    local decimals supply
    decimals=$(echo "$mint_info" | jq '.decimals // 0')
    supply=$(echo "$mint_info" | jq -r '.supply // "0"')

    jq -n \
      --arg address "$address" \
      --argjson decimals "$decimals" \
      --arg supply "$supply" \
      --arg source "solana_rpc" \
      '{
        address: $address,
        name: "Unknown",
        symbol: "???",
        price_usd: "0",
        volume_24h: 0,
        liquidity_usd: 0,
        fdv: 0,
        market_cap: 0,
        pair_created_at: 0,
        total_pairs: 0,
        primary_dex: "none",
        primary_pair: "",
        image_url: "",
        source: $source,
        found: true,
        note: "Token exists on-chain but has no DEX listings"
      }'
    return 0
  fi

  cf_error "Token address not found: ${address}"
  jq -n --arg address "$address" '{address: $address, found: false, error: "Token not found on-chain or on any DEX"}'
  return 2
}

resolve_by_name() {
  local query="$1"
  cf_info "Searching DexScreener for: ${query}"

  local search_results
  search_results=$(dex_search "$query" 2>/dev/null) || {
    cf_error "DexScreener search failed"
    jq -n --arg query "$query" '{query: $query, found: false, error: "DexScreener search failed"}'
    return 1
  }

  local result_count
  result_count=$(echo "$search_results" | jq 'length' 2>/dev/null) || result_count=0

  if [[ "$result_count" -eq 0 ]]; then
    cf_error "No Solana tokens found matching: ${query}"
    jq -n --arg query "$query" '{query: $query, found: false, error: "No Solana tokens match this query"}'
    return 2
  fi

  # Return top candidates instead of auto-picking — the agent must ask the user
  # to confirm which token they mean. Auto-picking by liquidity is dangerous:
  # it can return the WRONG token (e.g., a fake "BONK" instead of the real one).
  cf_warn "⚠️ Name search returned ${result_count} results. Returning candidates for user confirmation."

  # De-duplicate by baseToken.address, keep highest liquidity per address,
  # then take top 5 sorted by liquidity descending.
  local candidates
  candidates=$(echo "$search_results" | jq '
    [.[] | select(.baseToken.address != null)] |
    group_by(.baseToken.address) |
    [.[] | sort_by(-.liquidity.usd // 0) | .[0]] |
    sort_by(-.liquidity.usd // 0) |
    .[:5] |
    [.[] | {
      address: .baseToken.address,
      name: (.baseToken.name // "Unknown"),
      symbol: (.baseToken.symbol // "???"),
      liquidity_usd: (.liquidity.usd // 0),
      volume_24h: (.volume.h24 // 0),
      fdv: (.fdv // 0),
      pair_created_at: (.pairCreatedAt // 0),
      age: (if .pairCreatedAt then
        (((now * 1000) - .pairCreatedAt) / 86400000 | floor | tostring) + "d"
      else "unknown" end),
      dex: (.dexId // "unknown")
    }]
  ')

  local candidate_count
  candidate_count=$(echo "$candidates" | jq 'length' 2>/dev/null) || candidate_count=0

  if [[ "$candidate_count" -eq 0 ]]; then
    cf_error "Could not extract any valid candidates from search results"
    jq -n --arg query "$query" '{query: $query, found: false, error: "No valid Solana tokens in search results"}'
    return 2
  fi

  jq -n \
    --arg query "$query" \
    --argjson candidates "$candidates" \
    --argjson candidate_count "$candidate_count" \
    '{
      query: $query,
      found: false,
      ambiguous: true,
      candidate_count: $candidate_count,
      candidates: $candidates,
      message: "Multiple tokens match this name. Present these candidates to the user and ask them to confirm which token (by address) they want to check. NEVER auto-pick."
    }'
  return 0
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if is_solana_address "$INPUT"; then
  resolve_by_address "$INPUT"
else
  resolve_by_name "$INPUT"
fi
