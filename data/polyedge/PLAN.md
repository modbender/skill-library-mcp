# Polymarket Correlation Analyzer

**Project:** Cross-market arbitrage detection for prediction markets
**Status:** Planning → Build → Test → Release

---

## What It Does

Analyzes pairs of Polymarket markets to find mispriced correlations.

**Input:**
```
Market A: "Will Fed cut rates in Q1?" (currently 60%)
Market B: "Will S&P hit 6000 by June?" (currently 35%)
```

**Output:**
```json
{
  "market_a": { "question": "...", "price": 0.60 },
  "market_b": { "question": "...", "price": 0.35 },
  "correlation_estimate": 0.72,
  "expected_price_b": 0.46,
  "mispricing": 0.11,
  "signal": "BUY_YES_B",
  "confidence": "medium",
  "reasoning": "Historical: rate cuts → 70% chance of rally within 6mo"
}
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User / Agent                          │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTP Request
                      ▼
┌─────────────────────────────────────────────────────────┐
│              x402 Payment Layer                          │
│  (Returns 402 if not paid, accepts USDC on Base)        │
└─────────────────────┬───────────────────────────────────┘
                      │ If paid
                      ▼
┌─────────────────────────────────────────────────────────┐
│            Correlation Analyzer                          │
│  1. Fetch both markets from Polymarket API              │
│  2. Classify market types (politics, finance, etc.)     │
│  3. Look up historical correlation patterns             │
│  4. Calculate expected price vs actual                  │
│  5. Generate signal + confidence                        │
└─────────────────────────────────────────────────────────┘
```

---

## Testing Plan

### Phase 1: Unit Tests (Local)

```bash
# Test market fetching
python test_fetch_markets.py

# Test correlation logic
python test_correlation.py

# Test with known historical examples
python test_historical.py
```

**Test cases:**
- [ ] Valid market URLs return data
- [ ] Invalid URLs return clear errors
- [ ] Correlation math is correct (manual verification)
- [ ] Edge cases: closed markets, low liquidity, missing data

### Phase 2: Integration Tests (Local Server)

```bash
# Start local server (no x402)
python server.py --test-mode

# Hit endpoints
curl "http://localhost:8080/analyze?a=market1&b=market2"
```

**Test cases:**
- [ ] Server starts without errors
- [ ] Endpoints return valid JSON
- [ ] Error responses are informative
- [ ] Rate limiting works
- [ ] Timeout handling for slow Polymarket API

### Phase 3: x402 Payment Tests (Testnet)

```bash
# Deploy to Base Sepolia (testnet)
# Use test USDC

curl "https://test.gibson.example.com/analyze?a=...&b=..."
# Should return 402

# Pay with test wallet
x402 pay "https://test.gibson.example.com/analyze?a=...&b=..." --network base-sepolia
```

**Test cases:**
- [ ] 402 response includes correct payment instructions
- [ ] Payment verification works
- [ ] Paid requests return analysis
- [ ] Double-spend protection
- [ ] Refund handling for failed analysis

### Phase 4: Live Testing (Mainnet, Small Stakes)

- Deploy to production VPS
- Fund test wallet with $1 USDC
- Run 20 test calls
- Verify payments received
- Check analysis quality

---

## Security Checklist

### Code Security

- [ ] **No secrets in code** — All keys in environment variables
- [ ] **Input validation** — Sanitize all user inputs
- [ ] **No eval/exec** — Never execute user-provided strings
- [ ] **Dependency audit** — `npm audit` / `pip audit` before release
- [ ] **Rate limiting** — Prevent abuse (max 10 req/min per IP)

### API Security

- [ ] **HTTPS only** — No HTTP endpoints
- [ ] **CORS restricted** — Only allow known origins (or *)
- [ ] **No sensitive data in logs** — Redact wallet addresses in errors
- [ ] **Timeout all external calls** — Max 30s for Polymarket API

### Payment Security

- [ ] **Verify payment on-chain** — Don't trust headers alone
- [ ] **Check payment amount** — Reject underpayments
- [ ] **Idempotency** — Same payment can't unlock multiple requests
- [ ] **Recipient address hardcoded** — Never from user input

### Skill Publishing Security

- [ ] **No credential access** — Skill doesn't read user's .env or configs
- [ ] **Declared permissions** — Clear about what it accesses
- [ ] **Open source** — All code visible for audit
- [ ] **Minimal dependencies** — Only what's necessary
- [ ] **No post-install scripts** — No hidden execution

### Before ClawdHub Release

- [ ] Security self-review (grep for red flags)
- [ ] Test on fresh machine (no local state assumptions)
- [ ] Write clear SKILL.md with honest capability description
- [ ] Include example usage
- [ ] Add contact info for security reports

---

## Revenue Model

| Tier | Price | What You Get |
|------|-------|--------------|
| Free (skill) | $0 | Basic correlation check (2 markets) |
| Paid API | $0.05 | Deep analysis + historical patterns |
| Bulk | $0.03 | 100+ calls/day |

**Projected:**
- 100 calls/day × $0.05 = $5/day = $150/month
- If it's good, agents will use it

---

## Files Structure

```
polymarket-correlation/
├── SKILL.md              # ClawdHub skill file
├── _meta.json            # Skill metadata
├── README.md             # Documentation
├── src/
│   ├── analyzer.py       # Core correlation logic
│   ├── polymarket.py     # Polymarket API client
│   ├── patterns.py       # Historical correlation patterns
│   └── server.py         # x402-enabled HTTP server
├── tests/
│   ├── test_analyzer.py
│   ├── test_api.py
│   └── test_payments.py
├── data/
│   └── correlations.json # Known correlation patterns
└── deploy/
    ├── Dockerfile
    └── docker-compose.yml
```

---

## Timeline

| Phase | Task | Time |
|-------|------|------|
| 1 | Build core analyzer | 1-2 hours |
| 2 | Local testing | 30 min |
| 3 | x402 integration | 1 hour |
| 4 | Deploy to VPS | 30 min |
| 5 | Live testing | 30 min |
| 6 | ClawdHub publish | 15 min |
| 7 | MoltBook announcement | 15 min |

**Total:** ~4-5 hours to ship

---

## Go/No-Go Checklist

Before releasing:

- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] x402 payments work on mainnet
- [ ] Security checklist complete
- [ ] SKILL.md is accurate and honest
- [ ] Tested by at least one other agent (ask on MoltBook?)
- [ ] Bones approves

---

*Let's build this.* 🚀
