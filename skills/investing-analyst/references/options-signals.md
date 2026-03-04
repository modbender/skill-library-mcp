# Options Signals Reference

## IV vs Historical Volatility (HV) Signal

**Why it matters:** IV reflects the market's expected move. HV reflects what the stock has actually done. The gap between them tells you whether options are overpriced or underpriced.

### Signal Interpretation

| Condition | Meaning | Action |
|-----------|---------|--------|
| IV > HV by >20pp | Options EXPENSIVE — market pricing in fear/catalyst | Use spreads (cap premium paid), avoid naked longs |
| IV ≈ HV (±10pp) | Fair value | Long calls acceptable if thesis is clean |
| IV < HV by >10pp | Options CHEAP — market underpricing risk | Long calls, straddles can make sense |

### How to Find IV and HV

- **IV (Implied Volatility):** Your broker's options chain → look at the at-the-money strike for a general read. IV is shown per contract.
- **30-day HV:** Search "[ticker] historical volatility 30 day" or check Barchart.com → Options → Volatility.
- **Black-Scholes check:** Use the template sheet below to compare theoretical price vs. market price.

### Example

- Stock XYZ pre-earnings: IV 85%, HV 62% → IV is 23pp above HV → **EXPENSIVE**
- Decision: Use a call debit spread instead of a naked call. Buying the spread caps the premium you pay for elevated IV.

---

## Black-Scholes Template Sheet

**Make a copy for yourself:**
`https://docs.google.com/spreadsheets/d/1_Q9ZpGzA2zmuaBmE0R2XVdZHpRnWA2PRNSfmpDXf1as/`

→ File → Make a copy → save to your own Google Drive.

**Inputs:**
- S = Current stock price
- K = Strike price
- T = Days to expiration (as fraction: days/365)
- r = Risk-free rate (check current Fed Funds rate)
- σ = Volatility

**Workflow:**
1. Input **market IV** → output should ≈ market price (sanity check)
2. Input **30-day HV** → output = "fair value" based on realized vol
3. Gap between (1) and (2) = vol premium you're paying
4. If vol premium is large (>30%), strongly prefer spreads over naked longs

---

## Expected Move Calculation

The options market implies an expected move for any catalyst:

**Formula:** Expected Move ≈ ATM Call Price + ATM Put Price (the straddle price)

### Interpreting Expected Move

- If expected move = ±8%, your long call break-even must be within that range for a positive EV trade
- If your break-even requires >1.5× the expected move, you need very strong conviction

### Example

- Stock at $50, ATM straddle costs $4.50 → expected move ≈ ±$4.50 (±9%)
- You're considering a $55C (10% OTM) at $1.20 → break-even at expiry = $56.20 (12.4% move)
- Break-even exceeds expected move → needs a blow-out result to be profitable at expiry
- Alternative: close before earnings to avoid IV crush, or use a tighter strike

---

## Pre-Earnings Options Decision Tree

```
Is IV > HV by >15pp?
├── YES → Options expensive. Use spread (buy lower strike, sell higher)
│   ├── Strong conviction → Call debit spread (limits premium, limits upside)
│   └── Weak conviction → Pass. Wait for IV crush opportunity post-earnings
└── NO → IV is fair/cheap
    ├── Clean thesis + ITM/ATM strike → Long call acceptable
    └── OTM strike → Check if break-even is inside 1× expected move
```

## IV Crush Post-Earnings

IV spikes pre-earnings and collapses after the report regardless of direction. If holding calls through earnings:

- Options can lose 30-50% of value from IV crush alone even if the stock goes up modestly
- Hold through earnings only if: (a) you expect a move larger than what IV is pricing, AND (b) you've stress-tested against IV crush

**Rule of thumb:** If expected move post-earnings is +10% and your break-even needs +12%, don't hold through.
