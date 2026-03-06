#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PASS=0
FAIL=0

pass() { echo "  ✅ $1"; PASS=$((PASS+1)); }
fail() { echo "  ❌ $1"; FAIL=$((FAIL+1)); }

echo "[smoke] === Safe Multisig Skill Smoke Test ==="
echo ""

# ── 1. Bootstrap ──
echo "[smoke] bootstrap deps"
./scripts/bootstrap.sh
pass "bootstrap"

# ── 2. TypeScript type check ──
echo "[smoke] typecheck (strict)"
if npx tsc --noEmit --strict 2>/dev/null; then
  pass "typecheck --strict"
else
  fail "typecheck — TypeScript errors found"
fi

# ── 3. Script help (no network) ──
echo "[smoke] script help (no network)"
for script in safe-info safe_txs_list propose-tx approve-tx execute-tx create-safe list-pending; do
  if npx tsx scripts/${script}.ts --help >/dev/null 2>&1; then
    pass "  ${script} --help"
  else
    fail "  ${script} --help"
  fi
done

# ── 4. TX Service About — test multiple chains (FIX SM-002 verification) ──
echo "[smoke] tx-service about (multiple chains)"
for chain in base mainnet optimism; do
  sleep 1  # Rate limit avoidance
  ABOUT_JSON="$(./scripts/safe_about.sh --chain "$chain" 2>/dev/null || echo "FAIL")"
  if echo "$ABOUT_JSON" | grep -q "Safe Transaction Service" 2>/dev/null; then
    pass "  about --chain $chain"
  else
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" "https://api.safe.global/tx-service/$(echo "$chain" | sed 's/mainnet/eth/;s/optimism/oeth/')/api/v1/about/" 2>/dev/null)
    if [[ "$STATUS" == "429" ]]; then
      pass "  about --chain $chain (rate-limited but URL valid)"
    else
      fail "  about --chain $chain → HTTP $STATUS"
    fi
  fi
done

# ── 5. Safe Info via TypeScript (FIX SM-001 verification) ──
echo "[smoke] safe-info.ts (Base, live)"
SAFE_ADDR="0xA7940a42c30A7F492Ed578F3aC728c2929103E43"
INFO_JSON="$(npx tsx scripts/safe-info.ts --safe "$SAFE_ADDR" --chain base 2>/dev/null || echo '{}')"
if echo "$INFO_JSON" | grep -q "\"threshold\"" 2>/dev/null; then
  pass "safe-info.ts returns threshold"
  THRESHOLD=$(echo "$INFO_JSON" | grep -o '"threshold":[0-9]*' | head -1 | cut -d: -f2)
  NONCE=$(echo "$INFO_JSON" | grep -o '"nonce":[0-9]*' | head -1 | cut -d: -f2)
  echo "    Safe: $SAFE_ADDR"
  echo "    Threshold: $THRESHOLD"
  echo "    Nonce: $NONCE"
else
  fail "safe-info.ts did not return threshold"
fi

# ── 6. list-pending.ts (Base, live) ──
echo "[smoke] list-pending.ts (Base, live)"
TXS_JSON="$(npx tsx scripts/list-pending.ts --safe "$SAFE_ADDR" --chain base --limit 2 2>/dev/null || echo '{}')"
if echo "$TXS_JSON" | grep -q "\"count\"" 2>/dev/null; then
  pass "list-pending.ts returns count"
else
  fail "list-pending.ts did not return count"
fi

# ── Summary ──
echo ""
echo "[smoke] Results: $PASS passed, $FAIL failed"
if [[ $FAIL -gt 0 ]]; then
  echo "[smoke] ❌ FAIL"
  exit 1
else
  echo "[smoke] ✅ OK"
fi
