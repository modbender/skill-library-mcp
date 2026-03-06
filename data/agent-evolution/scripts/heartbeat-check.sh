#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
EVOLUTION="node $SCRIPT_DIR/evolution.js"

# Check if state exists
if [[ ! -f "$HOME/.openclaw/workspace/.agent-evolution/state.json" ]]; then
  echo '{"status":"not_initialized","message":"Run init first"}'
  exit 0
fi

alerts=$($EVOLUTION detect)
has_alerts=$(echo "$alerts" | node -e "const d=require('fs').readFileSync('/dev/stdin','utf8');console.log(JSON.parse(d).hasAlerts)" 2>/dev/null || echo "false")

stats=$($EVOLUTION stats)
low_weight=$(echo "$stats" | node -e "
  const d=JSON.parse(require('fs').readFileSync('/dev/stdin','utf8'));
  const low=d.rules.filter(r=>r.weight<0.5);
  console.log(JSON.stringify(low.map(r=>({id:r.id,weight:r.weight}))));
" 2>/dev/null || echo "[]")

never_exec=$(echo "$stats" | node -e "
  const d=JSON.parse(require('fs').readFileSync('/dev/stdin','utf8'));
  const ne=d.rules.filter(r=>r.execCount===0);
  console.log(JSON.stringify(ne.map(r=>r.id)));
" 2>/dev/null || echo "[]")

if [[ "$has_alerts" == "true" ]] || [[ "$low_weight" != "[]" ]] || [[ "$never_exec" != "[]" ]]; then
  echo "{\"status\":\"NEEDS_ATTENTION\",\"patternAlerts\":$alerts,\"lowWeightRules\":$low_weight,\"neverExecuted\":$never_exec}"
else
  echo '{"status":"ALL_CLEAR"}'
fi
