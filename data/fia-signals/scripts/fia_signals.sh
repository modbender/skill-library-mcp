#!/usr/bin/env bash
# Fía Signals — OpenClaw Skill Script
# Fetches real-time crypto market intelligence from x402.fiasignals.com
# Usage: fia_signals.sh <action> [symbol]

set -euo pipefail

API_BASE="https://x402.fiasignals.com"
ACTION="${1:-regime}"
SYMBOL="${2:-BTCUSDT}"

fetch() {
    local endpoint="$1"
    local http_code result
    result=$(curl -s --max-time 10 -w "\n%{http_code}" "${API_BASE}${endpoint}" 2>/dev/null)
    http_code=$(echo "$result" | tail -1)
    body=$(echo "$result" | head -1)
    if [[ "$http_code" == "402" ]]; then
        echo "⚠️  This endpoint requires payment (0.001-0.005 USDC via x402)"
        echo "   Discovery: ${API_BASE}/preview"
        echo "   Full docs: ${API_BASE}/.well-known/x402.json"
        exit 0
    fi
    if [[ "$http_code" != "200" ]]; then
        echo "Error: API returned HTTP $http_code for ${endpoint}" >&2
        exit 1
    fi
    echo "$body"
}

format_regime() {
    local data="$1"
    echo "$data" | python3 -c "
import json, sys
d = json.load(sys.stdin)
print(f\"Market Regime: {d.get('regime', 'Unknown')}\")
print(f\"Confidence: {d.get('confidence', 'Unknown')}\")
print(f\"RSI: {d.get('rsi', 'N/A')}\")
print(f\"ADX: {d.get('adx', 'N/A')}\")
print(f\"Recommendation: {d.get('recommendation', 'N/A')}\")
" 2>/dev/null || echo "$data"
}

format_fear_greed() {
    local data="$1"
    echo "$data" | python3 -c "
import json, sys
d = json.load(sys.stdin)
print(f\"Fear & Greed: {d.get('fear_greed_index', 'N/A')} — {d.get('classification', '')}\")
print(f\"Trend: {d.get('trend', 'N/A')}\")
print(f\"Signal: {d.get('signal', 'N/A')}\")
" 2>/dev/null || echo "$data"
}

format_signals() {
    local data="$1"
    echo "$data" | python3 -c "
import json, sys
d = json.load(sys.stdin)
print(f\"Symbol: {d.get('symbol', 'N/A')} @ \${d.get('price', 'N/A'):,.2f}\")
print(f\"RSI-14: {d.get('rsi_14', 'N/A')} ({d.get('rsi_signal', '')})\")
macd = d.get('macd', {})
print(f\"MACD: {macd.get('histogram', 'N/A')} ({macd.get('signal', '')})\")
bb = d.get('bollinger_bands', {})
print(f\"Bollinger %B: {bb.get('pct_b', 'N/A')} ({bb.get('signal', '')})\")
print(f\"Composite Signal: {d.get('composite_signal', 'N/A')}\")
" 2>/dev/null || echo "$data"
}

format_funding() {
    local data="$1"
    echo "$data" | python3 -c "
import json, sys
d = json.load(sys.stdin)
rates = d.get('funding_rates', d) if isinstance(d, dict) else d
if isinstance(rates, list):
    print('Top Funding Rates:')
    for r in rates[:5]:
        sym = r.get('symbol', r.get('s', '?'))
        rate = r.get('fundingRate', r.get('rate', '?'))
        print(f'  {sym}: {float(rate)*100:.4f}%')
else:
    print(json.dumps(d, indent=2))
" 2>/dev/null || echo "$data"
}

format_prices() {
    local data="$1"
    echo "$data" | python3 -c "
import json, sys
d = json.load(sys.stdin)
prices = d.get('prices', d) if isinstance(d, dict) else d
if isinstance(prices, dict):
    for sym, price in list(prices.items())[:10]:
        print(f'  {sym}: \${float(price):,.2f}')
elif isinstance(prices, list):
    for p in prices[:10]:
        print(f\"  {p.get('symbol','?')}: \${float(p.get('price', 0)):,.2f}\")
else:
    print(json.dumps(d, indent=2))
" 2>/dev/null || echo "$data"
}

case "$ACTION" in
    regime)
        echo "=== Fía Signals — Market Regime ==="
        data=$(fetch "/regime")
        format_regime "$data"
        ;;
    fear-greed|fg|feargreed)
        echo "=== Fía Signals — Fear & Greed ==="
        data=$(fetch "/fear-greed")
        format_fear_greed "$data"
        ;;
    signals|technical|ta)
        echo "=== Fía Signals — Technical Signals: ${SYMBOL} ==="
        data=$(fetch "/signals?symbol=${SYMBOL}")
        format_signals "$data"
        ;;
    funding|rates)
        echo "=== Fía Signals — Funding Rates ==="
        data=$(fetch "/funding")
        format_funding "$data"
        ;;
    prices|price)
        echo "=== Fía Signals — Prices ==="
        SYMBOLS="${SYMBOL//,/%2C}"
        data=$(fetch "/prices?symbols=${SYMBOLS}")
        format_prices "$data"
        ;;
    dominance|dom)
        echo "=== Fía Signals — Market Dominance ==="
        fetch "/dominance"
        ;;
    liquidations|liq)
        echo "=== Fía Signals — Recent Liquidations ==="
        fetch "/liquidations"
        ;;
    altseason|alt)
        echo "=== Fía Signals — Altseason Index ==="
        fetch "/altseason"
        ;;
    macro)
        echo "=== Fía Signals — Macro Signal Bundle ==="
        fetch "/macro"
        ;;


    preview|info)
        echo "=== Fía Signals — Free Preview ==="
        curl -s "${API_BASE}/preview" | python3 -c "
import json, sys
d = json.load(sys.stdin)
r = d.get('preview', {}).get('regime', {})
fg = d.get('preview', {}).get('fear_greed', {})
print('Regime:', r.get('regime', '?'), '| RSI:', r.get('rsi', '?'), '| ADX:', r.get('adx', '?'))
print('Fear & Greed:', fg.get('value', '?'), '-', fg.get('classification', '?'))
print('Paid endpoints:', len(d.get('paid_endpoints', [])))
print('Discovery:', d.get('discovery', ''))
"
        ;;
    help|--help|-h)
        echo "Fía Signals Skill — Available actions:"
        echo "  regime       — Market regime (TRENDING UP/DOWN/RANGING)"
        echo "  fear-greed   — Fear & Greed index with contrarian signal"
        echo "  signals [SYM]— RSI, MACD, Bollinger Bands (default: BTCUSDT)"
        echo "  funding      — Top funding rates"
        echo "  prices [SYMS]— Spot prices (comma-separated)"
        echo "  dominance    — BTC/ETH market dominance"
        echo "  liquidations — Recent liquidation events"
        echo "  altseason    — Alt season index"
        echo "  macro        — Cross-asset macro signals"
        ;;
    *)
        echo "Unknown action: $ACTION. Run with 'help' for usage."
        exit 1
        ;;
esac
