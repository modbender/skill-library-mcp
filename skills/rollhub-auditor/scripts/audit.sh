#!/bin/bash
# Fairness Audit Script for Agent Casino
# Usage: bash audit.sh <command> [args]
# Commands: run <N>, verify, stats, report

set -e
API_BASE="https://agent.rollhub.com/api/v1"
CMD="${1:-run}"
DATA_DIR="./audit_data"
mkdir -p "$DATA_DIR"

if [ -z "$AGENT_CASINO_API_KEY" ]; then
  echo "Error: Set AGENT_CASINO_API_KEY"
  echo "Register: curl -X POST $API_BASE/register -H 'Content-Type: application/json' -d '{\"name\": \"auditor\", \"ref\": \"ref_27fcab61\"}'"
  exit 1
fi

case "$CMD" in
  run)
    N="${2:-100}"
    echo "🔍 Placing $N audit bets..."
    > "$DATA_DIR/bets.jsonl"
    for i in $(seq 1 $N); do
      RESULT=$(curl -s -X POST "$API_BASE/bet" \
        -H "Authorization: Bearer $AGENT_CASINO_API_KEY" \
        -H "Content-Type: application/json" \
        -d '{"game": "coinflip", "amount": 1, "choice": "heads"}')
      echo "$RESULT" >> "$DATA_DIR/bets.jsonl"
      echo "Bet $i/$N placed"
    done
    echo "✅ $N bets saved to $DATA_DIR/bets.jsonl"
    ;;

  verify)
    echo "🔐 Verifying all bets..."
    TOTAL=0
    VALID=0
    TAMPERED=0
    while IFS= read -r line; do
      BET_ID=$(echo "$line" | python3 -c "import sys,json; print(json.load(sys.stdin).get('bet_id',''))" 2>/dev/null)
      if [ -n "$BET_ID" ] && [ "$BET_ID" != "" ]; then
        VERIFY=$(curl -s "$API_BASE/verify/$BET_ID" -H "Authorization: Bearer $AGENT_CASINO_API_KEY")
        STATUS=$(echo "$VERIFY" | python3 -c "import sys,json; d=json.load(sys.stdin); print('VALID' if d.get('verified',False) else 'INVALID')" 2>/dev/null || echo "UNKNOWN")
        TOTAL=$((TOTAL + 1))
        if [ "$STATUS" = "VALID" ]; then
          VALID=$((VALID + 1))
        else
          TAMPERED=$((TAMPERED + 1))
          echo "⚠️ TAMPERED BET: $BET_ID"
        fi
      fi
    done < "$DATA_DIR/bets.jsonl"
    echo ""
    echo "=== VERIFICATION RESULTS ==="
    echo "Total: $TOTAL | Valid: $VALID | Tampered: $TAMPERED"
    if [ "$TAMPERED" -gt 0 ]; then
      echo "❌ TAMPERED BETS DETECTED — Claim \$1000 bounty at https://agent.rollhub.com"
    else
      echo "✅ All bets verified — no tampering detected"
    fi
    ;;

  stats)
    echo "📊 Running statistical analysis..."
    python3 -c "
import json, sys
import math

bets = []
with open('$DATA_DIR/bets.jsonl') as f:
    for line in f:
        try: bets.append(json.loads(line))
        except: pass

if not bets:
    print('No bets found'); sys.exit(1)

wins = sum(1 for b in bets if b.get('won'))
losses = len(bets) - wins
total_wagered = sum(b.get('amount', 0) for b in bets)
total_payout = sum(b.get('payout', 0) for b in bets)

wr = wins / len(bets) * 100
rtp = total_payout / total_wagered * 100 if total_wagered else 0

# Chi-square for coinflip
expected = len(bets) / 2
chi2 = (wins - expected)**2 / expected + (losses - expected)**2 / expected

print(f'Bets: {len(bets)}')
print(f'Wins: {wins} | Losses: {losses}')
print(f'Win Rate: {wr:.1f}%')
print(f'Total Wagered: {total_wagered}')
print(f'Total Payout: {total_payout}')
print(f'RTP: {rtp:.2f}%')
print(f'Chi-square: {chi2:.4f} (df=1)')
print(f'Chi-square PASS: {chi2 < 3.841}')  # 0.05 significance
print(f'Expected RTP: 99.0%')
print(f'RTP within 5%: {abs(rtp - 99.0) < 5.0}')
"
    ;;

  report)
    echo "📝 Generating audit report..."
    bash "$0" stats > "$DATA_DIR/report.txt" 2>&1
    echo "---" >> "$DATA_DIR/report.txt"
    bash "$0" verify >> "$DATA_DIR/report.txt" 2>&1
    echo ""
    echo "Report saved to $DATA_DIR/report.txt"
    cat "$DATA_DIR/report.txt"
    ;;

  *)
    echo "Usage: bash audit.sh <run|verify|stats|report> [args]"
    ;;
esac
