#!/usr/bin/env bash
# ============================================================================
# analyze-risk.sh — Multi-point on-chain risk analysis for Solana tokens
# ============================================================================
# Usage: analyze-risk.sh <token_address>
#
# Runs all available risk checks against a Solana token and outputs a
# structured JSON report with individual scores and a composite risk rating.
#
# Data sources: Rugcheck.xyz API, DexScreener API, Solana RPC
# All read-only. No wallet interactions. No API keys required.
#
# Exit codes: 0 = success, 1 = error, 2 = token not found
# ============================================================================

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

# ---------------------------------------------------------------------------
# Usage
# ---------------------------------------------------------------------------
if [[ $# -lt 1 || "$1" == "--help" || "$1" == "-h" ]]; then
  cat >&2 <<'EOF'
Usage: analyze-risk.sh <token_address>

Runs a comprehensive rug-pull risk analysis on a Solana token.
Output: JSON with individual risk scores and composite rating.
EOF
  exit 1
fi

TOKEN_ADDRESS="$1"

if ! is_solana_address "$TOKEN_ADDRESS"; then
  cf_error "Invalid Solana address: ${TOKEN_ADDRESS}"
  cf_error "Use detect-token.sh first to resolve a name to an address."
  exit 1
fi

# ---------------------------------------------------------------------------
# Data Collection
# ---------------------------------------------------------------------------
cf_info "Analyzing token: ${TOKEN_ADDRESS}"

# --- Rugcheck Report (primary source) ---
cf_info "Fetching Rugcheck report..."
RUGCHECK_DATA=""
RUGCHECK_OK=false
if RUGCHECK_DATA=$(rugcheck_report "$TOKEN_ADDRESS" 2>/dev/null); then
  # Validate we got actual data
  local_score=$(echo "$RUGCHECK_DATA" | jq '.score // empty' 2>/dev/null)
  if [[ -n "$local_score" ]]; then
    RUGCHECK_OK=true
    cf_info "Rugcheck report retrieved (score: ${local_score})"
  else
    cf_warn "Rugcheck returned empty report"
  fi
else
  cf_warn "Rugcheck API unavailable, falling back to on-chain data"
fi

# --- DexScreener Data (market context) ---
cf_info "Fetching DexScreener data..."
DEX_DATA=""
DEX_OK=false
if DEX_DATA=$(dex_token "$TOKEN_ADDRESS" 2>/dev/null); then
  local_count=$(echo "$DEX_DATA" | jq 'length' 2>/dev/null) || local_count=0
  if [[ "$local_count" -gt 0 ]]; then
    DEX_OK=true
    cf_info "DexScreener: ${local_count} pairs found"
  fi
else
  cf_warn "DexScreener API unavailable"
fi

# --- Solana RPC (on-chain verification) ---
cf_info "Fetching on-chain data..."
MINT_DATA=""
MINT_OK=false
if MINT_DATA=$(solana_mint_info "$TOKEN_ADDRESS" 2>/dev/null); then
  if ! jq_is_null "$MINT_DATA" && [[ "$MINT_DATA" != "null" ]]; then
    MINT_OK=true
    cf_info "On-chain mint data retrieved"
  fi
else
  cf_warn "Solana RPC unavailable"
fi

# Check if we have enough data to proceed
if [[ "$RUGCHECK_OK" == "false" && "$DEX_OK" == "false" && "$MINT_OK" == "false" ]]; then
  cf_error "All data sources failed. Cannot analyze token."
  jq -n --arg addr "$TOKEN_ADDRESS" '{
    address: $addr,
    error: "All data sources failed",
    checks: [],
    composite_score: -1,
    tier: "UNKNOWN"
  }'
  exit 1
fi

# ---------------------------------------------------------------------------
# Risk Check Functions
# Each returns: { name, score (0-10), weight, reason, source, details }
# Score: 0 = safe, 10 = maximum risk
# ---------------------------------------------------------------------------

CHECKS="[]"

add_check() {
  local name="$1" score="$2" weight="$3" reason="$4" source="$5" details="${6:-}" data_available="${7:-true}"
  CHECKS=$(echo "$CHECKS" | jq \
    --arg name "$name" \
    --argjson score "$score" \
    --argjson weight "$weight" \
    --arg reason "$reason" \
    --arg source "$source" \
    --arg details "$details" \
    --argjson data_available "$data_available" \
    '. + [{name: $name, score: $score, weight: $weight, reason: $reason, source: $source, details: $details, data_available: $data_available}]')
}

# --- Check 1: Mint Authority ---
check_mint_authority() {
  local score=0 reason="" source="unknown"

  # Check Rugcheck first, then verify with on-chain data
  local mint_auth="null"

  if [[ "$RUGCHECK_OK" == "true" ]]; then
    mint_auth=$(echo "$RUGCHECK_DATA" | jq -r '.mintAuthority // "null"')
    source="rugcheck"
  fi

  # Cross-check with on-chain data (more authoritative)
  if [[ "$MINT_OK" == "true" ]]; then
    local onchain_mint_auth
    onchain_mint_auth=$(echo "$MINT_DATA" | jq -r '.mintAuthority // "null"')
    if [[ "$onchain_mint_auth" != "null" && -n "$onchain_mint_auth" ]]; then
      mint_auth="$onchain_mint_auth"
      source="solana_rpc"
    fi
  fi

  if [[ "$mint_auth" == "null" || -z "$mint_auth" ]]; then
    score=0
    reason="Mint authority revoked — no new tokens can be created"
  else
    score=10
    reason="Mint authority ACTIVE (${mint_auth:0:8}…) — creator can mint unlimited tokens"
  fi

  if [[ "$source" == "unknown" ]]; then
    score=5
    reason="Could not verify mint authority — NO DATA"
    source="none"
    add_check "Mint Authority" "$score" 2.0 "$reason" "$source" "" "false"
    return
  fi

  # Weight: 2.0 — most critical rug vector
  add_check "Mint Authority" "$score" 2.0 "$reason" "$source"
}

# --- Check 2: Freeze Authority ---
check_freeze_authority() {
  local score=0 reason="" source="unknown"

  local freeze_auth="null"

  if [[ "$RUGCHECK_OK" == "true" ]]; then
    freeze_auth=$(echo "$RUGCHECK_DATA" | jq -r '.freezeAuthority // "null"')
    source="rugcheck"
  fi

  # Cross-check with on-chain data (more authoritative)
  if [[ "$MINT_OK" == "true" ]]; then
    local onchain_freeze_auth
    onchain_freeze_auth=$(echo "$MINT_DATA" | jq -r '.freezeAuthority // "null"')
    if [[ "$onchain_freeze_auth" != "null" && -n "$onchain_freeze_auth" ]]; then
      freeze_auth="$onchain_freeze_auth"
      source="solana_rpc"
    fi
  fi

  if [[ "$freeze_auth" == "null" || -z "$freeze_auth" ]]; then
    score=0
    reason="No freeze authority — tokens cannot be frozen"
  else
    score=9
    reason="Freeze authority ACTIVE (${freeze_auth:0:8}…) — holder tokens can be frozen"
  fi

  if [[ "$source" == "unknown" ]]; then
    score=5
    reason="Could not verify freeze authority — NO DATA"
    source="none"
    add_check "Freeze Authority" "$score" 1.5 "$reason" "$source" "" "false"
    return
  fi

  # Weight: 1.5 — very serious (honeypot enabler)
  add_check "Freeze Authority" "$score" 1.5 "$reason" "$source"
}

# --- Check 3: Top Holder Concentration ---
check_holder_concentration() {
  local score=0 reason="" source="unknown" details=""

  if [[ "$RUGCHECK_OK" == "true" ]]; then
    source="rugcheck"
    local top10_pct
    top10_pct=$(echo "$RUGCHECK_DATA" | jq '[(.topHolders // [])[:10][] | .pct] | add // 0')
    local top1_pct
    top1_pct=$(echo "$RUGCHECK_DATA" | jq '(.topHolders // [])[0].pct // 0')
    local total_holders
    total_holders=$(echo "$RUGCHECK_DATA" | jq '.totalHolders // 0')
    local holder_count
    holder_count=$(echo "$RUGCHECK_DATA" | jq '(.topHolders // []) | length')

    # Format percentages for display
    local top10_fmt top1_fmt
    top10_fmt=$(printf "%.1f" "$top10_pct" 2>/dev/null || echo "$top10_pct")
    top1_fmt=$(printf "%.1f" "$top1_pct" 2>/dev/null || echo "$top1_pct")
    details="Top 10: ${top10_fmt}%, Top 1: ${top1_fmt}%, Total: $(format_number "$total_holders")"

    # Handle case where topHolders data is empty/unavailable
    if [[ "$holder_count" -eq 0 ]]; then
      # totalHolders=0 from Rugcheck is almost always a data gap, not reality.
      # Established tokens (e.g. BONK) often return 0 here. Treat as UNKNOWN.
      if [[ "$total_holders" -le 0 ]]; then
        score=5
        reason="Holder data unavailable — NO DATA (Rugcheck returned 0 holders, likely a data gap)"
        details="Top 10: N/A, Top 1: N/A, Total: N/A"
        add_check "Holder Concentration" "$score" 1.5 "$reason" "$source" "$details" "false"
        return
      elif [[ "$total_holders" -le 5 ]]; then
        score=9
        reason="Only ${total_holders} holder(s) — extreme concentration risk (no holder breakdown available)"
      else
        score=5
        reason="Holder breakdown unavailable — NO DATA (${total_holders} holders reported but no breakdown)"
        add_check "Holder Concentration" "$score" 1.5 "$reason" "$source" "$details" "false"
        return
      fi
    elif (( $(echo "$top10_pct > 80" | bc -l 2>/dev/null || echo 0) )); then
      score=10
      reason="Extreme concentration — top 10 hold ${top10_fmt}% of supply"
    elif (( $(echo "$top10_pct > 50" | bc -l 2>/dev/null || echo 0) )); then
      score=7
      reason="High concentration — top 10 hold ${top10_fmt}% of supply"
    elif (( $(echo "$top10_pct > 30" | bc -l 2>/dev/null || echo 0) )); then
      score=4
      reason="Moderate concentration — top 10 hold ${top10_fmt}% of supply"
    elif (( $(echo "$top10_pct > 15" | bc -l 2>/dev/null || echo 0) )); then
      score=2
      reason="Healthy distribution — top 10 hold ${top10_fmt}% of supply"
    else
      score=0
      reason="Well distributed — top 10 hold only ${top10_fmt}% of supply"
    fi
  else
    score=5
    reason="Holder data unavailable — NO DATA"
    source="none"
    add_check "Holder Concentration" "$score" 1.5 "$reason" "$source" "$details" "false"
    return
  fi

  # Weight: 1.5
  add_check "Holder Concentration" "$score" 1.5 "$reason" "$source" "$details"
}

# --- Check 4: LP Lock Status ---
check_lp_locked() {
  local score=0 reason="" source="unknown" details=""

  if [[ "$RUGCHECK_OK" == "true" ]]; then
    source="rugcheck"

    # Get the best LP lock percentage across all markets
    local best_lp_pct
    best_lp_pct=$(echo "$RUGCHECK_DATA" | jq '[(.markets // [])[]? | .lp.lpLockedPct // 0] | max // 0')
    local total_liq
    total_liq=$(echo "$RUGCHECK_DATA" | jq '.totalMarketLiquidity // 0')
    local market_count
    market_count=$(echo "$RUGCHECK_DATA" | jq '(.markets // []) | length')

    details="Best LP lock: $(format_pct "$best_lp_pct"), Markets: ${market_count}, Liquidity: \$$(printf '%.0f' "$total_liq")"

    if [[ "$market_count" -eq 0 ]]; then
      score=5
      reason="No DEX market data available — LP lock status NO DATA"
      add_check "LP Lock Status" "$score" 2.0 "$reason" "$source" "$details" "false"
      return
    elif (( $(echo "$best_lp_pct >= 95" | bc -l 2>/dev/null || echo 0) )); then
      score=0
      reason="LP strongly locked ($(format_pct "$best_lp_pct")) — liquidity pull very unlikely"
    elif (( $(echo "$best_lp_pct >= 80" | bc -l 2>/dev/null || echo 0) )); then
      score=2
      reason="LP mostly locked ($(format_pct "$best_lp_pct"))"
    elif (( $(echo "$best_lp_pct >= 50" | bc -l 2>/dev/null || echo 0) )); then
      score=5
      reason="LP partially locked ($(format_pct "$best_lp_pct")) — some risk of pull"
    elif (( $(echo "$best_lp_pct > 0" | bc -l 2>/dev/null || echo 0) )); then
      score=7
      reason="LP barely locked ($(format_pct "$best_lp_pct")) — high rug risk"
    else
      score=9
      reason="LP NOT locked (0%) — liquidity can be pulled at any time"
    fi
  else
    score=5
    reason="LP lock status unavailable — NO DATA"
    source="none"
    add_check "LP Lock Status" "$score" 2.0 "$reason" "$source" "$details" "false"
    return
  fi

  # Weight: 2.0 — THE classic rug mechanism
  add_check "LP Lock Status" "$score" 2.0 "$reason" "$source" "$details"
}

# --- Check 5: Token Age ---
check_token_age() {
  local score=0 reason="" source="unknown" details=""

  local created_at=0
  if [[ "$DEX_OK" == "true" ]]; then
    source="dexscreener"
    created_at=$(echo "$DEX_DATA" | jq '[.[].pairCreatedAt // 0] | min | select(. > 0) // 0')
  fi

  if [[ "$created_at" -gt 0 ]]; then
    local now_ms
    now_ms=$(( $(date +%s) * 1000 ))
    local age_hours=$(( (now_ms - created_at) / 3600000 ))
    local age_days=$(( age_hours / 24 ))

    details="Created: $(epoch_ms_to_date "$created_at"), Age: $(epoch_ms_to_age "$created_at")"

    if [[ $age_hours -lt 1 ]]; then
      score=10
      reason="Extremely new (<1 hour) — maximum risk period"
    elif [[ $age_hours -lt 24 ]]; then
      score=8
      reason="Very new (<24 hours) — most rugs happen in first day"
    elif [[ $age_days -lt 7 ]]; then
      score=6
      reason="New token (<7 days) — still in high-risk window"
    elif [[ $age_days -lt 30 ]]; then
      score=4
      reason="Relatively new (${age_days} days) — building track record"
    elif [[ $age_days -lt 180 ]]; then
      score=2
      reason="Established (${age_days} days)"
    else
      score=0
      reason="Mature token (${age_days} days / $(( age_days / 365 ))+ years)"
    fi
  else
    score=5
    reason="Token age unknown — NO DATA (no DEX listing found)"
    source="none"
    add_check "Token Age" "$score" 1.0 "$reason" "$source" "$details" "false"
    return
  fi

  # Weight: 1.0
  add_check "Token Age" "$score" 1.0 "$reason" "$source" "$details"
}

# --- Check 6: Liquidity Depth ---
check_liquidity() {
  local score=0 reason="" source="unknown" details=""

  local liquidity_usd=0 fdv=0
  if [[ "$DEX_OK" == "true" ]]; then
    source="dexscreener"
    liquidity_usd=$(echo "$DEX_DATA" | jq '[.[].liquidity.usd // 0] | add')
    fdv=$(echo "$DEX_DATA" | jq '[.[].fdv // 0] | max')
  fi

  if [[ "$RUGCHECK_OK" == "true" ]]; then
    local rc_liq
    rc_liq=$(echo "$RUGCHECK_DATA" | jq '.totalMarketLiquidity // 0')
    if (( $(echo "$rc_liq > $liquidity_usd" | bc -l 2>/dev/null || echo 0) )); then
      liquidity_usd="$rc_liq"
      source="rugcheck"
    fi
  fi

  details="Liquidity: \$$(printf '%.0f' "$liquidity_usd"), FDV: \$$(printf '%.0f' "$fdv")"

  if (( $(echo "$liquidity_usd < 1000" | bc -l 2>/dev/null || echo 0) )); then
    score=10
    reason="Negligible liquidity (<\$1K) — virtually untradeable"
  elif (( $(echo "$liquidity_usd < 10000" | bc -l 2>/dev/null || echo 0) )); then
    score=8
    reason="Very low liquidity (<\$10K) — extreme slippage, easy to manipulate"
  elif (( $(echo "$liquidity_usd < 50000" | bc -l 2>/dev/null || echo 0) )); then
    score=6
    reason="Low liquidity (<\$50K) — significant price impact on sells"
  elif (( $(echo "$liquidity_usd < 250000" | bc -l 2>/dev/null || echo 0) )); then
    score=3
    reason="Moderate liquidity (\$$(printf '%.0f' "$liquidity_usd"))"
  elif (( $(echo "$liquidity_usd < 1000000" | bc -l 2>/dev/null || echo 0) )); then
    score=1
    reason="Good liquidity (\$$(printf '%.0f' "$liquidity_usd"))"
  else
    score=0
    reason="Strong liquidity (\$$(printf '%.0f' "$liquidity_usd"))"
  fi

  # Check liquidity-to-FDV ratio if both available
  if (( $(echo "$fdv > 0 && $liquidity_usd > 0" | bc -l 2>/dev/null || echo 0) )); then
    local ratio
    ratio=$(echo "scale=4; $liquidity_usd / $fdv * 100" | bc -l 2>/dev/null || echo "0")
    local ratio_fmt
    ratio_fmt=$(printf "%.2f" "$ratio" 2>/dev/null || echo "$ratio")
    details="${details}, Liq/FDV: ${ratio_fmt}%"
    if (( $(echo "$ratio < 1" | bc -l 2>/dev/null || echo 0) )); then
      score=$(( score > 7 ? score : 7 ))
      reason="${reason} | Liq/FDV ratio critically low (${ratio_fmt}%)"
    fi
  fi

  # Weight: 1.0
  add_check "Liquidity Depth" "$score" 1.0 "$reason" "$source" "$details"
}

# --- Check 7: Rugcheck Risk Flags ---
check_rugcheck_flags() {
  if [[ "$RUGCHECK_OK" != "true" ]]; then
    add_check "Rugcheck Flags" 5 0.5 "Rugcheck data unavailable — NO DATA" "none" "" "false"
    return
  fi

  local source="rugcheck"
  local risk_count
  risk_count=$(echo "$RUGCHECK_DATA" | jq '(.risks // []) | length')
  local rugged
  rugged=$(echo "$RUGCHECK_DATA" | jq -r '.rugged // false')

  if [[ "$rugged" == "true" ]]; then
    add_check "Rugcheck Flags" 10 2.0 "⛔ TOKEN FLAGGED AS RUGGED by Rugcheck.xyz" "$source" "Confirmed rug-pull"
    return
  fi

  local risk_names
  risk_names=$(echo "$RUGCHECK_DATA" | jq -r '[(.risks // [])[]? | .name] | join(", ")' 2>/dev/null || echo "")
  local risk_total_score
  risk_total_score=$(echo "$RUGCHECK_DATA" | jq '[(.risks // [])[]? | .score] | add // 0')
  local has_danger
  has_danger=$(echo "$RUGCHECK_DATA" | jq '[(.risks // [])[]? | select(.level == "danger")] | length')

  local score=0 reason=""
  local details="Flags: ${risk_names:-none}"

  if [[ "$risk_count" -eq 0 ]]; then
    score=0
    reason="No risk flags detected by Rugcheck"
  elif [[ "$has_danger" -gt 0 ]]; then
    score=8
    reason="${risk_count} risk flag(s) including DANGER level: ${risk_names}"
  elif [[ "$risk_count" -ge 3 ]]; then
    score=6
    reason="${risk_count} risk flags: ${risk_names}"
  elif [[ "$risk_count" -ge 1 ]]; then
    score=3
    reason="${risk_count} risk flag(s): ${risk_names}"
  fi

  # Weight: 1.0
  add_check "Rugcheck Flags" "$score" 1.0 "$reason" "$source" "$details"
}

# --- Check 8: Insider Detection ---
check_insiders() {
  if [[ "$RUGCHECK_OK" != "true" ]]; then
    add_check "Insider Activity" 5 0.5 "Insider detection unavailable — NO DATA" "none" "" "false"
    return
  fi

  local source="rugcheck"
  local insiders_detected
  insiders_detected=$(echo "$RUGCHECK_DATA" | jq '.graphInsidersDetected // 0')
  local insider_networks
  insider_networks=$(echo "$RUGCHECK_DATA" | jq '(.insiderNetworks // []) | length' 2>/dev/null || echo "0")

  local score=0 reason=""
  local details="Insider networks: ${insider_networks}, Insiders detected: ${insiders_detected}"

  if [[ "$insiders_detected" -gt 10 ]]; then
    score=10
    reason="Significant insider activity detected (${insiders_detected} insiders in ${insider_networks} networks)"
  elif [[ "$insiders_detected" -gt 3 ]]; then
    score=7
    reason="Insider activity detected (${insiders_detected} insiders)"
  elif [[ "$insiders_detected" -gt 0 ]]; then
    score=4
    reason="Minor insider activity (${insiders_detected} insiders)"
  else
    score=0
    reason="No insider networks detected"
  fi

  # Weight: 1.5
  add_check "Insider Activity" "$score" 1.5 "$reason" "$source" "$details"
}

# --- Check 9: Transfer Fee / Tax ---
check_transfer_fee() {
  if [[ "$RUGCHECK_OK" != "true" ]]; then
    add_check "Transfer Fee" 5 0.5 "Transfer fee data unavailable — NO DATA" "none" "" "false"
    return
  fi

  local source="rugcheck"
  local fee_pct
  fee_pct=$(echo "$RUGCHECK_DATA" | jq '.transferFee.pct // 0')

  local score=0 reason=""

  if (( $(echo "$fee_pct > 10" | bc -l 2>/dev/null || echo 0) )); then
    score=10
    reason="Extremely high transfer fee (${fee_pct}%) — likely honeypot"
  elif (( $(echo "$fee_pct > 5" | bc -l 2>/dev/null || echo 0) )); then
    score=8
    reason="High transfer fee (${fee_pct}%) — significant tax on trades"
  elif (( $(echo "$fee_pct > 1" | bc -l 2>/dev/null || echo 0) )); then
    score=4
    reason="Transfer fee of ${fee_pct}%"
  elif (( $(echo "$fee_pct > 0" | bc -l 2>/dev/null || echo 0) )); then
    score=2
    reason="Small transfer fee (${fee_pct}%)"
  else
    score=0
    reason="No transfer fee"
  fi

  # Weight: 1.0
  add_check "Transfer Fee" "$score" 1.0 "$reason" "$source" "Fee: ${fee_pct}%"
}

# --- Check 10: Verification Status ---
check_verification() {
  if [[ "$RUGCHECK_OK" != "true" ]]; then
    add_check "Verification" 5 0.5 "Verification data unavailable — NO DATA" "none" "" "false"
    return
  fi

  local source="rugcheck"
  local jup_verified jup_strict
  jup_verified=$(echo "$RUGCHECK_DATA" | jq -r '.verification.jup_verified // false')
  jup_strict=$(echo "$RUGCHECK_DATA" | jq -r '.verification.jup_strict // false')

  local score=0 reason=""
  local details="Jupiter verified: ${jup_verified}, Jupiter strict: ${jup_strict}"

  if [[ "$jup_strict" == "true" ]]; then
    score=0
    reason="Jupiter strict-listed — highest verification tier"
  elif [[ "$jup_verified" == "true" ]]; then
    score=1
    reason="Jupiter verified (not strict-listed)"
  else
    score=4
    reason="Not verified on Jupiter — unvetted token"
  fi

  # Weight: 0.5 (informational, less direct risk indicator)
  add_check "Verification" "$score" 0.5 "$reason" "$source" "$details"
}

# ---------------------------------------------------------------------------
# Run all checks
# ---------------------------------------------------------------------------
cf_info "Running risk checks..."
check_mint_authority
check_freeze_authority
check_holder_concentration
check_lp_locked
check_token_age
check_liquidity
check_rugcheck_flags
check_insiders
check_transfer_fee
check_verification

# ---------------------------------------------------------------------------
# Compute composite score
# ---------------------------------------------------------------------------
# Weighted average of (score * weight), normalized to 0-100.
# Checks with data_available=false use weight=0 so missing data doesn't
# inflate or deflate the composite score. Only real data contributes.
COMPOSITE=$(echo "$CHECKS" | jq '
  [.[] | if .data_available == false then .weight = 0 else . end] |
  (map(.score * .weight) | add) as $weighted_sum |
  (map(10 * .weight) | add) as $max_possible |
  if $max_possible > 0 then ($weighted_sum / $max_possible * 100 | round) else 0 end
')

# ---------------------------------------------------------------------------
# CRITICAL OVERRIDE: Confirmed rugs MUST be CRITICAL tier
# A token flagged as rugged=true by Rugcheck.xyz must NEVER score below 85
# or appear as anything other than CRITICAL. The weighted average can dilute
# a single check's score — this hard override prevents that.
# ---------------------------------------------------------------------------
RUGGED_OVERRIDE=false
if [[ "$RUGCHECK_OK" == "true" ]]; then
  RUGGED_FLAG=$(echo "$RUGCHECK_DATA" | jq -r '.rugged // false')
  if [[ "$RUGGED_FLAG" == "true" ]]; then
    RUGGED_OVERRIDE=true
    if [[ "$COMPOSITE" -lt 85 ]]; then
      cf_warn "⛔ RUGGED OVERRIDE: Composite score ${COMPOSITE} forced to 85 — token flagged as RUGGED by Rugcheck.xyz"
      COMPOSITE=85
    fi
  fi
fi

# Determine risk tier
TIER=$(
  if [[ "$RUGGED_OVERRIDE" == "true" ]]; then echo "CRITICAL"
  elif [[ "$COMPOSITE" -le 15 ]]; then echo "SAFE"
  elif [[ "$COMPOSITE" -le 35 ]]; then echo "CAUTION"
  elif [[ "$COMPOSITE" -le 55 ]]; then echo "WARNING"
  elif [[ "$COMPOSITE" -le 75 ]]; then echo "DANGER"
  else echo "CRITICAL"
  fi
)

TIER_EMOJI=$(
  case "$TIER" in
    SAFE)     echo "🟢" ;;
    CAUTION)  echo "🟡" ;;
    WARNING)  echo "🟠" ;;
    DANGER)   echo "🔴" ;;
    CRITICAL) echo "⛔" ;;
    *)        echo "❓" ;;
  esac
)

# ---------------------------------------------------------------------------
# Build token metadata section
# ---------------------------------------------------------------------------
TOKEN_META="{}"
if [[ "$RUGCHECK_OK" == "true" ]]; then
  TOKEN_META=$(echo "$RUGCHECK_DATA" | jq '{
    name: (.tokenMeta.name // .verification.name // "Unknown"),
    symbol: (.tokenMeta.symbol // .verification.symbol // "???"),
    creator: .creator,
    deploy_platform: .deployPlatform,
    total_holders: .totalHolders,
    total_lp_providers: .totalLPProviders,
    total_market_liquidity: .totalMarketLiquidity,
    rugcheck_score: .score,
    rugcheck_normalized: .score_normalised,
    rugged: .rugged
  }')
fi

if [[ "$DEX_OK" == "true" ]]; then
  local_dex_meta=$(echo "$DEX_DATA" | jq '
    [.[] | select(.liquidity.usd != null)] | sort_by(-.liquidity.usd) | .[0] // {} |
    {
      dex_name: .baseToken.name,
      dex_symbol: .baseToken.symbol,
      price_usd: .priceUsd,
      volume_24h: .volume.h24,
      fdv: .fdv,
      market_cap: .marketCap,
      primary_dex: .dexId,
      pair_created_at: .pairCreatedAt
    }')
  TOKEN_META=$(echo "$TOKEN_META" "$local_dex_meta" | jq -s '
    .[0] * .[1] |
    # Fall back to DexScreener name/symbol if Rugcheck returned Unknown/???
    if (.name == "Unknown" or .name == null or .name == "") and .dex_name != null then .name = .dex_name else . end |
    if (.symbol == "???" or .symbol == null or .symbol == "") and .dex_symbol != null then .symbol = .dex_symbol else . end |
    del(.dex_name, .dex_symbol)
  ')
fi

# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------
cf_info "Analysis complete. Risk: ${TIER} (${COMPOSITE}/100)"

jq -n \
  --arg address "$TOKEN_ADDRESS" \
  --argjson token_meta "$TOKEN_META" \
  --argjson checks "$CHECKS" \
  --argjson composite "$COMPOSITE" \
  --arg tier "$TIER" \
  --arg tier_emoji "$TIER_EMOJI" \
  --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --arg rugcheck_available "$RUGCHECK_OK" \
  --arg dex_available "$DEX_OK" \
  --arg onchain_available "$MINT_OK" \
  '{
    address: $address,
    token: $token_meta,
    checks: $checks,
    composite_score: $composite,
    tier: $tier,
    tier_emoji: $tier_emoji,
    timestamp: $timestamp,
    data_sources: {
      rugcheck: ($rugcheck_available == "true"),
      dexscreener: ($dex_available == "true"),
      solana_rpc: ($onchain_available == "true")
    }
  }'
