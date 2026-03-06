#!/bin/bash
# Parallel batch data fetching for cron tasks
# Usage: bash batch_fetch.sh [profile]
# Profiles: closing (收盘), daily (日报), weekly (周报), morning (晨报), macro

PYTHON=python3
QUANT=$(dirname "$0")/quant.py
OUT=/tmp/quant_batch_$$
mkdir -p "$OUT"

profile=${1:-closing}

case "$profile" in
  closing)
    $PYTHON "$QUANT" stock_analysis > "$OUT/stock.json" 2>/dev/null &
    $PYTHON "$QUANT" northbound_flow > "$OUT/northbound.json" 2>/dev/null &
    $PYTHON "$QUANT" market_anomaly > "$OUT/anomaly.json" 2>/dev/null &
    $PYTHON "$QUANT" news_sentiment > "$OUT/news.json" 2>/dev/null &
    $PYTHON "$QUANT" gold_analysis > "$OUT/gold.json" 2>/dev/null &
    $PYTHON "$QUANT" margin_data > "$OUT/margin.json" 2>/dev/null &
    $PYTHON "$QUANT" lhb > "$OUT/lhb.json" 2>/dev/null &
    $PYTHON "$QUANT" top_amount > "$OUT/top_amount.json" 2>/dev/null &
    $PYTHON "$QUANT" save_daily > "$OUT/save.json" 2>/dev/null &
    ;;
  daily)
    $PYTHON "$QUANT" stock_analysis > "$OUT/stock.json" 2>/dev/null &
    $PYTHON "$QUANT" northbound_flow > "$OUT/northbound.json" 2>/dev/null &
    $PYTHON "$QUANT" global_overview > "$OUT/global.json" 2>/dev/null &
    ;;
  weekly)
    $PYTHON "$QUANT" stock_analysis > "$OUT/stock.json" 2>/dev/null &
    $PYTHON "$QUANT" global_overview > "$OUT/global.json" 2>/dev/null &
    ;;
  morning)
    $PYTHON "$QUANT" global_overview > "$OUT/global.json" 2>/dev/null &
    $PYTHON "$QUANT" northbound_flow > "$OUT/northbound.json" 2>/dev/null &
    ;;
  macro)
    $PYTHON "$QUANT" global_overview > "$OUT/global.json" 2>/dev/null &
    $PYTHON "$QUANT" northbound_flow > "$OUT/northbound.json" 2>/dev/null &
    ;;
esac

wait

echo "{"
first=1
for f in "$OUT"/*.json; do
  name=$(basename "$f" .json)
  [ $first -eq 0 ] && echo ","
  echo "\"$name\": $(cat "$f")"
  first=0
done
echo "}"

rm -rf "$OUT"
