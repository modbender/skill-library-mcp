#!/usr/bin/env bash
# ============================================================================
# format-report.sh — Format risk analysis JSON into a visual Markdown report
# ============================================================================
# Usage: format-report.sh [analysis.json]
#        cat analysis.json | format-report.sh
#
# Reads JSON from analyze-risk.sh (file argument or stdin) and produces
# a screenshotable Markdown report card with Anvil AI branding.
# ============================================================================

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Source shared library; provide local fallbacks if common.sh fails to load
if ! source "${SCRIPT_DIR}/common.sh" 2>/dev/null; then
  # Minimal fallbacks so format-report.sh can still render a report
  format_usd() {
    local val="$1"
    if [[ -z "$val" || "$val" == "0" || "$val" == "null" ]]; then echo "N/A"
    else printf "\$%.2f" "$val" 2>/dev/null || echo "\$$val"; fi
  }
  format_number() { printf "%'.0f" "$1" 2>/dev/null || echo "$1"; }
  format_pct() { printf "%.1f%%" "$1" 2>/dev/null || echo "${1}%"; }
  CF_DISCLAIMER="⚠️ DISCLAIMER: This report is for informational purposes only and does NOT constitute financial advice. Risk scores are algorithmic estimates based on on-chain data. Always do your own research (DYOR) before making investment decisions. CacheForge is not responsible for any financial losses."
fi

# ---------------------------------------------------------------------------
# Read input
# ---------------------------------------------------------------------------
if [[ $# -ge 1 && -f "$1" ]]; then
  INPUT=$(cat "$1")
elif [[ ! -t 0 ]]; then
  INPUT=$(cat)
else
  echo "Usage: format-report.sh [analysis.json]" >&2
  echo "       cat analysis.json | format-report.sh" >&2
  exit 1
fi

# Validate JSON
if ! echo "$INPUT" | jq empty 2>/dev/null; then
  echo "ERROR: Invalid JSON input" >&2
  exit 1
fi

# ---------------------------------------------------------------------------
# Extract fields
# ---------------------------------------------------------------------------
ADDRESS=$(echo "$INPUT" | jq -r '.address')
COMPOSITE=$(echo "$INPUT" | jq -r '.composite_score')
TIER=$(echo "$INPUT" | jq -r '.tier')
TIER_EMOJI=$(echo "$INPUT" | jq -r '.tier_emoji')
TIMESTAMP=$(echo "$INPUT" | jq -r '.timestamp')

TOKEN_NAME=$(echo "$INPUT" | jq -r '.token.name // "Unknown"')
TOKEN_SYMBOL=$(echo "$INPUT" | jq -r '.token.symbol // "???"')
PRICE_USD=$(echo "$INPUT" | jq -r '.token.price_usd // "N/A"')
FDV=$(echo "$INPUT" | jq -r '.token.fdv // 0')
MARKET_CAP=$(echo "$INPUT" | jq -r '.token.market_cap // 0')
VOLUME_24H=$(echo "$INPUT" | jq -r '.token.volume_24h // 0')
# Treat 0 holders as UNKNOWN — Rugcheck returns 0 for many established tokens
_raw_holders=$(echo "$INPUT" | jq -r '.token.total_holders // "N/A"')
if [[ "$_raw_holders" == "0" || "$_raw_holders" == "null" || -z "$_raw_holders" ]]; then
  TOTAL_HOLDERS="N/A"
else
  TOTAL_HOLDERS="$_raw_holders"
fi
TOTAL_LIQUIDITY=$(echo "$INPUT" | jq -r '.token.total_market_liquidity // 0')
RUGGED=$(echo "$INPUT" | jq -r '.token.rugged // false')
DEPLOY_PLATFORM=$(echo "$INPUT" | jq -r '.token.deploy_platform // "unknown"')

# Data source availability
SRC_RUGCHECK=$(echo "$INPUT" | jq -r '.data_sources.rugcheck')
SRC_DEX=$(echo "$INPUT" | jq -r '.data_sources.dexscreener')
SRC_RPC=$(echo "$INPUT" | jq -r '.data_sources.solana_rpc')

# ---------------------------------------------------------------------------
# Format helpers
# ---------------------------------------------------------------------------
# fmt_usd: alias for format_usd from common.sh (consolidated in v0.1.1)
fmt_usd() { format_usd "$@"; }

# Build a text progress bar: ██████░░░░ (for 6/10)
bar() {
  local score="$1"
  local max="${2:-10}"
  local filled=$score
  local empty=$(( max - filled ))
  local bar=""
  for ((i=0; i<filled; i++)); do bar+="█"; done
  for ((i=0; i<empty; i++)); do bar+="░"; done
  echo "$bar"
}

# Risk score color indicator
risk_indicator() {
  local score="$1"
  if [[ $score -le 2 ]]; then echo "🟢"
  elif [[ $score -le 4 ]]; then echo "🟡"
  elif [[ $score -le 6 ]]; then echo "🟠"
  elif [[ $score -le 8 ]]; then echo "🔴"
  else echo "⛔"
  fi
}

# ---------------------------------------------------------------------------
# Build report
# ---------------------------------------------------------------------------
# Dynamically size the box header to fit long token names
_header_line="Token:  \$${TOKEN_SYMBOL} (${TOKEN_NAME})"
_mint_line="Mint:   ${ADDRESS}"
_risk_line="Risk:   ${COMPOSITE}/100 ${TIER_EMOJI} ${TIER}"
_title_line="🛡️  Anvil AI Rug Report"
# Compute the widest content line (add 4 for "║  " + " ║" padding)
_max_len=58  # minimum width
for _line in "$_header_line" "$_mint_line" "$_risk_line" "$_title_line"; do
  _len=${#_line}
  (( _len > _max_len )) && _max_len=$_len
done
_box_w=$(( _max_len + 4 ))

# Build dynamic-width box
_top="╔"; _mid="╠"; _bot="╚"
for ((i=0; i<_box_w; i++)); do _top+="═"; _mid+="═"; _bot+="═"; done
_top+="╗"; _mid+="╣"; _bot+="╝"

printf '%s\n' "$_top"
printf '║  %-*s  ║\n' "$_max_len" "$_title_line"
printf '%s\n' "$_mid"
printf '║  %-*s  ║\n' "$_max_len" "$_header_line"
printf '║  %-*s  ║\n' "$_max_len" "$_mint_line"
printf '║  %-*s  ║\n' "$_max_len" "$_risk_line"
printf '%s\n' "$_bot"

# Rugged banner
if [[ "$RUGGED" == "true" ]]; then
  cat <<'RUGGED'

  ⛔⛔⛔⛔⛔⛔⛔⛔⛔⛔⛔⛔⛔⛔⛔⛔⛔⛔⛔⛔⛔⛔⛔⛔
  ⛔  THIS TOKEN HAS BEEN FLAGGED AS RUGGED  ⛔
  ⛔⛔⛔⛔⛔⛔⛔⛔⛔⛔⛔⛔⛔⛔⛔⛔⛔⛔⛔⛔⛔⛔⛔⛔

RUGGED
fi

# Market overview
cat <<MARKET

## 📊 Market Overview

| Metric | Value |
|--------|-------|
| Price | ${PRICE_USD} |
| Market Cap | $(fmt_usd "$MARKET_CAP") |
| FDV | $(fmt_usd "$FDV") |
| 24h Volume | $(fmt_usd "$VOLUME_24H") |
| Total Liquidity | $(fmt_usd "$TOTAL_LIQUIDITY") |
| Holders | ${TOTAL_HOLDERS} |
| Platform | ${DEPLOY_PLATFORM} |

MARKET

# Risk breakdown
echo "## 🔍 Risk Breakdown"
echo ""

CHECK_COUNT=$(echo "$INPUT" | jq '.checks | length')
for ((i=0; i<CHECK_COUNT; i++)); do
  NAME=$(echo "$INPUT" | jq -r ".checks[$i].name")
  SCORE=$(echo "$INPUT" | jq -r ".checks[$i].score")
  WEIGHT=$(echo "$INPUT" | jq -r ".checks[$i].weight")
  REASON=$(echo "$INPUT" | jq -r ".checks[$i].reason")
  SOURCE=$(echo "$INPUT" | jq -r ".checks[$i].source")
  DETAILS=$(echo "$INPUT" | jq -r ".checks[$i].details // empty")
  DATA_AVAILABLE=$(echo "$INPUT" | jq -r ".checks[$i].data_available // true")

  if [[ "$DATA_AVAILABLE" == "false" ]]; then
    # Distinct visual for "no data" — don't look like a real risk score
    printf '❓ **%-22s** ░░░░░░░░░░  ?/10  (×%.1f)\n' "$NAME" "$WEIGHT"
    printf '   └─ ⚠️ %s\n' "$REASON"
  else
    INDICATOR=$(risk_indicator "$SCORE")
    BAR=$(bar "$SCORE")
    printf '%s **%-22s** %s %2s/10  (×%.1f)\n' "$INDICATOR" "$NAME" "$BAR" "$SCORE" "$WEIGHT"
    printf '   └─ %s\n' "$REASON"
  fi
  if [[ -n "$DETAILS" ]]; then
    printf '   └─ _%s_\n' "$DETAILS"
  fi
  echo ""
done

# Composite score visual
echo "## 📈 Composite Score"
echo ""
echo '```'
# Build a 50-char wide score bar
FILLED=$(( COMPOSITE / 2 ))
EMPTY=$(( 50 - FILLED ))
SCORE_BAR=""
for ((i=0; i<FILLED; i++)); do SCORE_BAR+="█"; done
for ((i=0; i<EMPTY; i++)); do SCORE_BAR+="░"; done
printf '  [%s] %d/100 %s %s\n' "$SCORE_BAR" "$COMPOSITE" "$TIER_EMOJI" "$TIER"
echo ""
echo "  0         20        40        60        80       100"
echo "  |--SAFE---|--CAUTION-|--WARNING-|--DANGER--|CRITICAL|"
echo '```'
echo ""

# Data sources
echo "## 📡 Data Sources"
echo ""
SRC_RC_ICON=$( [[ "$SRC_RUGCHECK" == "true" ]] && echo "✅" || echo "❌" )
SRC_DX_ICON=$( [[ "$SRC_DEX" == "true" ]] && echo "✅" || echo "❌" )
SRC_RP_ICON=$( [[ "$SRC_RPC" == "true" ]] && echo "✅" || echo "❌" )
echo "| Source | Status |"
echo "|--------|--------|"
echo "| Rugcheck.xyz | ${SRC_RC_ICON} |"
echo "| DexScreener  | ${SRC_DX_ICON} |"
echo "| Solana RPC   | ${SRC_RP_ICON} |"
echo ""
echo "_Report generated: ${TIMESTAMP}_"
echo ""

# Links
echo "## 🔗 Links"
echo ""
echo "- [DexScreener](https://dexscreener.com/solana/${ADDRESS})"
echo "- [Rugcheck.xyz](https://rugcheck.xyz/tokens/${ADDRESS})"
echo "- [Solscan](https://solscan.io/token/${ADDRESS})"
echo "- [Birdeye](https://birdeye.so/token/${ADDRESS}?chain=solana)"
echo ""

# Disclaimer
cat <<DISCLAIMER
---

${CF_DISCLAIMER:-⚠️ DISCLAIMER: This report is for informational purposes only and does NOT constitute financial advice. Risk scores are algorithmic estimates based on on-chain data. Always do your own research (DYOR) before making investment decisions. CacheForge is not responsible for any financial losses.}

---

_🛡️ Powered by [Anvil AI](https://anvil-ai.io)_
DISCLAIMER
