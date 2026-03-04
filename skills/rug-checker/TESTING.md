# Test Plan — Rug Checker

## Prerequisites

```bash
# Verify dependencies
command -v bash && command -v curl && command -v jq && command -v bc && echo "OK"

# Verify API connectivity
curl -s "https://api.rugcheck.xyz/v1/stats/recent" | jq 'length'
curl -s "https://api.dexscreener.com/tokens/v1/solana/DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263" | jq '.[0].baseToken.name'
```

## Test Matrix

| Token | Address | Type | Expected Tier |
|-------|---------|------|---------------|
| BONK | `DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263` | Blue chip meme | 🟢 SAFE |
| USDC | `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v` | Stablecoin | 🟠 WARNING (has compliance authorities) |
| Recent pump.fun | Find via `curl -s "https://api.rugcheck.xyz/v1/stats/new_tokens" \| jq '.[0].mint'` | Brand new token | 🟡-⛔ varies |

## Test 1: Token Detection (detect-token.sh)

### By address (BONK)

```bash
bash scripts/detect-token.sh DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263
```

**Expected:** JSON with `found: true`, `name: "Bonk"`, `symbol: "Bonk"`, non-zero market data.

### By name search

```bash
bash scripts/detect-token.sh bonk
```

**Expected:** JSON with `found: true`, resolves to a BONK address, non-zero liquidity.

### Invalid address

```bash
bash scripts/detect-token.sh invalidaddress123
```

**Expected:** DexScreener search attempt (treated as name). If nothing found, JSON with `found: false`.

### No arguments

```bash
bash scripts/detect-token.sh
```

**Expected:** Usage help printed to stderr, exit code 1.

## Test 2: Risk Analysis (analyze-risk.sh)

### BONK (blue chip, expected: SAFE)

```bash
bash scripts/analyze-risk.sh DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263 2>/dev/null | jq '{tier, score: .composite_score, checks_count: (.checks | length)}'
```

**Expected:**
```json
{
  "tier": "SAFE",
  "score": 10-20,
  "checks_count": 10
}
```

**Verify:**
- Mint Authority: score 0 (revoked)
- Freeze Authority: score 0 (none)
- LP Lock: score 0 (100% locked)
- Verification: score 0 (Jupiter strict)
- All 3 data sources: true

### USDC (stablecoin, expected: WARNING)

```bash
bash scripts/analyze-risk.sh EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v 2>/dev/null | jq '{tier, score: .composite_score, name: .token.name, symbol: .token.symbol}'
```

**Expected:**
```json
{
  "tier": "WARNING",
  "score": 40-55,
  "name": "USD Coin",
  "symbol": "USDC"
}
```

**Verify:**
- Mint Authority: score 10 (Circle has mint authority — expected for stablecoin)
- Freeze Authority: score 9 (Circle has freeze authority — expected for compliance)
- Name/symbol falls back to DexScreener data (Rugcheck returns empty for USDC)
- Holder Concentration: acknowledges data unavailability (not "well distributed")
- LP Lock: acknowledges data unavailability (not "LP NOT locked")

### New pump.fun token

```bash
PUMP_TOKEN=$(curl -s "https://api.rugcheck.xyz/v1/stats/new_tokens" | jq -r '.[0].mint')
bash scripts/analyze-risk.sh "$PUMP_TOKEN" 2>/dev/null | jq '{tier, score: .composite_score, checks: [.checks[] | {name, score}]}'
```

**Expected:**
- Composite score > 15 (should NOT be SAFE for a brand-new token)
- Token Age check: score ≥ 8 (very new)
- Verification: score 4 (not on Jupiter)

## Test 3: Report Formatting (format-report.sh)

### Pipe from analyze-risk

```bash
bash scripts/analyze-risk.sh DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263 2>/dev/null | bash scripts/format-report.sh
```

**Verify:**
- Box header renders with token name and score
- Market overview table has non-N/A values
- All 10 checks listed with bars and scores
- Composite score bar aligns with score
- Data sources table shows ✅ for all three
- Links section has 4 working URLs
- Disclaimer present at bottom

### From file

```bash
bash scripts/analyze-risk.sh DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263 2>/dev/null > /tmp/test-report.json
bash scripts/format-report.sh /tmp/test-report.json
```

**Expected:** Same output as piped version.

### Invalid JSON

```bash
echo "not json" | bash scripts/format-report.sh
```

**Expected:** "ERROR: Invalid JSON input" on stderr, exit code 1.

### No input

```bash
bash scripts/format-report.sh
```

**Expected:** Usage help on stderr, exit code 1.

## Test 4: Edge Cases

### Token with no DexScreener data

Some very new tokens won't have DexScreener listings yet. The tool should:
- Still produce a report using Rugcheck + RPC data
- Token Age should show "unknown" (not crash)
- Liquidity should degrade gracefully

### All APIs down (simulate)

```bash
CF_HTTP_TIMEOUT=1 bash scripts/analyze-risk.sh DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263 2>/dev/null
```

With a 1-second timeout, if all APIs fail the tool should output JSON with `"composite_score": -1` and `"tier": "UNKNOWN"`.

## Test 5: Rate Limiting

```bash
# Run 5 rapid requests — should not trigger 429 errors
for i in $(seq 1 5); do
  bash scripts/detect-token.sh DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263 2>/dev/null | jq -r '.found'
done
```

**Expected:** All return `true` without rate-limit warnings.

## Actual Test Results (2026-02-15)

### BONK
- **detect-token.sh:** ✅ `found: true`, name: "Bonk", symbol: "Bonk"
- **analyze-risk.sh:** ✅ Score: 12/100, Tier: SAFE
  - Mint Authority: 0/10 (revoked) ✅
  - Freeze Authority: 0/10 (none) ✅
  - LP Lock: 0/10 (100% locked) ✅
  - Verification: 0/10 (Jupiter strict) ✅
  - All 3 data sources active ✅
- **format-report.sh:** ✅ Clean render, all sections present

### USDC
- **analyze-risk.sh:** ✅ Score: 46/100, Tier: WARNING
  - Name: "USD Coin" (DexScreener fallback works) ✅
  - Symbol: "USDC" ✅
  - Mint Authority: 10/10 (BJE5MMbq… — Circle) ✅
  - Freeze Authority: 9/10 (7dGbd2QZ… — Circle) ✅
  - Holder Concentration: "data unavailable" (correct for USDC) ✅
  - LP Lock: "No DEX market data" (correct for USDC on Rugcheck) ✅
- **format-report.sh:** ✅ Clean render

### Pump.fun Token (Cuckmaxxing / Wheelchair Fish)
- **analyze-risk.sh:** ✅ Score: 23-29/100, Tier: CAUTION
  - Creator history of rugged tokens flagged ✅
  - Token age: "Very new (<24 hours)" ✅
  - Rugcheck flags surfaced correctly ✅

### Bugs Found and Fixed
1. Holder Concentration: raw float in reason → formatted to 1 decimal place
2. Holder Concentration: 0 topHolders marked "well distributed" → now flags as data gap
3. Liq/FDV ratio: leading dot (`.2500%`) → formatted (`0.25%`)
4. Token name fallback: "Unknown" when Rugcheck has no data → falls back to DexScreener
5. LP Lock: 0 markets treated as "LP NOT locked" → "No DEX market data available"
6. epoch_ms_to_age: undefined variable `diff_days_rem` → fixed inline
